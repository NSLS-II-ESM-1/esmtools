__author__ = 'Elio Vescovo'
__version__ = '0.0.1'

# import python standard modules

# import 3rd party libraries
from PyQt5.QtGui import *

# import local python

class Ui_Toolbar(QToolBar):
    def __init__(self, parent=None):
        super(Ui_Toolbar, self).__init__(parent)

        self.bw_button_action = QAction('BaseWnd', self)


    def setupUi(self, Ui_Toolbar):
        self.ui_toolbar = QToolBar()
        self.ui_toolbar.addAction(self.bw_button_action)


