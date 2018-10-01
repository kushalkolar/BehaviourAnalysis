import pandas as pd
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from pyqtgraph.console import ConsoleWidget
from DataViewerModule.pandasviewer_mainwindow import Ui_MainWindow
from DataViewerModule.PlottingModule.PlottingClasses import PlotWidget
import sys
import ast

class PandasViewer(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None,*args, df = "none"):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
        
        self.ui.treeWidgetAllColums.setVisible(False)
        
        try:
            if type(df) == str:
                if not df.endswith("pickle"):
                    self.df = pd.read_csv(df, delimiter= "\t")
                else:
                    self.df = pd.read_pickle(df)
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

        self.ui.pushButtonApplyFilters.clicked.connect(self.apply_filter)
        self.ui.checkBoxUnique.clicked.connect(self.update_unique_values)
        self.ui.checkBoxSorting.clicked.connect(self.update_unique_values)
        self.ui.listWidgetUniqueValues.itemSelectionChanged.connect(self.row_selection)
        self.ui.checkBoxPreviewSelection.clicked.connect(self.row_selection)

        self.ui.tableWidgetSelectedData.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.tableWidgetSelectedData.customContextMenuRequested.connect(self.contextMenuEvent_SelectedData)

        self.ui.actionLoad_Dataset_into_Viewer.triggered.connect(self.load_dataset)
        self.ui.action_as_CSV.triggered.connect(lambda: self.save_selection(as_type = "csv"))
        self.ui.action_as_Pickle.triggered.connect(lambda: self.save_selection(as_type = "pickle"))
        self.toCSVAct = QtWidgets.QAction("&Save Selection to CSV", self, triggered = lambda: self.save_selection(as_type = "csv"))

        self.ui.groupBoxPlotting.setVisible(False)
        self.ui.framePlotWidget.setLayout(QtWidgets.QVBoxLayout())
        self.plot = PlotWidget()
        self.ui.framePlotWidget.layout().addWidget(self.plot)
        
        self.ui.pushButtonPlot.clicked.connect(self.update_plot)
        for plottype in ["violinplot", "lineplot", "scatterplot"]:
            self.ui.comboBoxPlotType.addItem(plottype)
            
        self.ui.listWidgetAppliedFilters.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.listWidgetAppliedFilters.customContextMenuRequested.connect(self.contextMenuEvent_AppliedFilters)

        self.removeFilteract = QtWidgets.QAction("&Remove Selected Filter(s)", self, triggered = self.remove_filters)

        self.ui.groupBoxPlotting.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.groupBoxPlotting.customContextMenuRequested.connect(self.contextMenuEvent_PlottingMenu)
        self.updatePlottingUIact = QtWidgets.QAction("&Update...", self, triggered = self.update_plotting_ui)

        self.ui.comboBoxPlotType.currentTextChanged.connect(self.toggle_colorselection)
        self.ui.comboBoxColorParam.setVisible(False)
        self.ui.labelColorParam.setVisible(False)

        self.ui.frameConsole.setLayout(QtWidgets.QVBoxLayout())
        self.console = ConsoleWidget(namespace={"self":self})
        self.ui.frameConsole.layout().addWidget(self.console)

    def contextMenuEvent_SelectedData(self, event):
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.toCSVAct)
        menu.popup(self.ui.tableWidgetSelectedData.mapToGlobal(event))
    
    def contextMenuEvent_AppliedFilters(self, event):
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.removeFilteract)
        menu.popup(self.ui.listWidgetAppliedFilters.mapToGlobal(event))

    def contextMenuEvent_PlottingMenu(self, event):
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.updatePlottingUIact)
        menu.popup(self.ui.groupBoxPlotting.mapToGlobal(event))

    def load_dataset(self):
        path = QtWidgets.QFileDialog.getOpenFileName()[0]
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


    def set_data(self, tableWidget, df):
        if "index" not in df.columns:
            df["index"] = df.index
        tableWidget.setColumnCount(len(df.columns))
        tableWidget.setHorizontalHeaderLabels(df.columns)
        tableWidget.setRowCount(len(df))
        for i in range(len(df.index)):
            for j in range(len(df.columns)):
                tableWidget.setItem(i,j,QtWidgets.QTableWidgetItem(str(df.iloc[i,j])))
        
    def set_column_widget(self):
        self.ui.listWidgetAllColumns.addItems(self.df.columns)

#THIS IS CODE TO SHOW COLUMNS IN A TREE WIDGET ITEM! SET VISIBLE TO FALSE IN __init__ TO SHOW THE WIDGET
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
        selected_columns = [self.ui.listWidgetSelectedColumns.item(i).text() for i in range(self.ui.listWidgetSelectedColumns.count())]
        for item in selection_to_add:
            if item not in selected_columns:
                self.ui.listWidgetSelectedColumns.addItem(item)        
        self.update_selected_data()

    def remove_from_selection(self):
        
        selection_to_remove = [item.text() for item in self.ui.listWidgetSelectedColumns.selectedItems()]
        selected_columns = [self.ui.listWidgetSelectedColumns.item(i).text() for i in range(self.ui.listWidgetSelectedColumns.count())]
        print(selection_to_remove)
        print(selected_columns)
        self.ui.listWidgetSelectedColumns.clear()
        for item in selected_columns:
            if item not in selection_to_remove:
                self.ui.listWidgetSelectedColumns.addItem(item)
            
        self.update_selected_data()
    
    def update_selected_data(self):
        selection = [self.ui.listWidgetSelectedColumns.item(i).text() for i in range(self.ui.listWidgetSelectedColumns.count())]
#        self.df_selection = self.df[selection]
        self.apply_filters()
        self.set_data(self.ui.tableWidgetSelectedData, self.df_selection)

        self.ui.comboBoxSelectedColumns.clear()
        self.ui.comboBoxSelectedColumns.addItem("index")
        for item in selection:
            self.ui.comboBoxSelectedColumns.addItem(item)

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
#        x = 1
#        
#        while filtername in self.filters.keys():
#            filtername += str(x).zfill(2)
#            x+=1
        
        include = self.ui.radioButtonInclude.isChecked()
        
        if self.df[col].dtype == "O":
            selection = [x.data(0) for x in self.ui.listWidgetUniqueValues.selectedItems()]
            
        else:
            selection = [ast.literal_eval(x.data(0)) for x in self.ui.listWidgetUniqueValues.selectedItems()]
                
        self.filters[filtername] = (col, include, selection)
    
    
    def apply_filters(self):
        columns = [self.ui.listWidgetSelectedColumns.item(i).text() for i in range(self.ui.listWidgetSelectedColumns.count())]
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


    def apply_filter(self):
        self.create_filter()
        self.apply_filters()
        self.set_data(self.ui.tableWidgetSelectedData, self.df_selection)
        self.ui.checkBoxPreviewSelection.setChecked(False)
        self.update_unique_values()
        self.update_plotting_ui()
        
        
    def save_selection(self, as_type):
        filename = QtWidgets.QFileDialog.getSaveFileName()[0]
        if as_type == "csv":
            if not filename.endswith(".txt"):
                filename += ".txt"
                self.df_selection.to_csv(filename, sep = "\t")
        elif as_type == "pickle":
            if not filename.endswith(".pickle"):
                filename += ".pickle"
                self.df_selection.to_pickle(filename)
        print(filename)

    def update_plotting_ui(self):
        self.ui.groupBoxPlotting.setVisible(True)
        for box in [self.ui.comboBoxXData, self.ui.comboBoxYData]:
            box.clear()
            box.addItems(self.df_selection.columns)
        self.toggle_colorselection()

    def toggle_colorselection(self, text = "None"):
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
                    to_plot.append(self.df_selection[y_data][self.df_selection[x_data] == group].dropna().values.tolist())

                ax.violinplot(to_plot)
                try:
                    ax.set_xticks([x+1 for x in range(len(groups))])
                    ax.set_xticklabels(groups)
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
                                   c = self.df_selection.loc[self.df_selection[x_data].notnull(), colorparam])
                except:
                    try:
                        progress = 0
                        colordict = {}
                        counter = 0
                        for x in self.df_selection[colorparam].unique():
                            colordict[x] = counter
                            counter+=1
                        colors = [colordict[key] for key in self.df_selection[colorparam]]
                        x = self.df_selection[x_data]
                        y = self.df_selection[y_data]
                        ax.scatter(x, y,c=colors)
                    except Exception as e:
                        print(progress, str(e))

                ax.set_xlabel(x_data)
                ax.set_ylabel(y_data)
                self.plot.canvas.figure.tight_layout()
                self.plot.canvas.draw()

        except Exception as e:
            e = str(e)
            QtWidgets.QMessageBox.warning(self, "Error in plot", "It seems that you are making an impossible plot. Please look at your parameters. \n This is what the computer has to say: \n '"+e+"'")
            