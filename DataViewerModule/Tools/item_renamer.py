
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from scipy import stats
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
from DataViewerModule.Tools.item_renamer_ui import Ui_Form

class ItemRenamer(QtWidgets.QWidget):
    def __init__(self, parent = None, *args, parent_module = None):
        QtWidgets.QWidget.__init__(self, parent, *args)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.show()

        self.pm = parent_module

        self.ui.listWidgetAllColumns.addItems(self.pm.df_selection.columns)
        self.ui.listWidgetAllColumns.itemSelectionChanged.connect(self.setItemColumn)
        self.ui.lineEditSearchColumns.textChanged.connect(self.search_columns)
        self.ui.lineEditSearchItems.textChanged.connect(self.search_items)

        self.ui.pushButtonAddToChange.clicked.connect(self.add_items_to_rename)

        self.ui.pushButtonOverwrite.clicked.connect(self.overwrite)
        self.ui.pushButtonOverwriteAll.clicked.connect(lambda: self.overwrite(all = True))
        self.ui.pushButtonRemoveSelection.clicked.connect(self.remove_selected_items)

    def setItemColumn(self):
        try:
            col = self.ui.listWidgetAllColumns.currentItem().text()
            unique_items = list(self.pm.df_selection[col].unique())
            self.ui.listWidgetUniqueItems.clear()
            self.ui.listWidgetUniqueItems.addItems(unique_items)
        except Exception as e:
            if QtWidgets.QMessageBox.warning(self, "Need to convert to string for renaming operation",
                                             "A conversion from the current datatype to string is required for the renaming operation. Continue?",
                                             QtWidgets.QMessageBox.Ok,
                                             QtWidgets.QMessageBox.Cancel) == QtWidgets.QMessageBox.Ok:
                self.pm.df_selection[col] = self.pm.df_selection[col].astype("str")
                self.pm.df[col] = self.pm.df[col].astype("str")
                self.setItemColumn()

    def search_columns(self):
        query = self.ui.lineEditSearchColumns.text()
        cols = [col for col in self.pm.df_selection.columns if query.lower() in col.lower()]
        self.ui.listWidgetAllColumns.clear()
        self.ui.listWidgetAllColumns.addItems(cols)

    def search_items(self):
        query = self.ui.lineEditSearchItems.text()
        col = self.ui.listWidgetAllColumns.currentItem().text()
        items = list(self.pm.df_selection[col].unique())
        selected_items = [item for item in items if query.lower() in item.lower()]
        self.ui.listWidgetUniqueItems.clear()
        self.ui.listWidgetUniqueItems.addItems(selected_items)

    def add_items_to_rename(self):
        present_items = [self.ui.listWidgetToRename.item(i).text() for i in range(self.ui.listWidgetToRename.count())]
        items = [item.text() for item in self.ui.listWidgetUniqueItems.selectedItems() if item.text() not in present_items]
        self.ui.listWidgetToRename.addItems(items)

    def remove_selected_items(self):
        items_to_remove = [item.text() for item in self.ui.listWidgetToRename.selectedItems()]
        all_items = [self.ui.listWidgetToRename.item(i).text() for i in range(self.ui.listWidgetToRename.count()) if self.ui.listWidgetToRename.item(i).text() not in items_to_remove]
        self.ui.listWidgetToRename.clear()
        self.ui.listWidgetToRename.addItems(all_items)

    def overwrite(self, all = False):
        if len(self.ui.lineEditNewName.text()) < 2:
            QtWidgets.QMessageBox.warning(self, "Short name warning", "For safety reasons you can not enter such a short name.")
        else:
            try:
                old_names = [self.ui.listWidgetToRename.item(i).text() for i in range(self.ui.listWidgetToRename.count())]
                new_name = self.ui.lineEditNewName.text()
                col = self.ui.listWidgetAllColumns.currentItem().text()
                for name in old_names:
                    self.pm.df_selection[col][self.pm.df_selection[col] == name] = new_name
                    if all:
                        self.pm.df[col][self.pm.df[col] == name] = new_name


                self.pm.set_data(self.pm.ui.tableWidgetSelectedData, self.pm.df_selection)
                if all:
                    self.pm.set_data(self.pm.ui.tableWidgetAllData, self.pm.df)

                self.setItemColumn()
                self.search_items()
                self.ui.listWidgetToRename.clear()

            except Exception as e:
                print(e)