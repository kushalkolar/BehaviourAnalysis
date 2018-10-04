# -*- coding: utf-8 -*-

"""
Created on Mon Feb  5 13:20:50 2018

@author: ddo003
"""

from CenterfinderModule.centerfinder_with_graphics import Ui_Form
from CenterfinderModule.CenterFinder import Centerfinder
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from threading import Thread
import numpy as np
import pandas as pd
import cv2
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

        self.ui.graphicsView.ui.menuBtn.hide()
        self.ui.graphicsView.ui.roiBtn.hide()
        # self.ui.graphicsView.ui.histogram.hide()

        self.ui.pushButtonOverwrite.setEnabled(True)
        self.show()
        self.ui.pushButtonOverwrite.clicked.connect(self.overwrite_center)
        self.ui.checkBoxOverwrite.clicked.connect(self.toggle_overwrite)
        self.overwrite = False
        self.data_path = data_path
        if self.data_path == False:
            self.data_path = QtWidgets.QFileDialog.getExistingDirectory(caption = "Select directory or drive that contains the video files you are working with")

        self.all_videos = [os.path.join(root, f) for root, dirs, files in os.walk(self.data_path) for f in files if ".avi" in f]
    
        self.project_path = project_path
        self.vid_dict = {}
        self.videos_not_found = []
        
        self.selection = selection

        for selected in self.selection:
            try:
                vid = [x for x in self.all_videos if selected.text(0) in x]
                self.vid_dict[selected.text(0)] = vid[0]
            except:
                self.videos_not_found.append(selected)
        if len(self.videos_not_found) > 0:
            QtWidgets.QMessageBox.warning(self, "Videos Not Found", str(len(self.videos_not_found))+" out of "+ str(len(self.selection)) +" not found in selected path")
        for vid in self.videos_not_found:
            self.selection.remove(vid)

        self.ui.comboBoxThresholdMethod.addItem("NONE")
        self.ui.comboBoxThresholdMethod.addItem("BINARY")
        self.ui.comboBoxThresholdMethod.addItem("TOZERO")
        self.ui.comboBoxThresholdMethod.currentTextChanged.connect(self.check_thresholding_method)
        self.ui.comboBoxThresholdMethod.currentIndexChanged.connect(self.process_item)
        self.ui.pushButtonRedoCenter.clicked.connect(self.process_item)
        self.ui.listWidgetVideos.itemSelectionChanged.connect(self.process_item)
        self.ui.listWidgetVideos.itemDoubleClicked.connect(self.process_item)
        self.ui.pushButtonStartStop.clicked.connect(self.start_stop)
        self.check_thresholding_method(self.ui.comboBoxThresholdMethod.currentText())
        self.counter = 0

        self.ui.listWidgetVideos.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.listWidgetVideos.customContextMenuRequested.connect(self.contextMenuEvent_listwidgetVideos)

        self.flag_dataKeepaction = QtWidgets.QAction("&Flag and keep center", self, triggered = lambda: self.flag_data(delete = False))
        self.flag_dataDeleteaction = QtWidgets.QAction("&Flag and delete center", self, triggered = lambda: self.flag_data(delete = True))



        for item in self.selection:
            to_add = QtGui.QListWidgetItem(item.text(0))
            to_add.setData(1,item.text(1))
            if "center.txt" in os.listdir(item.text(1)):
                to_add.setBackground(QtGui.QColor("lightblue"))
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

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.overwrite_center()
        elif event.key() == QtCore.Qt.Key_Shift:
            self.process_item()
        elif event.key() == QtCore.Qt.Key_Delete:
            self.flag_data(delete = True)
        elif event.key() == QtCore.Qt.Key_Backspace:
            self.flag_data(delete = False)

    def contextMenuEvent_listwidgetVideos(self, event):
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.flag_dataDeleteaction)
        menu.addAction(self.flag_dataKeepaction)
        menu.popup(self.ui.listWidgetVideos.mapToGlobal(event))

    def flag_data(self, delete = False):
        if delete == True:
            self.ui.listWidgetVideos.currentItem().setBackground(QtGui.QColor("red"))
            destination_path = self.ui.listWidgetVideos.currentItem().data(1)
            files_in_destination_path = os.listdir(destination_path)
            for file in files_in_destination_path:
                if "center" in file and file.endswith(".txt"):
                    os.remove(os.path.join(destination_path, file))
                elif "metadata" in file:
                    meta_df_file = os.path.join(destination_path, "metadata.txt")
                    meta_df = pd.read_csv(meta_df_file, delimiter="\t")
                    to_drop = [col for col in meta_df.columns if "center" in col]
                    meta_df.drop(to_drop, axis = 1, inplace = True)
                    meta_df.to_csv(meta_df_file, sep = "\t")
        else:
            self.ui.listWidgetVideos.currentItem().setBackground(QtGui.QColor("orangered"))



    def toggle_overwrite(self):
        if self.ui.checkBoxOverwrite.isChecked():
            self.ui.pushButtonOverwrite.setEnabled(False)
        else:
            self.ui.pushButtonOverwrite.setEnabled(True)
        self.overwrite = self.ui.checkBoxOverwrite.isChecked()

    def check_thresholding_method(self, text):
        if text.lower() == "none":
            self.ui.spinBoxThreshold.setEnabled(False)
        else:
            self.ui.spinBoxThreshold.setEnabled(True)

    def overwrite_center(self):
        self.overwrite = True
        self.process_item()
        self.overwrite = False

    def process_item(self):
        vid = self.ui.listWidgetVideos.currentItem().data(0)
        path_to_vid = self.vid_dict[vid]
        destination_path = self.ui.listWidgetVideos.currentItem().data(1)

        if "center.txt" in os.listdir(destination_path) and not self.overwrite:
            center, img_edit, img_orig = self.find_center(path_to_vid)
            metadata_path = [os.path.join(destination_path,x) for x in os.listdir(destination_path) if "metadata" in x][0]
            metadata = pd.read_csv(metadata_path, delimiter=  "\t")
            x_orig = metadata["center_x"]
            y_orig = metadata["center_y"]
            r_orig = metadata["center_r"]
            x_new, y_new, r_new = center
            for img in [img_edit, img_orig]:
                # new circle in green with a blue center
                cv2.circle(img, (x_new, y_new), r_new, (0, 255, 0), 4)
                cv2.circle(img, (x_new, y_new), 2, (255,0,0), 4)
                #original circle in blue with a red center
                cv2.circle(img, (x_orig, y_orig), r_orig,(0,0, 255), 2)
                cv2.circle(img, (x_orig, y_orig), 2, (0,0,255), 4)

            img = np.hstack([img_edit, img_orig])
            self.ui.graphicsView.setImage(np.swapaxes(img, 0, 1))
        else:
            center, img_edit, img_orig = self.find_center(path_to_vid)
            x_new, y_new, r_new = center
            for img in [img_edit, img_orig]:
                # new circle in green with a blue center
                cv2.circle(img, (x_new, y_new), r_new, (0, 255, 0), 4)
                cv2.circle(img, (x_new, y_new), 2, (255,0,0), 4)
            img = np.hstack([img_edit, img_orig])
            self.ui.graphicsView.setImage(np.swapaxes(img, 0, 1))
            self.save_center(destination_path, center)


    def save_center(self, destination_path, center):
        x,y,r = center
        with open(os.path.join(destination_path, "center.txt"), "w") as f:
            f.write("X\tY\tR\n")
            for param in [x, y, r]:
                f.write(str(param) + "\t")
        self.ui.listWidgetVideos.currentItem().setBackground(QtGui.QColor("lightgreen"))
        self.corner_correction(destination_path)


    def get_params(self):
        params = {'minRadius':self.ui.spinBoxminRadius.value(),
                          'maxRadius':self.ui.spinBoxmaxRadius.value(),
                          'param1':self.ui.spinBoxparam1.value(),
                          'param2':self.ui.spinBoxparam2.value(),
                          'threshold':self.ui.spinBoxThreshold.value(),
                          'thresholdmethod' : self.ui.comboBoxThresholdMethod.currentText(),
                          'iterations' : self.ui.spinBoxIterations.value(),
                          'weight' : self.ui.spinBoxContrastWeight.value(),
                          'gamma':self.ui.spinBoxGamma.value()}
        return params

    def find_center(self, path):
        params = self.get_params()
        cf = Centerfinder(**params)
        circles, img_edit, img_orig = cf.find(path)
        return circles, img_edit, img_orig

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
                    self.process_item()

                else:
                    break


            self.alive = False
            self.ui.pushButtonStartStop.setText("Start")
            self.ui.pushButtonStartStop.setChecked(False)
            self.ui.checkBoxOverwrite.setChecked(False)
            self.toggle_overwrite()
