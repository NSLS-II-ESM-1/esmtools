# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SES_plot_GUI.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Main_window(object):
    def setupUi(self, Main_window):
        Main_window.setObjectName("Main_window")
        Main_window.resize(1400, 1200)
        font = QtGui.QFont()
        font.setFamily("Sans")
        font.setPointSize(12)
        Main_window.setFont(font)
        self.centralwidget = QtWidgets.QWidget(Main_window)
        font = QtGui.QFont()
        font.setFamily("Century Schoolbook L")
        font.setPointSize(12)
        font.setItalic(True)
        self.centralwidget.setFont(font)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(40, 50, 551, 61))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit_dir = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_dir.setObjectName("lineEdit_dir")
        self.gridLayout.addWidget(self.lineEdit_dir, 1, 0, 1, 1)
        self.lineEdit_file = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_file.setObjectName("lineEdit_file")
        self.gridLayout.addWidget(self.lineEdit_file, 1, 1, 1, 1)
        self.pushButton_unzip = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.pushButton_unzip.setObjectName("pushButton_unzip")
        self.gridLayout.addWidget(self.pushButton_unzip, 1, 2, 1, 1)
        self.fixed_label_energy_center = QtWidgets.QLabel(self.gridLayoutWidget)
        self.fixed_label_energy_center.setAlignment(QtCore.Qt.AlignCenter)
        self.fixed_label_energy_center.setObjectName("fixed_label_energy_center")
        self.gridLayout.addWidget(self.fixed_label_energy_center, 0, 0, 1, 1)
        self.fixed_label_energy_width = QtWidgets.QLabel(self.gridLayoutWidget)
        self.fixed_label_energy_width.setAlignment(QtCore.Qt.AlignCenter)
        self.fixed_label_energy_width.setObjectName("fixed_label_energy_width")
        self.gridLayout.addWidget(self.fixed_label_energy_width, 0, 1, 1, 1)
        self.label_scan_status = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_scan_status.setAlignment(QtCore.Qt.AlignCenter)
        self.label_scan_status.setObjectName("label_scan_status")
        self.gridLayout.addWidget(self.label_scan_status, 0, 2, 1, 1)
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(210, 140, 991, 981))
        self.widget.setObjectName("widget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gv_00 = ImageView(self.widget)
        self.gv_00.setObjectName("gv_00")
        self.gridLayout_2.addWidget(self.gv_00, 0, 0, 1, 1)
        self.gv_01 = ImageView(self.widget)
        self.gv_01.setObjectName("gv_01")
        self.gridLayout_2.addWidget(self.gv_01, 0, 1, 1, 1)
        self.gv_11 = ImageView(self.widget)
        self.gv_11.setObjectName("gv_11")
        self.gridLayout_2.addWidget(self.gv_11, 1, 0, 1, 1)
        self.gv_12 = ImageView(self.widget)
        self.gv_12.setObjectName("gv_12")
        self.gridLayout_2.addWidget(self.gv_12, 1, 1, 1, 1)
        Main_window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1400, 29))
        self.menubar.setObjectName("menubar")
        self.menuOpen = QtWidgets.QMenu(self.menubar)
        self.menuOpen.setObjectName("menuOpen")
        Main_window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Main_window)
        self.statusbar.setObjectName("statusbar")
        Main_window.setStatusBar(self.statusbar)
        self.actionLoad = QtWidgets.QAction(Main_window)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../icons/arrow-circle-225.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionLoad.setIcon(icon)
        self.actionLoad.setObjectName("actionLoad")
        self.menuOpen.addAction(self.actionLoad)
        self.menubar.addAction(self.menuOpen.menuAction())

        self.retranslateUi(Main_window)
        QtCore.QMetaObject.connectSlotsByName(Main_window)

    def retranslateUi(self, Main_window):
        _translate = QtCore.QCoreApplication.translate
        Main_window.setWindowTitle(_translate("Main_window", "SES_plot"))
        self.pushButton_unzip.setText(_translate("Main_window", "UnZip"))
        self.fixed_label_energy_center.setText(_translate("Main_window", "Directory"))
        self.fixed_label_energy_width.setText(_translate("Main_window", "File"))
        self.label_scan_status.setText(_translate("Main_window", "Idle"))
        self.menuOpen.setTitle(_translate("Main_window", "File"))
        self.actionLoad.setText(_translate("Main_window", "Load"))

from pyqtgraph import ImageView

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Main_window = QtWidgets.QMainWindow()
    ui = Ui_Main_window()
    ui.setupUi(Main_window)
    Main_window.show()
    sys.exit(app.exec_())

