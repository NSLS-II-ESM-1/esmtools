# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'axes_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(40, 250, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(93, 82, 262, 130))
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_dlg_actual = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_dlg_actual.setFont(font)
        self.label_dlg_actual.setObjectName("label_dlg_actual")
        self.gridLayout.addWidget(self.label_dlg_actual, 0, 0, 1, 1)
        self.lineEdit_dlg_actual = QtWidgets.QLineEdit(self.widget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lineEdit_dlg_actual.setFont(font)
        self.lineEdit_dlg_actual.setObjectName("lineEdit_dlg_actual")
        self.gridLayout.addWidget(self.lineEdit_dlg_actual, 0, 1, 1, 1)
        self.label_dlg_mtr = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_dlg_mtr.setFont(font)
        self.label_dlg_mtr.setObjectName("label_dlg_mtr")
        self.gridLayout.addWidget(self.label_dlg_mtr, 1, 0, 1, 1)
        self.doubleSpinBox_dlg_mtr = QtWidgets.QDoubleSpinBox(self.widget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.doubleSpinBox_dlg_mtr.setFont(font)
        self.doubleSpinBox_dlg_mtr.setFrame(True)
        self.doubleSpinBox_dlg_mtr.setAlignment(QtCore.Qt.AlignCenter)
        self.doubleSpinBox_dlg_mtr.setButtonSymbols(QtWidgets.QAbstractSpinBox.PlusMinus)
        self.doubleSpinBox_dlg_mtr.setDecimals(4)
        self.doubleSpinBox_dlg_mtr.setObjectName("doubleSpinBox_dlg_mtr")
        self.gridLayout.addWidget(self.doubleSpinBox_dlg_mtr, 1, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setText("")
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.doubleSpinBox_dlg_range = QtWidgets.QDoubleSpinBox(self.widget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.doubleSpinBox_dlg_range.setFont(font)
        self.doubleSpinBox_dlg_range.setAlignment(QtCore.Qt.AlignCenter)
        self.doubleSpinBox_dlg_range.setButtonSymbols(QtWidgets.QAbstractSpinBox.PlusMinus)
        self.doubleSpinBox_dlg_range.setDecimals(4)
        self.doubleSpinBox_dlg_range.setObjectName("doubleSpinBox_dlg_range")
        self.gridLayout.addWidget(self.doubleSpinBox_dlg_range, 3, 1, 1, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_dlg_actual.setText(_translate("Dialog", "Actual"))
        self.label_dlg_mtr.setText(_translate("Dialog", "Axes"))
        self.label_3.setText(_translate("Dialog", "Range"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

