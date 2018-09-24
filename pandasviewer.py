import pandas as pd
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from pandasviewer_ui import Ui_Form


class PandasViewer(QtWidgets.QWidget):
    def __init__(self, parent = None,*args, df):
        QtWidgets.QWidget.__init__(self, parent, *args)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.df = df   
        self.set_data(self.ui.tableWidgetAllData, self.df)
        self.set_column_widget()
        
        self.ui.pushButtonAddToSelection.clicked.connect(self.add_to_selection)
        self.ui.pushButtonRemoveFromSelection.clicked.connect(self.remove_from_selection)

    
    def set_data(self, tableWidget, df):
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
        self.df_selection = self.df[selection]
        self.set_data(self.ui.tableWidgetSelectedData, self.df_selection)

        self.ui.comboBoxSelectedColumns.clear()
        for item in selection:
            self.ui.comboBoxSelectedColumns.addItem(item)