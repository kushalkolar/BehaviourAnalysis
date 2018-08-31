# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 10:02:53 2018

@author: install
"""


import pandas as pd
import os
from multiprocessing import Pool

class DataHandler:
    def __init__(self, path):
        self.path = path
        self.folders = [os.path.join(self.path, x) for x in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, x))]

        self.common_metadata_frame = "None"

    def calculate_all_parameters(self):

        if __name__ == "__main__":
            for folder in self.folders:
                if "dataframes" not in folder.lower():
                    self._calculate_parameters(folder)



    def _calculate_parameters(self, folder):
        metadata_path = os.path.join(folder, "metadata.txt")
        metadata = pd.read_csv(metadata_path, delimiter = "\t")
        if "path" not in metadata.columns:
            metadata["path"] = metadata_path
            metadata.to_csv(metadata_path, sep = "\t")

        tracking_data_file = [x for x in os.listdir(os.path.join(self.path, folder)) if "tracking" in x.lower()][0]
        tracking_data_file = os.path.join(folder, tracking_data_file)
        tracking_data = pd.read_csv(tracking_data_file, delimiter = "\t", names = ["Frame", "Arena", "Track", "X","Y","Label"])
        tracks = []
        for t in tracking_data.Track:
            if t not in tracks:
                tracks.append(t)
                

        crowdsize = int(folder.split("_")[3])
        if len(tracks) > crowdsize:
            print("Tracecount exceeded animal count for "+folder)
            print('\n')
            print("crowdsize = ", crowdsize, " tracecount = ", len(tracks))

        else:
            if type(self.common_metadata_frame) == type("None"):
                cols = metadata.columns
                self.common_metadata_frame = pd.DataFrame(data = None, columns=cols)
            
            self.common_metadata_frame = pd.concat([self.common_metadata_frame, metadata], axis=0, join="outer",
                                                   join_axes=None, ignore_index=False)
            for t in tracks:
                df = pd.DataFrame()
                df["Frame"] = tracking_data["Frame"].loc[tracking_data.Track == t]
                df["X"] = tracking_data["X"].loc[tracking_data.Track == t]
                df["Y"] = tracking_data["Y"].loc[tracking_data.Track == t]
                savename = "dataframe_"+str(t)+".txt"
                df.to_csv(os.path.join(os.path.abspath(folder), savename), sep = "\t")

        return(folder)




