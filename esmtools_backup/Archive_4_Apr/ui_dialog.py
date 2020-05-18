# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dlg_win(object):
    def setupUi(self, dlg_win):
        dlg_win.setObjectName("dlg_win")
        dlg_win.resize(227, 164)
        self.centralwidget = QtWidgets.QWidget(dlg_win)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_dlg_minus = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_dlg_minus.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/arrow-270.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_dlg_minus.setIcon(icon)
        self.pushButton_dlg_minus.setObjectName("pushButton_dlg_minus")
        self.horizontalLayout.addWidget(self.pushButton_dlg_minus)
        self.doubleSpinBox_step = QtWidgets.QDoubleSpinBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.doubleSpinBox_step.setFont(font)
        self.doubleSpinBox_step.setAlignment(QtCore.Qt.AlignCenter)
        self.doubleSpinBox_step.setObjectName("doubleSpinBox_step")
        self.horizontalLayout.addWidget(self.doubleSpinBox_step)
        self.pushButton_dlg_plus = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_dlg_plus.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons/arrow-090.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_dlg_plus.setIcon(icon1)
        self.pushButton_dlg_plus.setObjectName("pushButton_dlg_plus")
        self.horizontalLayout.addWidget(self.pushButton_dlg_plus)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        dlg_win.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(dlg_win)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 227, 20))
        self.menubar.setObjectName("menubar")
        dlg_win.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(dlg_win)
        self.statusbar.setObjectName("statusbar")
        dlg_win.setStatusBar(self.statusbar)

        self.retranslateUi(dlg_win)
        QtCore.QMetaObject.connectSlotsByName(dlg_win)

    def retranslateUi(self, dlg_win):
        _translate = QtCore.QCoreApplication.translate
        dlg_win.setWindowTitle(_translate("dlg_win", "Tweaking"))
    


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dlg_win = QtWidgets.QMainWindow()
    ui = Ui_dlg_win()
    ui.setupUi(dlg_win)
    dlg_win.show()
    sys.exit(app.exec_())

