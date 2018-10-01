# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pandasviewer_mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.tabWidget_2 = QtWidgets.QTabWidget(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget_2.sizePolicy().hasHeightForWidth())
        self.tabWidget_2.setSizePolicy(sizePolicy)
        self.tabWidget_2.setObjectName("tabWidget_2")
        self.AllColumns = QtWidgets.QWidget()
        self.AllColumns.setObjectName("AllColumns")
        self.gridLayout = QtWidgets.QGridLayout(self.AllColumns)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButtonAddToSelection = QtWidgets.QPushButton(self.AllColumns)
        self.pushButtonAddToSelection.setObjectName("pushButtonAddToSelection")
        self.gridLayout.addWidget(self.pushButtonAddToSelection, 1, 0, 1, 1)
        self.listWidgetAllColumns = QtWidgets.QListWidget(self.AllColumns)
        self.listWidgetAllColumns.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidgetAllColumns.setObjectName("listWidgetAllColumns")
        self.gridLayout.addWidget(self.listWidgetAllColumns, 0, 0, 1, 1)
        self.tabWidget_2.addTab(self.AllColumns, "")
        self.SelectedColumns = QtWidgets.QWidget()
        self.SelectedColumns.setObjectName("SelectedColumns")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.SelectedColumns)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.listWidgetSelectedColumns = QtWidgets.QListWidget(self.SelectedColumns)
        self.listWidgetSelectedColumns.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidgetSelectedColumns.setObjectName("listWidgetSelectedColumns")
        self.gridLayout_4.addWidget(self.listWidgetSelectedColumns, 0, 0, 1, 1)
        self.pushButtonRemoveFromSelection = QtWidgets.QPushButton(self.SelectedColumns)
        self.pushButtonRemoveFromSelection.setObjectName("pushButtonRemoveFromSelection")
        self.gridLayout_4.addWidget(self.pushButtonRemoveFromSelection, 1, 0, 1, 1)
        self.tabWidget_2.addTab(self.SelectedColumns, "")
        self.RowFilters = QtWidgets.QWidget()
        self.RowFilters.setObjectName("RowFilters")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.RowFilters)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.comboBoxSelectedColumns = QtWidgets.QComboBox(self.RowFilters)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBoxSelectedColumns.sizePolicy().hasHeightForWidth())
        self.comboBoxSelectedColumns.setSizePolicy(sizePolicy)
        self.comboBoxSelectedColumns.setObjectName("comboBoxSelectedColumns")
        self.horizontalLayout_2.addWidget(self.comboBoxSelectedColumns)
        self.checkBoxUnique = QtWidgets.QCheckBox(self.RowFilters)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBoxUnique.sizePolicy().hasHeightForWidth())
        self.checkBoxUnique.setSizePolicy(sizePolicy)
        self.checkBoxUnique.setObjectName("checkBoxUnique")
        self.horizontalLayout_2.addWidget(self.checkBoxUnique)
        self.checkBoxSorting = QtWidgets.QCheckBox(self.RowFilters)
        self.checkBoxSorting.setObjectName("checkBoxSorting")
        self.horizontalLayout_2.addWidget(self.checkBoxSorting)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.listWidgetUniqueValues = QtWidgets.QListWidget(self.RowFilters)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(5)
        sizePolicy.setHeightForWidth(self.listWidgetUniqueValues.sizePolicy().hasHeightForWidth())
        self.listWidgetUniqueValues.setSizePolicy(sizePolicy)
        self.listWidgetUniqueValues.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidgetUniqueValues.setObjectName("listWidgetUniqueValues")
        self.verticalLayout.addWidget(self.listWidgetUniqueValues)
        self.label_4 = QtWidgets.QLabel(self.RowFilters)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.listWidgetAppliedFilters = QtWidgets.QListWidget(self.RowFilters)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidgetAppliedFilters.sizePolicy().hasHeightForWidth())
        self.listWidgetAppliedFilters.setSizePolicy(sizePolicy)
        self.listWidgetAppliedFilters.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.listWidgetAppliedFilters.setObjectName("listWidgetAppliedFilters")
        self.verticalLayout.addWidget(self.listWidgetAppliedFilters)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.radioButtonInclude = QtWidgets.QRadioButton(self.RowFilters)
        self.radioButtonInclude.setChecked(True)
        self.radioButtonInclude.setObjectName("radioButtonInclude")
        self.horizontalLayout.addWidget(self.radioButtonInclude)
        self.radioButtonLessThan = QtWidgets.QRadioButton(self.RowFilters)
        self.radioButtonLessThan.setObjectName("radioButtonLessThan")
        self.horizontalLayout.addWidget(self.radioButtonLessThan)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.checkBoxPreviewSelection = QtWidgets.QCheckBox(self.RowFilters)
        self.checkBoxPreviewSelection.setObjectName("checkBoxPreviewSelection")
        self.horizontalLayout_3.addWidget(self.checkBoxPreviewSelection)
        self.pushButtonApplyFilters = QtWidgets.QPushButton(self.RowFilters)
        self.pushButtonApplyFilters.setObjectName("pushButtonApplyFilters")
        self.horizontalLayout_3.addWidget(self.pushButtonApplyFilters)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.tabWidget_2.addTab(self.RowFilters, "")
        self.gridLayout_6.addWidget(self.tabWidget_2, 0, 0, 1, 1)
        self.gridLayout_5.addWidget(self.groupBox, 0, 0, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.AllData = QtWidgets.QWidget()
        self.AllData.setObjectName("AllData")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.AllData)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tableWidgetAllData = QtWidgets.QTableWidget(self.AllData)
        self.tableWidgetAllData.setObjectName("tableWidgetAllData")
        self.tableWidgetAllData.setColumnCount(0)
        self.tableWidgetAllData.setRowCount(0)
        self.gridLayout_2.addWidget(self.tableWidgetAllData, 0, 0, 1, 1)
        self.tabWidget.addTab(self.AllData, "")
        self.SelectedData = QtWidgets.QWidget()
        self.SelectedData.setObjectName("SelectedData")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.SelectedData)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.tableWidgetSelectedData = QtWidgets.QTableWidget(self.SelectedData)
        self.tableWidgetSelectedData.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tableWidgetSelectedData.setObjectName("tableWidgetSelectedData")
        self.tableWidgetSelectedData.setColumnCount(0)
        self.tableWidgetSelectedData.setRowCount(0)
        self.gridLayout_3.addWidget(self.tableWidgetSelectedData, 0, 2, 1, 1)
        self.tabWidget.addTab(self.SelectedData, "")
        self.gridLayout_5.addWidget(self.tabWidget, 0, 1, 1, 1)
        self.groupBoxPlotting = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBoxPlotting.sizePolicy().hasHeightForWidth())
        self.groupBoxPlotting.setSizePolicy(sizePolicy)
        self.groupBoxPlotting.setObjectName("groupBoxPlotting")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.groupBoxPlotting)
        self.gridLayout_7.setObjectName("gridLayout_7")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_7.addItem(spacerItem, 3, 0, 1, 1)
        self.framePlotWidget = QtWidgets.QFrame(self.groupBoxPlotting)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.framePlotWidget.sizePolicy().hasHeightForWidth())
        self.framePlotWidget.setSizePolicy(sizePolicy)
        self.framePlotWidget.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.framePlotWidget.setFrameShadow(QtWidgets.QFrame.Raised)
        self.framePlotWidget.setObjectName("framePlotWidget")
        self.gridLayout_7.addWidget(self.framePlotWidget, 1, 0, 1, 1)
        self.framePlotControls = QtWidgets.QFrame(self.groupBoxPlotting)
        self.framePlotControls.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.framePlotControls.setFrameShadow(QtWidgets.QFrame.Raised)
        self.framePlotControls.setObjectName("framePlotControls")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.framePlotControls)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.framePlotControls)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_3.addWidget(self.label_2)
        self.comboBoxXData = QtWidgets.QComboBox(self.framePlotControls)
        self.comboBoxXData.setObjectName("comboBoxXData")
        self.verticalLayout_3.addWidget(self.comboBoxXData)
        self.horizontalLayout_4.addLayout(self.verticalLayout_3)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.framePlotControls)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.comboBoxYData = QtWidgets.QComboBox(self.framePlotControls)
        self.comboBoxYData.setObjectName("comboBoxYData")
        self.verticalLayout_2.addWidget(self.comboBoxYData)
        self.horizontalLayout_4.addLayout(self.verticalLayout_2)
        self.gridLayout_8.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_3 = QtWidgets.QLabel(self.framePlotControls)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_4.addWidget(self.label_3)
        self.gridLayout_8.addLayout(self.verticalLayout_4, 1, 0, 1, 1)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.comboBoxPlotType = QtWidgets.QComboBox(self.framePlotControls)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBoxPlotType.sizePolicy().hasHeightForWidth())
        self.comboBoxPlotType.setSizePolicy(sizePolicy)
        self.comboBoxPlotType.setObjectName("comboBoxPlotType")
        self.horizontalLayout_5.addWidget(self.comboBoxPlotType)
        self.labelColorParam = QtWidgets.QLabel(self.framePlotControls)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelColorParam.sizePolicy().hasHeightForWidth())
        self.labelColorParam.setSizePolicy(sizePolicy)
        self.labelColorParam.setObjectName("labelColorParam")
        self.horizontalLayout_5.addWidget(self.labelColorParam)
        self.comboBoxColorParam = QtWidgets.QComboBox(self.framePlotControls)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBoxColorParam.sizePolicy().hasHeightForWidth())
        self.comboBoxColorParam.setSizePolicy(sizePolicy)
        self.comboBoxColorParam.setObjectName("comboBoxColorParam")
        self.horizontalLayout_5.addWidget(self.comboBoxColorParam)
        self.gridLayout_8.addLayout(self.horizontalLayout_5, 2, 0, 1, 1)
        self.pushButtonPlot = QtWidgets.QPushButton(self.framePlotControls)
        self.pushButtonPlot.setObjectName("pushButtonPlot")
        self.gridLayout_8.addWidget(self.pushButtonPlot, 3, 0, 1, 1)
        self.gridLayout_7.addWidget(self.framePlotControls, 0, 0, 1, 1)
        self.frameConsole = QtWidgets.QFrame(self.groupBoxPlotting)
        self.frameConsole.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameConsole.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameConsole.setObjectName("frameConsole")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.frameConsole)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_5 = QtWidgets.QLabel(self.frameConsole)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_5.addWidget(self.label_5)
        self.gridLayout_7.addWidget(self.frameConsole, 2, 0, 1, 1)
        self.gridLayout_5.addWidget(self.groupBoxPlotting, 0, 2, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menuTools = QtWidgets.QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        self.menuSave_Selected_Data = QtWidgets.QMenu(self.menuTools)
        self.menuSave_Selected_Data.setObjectName("menuSave_Selected_Data")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_as_CSV = QtWidgets.QAction(MainWindow)
        self.action_as_CSV.setObjectName("action_as_CSV")
        self.action_as_Pickle = QtWidgets.QAction(MainWindow)
        self.action_as_Pickle.setObjectName("action_as_Pickle")
        self.actionLoad_Dataset_into_Viewer = QtWidgets.QAction(MainWindow)
        self.actionLoad_Dataset_into_Viewer.setObjectName("actionLoad_Dataset_into_Viewer")
        self.menuSave_Selected_Data.addAction(self.action_as_CSV)
        self.menuSave_Selected_Data.addAction(self.action_as_Pickle)
        self.menuTools.addAction(self.actionLoad_Dataset_into_Viewer)
        self.menuTools.addAction(self.menuSave_Selected_Data.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget_2.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox.setTitle(_translate("MainWindow", "Data Selection"))
        self.pushButtonAddToSelection.setText(_translate("MainWindow", "Add to Selection"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.AllColumns), _translate("MainWindow", "All Columns"))
        self.pushButtonRemoveFromSelection.setText(_translate("MainWindow", "Remove from Selection"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.SelectedColumns), _translate("MainWindow", "Selected Columns"))
        self.checkBoxUnique.setText(_translate("MainWindow", "Unique vals"))
        self.checkBoxSorting.setText(_translate("MainWindow", "Sort"))
        self.label_4.setText(_translate("MainWindow", "Applied Filters:"))
        self.radioButtonInclude.setText(_translate("MainWindow", "include"))
        self.radioButtonLessThan.setText(_translate("MainWindow", "exclude"))
        self.checkBoxPreviewSelection.setText(_translate("MainWindow", "Preview Selection"))
        self.pushButtonApplyFilters.setText(_translate("MainWindow", "Apply"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.RowFilters), _translate("MainWindow", "Row Filters"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.AllData), _translate("MainWindow", "All Data"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.SelectedData), _translate("MainWindow", "Selected Data"))
        self.groupBoxPlotting.setTitle(_translate("MainWindow", "PlottingControls"))
        self.label_2.setText(_translate("MainWindow", "X-Data"))
        self.label.setText(_translate("MainWindow", "Y-Data"))
        self.label_3.setText(_translate("MainWindow", "Plot Type"))
        self.labelColorParam.setText(_translate("MainWindow", "Color by:"))
        self.pushButtonPlot.setText(_translate("MainWindow", "Plot"))
        self.label_5.setText(_translate("MainWindow", "Python Console:"))
        self.menuTools.setTitle(_translate("MainWindow", "Tools"))
        self.menuSave_Selected_Data.setTitle(_translate("MainWindow", "Save Selected Data..."))
        self.action_as_CSV.setText(_translate("MainWindow", "...as CSV"))
        self.action_as_Pickle.setText(_translate("MainWindow", "...as Pickle"))
        self.actionLoad_Dataset_into_Viewer.setText(_translate("MainWindow", "Load Dataset into Viewer"))
