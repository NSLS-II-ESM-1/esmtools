__author__ = 'Elio Vescovo'
__version__ = '0.0.1'

# import python standard modules

# import 3rd party libraries
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# import local python scripts

class Ui_DockWidget(QObject):

    def setupUi(self, DataList):

        DataList.setObjectName('data area')

        self.ui_datalist_DockWidget =QDockWidget('Data Area', DataList)
        self.ui_datalist_DockWidget.setAllowedAreas(Qt.RightDockWidgetArea)

        self.data_list = QListWidget()
        self.data3D_list = QListWidget()

        self.vlay = QVBoxLayout()
        self.vlay.addWidget(self.data_list)
        self.vlay.addWidget(self.data3D_list)
        self.datawdg= QWidget()
        self.datawdg.setLayout(self.vlay)
        self.ui_datalist_DockWidget.setWidget(self.datawdg)



