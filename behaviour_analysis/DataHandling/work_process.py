import sys
import multiprocessing
import pickle
import os
import pandas as pd
import numpy as np

np.warnings.filterwarnings("ignore")


from sklearn.preprocessing import scale


def lH(trace, window):
    lH = np.zeros(window)
    lH[:] = np.nan
    for ii in range(len(trace) - window):
        try:
            M = trace[["X_zero", "Y_zero"]].loc[ii:ii + window]
            if len(M.dropna()) == len(M):

                #                 M = M- M.mean(axis = 0)

                Mx = M.X_zero.values.reshape(-1, 1)
                My = M.Y_zero.values.reshape(-1, 1)

                Mx = scale(Mx)
                My = scale(My)

                M = np.dstack([Mx, My])

                U, S, V = np.linalg.svd(M)

                hats_array = S / S.sum()

                H = -np.sum(hats_array * np.log2(hats_array))
                lH = np.hstack((lH, H))

            else:
                lH = np.hstack((lH, np.nan))
        except Exception as e:
            print(e)
            lH = np.hstack((lH, np.nan))
    return (lH)


def cart2pol(x, y):
    rho = np.sqrt(x ** 2 + y ** 2)
    phi = np.arctan2(y, x)
    return rho, phi


def _calculate_parameters(folder):
    try:
        sys.stdout.write(folder+ "\n")
        metadata_path = os.path.join(folder, "metadata.txt")
        metadata = pd.read_csv(metadata_path, delimiter="\t")
#        temperatures = pd.read_csv(os.path.join(folder, "logged_temperatures.txt"), delimiter = "\t")

        if "metadatapath" not in metadata.columns:
            metadata["metadatapath"] = metadata_path
            metadata.to_csv(metadata_path, sep="\t")

        tracking_data_file = [x for x in os.listdir(folder) if "tracking" in x.lower()][0]
        tracking_data_file = os.path.join(folder, tracking_data_file)
        tracking_data = pd.read_csv(tracking_data_file, delimiter="\t",
                                    names=["Frame", "Arena", "Track", "X", "Y", "Label"])
        tracks = []
        for t in tracking_data.Track:
            if t not in tracks:
                tracks.append(t)

        crowdsize = int(folder.split("_")[3])
        if len(tracks) > crowdsize:
            print("Tracecount exceeded animal count for " + folder)
            print('\n')
            print("crowdsize = ", crowdsize, " tracecount = ", len(tracks))

        else:
            # if type(self.common_metadata_frame) == type("None"):
            #     cols = metadata.columns
            #     self.common_metadata_frame = pd.DataFrame(data = None, columns=cols)
            #
            # self.common_metadata_frame = pd.concat([self.common_metadata_frame, metadata], axis=0, join="outer",
            #                                        join_axes=None, ignore_index=False)
            for t in tracks:
                df = pd.DataFrame()
                df["Frame"] = tracking_data["Frame"].loc[tracking_data.Track == t]
                df["time"] = df["Frame"] / metadata.framerate[0]
                df["X"] = tracking_data["X"].loc[tracking_data.Track == t]
                df["Y"] = tracking_data["Y"].loc[tracking_data.Track == t]

                df = df.iloc[1:]

                df["X"] = df["X"] - metadata.center_x_adj[0]
                df["Y"] = df["Y"] - metadata.center_y_adj[0]


                calibration_factor = 6000 / metadata.center_r[0]

                df["X_zero"] = df["X"] * calibration_factor
                df["Y_zero"] = df["Y"] * calibration_factor

                spacer_frame = pd.DataFrame({"Frame": range(df.Frame.iloc[-1])})
                df = pd.merge(spacer_frame, df, how="outer", on="Frame")
                
                coords = np.hstack((df.X_zero.values.reshape(-1, 1), df.Y_zero.values.reshape(-1, 1)))
                df["from_center"] = np.linalg.norm(np.array([0, 0]) - coords, axis=1)

                for p in [1,5,30]:
                    dists = np.linalg.norm(coords[p:] - coords[:-p], axis=1)
                    spacer = np.zeros(p)
                    spacer[:] = np.nan
                    pstring = str(p).zfill(3)
                    df["distances" + pstring] = np.hstack((spacer, dists))
                    df["rho"+ pstring], df["phi"+ pstring] = cart2pol(df.X_zero.diff(periods = p), df.Y_zero.diff(periods = p))
                    df["speed" + pstring] = (df["distances" + pstring] / (1 / metadata.framerate[0])) / p
                    df["acceleration" + pstring] = df["speed" + pstring].diff()
                    turns = np.array(df["phi"+ pstring].diff(periods=p))
                    turns[turns > np.pi] -= 2 * np.pi
                    turns[turns < -np.pi] += 2 * np.pi
                    df["turn" + pstring] = turns

                #Displacement calculated from first not-nan coordinate.
                # nan = np.where(np.isnan(coords[:,0]))[0] #get indices of nans from coords
                #
                # if np.any(nan == 0): #if the first value is indeed nan, find first not nan
                #     nan_diff = np.diff(nan)  #take differences, each time the diff is >1 there have been actual values in between
                #     first_not_nan = np.where(nan_diff > 1)[0][0] + 1 #first place there is a diff>1 in indices of nans is the place the first non-nan item is.
                # else:
                #     first_not_nan = 0 #if zero not found in indiced of nans zeroth index is not nan then this can be used.

                #the following three lines do a better job at the same task than the previous 10.
                first_not_nan =  0
                while np.isnan(coords[first_not_nan, 0]):
                    first_not_nan+=1

                df["displacement"] = np.linalg.norm(coords[first_not_nan] - coords, axis = 1)

                roaming = np.zeros(shape = len(df))
                roaming_index = df.loc[(df["speed030"] > 500) & (df["turn005"].diff() < 1.2)].index
                roaming[roaming_index] = 1
                df["roaming"] = roaming

                complexity = lH(df, 30)
                df["lH"] = complexity

                to_drop = [x for x in df.columns if "unnamed" in x.lower()]
                df.drop(to_drop, axis = 1, inplace = True)

                stims = pd.read_csv(os.path.join(folder, "stimuli_profile.txt"), delimiter = "\t")
                if len(stims) > 0:
                    df["stim_on"] = ["off" for x in range(len(df))]
                    for ii in stims.index:
                        time_on = stims.time_on[ii]
                        time_off = stims.time_off[ii]
                        df.loc[(df.time >= time_on) & (df.time <= time_off), "stim_on"] = stims.message_on[ii]

                savename = "dataframe_" + str(t) + ".pickle"
                df.to_pickle(os.path.join(os.path.abspath(folder), savename))

                if savename not in metadata.columns:
                    metadata["dataframepath"] = os.path.join(os.path.abspath(folder), savename)
                    metadata.to_csv(metadata_path, sep="\t")


        return (folder)
    except Exception as e:
        print(e)
        return(folder)



if __name__ == "__main__":
    sys.stdout.write("Starting processing pool \n")
    pickle_file = sys.argv[1]
    n_threads = int(sys.argv[2])
    with open(pickle_file, "rb") as f:
        to_do = pickle.load(f)
    print("loaded pickle \n")
    os.remove(pickle_file)

    to_do = [x for x in to_do if "exp" in x.lower()]

    p = multiprocessing.Pool(n_threads)

    results = p.map(_calculate_parameters, to_do)

    p.terminate()
    p.close()




