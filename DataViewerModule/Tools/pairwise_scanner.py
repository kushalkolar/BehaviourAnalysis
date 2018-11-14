from DataViewerModule.Tools.pairwise_categorical_ui import Ui_Form
from DataViewerModule.PlottingModule.PlottingClasses import PlotWidget
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from scipy import stats
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

class PairwiseScanner(QtWidgets.QWidget):
    def __init__(self, parent = None, *args, parent_module = None):
        QtWidgets.QWidget.__init__(self, parent, *args)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.show()

        self.pm = parent_module
        self.df = self.pm.df_selection

        self.ui.framePlotWidget.setLayout(QtWidgets.QVBoxLayout())
        self.plot = PlotWidget()
        self.ui.framePlotWidget.layout().addWidget(self.plot)

        self.ui.listWidgetAllColumns.addItems(self.df.columns)

        self.transformation_names = ["none", "square root", "natural logarithm", "reciprocal", "reciprocal sqrt",
                                    "exponential"]
        for transform in self.transformation_names:
            self.ui.comboBoxTransformations.addItem(transform)

        for test in ["MannWhitney U", "Students T-test"]:
            self.ui.comboBoxTests.addItem(test)


        self.ui.pushButtonAddNum.clicked.connect(lambda: self.addToColumn(self.ui.listWidgetNumericals))
        self.ui.pushButtonAddCat.clicked.connect(self.addCategorical)
        self.ui.pushButtonFindSignificance.clicked.connect(self.scan)

        self.ui.listWidgetCategorical.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.listWidgetCategorical.customContextMenuRequested.connect(self.contextMenuEventCategorical)
        self.ui.listWidgetNumericals.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.listWidgetNumericals.customContextMenuRequested.connect(self.contextMenuEventNumericals)

        # Actions:
        self.deleteSelectionCategoricalAction = QtWidgets.QAction("Delete Selection", self,
                                                                   triggered=lambda: self.deleteSelection(
                                                                       self.ui.listWidgetCategorical))
        self.deleteSelectionNumericalsAction = QtWidgets.QAction("Delete Selection", self,
                                                                 triggered=lambda: self.deleteSelection(
                                                                     self.ui.listWidgetNumericals))

    def contextMenuEventCategorical(self, event):
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.deleteSelectionCategoricalAction)
        menu.popup(self.ui.listWidgetCategorical.mapToGlobal(event))

    def contextMenuEventNumericals(self, event):
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.deleteSelectionNumericalsAction)
        menu.popup(self.ui.listWidgetNumericals.mapToGlobal(event))

    def deleteSelection(self, listwidget):
        selection = [item.text() for item in listwidget.selectedItems()]
        present = [listwidget.item(i).text() for i in range(listwidget.count())]
        to_add = [item for item in present if item not in selection]
        listwidget.clear()
        listwidget.addItems(to_add)

    def addToColumn(self, listwidget):
        selection = [item.text() for item in self.ui.listWidgetAllColumns.selectedItems()]
        present = [listwidget.item(i).text() for i in range(listwidget.count())]
        selection = [x for x in selection if x not in present]
        listwidget.addItems(selection)

    def addCategorical(self):
        selection = [item.text() for item in self.ui.listWidgetAllColumns.selectedItems()]
        self.ui.listWidgetCategorical.clear()
        if len(selection) > 1:
            QtWidgets.QMessageBox.warning(self, "Too many items error", "You can only select one categorical. Please choose one and try again.")
        else:
            try:
                categorical = selection[0]
                self.ui.labelCategoricalName.setText("Categorical: "+categorical)
                self.ui.listWidgetCategorical.addItems(list(self.pm.df_selection[categorical].unique()))
                self.categorical = categorical
            except Exception as e:
                if QtWidgets.QMessageBox.warning(self, "Categorical as wrong datatype",
                                              "For the requested analysis the selected column must be converted to stringtype. You will only want to do this if you are certain your selected column is actually a categorical. \n\n Knowing what you know now, do you wish to continue?",
                                                 QtWidgets.QMessageBox.Yes,
                                                 QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes:
                    self.pm.df_selection[categorical] = self.pm.df_selection[categorical].astype(str)
                    self.ui.listWidgetCategorical.addItems(list(self.pm.df_selection[categorical].unique()))

    def find_pairs(self):
        selection = [item.text() for item in self.ui.listWidgetCategorical.selectedItems()]
        present = [self.ui.listWidgetCategorical.item(i).text() for i in range(self.ui.listWidgetCategorical.count())]

        if len(selection) == 0:
            selection = present

        pairs = []
        for x in selection:
            for y in present:
                if x != y:
                    pair = [x,y]
                    pair.sort()
                    if pair not in pairs:
                        pairs.append(pair)
        return(pairs)

    def _transorm(self, to_transform, transformation):
        if transformation == "none":
            transformed = to_transform
        elif transformation == "square root":
            transformed = np.sqrt(to_transform)
        elif transformation == "natural logarithm":
            transformed = np.log(to_transform)
        elif transformation == "reciprocal":
            transformed = 1 / to_transform
        elif transformation == "reciprocal sqrt":
            transformed = 1 / (np.sqrt(to_transform))
        else:
            transformed = to_transform ** 2
        return transformed

    def scan(self):
        try:
            pairs = self.find_pairs()
            test = self.ui.comboBoxTests.currentText()
            alpha = self.ui.doubleSpinBoxAlpha.value()
            transformation = self.ui.comboBoxTransformations.currentText()

            if self.ui.checkBoxBonferroni.isChecked():
                alpha = alpha / len(pairs)
            results = ""
            pval_array = "none"
            numericals = [self.ui.listWidgetNumericals.item(i).text() for i in range(self.ui.listWidgetNumericals.count())]
            for numerical in tqdm(numericals):
                results += "\n\n****    "+numerical+"    **** \n \n"
                numerical_pval_array = "none"
                for pair in pairs:
                    groups = [self.df[numerical][self.df[self.categorical] == pair[0]].dropna().values,self.df[numerical][self.df[self.categorical] == pair[1]].dropna().values]
                    groups = [self._transorm(group, transformation) for group in groups]
                    if "whitn" in test.lower():
                        pval = stats.mannwhitneyu(groups[0], groups[1])[1]
                    else:
                        pval = stats.ttest_ind(groups[0], groups[1])[1]
                    results = results +pair[0] + " vs " + pair[1] +"    :  "+str(pval)
                    if pval < alpha:
                        results += " *"
                    results += "\n"
                    if numerical_pval_array == "none":
                        numerical_pval_array = np.array([pval])
                    else:
                        numerical_pval_array = np.vstack([numerical_pval_array, np.array([pval])])

                try:
                    pval_array = np.hstack([pval_array, numerical_pval_array])
                except Exception as e:
                    print(e)
                    pval_array = numerical_pval_array


            self.ui.textEditResults.setText(results)

            print(pval_array)
            pval_array[pval_array < alpha] = 0
            pval_array[pval_array > alpha] = 1
            self.plot.canvas.clear()
            ax = self.plot.canvas.figure.gca()
            ax.imshow(pval_array, cmap="brg_r")
            ax.set_xticks([x for x in range(len(numericals))])
            ax.set_xticklabels(numericals, rotation=90)
            ax.set_yticks([x for x in range(len(pairs))])
            ax.set_yticklabels([x[0]+" vs "+x[1] for x in pairs])
            self.plot.canvas.figure.tight_layout()
            self.plot.canvas.draw()
        except Exception as e:
            print(e)


