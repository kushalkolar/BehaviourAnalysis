# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 10:02:53 2018

@author: install
"""



import os
import pickle
import sys
import time
import subprocess
from threading import Thread
import psutil
from pyqtgraph import QtCore, QtGui
import pandas as pd
import numpy as np
from tqdm import tqdm

class WaitingThread(QtCore.QThread):
    def __init__(self, object_to_guard):
        QtCore.QThread.__init__(self)
        self.object_to_guard = object_to_guard
        self.my_signal = QtCore.pyqtSignal()

    def run(self):
        while self.object_to_guard.alive:
            self.my_signal.emit()
            time.sleep(0.5)



class DataHandler:
    def __init__(self, path, selection = False,  calibration_factor = 0):
        
        self.path = path
            
        if selection:
            self.folders = selection
        else:
            self.folders = [os.path.join(self.path, x) for x in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, x)) and "exp" in x.lower()]

            
        self.calibration_factor = calibration_factor
        
    def calculate_all_parameters(self):
        self.alive = True
        self.work_thread = Thread(target = self._start_subprocess)
        self.work_thread.start()

        self.timer_thread = Thread(target=self._start_timer, args = (self.work_thread,))
        self.timer_thread.start()

    def _start_timer(self, t):
        to_do = len(self.folders)
        pb_length = 50
        start_time = time.time()
        while t.isAlive():
            self.elapsed = time.time() - start_time
            self.cpu = psutil.cpu_percent()
            done = len([os.path.join(root, f) for root, dirs, files in os.walk(self.path) for f in files if "dataframe" in f and os.path.getmtime(os.path.join(root, f)) > start_time])
            percentage_done = (done/to_do)* 100
            try:
                etc = time.strftime("%H:%M:%S", time.gmtime((self.elapsed/(percentage_done)*100) - self.elapsed))
            except:
                etc = time.strftime("%H:%M:%S", time.gmtime((self.elapsed/(0.0000001)*100) - self.elapsed))

            sys.stdout.write("\rTime spent "+time.strftime('%H:%M:%S', time.gmtime(self.elapsed)) +
                             " ETC: "+etc+
                             " CPU: "+str(self.cpu).zfill(4)+
                             "%  Progress: ["+"#"*int(pb_length*(percentage_done/100))+"-"*int(pb_length-(pb_length*(percentage_done/100)))+"] "+
                             str(np.round(percentage_done, 1))+"%    "+
                             str(done)+"/"+str(len(self.folders))+"      ")

            time.sleep(0.1)
        self.alive = False
        sys.stdout.write("\n Calculating Parameters Finished \n")
        sys.stdout.write("\n Gathering Data for Metadataframe\n")
        self.gather_common_dataframe()


        
    
    def _start_subprocess(self):
        pickle_path = os.path.join(self.path, "to_do.pickle")
        with open(pickle_path, "wb") as f:
            print("pickling....")
            pickle.dump(self.folders, f)
        try:
            print("starting subprocess")
            p = subprocess.Popen(["python", 'DataHandling/work_process.py', pickle_path], stdin = subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            p.communicate()
        except Exception as e:
            print(e)

    def gather_common_dataframe(self):
        # metadataframes = [pd.read_csv(os.path.join(folder, "metadata.txt"), delimiter = "\t") for folder in self.folders for x in os.listdir(folder) if "dataframe" in x.lower()]
        # for df in tqdm(metadataframes, desc = "Gathering all individual metadataframes"):
        #     to_drop = [x for x in df.columns if "unnamed" in x.lower()]
        #     df.drop(to_drop, axis = 1, inplace = True)
        #
        # dataframes = [pd.read_csv(os.path.join(folder, x), delimiter = "\t") for folder in self.folders for x in os.listdir(folder) if "dataframe" in x.lower()]
        #
        # columns = []
        # for df in tqdm(dataframes, desc = "Gathering all column descriptors"):
        #     for col in df.columns:
        #         if col != "X" or col != "Y" or col != "X_zero" or col != "Y_zero":
        #             if col not in columns:
        #                 columns.append(col)
        #
        # params = ["mean", "median", "min", "max"]
        # col_dict = {}
        # for param in params:
        #     for col in columns:
        #         col_dict[col+"_"+param] = []
        #
        # for df in tqdm(dataframes, desc = "Gathering all single-value and metadata descriptors"):
        #     for col in columns:
        #         col_dict[col+"_mean"].append(df[col].mean())
        #         col_dict[col+"_median"].append(df[col].median())
        #         col_dict[col+"_min"].append(df[col].min())
        #         col_dict[col+"_max"].append(df[col].max())


        """
        FOLLOWING BLOCK IS PROGRESS ON IMPROVING THIS METHOD
        """
        metadataframes = []
        for folder in tqdm([os.path.join(self.path, x) for x in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, x)) and "exp" in x.lower()], desc="Gathering all single-value and metadata descriptors"):

            for f in os.listdir(folder):
                if "dataframe" in f.lower() and "pickle" in f.lower():
                    df = pd.read_pickle(os.path.join(folder, f))
                    metadataframe = pd.read_csv(os.path.join(folder, "metadata.txt"), delimiter="\t")
                    for col in df.columns:
                        if col not in ["X","Y","X_zero","Y_zero","time","Frame", "stim_on"]:
                            metadataframe[col + "_mean"] = [df[col].mean()]
                            metadataframe[col + "_median"] = [df[col].median()]
                            metadataframe[col + "_min"] = [df[col].min()]
                            metadataframe[col + "_max"] = [df[col].max()]

                    metadataframe["percentage_notnull"] = [len(df.X.notnull()) / len(df)]


                    stims = pd.read_csv(os.path.join(folder, "stimuli_profile.txt"), delimiter="\t")

                    try:
                        if len(stims) > 0:
                            counter = 1
                            for ii in stims.index:
                                time_on = stims.time_on[ii]
                                time_off = stims.time_off[ii]
                                stimname = stims.message_on[ii]
                                for col in df.columns:
                                    if col not in ["X", "Y", "X_zero", "Y_zero", "time", "Frame", "stim_on"]:
                                        delta_on = (df[col][(df["time"]>= time_on) & (df["time"] <= time_on+30)].mean())-(df[col][(df["time"]>= time_on - 30) & (df["time"] <= time_on)].mean())
                                        delta_off = (df[col][(df["time"]>= time_off) & (df["time"] <= time_off+30)].mean())-(df[col][(df["time"]>= time_off - 30) & (df["time"] <= time_off)].mean())

                                        metadataframe["deltaOn_"+stimname+"_"+col+"_"+str(counter).zfill(2)] = [delta_on]
                                        metadataframe["deltaOff_"+stimname+"_"+col+"_"+str(counter).zfill(2)] = [delta_off]
                                counter+=1
                    except Exception as e:
                        print(e)

                    metadataframe["stimuli"] = [len(stims)]
                    metadataframe["stimuli_profile"] = [stims]
                    metadataframe["temperaturepath"] = [os.path.join(folder, "logged_temperatures.txt")]
                    metadataframes.append(metadataframe)
                    if "crowdsize" not in metadataframe.columns:
                        metadataframe["crowdsize"] = [int(folder.split("_")[3])]

                    if "exposture" in metadataframe.columns:
                        metadataframe.rename(columns = {"exposture":"exposure"}, inplace = True)



        self.metadataframe = pd.concat(metadataframes, sort = True, ignore_index=True)
        to_drop = [x for x in self.metadataframe.columns if "unnamed" in x.lower()]
        self.metadataframe.drop(to_drop, axis=1, inplace=True)
        if not os.path.exists(os.path.join(self.path, "dataframes")):
            os.mkdir(os.path.join(self.path,  "dataframes"))
        self.metadataframe.to_pickle(os.path.join(self.path, "dataframes\\common_data.pickle"))

        # for key in col_dict.keys():
        #     self.metadataframe[key] = col_dict[key]
        #
        # for folder in tqdm(self.folders, desc = "Adding Stimuli information to metadataframe"):
        #     lightstim = pd.read_csv(os.path.join(folder))












