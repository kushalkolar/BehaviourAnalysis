import ast
import os
import pickle
import sys

import numpy as np
import pandas as pd
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from pyqtgraph.console import ConsoleWidget
from scipy import stats
from sklearn.preprocessing import scale, minmax_scale

from DataViewerModule.PlottingModule.PlottingClasses import PlotWidget
from DataViewerModule.Tools.item_renamer import ItemRenamer
from DataViewerModule.Tools.scannermodule import SignificanceScanner
from DataViewerModule.Tools.ssmd_scanner import SSMDScanner
from DataViewerModule.pandasviewer_mainwindow import Ui_MainWindow


class PandasViewer(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, *args, df="none", path=None):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Data Explorer")
        self.setWindowIcon(QtGui.QIcon("icons/pickle.png"))
        self.show()

        self.ui.treeWidgetAllColums.setVisible(False)
        self.path = path
        try:
            if type(df) == str:
                if not df.endswith("pickle"):
                    self.df = pd.read_csv(df, delimiter="\t")
                else:
                    self.df = pd.read_pickle(df)
                self.path = os.path.dirname(df)
            elif type(df) == pd.core.frame.DataFrame:
                self.df = df
        except Exception as e:
            self.df = pd.DataFrame()
        #            QtWidgets.QMessageBox.warning(self, "Could not open DataFrame", str(e))

        self.set_data(self.ui.tableWidgetAllData, self.df)
        self.set_column_widget()

        self.filters = {}

        self.ui.pushButtonAddToSelection.clicked.connect(self.add_to_selection)
        self.ui.pushButtonRemoveFromSelection.clicked.connect(self.remove_from_selection)

        self.ui.comboBoxSelectedColumns.currentIndexChanged.connect(self.update_unique_values)

        self.ui.pushButtonApplyFilters.clicked.connect(self.apply_new_filter)
        self.ui.checkBoxUnique.clicked.connect(self.update_unique_values)
        self.ui.checkBoxSorting.clicked.connect(self.update_unique_values)
        self.ui.listWidgetUniqueValues.itemSelectionChanged.connect(self.row_selection)
        self.ui.checkBoxPreviewSelection.clicked.connect(self.row_selection)

        self.ui.tableWidgetSelectedData.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.tableWidgetSelectedData.customContextMenuRequested.connect(self.contextMenuEvent_SelectedData)

        self.ui.actionLoad_Dataset_into_Viewer.triggered.connect(self.load_dataset)
        self.ui.action_as_CSV.triggered.connect(lambda: self.save_selection(as_type="csv"))
        self.ui.action_as_Pickle.triggered.connect(lambda: self.save_selection(as_type="pickle"))
        self.toCSVAct = QtWidgets.QAction("&Save Selection to CSV", self,
                                          triggered=lambda: self.save_selection(as_type="csv"))
        self.removeAllFiltersAct = QtWidgets.QAction("&Remove all Filters", self, triggered=self.remove_all_filters)

        self.ui.actionRoaming.triggered.connect(lambda: self.start_roaming_calculator(self.df_selection))
        self.ui.actionData.triggered.connect(lambda: self.hide_unhide_widget(self.ui.tabWidget, self.ui.actionData))
        self.ui.actionPlotting.triggered.connect(
            lambda: self.hide_unhide_widget(self.ui.groupBoxPlotting, self.ui.actionPlotting))
        self.ui.actionData_Selection.triggered.connect(
            lambda: self.hide_unhide_widget(self.ui.groupBox, self.ui.actionData_Selection))
        self.ui.actionTransforms.triggered.connect(
            lambda: self.hide_unhide_widget(self.ui.frameTransform, self.ui.actionTransforms))
        self.ui.actionStatistics.triggered.connect(
            lambda: self.hide_unhide_widget(self.ui.frameStatistics, self.ui.actionStatistics))
        self.ui.frameConsole.setVisible(False)
        self.ui.frameStatistics.setVisible(False)
        self.ui.actionConsole.triggered.connect(self.open_console)
        self.ui.pushButtonCloseConsole.clicked.connect(self.close_console)

        self.ui.actionData_Selection.setIcon(QtGui.QIcon("icons/checkmark.png"))
        self.ui.actionData.setIcon(QtGui.QIcon("icons/checkmark.png"))

        self.ui.groupBoxPlotting.setVisible(False)
        self.ui.framePlotWidget.setLayout(QtWidgets.QVBoxLayout())
        self.plot = PlotWidget()
        self.ui.framePlotWidget.layout().addWidget(self.plot)

        self.ui.pushButtonPlot.clicked.connect(self.update_plot)
        for plottype in ["violinplot", "lineplot", "scatterplot"]:
            self.ui.comboBoxPlotType.addItem(plottype)

        self.ui.listWidgetAppliedFilters.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.listWidgetAppliedFilters.customContextMenuRequested.connect(self.contextMenuEvent_AppliedFilters)

        self.removeFilteract = QtWidgets.QAction("&Remove Selected Filter(s)", self, triggered=self.remove_filters)
        self.loadFiltersetact = QtWidgets.QAction("&Load Filterset", self, triggered=self.load_filterset)
        self.saveFiltersetact = QtWidgets.QAction("&Save Filterset", self, triggered=self.save_filterset)

        self.ui.groupBoxPlotting.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.groupBoxPlotting.customContextMenuRequested.connect(self.contextMenuEvent_PlottingMenu)
        self.updatePlottingUIact = QtWidgets.QAction("&Update...", self, triggered=self.update_plotting_ui)

        self.ui.comboBoxPlotType.currentTextChanged.connect(self.toggle_colorselection)
        self.ui.comboBoxColorParam.setVisible(False)
        self.ui.labelColorParam.setVisible(False)

        self.ui.frameTransform.setVisible(False)
        for transform in ["none", "square root", "natural logarithm", "reciprocal", "reciprocal sqrt", "exponential"]:
            self.ui.comboBoxTransformations.addItem(transform)

        self.ui.pushButtonTransformData.clicked.connect(self.transform)
        self.ui.pushButtonAddTransformToData.clicked.connect(self.add_transformation_to_data)
        self.ui.actionScan_for_significance.triggered.connect(self.start_significance_scanner)
        self.ui.actionPairwaise_Test_Categorical.triggered.connect(self.start_pairwise_scanner)

        self.ui.actionminmax_scale.triggered.connect(lambda: self.normalize_data("minmax"))
        self.ui.actionmean_scale.triggered.connect(lambda: self.normalize_data("mean"))

        self.ui.pushButtonTest.clicked.connect(self.run_statistics)
        for test in ["Kruskal-Wallis", "Oneway ANOVA"]:
            self.ui.comboBoxStatisticalTests.addItem(test)

        self.ui.actionRename_items_in_column.triggered.connect(self.start_item_renamer)

    def contextMenuEvent_SelectedData(self, event):
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.toCSVAct)
        menu.addAction(self.removeAllFiltersAct)
        menu.popup(self.ui.tableWidgetSelectedData.mapToGlobal(event))

    def contextMenuEvent_AppliedFilters(self, event):
        menu = QtWidgets.QMenu(self)
        if len(self.ui.listWidgetAppliedFilters.selectedItems()) > 0:
            menu.addAction(self.removeFilteract)
            menu.addAction(self.saveFiltersetact)
        menu.addAction(self.loadFiltersetact)
        menu.popup(self.ui.listWidgetAppliedFilters.mapToGlobal(event))

    def contextMenuEvent_PlottingMenu(self, event):
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.updatePlottingUIact)
        menu.popup(self.ui.groupBoxPlotting.mapToGlobal(event))

    def load_dataset(self):
        path = QtWidgets.QFileDialog.getOpenFileName(caption="Select a file (.pickle, or tab delimited txt",
                                                     directory=self.path)[0]
        self.path = os.path.dirname(path)
        self.filters = {}
        try:
            if type(path) == str:
                if not path.endswith("pickle"):
                    self.df = pd.read_csv(path, delimiter="\t")
                else:
                    self.df = pd.read_pickle(path)
        except Exception as e:
            print(e)

        self.df_selection = pd.DataFrame()

        self.set_data(self.ui.tableWidgetAllData, self.df)
        self.set_data(self.ui.tableWidgetSelectedData, self.df_selection)
        self.set_column_widget()

    def check_datatype(self):

        def find_datatype(data):
            try:
                if len(data.dropna().unique()) / len(data.dropna()) < 0.08:
                    return ("categorical")
                elif data.dtype == type("str") or data.dtype == "O" or "index" in col.lower():
                    return ("categorical")
                else:
                    return ("numerical")
            except:
                return ("categorical")

        if not hasattr(self, "datatype_columns"):
            self.datatype_columns = {}

            for col in self.df.columns:
                self.datatype_columns[col] = {"datatype": find_datatype(self.df[col]),
                                              "userdefined": False}
        else:
            for col in self.df.columns:
                if col in self.datatype_columns.keys():
                    if not self.datatype_columns[col]["userdefined"]:
                        self.datatype_columns[col] = {"datatype": find_datatype(self.df[col]),
                                                      "userdefined": False}
                else:
                    self.datatype_columns[col] = {"datatype": find_datatype(self.df[col]),
                                                  "userdefined": False}

    # def set_data(self, tableView, df):
    #     model = PandasModel(df)
    #     tableView.setModel(model)

    def set_data(self, tableWidget, df):
        if "index" not in df.columns:
            df["index"] = df.index
        tableWidget.setColumnCount(len(df.columns))
        tableWidget.setHorizontalHeaderLabels(df.columns)
        tableWidget.setRowCount(len(df))
        for i in range(len(df.index)):
            for j in range(len(df.columns)):
                tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(df.iloc[i, j])))

    def set_column_widget(self):
        self.ui.listWidgetAllColumns.clear()
        self.ui.listWidgetAllColumns.addItems(self.df.columns)
        self.colour_listwidget_by_datatype(self.ui.listWidgetAllColumns)

    def colour_listwidget_by_datatype(self, widget):
        try:
            self.check_datatype()
            for i in range(widget.count()):
                item = widget.item(i)
                text = item.text()
                if self.datatype_columns[text]['datatype'] == "categorical":
                    item.setBackground(QtGui.QColor(252, 186, 3, 50))
                else:
                    item.setBackground(QtGui.QColor(0, 255, 68, 50))
        except Exception as e:
            print(str(e))

    # THIS IS CODE TO SHOW COLUMNS IN A TREE WIDGET ITEM! SET VISIBLE TO TRUE IN __init__ TO SHOW THE WIDGET
    #        to_branch = list(set([x.split("_")[0] for  x in self.df.columns if len(x.split("_"))>1]))
    #        singles = list(set([x for x in self.df.columns if len(x.split("_")) == 1 and x not in to_branch]))
    #
    #        for element in to_branch:
    #            parentItem = QtWidgets.QTreeWidgetItem(self.ui.treeWidgetAllColums, [element])
    #            to_add = [x for x in self.df.columns if x.startswith(element)]
    #            for item_to_add in to_add:
    #                item = QtWidgets.QTreeWidgetItem(parentItem, [item_to_add])
    #                item.setData(1,0,item_to_add)
    #        for single in singles:
    #            item = QtWidgets.QTreeWidgetItem(self.ui.treeWidgetAllColums, [single])
    #            item.setData(1,0,single)

    def add_to_selection(self):
        selection_to_add = [item.text() for item in self.ui.listWidgetAllColumns.selectedItems()]
        selected_columns = [self.ui.listWidgetSelectedColumns.item(i).text() for i in
                            range(self.ui.listWidgetSelectedColumns.count())]
        for item in selection_to_add:
            if item not in selected_columns:
                self.ui.listWidgetSelectedColumns.addItem(item)
        self.update_selected_data()

    def remove_from_selection(self):

        selection_to_remove = [item.text() for item in self.ui.listWidgetSelectedColumns.selectedItems()]
        selected_columns = [self.ui.listWidgetSelectedColumns.item(i).text() for i in
                            range(self.ui.listWidgetSelectedColumns.count())]
        print(selection_to_remove)
        print(selected_columns)
        self.ui.listWidgetSelectedColumns.clear()
        for item in selected_columns:
            if item not in selection_to_remove:
                self.ui.listWidgetSelectedColumns.addItem(item)

        self.update_selected_data()

    def update_selected_data(self):
        selection = [self.ui.listWidgetSelectedColumns.item(i).text() for i in
                     range(self.ui.listWidgetSelectedColumns.count())]
        #        self.df_selection = self.df[selection]
        self.apply_filters()
        self.set_data(self.ui.tableWidgetSelectedData, self.df_selection)

        self.ui.comboBoxSelectedColumns.clear()
        self.ui.comboBoxSelectedColumns.addItem("index")
        for item in selection:
            self.ui.comboBoxSelectedColumns.addItem(item)
        self.update_plotting_ui()
        self.colour_listwidget_by_datatype(self.ui.listWidgetSelectedColumns)

    def update_unique_values(self):
        self.ui.listWidgetUniqueValues.clear()
        try:
            col = self.ui.comboBoxSelectedColumns.currentText()
            if col != "index":
                if self.ui.checkBoxUnique.isChecked():
                    list_of_vals = [x for x in pd.unique(self.df_selection[col])]
                else:
                    list_of_vals = [x for x in self.df_selection[col]]
                if self.ui.checkBoxSorting.isChecked():
                    list_of_vals.sort()

            else:
                list_of_vals = [str(x) for x in self.df_selection.index]

            self.ui.listWidgetUniqueValues.addItems([str(x) for x in list_of_vals])
        except:
            sys.stdout.write("\n No selectable columns")

    def create_filter(self):
        col = self.ui.comboBoxSelectedColumns.currentText()
        filtername = col
        include = self.ui.radioButtonInclude.isChecked()

        if self.df[col].dtype == "O":
            selection = [x.data(0) for x in self.ui.listWidgetUniqueValues.selectedItems()]

        else:
            selection = [ast.literal_eval(x.data(0)) for x in self.ui.listWidgetUniqueValues.selectedItems()]

        if col in self.filters.keys() and include == False:
            prev_selection = self.filters[col][2]
            selection = selection + prev_selection
        self.filters[filtername] = (col, include, selection)

    def apply_filters(self):
        columns = [self.ui.listWidgetSelectedColumns.item(i).text() for i in
                   range(self.ui.listWidgetSelectedColumns.count())]
        self.df_selection = self.df[columns]
        self.ui.listWidgetAppliedFilters.clear()
        for filt in self.filters.keys():
            self.ui.listWidgetAppliedFilters.addItem(filt)
            col, include, selection = self.filters[filt]
            if col != "index":
                if include:
                    self.df_selection = self.df_selection[self.df_selection[col].isin(selection)]
                else:
                    self.df_selection = self.df_selection[~self.df_selection[col].isin(selection)]
            else:
                if include:
                    self.df_selection = self.df_selection.loc[self.df_selection.index.isin(selection)]
                else:
                    self.df_selection = self.df_selection.loc[~self.df_selection.index.isin(selection)]

    def remove_filters(self):
        filter_to_remove = self.ui.listWidgetAppliedFilters.selectedItems()[0].text()
        print("Removing :", filter_to_remove)
        self.filters.pop(filter_to_remove)
        self.update_selected_data()

    def remove_all_filters(self):
        self.filters = {}
        self.update_selected_data()

    def load_filterset(self):
        path_to_filter = QtWidgets.QFileDialog.getOpenFileName(directory=self.path)[0]
        with open(path_to_filter, "rb") as f:
            self.filters = pickle.load(f)
        columns = [self.ui.listWidgetSelectedColumns.item(i).text() for i in
                   range(self.ui.listWidgetSelectedColumns.count())]
        for key in self.filters.keys():
            if key not in columns:
                self.ui.listWidgetSelectedColumns.addItem(key)
        self.apply_filters()
        self.update_selected_data()

    def save_filterset(self):
        savepath = QtWidgets.QFileDialog.getSaveFileName(directory=self.path)[0]
        if not savepath.endswith(".flt"):
            savepath += ".flt"
        with open(savepath, "wb") as f:
            pickle.dump(self.filters, f)

    def row_selection(self):
        col = self.ui.comboBoxSelectedColumns.currentText()

        if self.df[col].dtype == "O":
            selection = [x.data(0) for x in self.ui.listWidgetUniqueValues.selectedItems()]

        else:
            selection = [ast.literal_eval(x.data(0)) for x in self.ui.listWidgetUniqueValues.selectedItems()]

        if col != "index":
            if self.ui.radioButtonInclude.isChecked():
                self.df_selection_rows = self.df_selection[self.df_selection[col].isin(selection)]
            else:
                self.df_selection_rows = self.df_selection[~self.df_selection[col].isin(selection)]

        else:
            if self.ui.radioButtonInclude.isChecked():
                self.df_selection_rows = self.df_selection.loc[self.df_selection.index.isin(selection)]
            else:
                self.df_selection_rows = self.df_selection.loc[~self.df_selection.index.isin(selection)]

        if self.ui.checkBoxPreviewSelection.isChecked():
            self.set_data(self.ui.tableWidgetSelectedData, self.df_selection_rows)
        else:
            self.set_data(self.ui.tableWidgetSelectedData, self.df_selection)

    def apply_new_filter(self):
        self.create_filter()
        self.apply_filters()
        self.set_data(self.ui.tableWidgetSelectedData, self.df_selection)
        self.ui.checkBoxPreviewSelection.setChecked(False)
        self.update_unique_values()
        self.update_plotting_ui()

    def save_selection(self, as_type):
        filename = QtWidgets.QFileDialog.getSaveFileName(caption="Select Saving Location", directory=self.path)[0]
        if as_type == "csv":
            if not filename.endswith(".txt"):
                filename += ".txt"
                self.df_selection.to_csv(filename, sep="\t")
        elif as_type == "pickle":
            if not filename.endswith(".pickle"):
                filename += ".pickle"
                self.df_selection.to_pickle(filename)
        print(filename)

    def update_plotting_ui(self):
        self.ui.groupBoxPlotting.setVisible(True)
        xdata_text = self.ui.comboBoxXData.currentText()
        ydata_text = self.ui.comboBoxYData.currentText()
        color_text = self.ui.comboBoxColorParam.currentText()
        for box in [self.ui.comboBoxXData, self.ui.comboBoxYData]:
            box.clear()
            box.addItems(self.df_selection.columns)
        self.ui.comboBoxXData.setCurrentText(xdata_text)
        self.ui.comboBoxYData.setCurrentText(ydata_text)
        self.ui.comboBoxColorParam.setCurrentText(color_text)
        self.toggle_colorselection(text=self.ui.comboBoxPlotType.currentText())

    def toggle_colorselection(self, text="None"):
        if text == "None":
            text = self.ui.comboBoxColorParam.currentText()
        if "scatter" in text:
            self.ui.comboBoxColorParam.setVisible(True)
            self.ui.labelColorParam.setVisible(True)
            self.ui.comboBoxColorParam.clear()
            self.ui.comboBoxColorParam.addItems(self.df_selection.columns)
        else:
            self.ui.comboBoxColorParam.setVisible(False)
            self.ui.labelColorParam.setVisible(False)

    def update_plot(self):
        try:
            self.plot.canvas.clear()
            plottype = self.ui.comboBoxPlotType.currentText()
            x_data = self.ui.comboBoxXData.currentText()
            y_data = self.ui.comboBoxYData.currentText()
            if plottype == "violinplot":
                ax = self.plot.canvas.figure.add_subplot(111)
                groups = self.df_selection[x_data].unique().tolist()
                to_plot = []
                for group in groups:
                    to_plot.append(
                        self.df_selection[y_data][self.df_selection[x_data] == group].dropna().values.tolist())

                ax.violinplot(to_plot)
                try:
                    ax.set_xticks([x + 1 for x in range(len(groups))])
                    if max([len(str(x)) for x in groups]) > 10:
                        rotation = 90
                    else:
                        rotation = 0
                    ax.set_xticklabels(groups, rotation=rotation)
                    ax.set_xlabel(x_data)
                    ax.set_ylabel(y_data)
                    self.plot.canvas.figure.tight_layout()
                    self.plot.canvas.draw()
                except:
                    pass
            elif plottype == "lineplot":
                ax = self.plot.canvas.figure.add_subplot(111)
                ax.plot(self.df_selection[x_data], self.df_selection[y_data])
                ax.set_xlabel(x_data)
                ax.set_ylabel(y_data)
                self.plot.canvas.figure.tight_layout()
                self.plot.canvas.draw()

            elif plottype == "scatterplot":
                ax = self.plot.canvas.figure.add_subplot(111)
                colorparam = self.ui.comboBoxColorParam.currentText()
                try:
                    ax.scatter(self.df_selection[x_data].dropna(), self.df_selection[y_data].dropna(),
                               c=self.df_selection.loc[self.df_selection[x_data].notnull(), colorparam])
                except:
                    try:
                        progress = 0
                        colordict = {}
                        counter = 0
                        for x in self.df_selection[colorparam].unique():
                            colordict[x] = counter
                            counter += 1
                        colors = [colordict[key] for key in self.df_selection[colorparam]]
                        x = self.df_selection[x_data]
                        y = self.df_selection[y_data]
                        ax.scatter(x, y, c=colors)
                    except Exception as e:
                        print(progress, str(e))

                ax.set_xlabel(x_data)
                ax.set_ylabel(y_data)
                self.plot.canvas.figure.tight_layout()
                self.plot.canvas.draw()

        except Exception as e:
            e = str(e)
            QtWidgets.QMessageBox.warning(self, "Error in plot",
                                          "It seems that you are making an impossible plot. Please look at your parameters. \n This is what the computer has to say: \n '" + e + "'")

    def open_console(self):
        if not self.ui.frameConsole.isVisible():
            if hasattr(self, "console"):
                if self.ui.frameConsole.isVisible() == False:
                    self.ui.frameConsole.setVisible(True)
                if self.ui.groupBoxPlotting.isVisible() == False:
                    self.ui.actionPlotting.setIcon(QtGui.QIcon("icons/checkmark.png"))
                    self.ui.groupBoxPlotting.setVisible(True)
            else:
                self.ui.frameConsole.setLayout(QtWidgets.QVBoxLayout())
                self.console = ConsoleWidget(namespace={"viewer": self, "pd": pd, "np": np, "os": os},
                                             text="\r This console has access to everything in the namespace of this viewer. "
                                                  "\n Example: viewer.df refers to the complete dataframe. viewer.df_selection refers to currently selected data "
                                                  "\n UI widgets are accessible using viewer.ui, like viewer.ui.console for this console."
                                                  "\n imported libraries: pandas as pd, numpy as np, os ")
                self.ui.frameConsole.layout().addWidget(self.console)
                self.ui.frameConsole.setVisible(True)
                self.ui.groupBoxPlotting.setVisible(True)
                self.ui.actionConsole.setIcon(QtGui.QIcon("icons/checkmark.png"))
        else:
            self.close_console()

    def close_console(self):
        if hasattr(self, "console"):
            self.console.setParent(None)
            delattr(self, "console")
            self.ui.frameConsole.setVisible(False)
            self.ui.actionConsole.setIcon(QtGui.QIcon())

    def hide_unhide_widget(self, widget, action):
        if widget.isVisible():
            widget.setVisible(False)
            action.setIcon(QtGui.QIcon())
        else:
            widget.setVisible(True)
            action.setIcon(QtGui.QIcon("icons/checkmark.png"))

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

    def transform(self):
        to_transform = self.df_selection[self.ui.comboBoxYData.currentText()]
        transformation = self.ui.comboBoxTransformations.currentText()
        transformed = self._transorm(to_transform, transformation)
        try:
            self.plot.canvas.clear()
            plottype = self.ui.comboBoxPlotType.currentText()
            x_data = self.ui.comboBoxXData.currentText()
            if plottype == "violinplot":
                ax = self.plot.canvas.figure.add_subplot(111)
                groups = self.df_selection[x_data].unique().tolist()
                to_plot = []
                for group in groups:
                    to_plot.append(
                        transformed[self.df_selection[x_data] == group].dropna().values.tolist())

                ax.violinplot(to_plot)
                try:
                    ax.set_xticks([x + 1 for x in range(len(groups))])
                    if max([len(str(x)) for x in groups]) > 10:
                        rotation = 90
                    else:
                        rotation = 0
                    ax.set_xticklabels(groups, rotation=rotation)
                    ax.set_xlabel(x_data)
                    ax.set_ylabel(transformation)
                    self.plot.canvas.figure.tight_layout()
                    self.plot.canvas.draw()
                except Exception as e:
                    print(f"{e}")
            elif plottype == "lineplot":
                ax = self.plot.canvas.figure.add_subplot(111)
                ax.plot(self.df_selection[x_data], transformed)
                ax.set_xlabel(x_data)
                ax.set_ylabel(transformation)
                self.plot.canvas.figure.tight_layout()
                self.plot.canvas.draw()

            elif plottype == "scatterplot":
                ax = self.plot.canvas.figure.add_subplot(111)
                colorparam = self.ui.comboBoxColorParam.currentText()
                try:
                    ax.scatter(self.df_selection[x_data].dropna(), transformed.dropna(),
                               c=self.df_selection.loc[self.df_selection[x_data].notnull(), colorparam])
                except:
                    try:
                        progress = 0
                        colordict = {}
                        counter = 0
                        for x in self.df_selection[colorparam].unique():
                            colordict[x] = counter
                            counter += 1
                        colors = [colordict[key] for key in self.df_selection[colorparam]]
                        x = self.df_selection[x_data]
                        y = transformed
                        ax.scatter(x, y, c=colors)
                    except Exception as e:
                        print(progress, str(e))

                ax.set_xlabel(x_data)
                ax.set_ylabel(transformation)
                self.plot.canvas.figure.tight_layout()
                self.plot.canvas.draw()

        except Exception as e:
            e = str(e)
            QtWidgets.QMessageBox.warning(self, "Error in plot",
                                          "It seems that you are making an impossible plot. Please look at your parameters. \n This is what the computer has to say: \n '" + e + "'")

    def add_transformation_to_data(self):
        names = {"none": "none", "square root": "sqrt", "natural logarithm": "ln", "reciprocal": "rcp",
                 "reciprocal sqrt": "rcpsqrt", "exponential": "exp"}
        param = self.ui.comboBoxYData.currentText()
        to_transform = self.df_selection[param]
        transformation = self.ui.comboBoxTransformations.currentText()
        transformed = self._transorm(to_transform, transformation)
        colname = param + "_" + names[transformation]
        self.df_selection[colname] = transformed
        self.update_plotting_ui()
        self.set_data(self.ui.tableWidgetSelectedData, self.df_selection)

    def normalize_data(self, scaling_type="minmax"):
        to_scale = [col for col in self.df_selection.columns if self.datatype_columns[col]["datatype"] == "numerical"]
        if scaling_type == "minmax":
            minimum, ok = QtWidgets.QInputDialog.getDouble(self, "Set min value", "Input a number", value=-1)
            maximum, ok = QtWidgets.QInputDialog.getDouble(self, "Set max value", "Input a number", value=1)
            self.df_selection[to_scale] = minmax_scale(self.df_selection[to_scale], feature_range=(minimum, maximum))
        else:
            self.df_selection[to_scale] = scale(self.df_selection[to_scale])

        self.set_data(self.ui.tableWidgetSelectedData, self.df_selection)

    def start_significance_scanner(self):
        significance_scanner = SignificanceScanner(parent_module=self)
        significance_scanner.show()

    def start_pairwise_scanner(self):
        # pairwise_scanner = PairwiseScanner(parent_module=self)
        try:
            pairwise_scanner = SSMDScanner(parent_module=self)
            pairwise_scanner.show()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error starting scannermodule",
                                          "This is what the computer has to say: \n '" + str(
                                              e) + " \n \n Have you selected any data?")

    def run_statistics(self):
        test = self.ui.comboBoxStatisticalTests.currentText()
        alpha = self.ui.doubleSpinBoxAlpha.value()
        x_data = self.ui.comboBoxXData.currentText()
        y_data = self.ui.comboBoxYData.currentText()
        groups = self.df_selection[x_data].unique().tolist()
        to_plot = []
        for group in groups:
            to_plot.append(self.df_selection[y_data][self.df_selection[x_data] == group].dropna().values.tolist())
        if "kruskal" in test.lower():
            pval = stats.kruskal(*to_plot)[1]
        else:
            pval = stats.f_oneway(*to_plot)[1]
        self.ui.lineEditPvalue.setText(str(pval))
        sys.stdout.write("\n Results for " + test + " " + x_data + " vs " + y_data + " \n pval= " + str(pval) + "\n")

    def start_item_renamer(self):
        self.item_renamer = ItemRenamer(parent_module=self)

    def start_roaming_calculator(self, data):
        print("Roaming Calculater currently not implemented")
