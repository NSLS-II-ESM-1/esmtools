#!/usr/bin/env python3

__author__ = 'Elio Vescovo'
__version__ = '0.0.1'

# import python standard modules
import sys
import os
import glob
import platform

# import 3rd party libraries
#from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiArea, QAction, QMdiSubWindow, QTextEdit, QDockWidget, \
    QListWidget, QWidget, QGridLayout, QListWidgetItem, QToolBar

import numpy as np
import pyqtgraph as pg
from igor.binarywave import load as loadibw

# import local python
from main_window import MDIWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('ARPES Viewer')
    mdi = MDIWindow()
    mdi.resize(1500, 900)
    mdi.show()
    app.exec_()

if __name__ == '__main__':
    main()

