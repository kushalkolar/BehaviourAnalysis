


from DataViewerModule.scanner_ui import Ui_Form
from DataViewerModule.PlottingModule.PlottingClasses import PlotWidget
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from scipy import stats
import pandas as pd
import numpy as np

class SignificanceScanner(QtWidgets.QWidget):
    def __init__(self, parent = None, *args, df):
        QtWidgets.QWidget.__init__(self, parent, *args)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.df = df

        self.ui.listWidgetAllColumns.addItems(self.df.columns)
        self.ui.pushButtonAddCat.clicked.connect(lambda: self.addToColumn(self.ui.listWidgetCategoricals))
        self.ui.pushButtonAddNum.clicked.connect(lambda: self.addToColumn(self.ui.listWidgetNumericals))
        self.ui.pushButtonClearCat.clicked.connect(self.ui.listWidgetCategoricals.clear)
        self.ui.pushButtonClearNum.clicked.connect(self.ui.listWidgetNumericals.clear)
        self.ui.pushButtonFindSignificance.clicked.connect(self.scan_significance)
        self.transformation_names = ["none","square root", "natural logarithm", "reciprocal", "reciprocal sqrt", "exponential"]
        
        for transform in self.transformation_names:
            self.ui.comboBoxTransformations.addItem(transform)
        
        for test in ["kruskal wallis", "oneway anova"]:
            self.ui.comboBoxTests.addItem(test)
        
        
        self.ui.framePlotWidget.setLayout(QtWidgets.QVBoxLayout())
        self.plot = PlotWidget()
        self.ui.framePlotWidget.layout().addWidget(self.plot)
        self.ui.framePlotWidget.setVisible(False)
        self.show()
        
    def addToColumn(self, listwidget):
        selection = [item.text() for item in self.ui.listWidgetAllColumns.selectedItems()]
        present = [item.text() for item in listwidget.selectedItems()]
        selection = [x for x in selection if x not in present]
        listwidget.addItems(selection)
        
        
    def _transorm(self, to_transform, transformation):
        if transformation == "none":
            transformed = to_transform
        elif transformation == "square root":
            transformed = np.sqrt(to_transform)
        elif transformation == "natural logarithm":
            transformed = np.log(to_transform)
        elif transformation == "reciprocal":
            transformed = 1/to_transform
        elif transformation == "reciprocal sqrt":
            transformed = 1/(np.sqrt(to_transform))
        else:
            transformed = to_transform**2
        return transformed
    
    
    def scan_significance(self):
        data = self.df
        categoricals = [self.ui.listWidgetCategoricals.item(i).text() for i in range(self.ui.listWidgetCategoricals.count())]
        numericals = [self.ui.listWidgetNumericals.item(i).text() for i in range(self.ui.listWidgetNumericals.count())]
        alpha = self.ui.doubleSpinBoxAlpha.value()
        transformation = self.ui.comboBoxTransformations.currentText()
        test = self.ui.comboBoxTests.currentText()
        pval_array = np.zeros(len(numericals))
        for categorical in categoricals:
            catogeries = list(data[categorical].unique())
            pvals = np.array([])
            for num in numericals:
                data_to_compare = []
                for catogery in catogeries:
                    subdata = data[num].loc[data[categorical]== catogery].dropna().values
                    subdata = self._transorm(subdata, transformation)                    
                    data_to_compare.append(list(subdata))
                
                if "anova" in test.lower():
                    pval = stats.f_oneway(*data_to_compare)[1]
                else:
                    pval = stats.kruskal(*data_to_compare)[1]
                if pval > alpha:
                    pval = False
                else:
                    pval = True
                pvals = np.hstack([pvals, pval])
            pval_array = np.vstack([pval_array, pvals])
        pval_array = pval_array[1:,:]
        
        self.ui.framePlotWidget.setVisible(True)
        ax = self.plot.canvas.figure.gca()
        ax.imshow(pval_array, cmap = "brg")
        ax.set_xticks([x for x in range(len(numericals))])
        ax.set_xticklabels(numericals, rotation = 90)
        ax.set_yticks([x for x in range(len(categoricals))])
        ax.set_yticklabels(categoricals)
        self.plot.canvas.figure.tight_layout()
        self.plot.canvas.draw()
        print(pval_array)
        
        