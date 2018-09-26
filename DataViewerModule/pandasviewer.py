import pandas as pd
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from pandasviewer_ui import Ui_Form
from PlottingModule.PlottingClasses import PlotWidget
import sys
import ast

class PandasViewer(QtWidgets.QWidget):
    def __init__(self, parent = None,*args, df):
        QtWidgets.QWidget.__init__(self, parent, *args)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.df = df   
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

        self.toCSVAct = QtWidgets.QAction("&Save Selection to CSV", self, triggered = self.save_selection_to_csv)

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

    def contextMenuEvent_SelectedData(self, event):
        geometry = self.geometry()
        x, y, w, h = geometry.getCoords()
        menu = QtWidgets.QMenu(self)
        location = QtCore.QPoint()
        x += event.x() + 200
        y += event.y() +50
        location.setX(x)
        location.setY(y)

        menu.addAction(self.toCSVAct)
        menu.popup(location)
    
    def contextMenuEvent_AppliedFilters(self, event):
        geometry = self.geometry()
        x, y, w, h = geometry.getCoords()
        menu = QtWidgets.QMenu(self)
        location = QtCore.QPoint()
        x += event.x() + 200
        y += event.y() +50
        location.setX(x)
        location.setY(y)

        menu.addAction(self.removeFilteract)
        menu.popup(location)

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
        filters_to_remove = self.ui.listWidgetAppliedFilters.selectedItems()[0].text()
        print("Removing :", filters_to_remove)
        for filt in filters_to_remove:
            self.filters.pop(filt)
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
            
        filtername = col
        x = 1
        while filtername in self.filters.keys():
            filtername += str(x).zfill(2)
            x+=1
        self.filters[filtername] = (col, self.radioButtonInclude.isChecked(), selection)

    def apply_filter(self):
#        self.df_selection = self.df_selection_rows
        self.create_filter()
        self.apply_filters()
        self.set_data(self.ui.tableWidgetSelectedData, self.df_selection)
        self.ui.checkBoxPreviewSelection.setChecked(False)
        self.update_unique_values()
        self.update_plotting_ui()
        
        
    def save_selection_to_csv(self):
        filename = QtWidgets.QFileDialog.getSaveFileName()
        self.df_selection.to_csv(filename, sep = "\t")
        
    def update_plotting_ui(self):
        self.ui.groupBoxPlotting.setVisible(True)
        for box in [self.ui.comboBoxXData, self.ui.comboBoxYData]:
            box.clear()
            box.addItems(self.df_selection.columns)

    def update_plot(self):
        self.plot.canvas.clear()
        plottype = self.ui.comboBoxPlotType.currentText()
        if plottype == "violinplot":
            ax = self.plot.canvas.figure.add_subplot(111)
            x_data = self.ui.comboBoxXData.currentText()
            y_data = self.ui.comboBoxYData.currentText()
            groups = self.df_selection[x_data].unique().tolist()
            to_plot = []
            for group in groups:
                to_plot.append(self.df_selection[y_data][self.df_selection[x_data] == group].values.tolist())
            
            ax.violinplot(to_plot)
            try:
                ax.set_xticks([x+1 for x in range(len(groups))])
                ax.set_xticklabels(groups)
                ax.set_xlabel(x_data)
                ax.set_ylabel(y_data)
                self.plot.canvas.figure.tight_layout()
            except:
                pass
            