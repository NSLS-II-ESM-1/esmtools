import sys
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import random

class TestClass(QtGui.QMainWindow):
    #####################################################
    def __init__(self):
        super(TestClass, self).__init__()
        self.initUI()
    ####################################################
    # GUI construction
    def initUI(self):
        self.setWindowTitle("Mouse Point, x & y")
        win = QtGui.QWidget()
        # creates plot
        self.plot = pg.PlotWidget()
        self.plot.setLabel('left', "B", units='T')
        self.plot.setLabel('bottom', "t", units='s')
        self.plot.showGrid(x=1, y=1, alpha=None)
        self.setCentralWidget(win)
        self.setGeometry(600, 600, 600, 600)
        self.setWindowTitle('Mouse Point, x& y GUI')

        # Create some widgets to be placed inside
        btnRandon = QtGui.QPushButton('Random Function')
        # Create a grid layout to manage the widgets size and position
        layout = QtGui.QGridLayout(win)

        # Add widgets to the layout in their proper positions
        layout.addWidget(btnRandon, 0, 0) # button to show or hide the OldB
        layout.addWidget(self.plot, 1, 0)

        mypen = pg.mkPen('y', width=1)
        self.curve = self.plot.plot(x=[], y=[], pen=mypen)

        # Plot
        self.t_plot_max = 30
        self.fe = 10e3
        self.t = np.arange(-1 * self.t_plot_max, 0, 1.0 / self.fe)
        self.len_signal = len(self.t)
        self.signal = np.zeros(self.len_signal, dtype=np.double)

        btnRandon.clicked.connect(self.buttonRandomClicked)
        self.curve.scene().sigMouseMoved.connect(self.onMouseMoved)

    def onMouseMoved(self, point):
        p = self.plot.plotItem.vb.mapSceneToView(point)
        self.statusBar().showMessage("{}-{}".format(p.x(), p.y()))

    def buttonRandomClicked(self):
        print ("Show/Hide OldB")
        self.signal = np.random.rand(20)
        self.curve.setData(self.signal)


# MAIN ##################################################
def main():
    app = QtGui.QApplication(sys.argv)
    ex = TestClass()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()