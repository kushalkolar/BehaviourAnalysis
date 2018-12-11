from DataViewerModule.Tools.pairwise_categorical_ui import Ui_Form
#from DataViewerModule.PlottingModule.PlottingClasses import PlotWidget
from DataViewerModule.Tools.pairwise_scanner import  PairwiseScanner

from pairwise_categorical_ui import Ui_Form
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from scipy import stats
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm



class SSMD_scanner(PairwiseScanner):
    def __init__(self, *args, parent_module = "none"):
        self.pm = parent_module
        PairwiseScanner.__init__(self, *args, parent_module = self.pm)
        
        self.ui.label_4.setText("Mean or Median")
#        self.ui.label_4.setVisible(False)
        self.ui.label_5.setVisible(False)
        self.ui.label_6.setVisible(False)
        self.ui.comboBoxTests.setVisible(False)
        self.ui.checkBoxBonferroni.setVisible(False)
        self.ui.doubleSpinBoxAlpha.setVisible(False)
        
        self.setWindowTitle("SSMD")
        
        self.ui.tabWidget.setTabText(0,"SSMD Graph")
        self.ui.tabWidget.setTabText(1,"SSMD Values")
        
        self.ui.comboBoxTransformations.clear()
        for x in ["median", "mean"]:
            self.ui.comboBoxTransformations.addItem(x)
        
        self.ui.pushButtonFindSignificance.setText("Create SSMD Graph")
        
        

        self.show()

    def scan(self):
        ax = self.plot.canvas.figure.gca()
        
        
        
        
        
        self.plot.canvas.draw()
        


if __name__ == "__main__":
    ssmd = SSMD_scanner(parent_module = window.pv)