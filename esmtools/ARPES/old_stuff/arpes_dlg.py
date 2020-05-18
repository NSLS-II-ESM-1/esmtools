import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PyQt5 import QtWidgets,  QtCore,  QtGui ,  uic,  Qt
from PyQt5.QtWidgets import QWidget,  QFileDialog
from PyQt5.QtWidgets import QApplication,  QTableWidgetItem,  QMainWindow,  QToolBar,  QAction,  QLabel,  QCheckBox,  QStatusBar
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
import pkg_resources
import sys,  os,  glob





class File_dlg(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 file dialogs - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.openFileNameDialog()
        self.openFileNamesDialog()
        self.saveFileDialog()

        self.show()

    def openDirNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        dirName = QFileDialog.getExistingDirectory(self, "Open Directory", "/nsls2/xf21id1/csv_files/XPS/2019_02_21/Cr0.22BiSe",
                                                   options=options)
#        print(dirName)
        return (dirName)

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "/nsls2/xf21id1/csv_files/XPS",
                                                  "All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName)
            return (fileName)

    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                                "All Files (*);;Python Files (*.py)", options=options)
        if files:
            print(files)

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)
