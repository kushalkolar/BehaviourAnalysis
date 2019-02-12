from DataViewerModule.Tools.pairwise_categorical_ui import Ui_Form
from DataViewerModule.PlottingModule.PlottingClasses import PlotWidget
from DataViewerModule.Tools.pairwise_scanner import  PairwiseScanner

#from pairwise_categorical_ui import Ui_Form
#from DataViewerModule.Tools.pairwise_categorical_ui import Ui_Form
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from scipy import stats
import pandas as pd
import numpy as np
import os
import time
import matplotlib.pyplot as plt
from tqdm import tqdm



class SSMDScanner(PairwiseScanner):
    def __init__(self, *args, parent_module = "none"):
        self.pm = parent_module
        PairwiseScanner.__init__(self, *args, parent_module = self.pm)


#         self.ui.label_4.setText("Mean or Median")
# #        self.ui.label_4.setVisible(False)
#         self.ui.label_5.setVisible(False)
#         self.ui.label_6.setVisible(False)
#         self.ui.comboBoxTests.setVisible(False)
#         self.ui.checkBoxBonferroni.setVisible(False)
#         self.ui.doubleSpinBoxAlpha.setVisible(False)
#
        self.setWindowTitle("SSMD")
        self.setWindowIcon(QtGui.QIcon("icons/ssmd.png"))

        self.ui.tabWidget.setTabText(0,"P-Value Graph")
        self.ui.tabWidget.setTabText(1,"SSMD Graph")
        
        # self.ui.comboBoxTransformations.clear()
        # for x in ["median", "mean"]:
        #     self.ui.comboBoxTransformations.addItem(x)

        for x in ["mean", "median"]:
            self.ui.comboBoxSSMDtype.addItem(x)

        self.ui.pushButtonRunPairs.setText("Create SSMD Graph")


        self.ui.frameSSMDPlotWidget.setLayout(QtWidgets.QVBoxLayout())
        self.SSMDplot = PlotWidget()
        self.ui.frameSSMDPlotWidget.layout().addWidget(self.SSMDplot)

        self.ui.frameMaskedPlotWidget.setLayout(QtWidgets.QVBoxLayout())
        self.maskedplot = PlotWidget()
        self.ui.frameMaskedPlotWidget.layout().addWidget(self.maskedplot)

        self.show()

    def get_ssmd(self, group1, group2, mode="mean"):
        if mode != "mean":
            return (np.median(group1) - np.median(group2)) / np.sqrt((group1.var() + group2.var()))
        else:
            return (group1.mean() - group2.mean()) / np.sqrt((group1.var() + group2.var()))

    def scan(self):
        try:
            pairs = self.find_pairs()
            test = self.ui.comboBoxTests.currentText()
            alpha = self.ui.doubleSpinBoxAlpha.value()
            transformation = self.ui.comboBoxTransformations.currentText()
            ssmd_mode = self.ui.comboBoxSSMDtype.currentText()

            if self.ui.checkBoxBonferroni.isChecked():
                alpha = alpha / len(pairs)
            results = ""
            pval_array = "none"
            ssmd_array = "none"
            numericals = [self.ui.listWidgetNumericals.item(i).text() for i in range(self.ui.listWidgetNumericals.count())]
            failed_date_matches = []
            for numerical in tqdm(numericals):
                results += "\n\n****    "+numerical+"    **** \n \n"
                numerical_pval_array = "none"
                local_ssmd_array = "none"
                for pair in pairs:
                    if self.ui.checkBoxDateMatching.isChecked():
                        dates = self.df["date"].loc[self.df[self.categorical] == pair[0]].unique()
                        print(dates)
                        group1 = self.df[numerical].loc[self.df[self.categorical] == pair[0]].dropna().values
                        group2 = self.df[numerical].loc[(self.df[self.categorical] == pair[1]) & (self.df["date"].isin(dates))].dropna().values
                        if len(group2) < 5:
                            group2 = self.df[numerical].loc[self.df[self.categorical] == pair[1]]
                            if pair not in failed_date_matches:
                                failed_date_matches.append(pair)
                        groups = [group1, group2]

                    elif not self.ui.checkBoxDateMatching.isChecked():
                        groups = [self.df[numerical].loc[self.df[self.categorical] == pair[0]].dropna().values, self.df[numerical].loc[self.df[self.categorical] == pair[1]].dropna().values]



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

                    ssmd = self.get_ssmd(groups[0], groups[1], mode=ssmd_mode)

                    if local_ssmd_array == "none":
                        local_ssmd_array = np.array([ssmd])
                    else:
                        local_ssmd_array = np.vstack([local_ssmd_array, np.array([ssmd])])


                try:
                    pval_array = np.hstack([pval_array, numerical_pval_array])
                except Exception as e:
                    print(e)
                    pval_array = numerical_pval_array


                try:
                    ssmd_array = np.hstack([ssmd_array, local_ssmd_array])
                except Exception as e:
                    ssmd_array = local_ssmd_array



            self.ui.textEditResults.setText(results)

            to_save = pd.DataFrame(data=ssmd_array, columns=numericals)
            to_save["categorical"] = [x[0]+" vs "+x[1] for x in pairs]
            to_save.to_csv(os.path.join(self.pm.path, time.strftime("%Y%m%d%H%M%S")+"_SSMD_array.txt"), sep="\t",)

            to_save = pd.DataFrame(data=pval_array, columns=numericals)
            to_save["categorical"] = [x[0] + " vs " + x[1] for x in pairs]
            to_save.to_csv(os.path.join(self.pm.path, time.strftime("%Y%m%d%H%M%S") + "_pval_array.txt"), sep = "\t",)

            to_save=None

            print(pval_array)
            pval_array[pval_array < alpha] = 0
            pval_array[pval_array > alpha] = 1

            masked_ssmd_array = ssmd_array.copy()
            masked_ssmd_array[pval_array == 1] = np.nan

            maxval = np.max(np.abs(ssmd_array))
            minval = -maxval

            self.plot.canvas.clear()
            ax = self.plot.canvas.figure.gca()
            ax.imshow(pval_array, cmap="brg_r")
            ax.set_xticks([x for x in range(len(numericals))])
            ax.set_xticklabels(numericals, rotation=90)
            ax.set_yticks([x for x in range(len(pairs))])
            ax.set_yticklabels([x[0]+" vs "+x[1] for x in pairs])
            self.plot.canvas.figure.tight_layout()
            self.plot.canvas.draw()


            self.SSMDplot.canvas.clear()
            ax = self.SSMDplot.canvas.figure.gca()
            ax.imshow(ssmd_array, vmin = minval, vmax = maxval, cmap="bwr")
            ax.set_xticks([x for x in range(len(numericals))])
            ax.set_xticklabels(numericals, rotation=90)
            ax.set_yticks([x for x in range(len(pairs))])
            ax.set_yticklabels([x[0]+" vs "+x[1] for x in pairs])
            self.SSMDplot.canvas.figure.tight_layout()
            self.SSMDplot.canvas.draw()

            self.maskedplot.canvas.clear()
            ax = self.maskedplot.canvas.figure.gca()
            ax.imshow(masked_ssmd_array, vmin = minval, vmax = maxval, cmap="bwr")
            ax.set_xticks([x for x in range(len(numericals))])
            ax.set_xticklabels(numericals, rotation=90)
            ax.set_yticks([x for x in range(len(pairs))])
            ax.set_yticklabels([x[0]+" vs "+x[1] for x in pairs])
            self.maskedplot.canvas.figure.tight_layout()
            self.maskedplot.canvas.draw()

            if self.ui.checkBoxDateMatching.isChecked() and len(failed_date_matches) > 0:
                failed_matches = ""
                for match in failed_date_matches:
                    failed_matches +=  "\n"+str(match[0])+" vs "+str(match[1])
                QtWidgets.QMessageBox.warning(self, "Date Matching Warning", "Date Matching failed for the following: \n"+failed_matches+" \n \n Comparison completed without date matching.")

        except Exception as e:
            print(e)


if __name__ == "__main__":
    ssmd = SSMDScanner(parent_module = window.pv)