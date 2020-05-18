__author__ = 'Elio Vescovo'
__version__ = '0.0.1'

# import python standard modules

# import 3rd party libraries
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import pyqtgraph as pg

# import local python

from ui.ui_menubar import Ui_Menubar
from ui.ui_toolbar import Ui_Toolbar

class Ui_MDIWindow(QObject):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        self.ui_central_widget = QWidget(MainWindow)
        self.mdi = QMdiArea()
        MainWindow.setCentralWidget(self.mdi)

        self.base_wd = QMdiSubWindow()
        self.base_wd.setAttribute(Qt.WA_DeleteOnClose, False)
        self.base_wd.resize(600, 600)
        self.base_wd.plt_i = pg.PlotItem(labels={'left': ('slits', 'degrees'), 'bottom': ('Kin. Energy', 'eV')})
        self.base_wd.plt_iv = pg.ImageView(view=self.base_wd.plt_i)
        self.base_wd.setWidget(self.base_wd.plt_iv)
        self.base_wd.setWindowTitle("plot window")
        self.mdi.addSubWindow(self.base_wd)
        self.base_wd.show()

# MENUBAR
        self.ui_menubar = Ui_Menubar()
        self.ui_menubar.setupUi(self)

# TOOLBAR
        self.ui_toolbar = Ui_Toolbar()
        self.ui_toolbar.setupUi(self)
