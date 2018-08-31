# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 09:50:02 2018

@author: install
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 13:20:50 2018

@author: ddo003
"""

from mainwindow import Ui_MainWindow
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets, uic
import pyqtgraph
import sys, os, shutil
from tqdm import tqdm
from supportclasses import DataHandler
from CenterfinderModule.CenterFindingWindow import CenterFindingWindow
from CenterfinderModule.CenterFinder import Centerfinder
from threading import Thread
##Load creatorfile and 
#qtCreatorFile = "mainwindow.ui" # Enter file here. 
#Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
# 
#from mainwindow import *

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.ui = Ui_MainWindow()
    
        self.ui.setupUi(self)

        self.setWindowIcon(QtGui.QIcon("icons/centerfinder.png"))
        self.project_path = None
        self.ui.menuTools.setEnabled(False)

        self.ui.tabWidgetFolders.currentChanged.connect(self.update_tree)

        self.ui.actionNew_Project.triggered.connect(self.new_project)

        self.ui.treeWidgetDataFolder.itemDoubleClicked.connect(self.item_double_clicked)
        self.ui.treeWidgetProjectFolder.itemDoubleClicked.connect(self.item_double_clicked)

        self.ui.actionCenterfinding.triggered.connect(self.open_centerfinding_window)

    def new_project(self):
        self.project_path = QtWidgets.QFileDialog.getExistingDirectory(caption="Choose a project path")
        self.data_path = QtWidgets.QFileDialog.getExistingDirectory(caption="Select Data Folder")

        if not os.path.exists(os.path.join(self.project_path, "dataframes")):
            os.mkdir(os.path.join(self.project_path, "dataframes"))

        t = Thread(target=self._new_project)
        t.start()

        self.display_folder_structure(self.project_path, self.ui.treeWidgetProjectFolder)
        self.display_folder_structure(self.data_path, self.ui.treeWidgetDataFolder)
        self.ui.menuTools.setEnabled(True)
        self.ui.actionNew_Project.setEnabled(False)

    def _new_project(self):
        dirs = [root for root, dirs, files in os.walk(self.data_path) if
                ".avi" in " ".join(files) and "metadata.txt" in " ".join(files)]

        for d in tqdm(dirs):
            try:

                #check if files are in the folders
                stimuli_profile = "None"
                metadata = "None"
                temperature = "None"
                arena = "None"
                tracking = "None"
                for root, directories, files in os.walk(d):
                    for f in files:
                        if "stimuli_profile" in f:
                            stimuli_profile = os.path.join(root, f)
                        elif "metadata" in f:
                            metadata = os.path.join(root, f)
                        elif "temperature" in f:
                            temperature = os.path.join(root, f)
                        elif "arena.txt" in f.lower():
                            arena = os.path.join(root, f)
                        elif "tracking" in f.lower() and "realspace" not in f.lower():
                            tracking  = os.path.join(root, f)

                all_files_there = True
                for f in [stimuli_profile, metadata, temperature, arena, tracking]:
                    if f == "None":
                        all_files_there = False

                if all_files_there:
                    if "exp_" not in d.lower():
                        newdir = os.path.join(self.project_path, "Exp_"+d.split("\\")[-1])
                    else:
                        newdir = os.path.join(self.project_path, d.split("\\")[-1])
                    if not os.path.exists(newdir):
                        os.mkdir(newdir)
                    for f in [stimuli_profile, metadata, temperature, arena, tracking]:
                        shutil.copy2(os.path.join(root, f), newdir)
                else:
                    print("Not all files present for ", d)

                # for root, directories, files in os.walk(d):
                #     for f in files:
                #         if "stimuli_profile" in f or "metadata" in f or "temperature" in f or "arena.txt" in f.lower():
                #             shutil.copy2(os.path.join(root, f), newdir)
                #         if "tracking" in f.lower() and "realspace" not in f.lower():
                #             shutil.copy2(os.path.join(root, f), newdir)

            except:
                pass

        self.update_tree(0)


    def update_tree(self, index):
        print(index)
        try:
            self.ui.treeWidgetProjectFolder.clear()
            self.display_folder_structure(self.project_path, self.ui.treeWidgetProjectFolder)
        except:
            print("No paths set. This is likely not so helpful.")

    def display_folder_structure(self, path, tree):
        for element in os.listdir(path):
            path_info = os.path.join(path, element)
            parent_item = QtWidgets.QTreeWidgetItem(tree,  [os.path.basename(element)])
            parent_item.setData(1,0,path_info)

            if os.path.isdir(path_info):
                self.display_folder_structure(path_info, parent_item)
                parent_item.setIcon(0, QtGui.QIcon("icons/folder.ico"))

            else:
                if path_info.endswith(".avi"):
                    parent_item.setIcon(0, QtGui.QIcon("icons/video.ico"))

                else:
                    parent_item.setIcon(0, QtGui.QIcon("icons/file.ico"))

    def find_center(self, path):
        cf = Centerfinder()
        circles = cf.find(path, show_result=True)
        print(circles)

    def item_double_clicked(self, item):
        text = item.text(1)
        print(text)
        try:
            if text.endswith(".avi"):
                self.find_center(text)
            elif text.endswith(".txt"):
                os.popen("notepad "+text)
        except:
            print("No action connected to files with this extension")

    def open_centerfinding_window(self):
        self.centerfinding_window = CenterFindingWindow(data_path = self.data_path, project_path = self.project_path)
        self.centerfinding_window.show()



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Analyze")
    window.show()
#    sys.exit(app.exec_())
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()
