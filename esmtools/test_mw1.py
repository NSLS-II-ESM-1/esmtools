import os
import glob
import platform
import sys
#from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiArea, QAction, QMdiSubWindow, QTextEdit

import numpy as np
import pyqtgraph as pg
from igor.binarywave import load as loadibw

import .\arpes\arpes_dlg as dlg



class MDIWindow(QMainWindow):
    count = 0

    def __init__(self):
        super().__init__()

        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)
        bar = self.menuBar()

        self.current_dir = None

        file = bar.addMenu("File")
        file.addAction("New")
        file.addAction("cascade")
        file.addAction("Tiled")
        file.triggered[QAction].connect(self.WindowTrig)
        self.setWindowTitle("MDI Application")

        load = bar.addMenu("Load")
        load.addAction("2D")
        load.addAction("3D")
        load.triggered[QAction].connect(self.self.dir_open)



    def WindowTrig(self, p):

        if p.text() == "New":
            MDIWindow.count = MDIWindow.count + 1
            sub = QMdiSubWindow()
            sub.setWidget(QTextEdit())
            sub.setWindowTitle("Sub Window" + str(MDIWindow.count))
            self.mdi.addSubWindow(sub)
            sub.show()

        if p.text() == "cascade":
            self.mdi.cascadeSubWindows()

        if p.text() == "Tiled":
            self.mdi.tileSubWindows()


    def dir_open(self, p):

        if p.text() == "1D":
            self.current_dir = dlg.File_dlg.openDirNameDialog(self)
            files_ls = glob.glob(self.current_dir + '/*.ibw')
            fls = [f[len(self.current_dir) + 1:] for f in files_ls]
            print(fls)
#            self.twoD_list.addItems(fls)
#            self.threeD_list.addItems(zip)
        if p.text() == "2D":
            self.current_dir = dlg.File_dlg.openDirNameDialog(self)
            zip_ls = glob.glob(self.current_dir + '/*.zip')
            zp = [f[len(self.current_dir) + 1:] for f in zip_ls]
            print(zp)
#            self.twoD_list.addItems(fls)
#            self.threeD_list.addItems(zip)




app = QApplication(sys.argv)
mdi = MDIWindow()
mdi.show()
app.exec_()

