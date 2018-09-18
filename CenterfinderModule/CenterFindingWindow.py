# -*- coding: utf-8 -*-

"""
Created on Mon Feb  5 13:20:50 2018

@author: ddo003
"""

from CenterfinderModule.centerfinder_ui import Ui_Form
from CenterfinderModule.CenterFinder import Centerfinder
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from threading import Thread
import numpy as np
import pandas as pd
import pyqtgraph
import sys, os
from tqdm import tqdm



class CenterFindingWindow(QtWidgets.QWidget):
    def __init__(self, parent = None, *args, data_path = False, project_path, selection = False):
        QtWidgets.QWidget.__init__(self, parent, *args)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowTitle("CenterFinder")
        self.setWindowIcon(QtGui.QIcon("icons/centerfinder.png"))
        self.data_path = data_path
        if self.data_path == False:
            self.data_path = QtWidgets.QFileDialog.getExistingDirectory(caption = "Select directory or drive that contains the video files you are working with")
        
        self.all_videos = [os.path.join(root, f) for root, dirs, files in os.walk(self.data_path) for f in files if ".avi" in f]
    
        self.project_path = project_path
        self.vid_dict = {}
        self.videos_done = []
        
        self.selection = selection

        self.ui.comboBoxThresholdMethod.addItem("NONE")
        self.ui.comboBoxThresholdMethod.addItem("BINARY")
        self.ui.comboBoxThresholdMethod.addItem("TOZERO")
        self.ui.comboBoxThresholdMethod.currentTextChanged.connect(self.check_thresholding_method)


        self.ui.comboBoxThresholdMethod.currentIndexChanged.connect(self.find_video_center)
        self.ui.pushButtonRedoCenter.clicked.connect(self.find_video_center)

        self.ui.listWidgetVideos.itemSelectionChanged.connect(self.find_video_center)
        self.ui.listWidgetVideos.itemDoubleClicked.connect(self.find_video_center)

        self.ui.pushButtonStartStop.clicked.connect(self.start_stop)

        self.check_thresholding_method(self.ui.comboBoxThresholdMethod.currentText())
        self.counter = 0

        for item in self.selection:
            to_add = QtGui.QListWidgetItem(item.text(0))
            to_add.setData(1,item.text(1))
            self.ui.listWidgetVideos.addItem(to_add)
        
#        for root, dirs, files in os.walk(self.data_path):
#            for f in files:
#                if ".avi" in f.lower():
#                    if "inverted" in f.lower():
#                        destination_path = os.path.join(self.project_path, "Exp_" + f[:-13])
#                    else:
#                        destination_path = os.path.join(self.project_path, "Exp_" + f)
#                        destination_path = destination_path.rstrip(".avi")
#                    if os.path.exists(destination_path):
#                        self.vid_dict[f] = os.path.join(root, f)
#                        self.ui.listWidgetVideos.addItem(f)

    def check_thresholding_method(self, text):
        if text.lower() == "none":
            self.ui.spinBoxThreshold.setEnabled(False)
        else:
            self.ui.spinBoxThreshold.setEnabled(True)


    def find_video_center(self):
        destination_path = self.ui.listWidgetVideos.currentItem().data(1)
        path_to_raw_data = os.path.join(destination_path, "path_to_raw_data.txt")
        with open(path_to_raw_data, "r") as f:
            path_to_raw_data = f.readlines()[0]
        vid = [os.path.join(path_to_raw_data, x) for x in os.listdir(path_to_raw_data) if ".avi" in x][0]
#        vid = self.ui.listWidgetVideos.currentItem().text()
#        item = self.ui.listWidgetVideos.findItems(vid, QtCore.Qt.MatchExactly)[0]
#        print(vid)

        try:
            circles = self.find_center(vid)
            x,y,r = circles

#            if "inverted" in vid.lower():
#                destination_path = os.path.join(self.project_path, "Exp_"+vid[:-13])
#            else:
#                destination_path = os.path.join(self.project_path, "Exp_" + vid)
#                destination_path = destination_path.rstrip(".avi")

            if not os.path.exists(destination_path):
                print("No path exists for ", vid)

            with open(os.path.join(destination_path, "center.txt"), "w") as f:
                f.write("X\tY\tR\n")
                for param in [x,y,r]:
                    f.write(str(param)+"\t")
            self.ui.listWidgetVideos.currentItem().setBackground(QtGui.QColor("lightgreen"))
            self.corner_correction(destination_path)
            self.videos_done.append(vid)
        except Exception as e:
            print(e)
            self.ui.listWidgetVideos.currentItem().setBackground(QtGui.QColor("red"))




    def find_center(self, path):
        cf = Centerfinder(minRadius=self.ui.spinBoxminRadius.value(),
                          maxRadius=self.ui.spinBoxmaxRadius.value(),
                          param1=self.ui.spinBoxparam1.value(),
                          param2=self.ui.spinBoxparam2.value(),
                          threshold=self.ui.spinBoxThreshold.value(),
                          thresholdmethod = self.ui.comboBoxThresholdMethod.currentText(),
                          iterations = self.ui.spinBoxIterations.value(),
                          weight = self.ui.spinBoxContrastWeight.value(),
                          gamma=self.ui.spinBoxGamma.value())


        circles = cf.find(path, show_result=True)
        return circles

    def corner_correction(self, path):
        files = os.listdir(path)

        arena_file = os.path.join(path, [f for f in files if "arena" in f.lower()][0])
        with open(arena_file, "r") as f:
            arena_corners = f.readlines()[1].strip("\n").split("\t")[:2]
        arena_x = int(arena_corners[0])
        arena_y = int(arena_corners[1])

        center_file = os.path.join(path, [f for f in files if "center" in f.lower()][0])

        with open(center_file, "r") as f:
            center = f.readlines()[1].strip("\n").split("\t")
        center_x = int(center[0])
        center_y = int(center[1])
        center_r = int(center[2])

        center_x_adj = center_x - arena_x
        center_y_adj = center_y - arena_y

        meta_df_file = os.path.join(path, "metadata.txt")
        meta_df = pd.read_csv(meta_df_file,  delimiter = "\t")

        meta_df["center_x_adj"] = [center_x_adj]
        meta_df["center_y_adj"] = [center_y_adj]
        meta_df["center_x"] = [center_x]
        meta_df["center_y"] = [center_y]
        meta_df["center_r"] = [center_r]
        meta_df.to_csv(os.path.join(path, "metadata.txt"), sep = "\t")



    def start_stop(self):
        if self.ui.pushButtonStartStop.isChecked():
            self.ui.pushButtonStartStop.setText("Pause")
            t = Thread(target = self.automatic)
            t.start()

        else:
            self.ui.pushButtonStartStop.setText("Start")
            self.alive = False

    def automatic(self):
        self.alive = True
        to_do = []
        while self.alive:
            for x in range(np.max([self.ui.listWidgetVideos.currentRow(),0]), self.ui.listWidgetVideos.count()):
                vid = self.ui.listWidgetVideos.item(x)

                if self.alive:
                    self.ui.listWidgetVideos.setCurrentItem(vid)
                    self.find_video_center()

                else:
                    break


            self.alive = False
            self.ui.pushButtonStartStop.setText("Start")
            self.ui.pushButtonStartStop.setChecked(False)
