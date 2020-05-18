__author__ = 'Elio Vescovo'
__version__ = '0.0.1'

# import python standard modules

# import 3rd party libraries
from PyQt5.QtGui import *

# import local python

class Ui_Menubar(QMenuBar):
    def __init__(self, parent=None):
        super(Ui_Menubar, self).__init__(parent)

        self.new_action = QAction(QIcon('exit.png'), '&New', self)
        self.cascade_action = QAction(QIcon('exit.png'), '&Cascade', self)
        self.tiled_action = QAction(QIcon('exit.png'), '&Tiled', self)
        self.exit_action = QAction(QIcon('exit.png'), '&Exit', self)

        self.twoD_action = QAction(QIcon('exit.png'), '2D', self)
        self.threeD_action = QAction(QIcon('exit.png'), '3D', self)

#        self.exit_action.triggered.connect(self.close)

    def setupUi(self, Ui_Menubar):
        self.ui_menubar = QMenuBar()
        #
        # file menu actions:
        # add file menu and file menu actions
        self.file_menu = self.ui_menubar.addMenu('&File')
        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.cascade_action)
        self.file_menu.addAction(self.tiled_action)
        self.file_menu.addAction(self.exit_action)

 #       self.file_menu.triggered[QAction].connect(self.WindowTrig)

        self.load_menu = self.ui_menubar.addMenu("&Load")
        self.load_menu.addAction(self.twoD_action)
        self.load_menu.addAction(self.threeD_action)

  #      self.load_menu.triggered[QAction].connect(self.dir_open)
