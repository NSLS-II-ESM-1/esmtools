"""
Demonstrates some customized mouse interaction by drawing a crosshair that follows
the mouse.


"""

#import initExample ## Add path to library (just for examples; you do not need this)
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Point import Point

#generate layout
app = QtGui.QApplication([])
win = pg.GraphicsWindow()
win.setWindowTitle('pyqtgraph example: crosshair')
label = pg.LabelItem(justify='right')
win.addItem(label)
p1 = win.addPlot(row=1, col=0)
p2 = win.addPlot(row=2, col=0)

region = pg.LinearRegionItem()
region.setZValue(10)
# Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this
# item when doing auto-range calculations.
p2.addItem(region, ignoreBounds=True)

#pg.dbg()
p1.setAutoVisible(y=True)


#create numpy arrays
#make the numbers large to show that the xrange shows data from 10000 to all the way 0
data1 = 10000 + 15000 * pg.gaussianFilter(np.random.random(size=10000), 10) + 3000 * np.random.random(size=10000)
data2 = 15000 + 15000 * pg.gaussianFilter(np.random.random(size=10000), 10) + 3000 * np.random.random(size=10000)

p1.plot(data1, pen="r")
p1.plot(data2, pen="g")

p2.plot(data1, pen="w")

def update():
    region.setZValue(10)
    minX, maxX = region.getRegion()
    p1.setXRange(minX, maxX, padding=0)

region.sigRegionChanged.connect(update)

def updateRegion(window, viewRange):
    rgn = viewRange[0]
    region.setRegion(rgn)

p1.sigRangeChanged.connect(updateRegion)

region.setRegion([1000, 2000])

#cross hair
vLine = pg.InfiniteLine(angle=90, movable=False)
hLine = pg.InfiniteLine(angle=0, movable=False)
p1.addItem(vLine, ignoreBounds=True)
p1.addItem(hLine, ignoreBounds=True)


vb = p1.vb

def mouseMoved(evt):
    pos = evt[0]  ## using signal proxy turns original arguments into a tuple
    if p1.sceneBoundingRect().contains(pos):
        mousePoint = vb.mapSceneToView(pos)
        index = int(mousePoint.x())
        if index > 0 and index < len(data1):
            label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), data1[index], data2[index]))
        vLine.setPos(mousePoint.x())
        hLine.setPos(mousePoint.y())



proxy = pg.SignalProxy(p1.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)
#p1.scene().sigMouseMoved.connect(mouseMoved)


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()






"""
Demonstrate the use of layouts to control placement of multiple plots / views /
labels


"""

## Add path to library (just for examples; you do not need this)
import initExample

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np

app = QtGui.QApplication([])
view = pg.GraphicsView()
l = pg.GraphicsLayout(border=(100,100,100))
view.setCentralItem(l)
view.show()
view.setWindowTitle('pyqtgraph example: GraphicsLayout')
view.resize(800,600)

## Title at top
text = """
This example demonstrates the use of GraphicsLayout to arrange items in a grid.<br>
The items added to the layout must be subclasses of QGraphicsWidget (this includes <br>
PlotItem, ViewBox, LabelItem, and GrphicsLayout itself).
"""
l.addLabel(text, col=1, colspan=4)
l.nextRow()

## Put vertical label on left side
l.addLabel('Long Vertical Label', angle=-90, rowspan=3)

## Add 3 plots into the first row (automatic position)
p1 = l.addPlot(title="Plot 1")
p2 = l.addPlot(title="Plot 2")
vb = l.addViewBox(lockAspect=True)
img = pg.ImageItem(np.random.normal(size=(100,100)))
vb.addItem(img)
vb.autoRange()


## Add a sub-layout into the second row (automatic position)
## The added item should avoid the first column, which is already filled
l.nextRow()
l2 = l.addLayout(colspan=3, border=(50,0,0))
l2.setContentsMargins(10, 10, 10, 10)
l2.addLabel("Sub-layout: this layout demonstrates the use of shared axes and axis labels", colspan=3)
l2.nextRow()
l2.addLabel('Vertical Axis Label', angle=-90, rowspan=2)
p21 = l2.addPlot()
p22 = l2.addPlot()
l2.nextRow()
p23 = l2.addPlot()
p24 = l2.addPlot()
l2.nextRow()
l2.addLabel("HorizontalAxisLabel", col=1, colspan=2)

## hide axes on some plots
p21.hideAxis('bottom')
p22.hideAxis('bottom')
p22.hideAxis('left')
p24.hideAxis('left')
p21.hideButtons()
p22.hideButtons()
p23.hideButtons()
p24.hideButtons()


## Add 2 more plots into the third row (manual position)
p4 = l.addPlot(row=3, col=1)
p5 = l.addPlot(row=3, col=2, colspan=2)

## show some content in the plots
p1.plot([1,3,2,4,3,5])
p2.plot([1,3,2,4,3,5])
p4.plot([1,3,2,4,3,5])
p5.plot([1,3,2,4,3,5])



## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

***********************************************************************************
# -*- coding: utf-8 -*-
"""
This example demonstrates the use of ImageView, which is a high-level widget for 
displaying and analyzing 2D and 3D data. ImageView provides:

  1. A zoomable region (ViewBox) for displaying the image
  2. A combination histogram and gradient editor (HistogramLUTItem) for
     controlling the visual appearance of the image
  3. A timeline for selecting the currently displayed frame (for 3D data only).
  4. Tools for very basic analysis of image data (see ROI and Norm buttons)

"""
## Add path to library (just for examples; you do not need this)
import initExample

import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg

# Interpret image data as row-major instead of col-major
pg.setConfigOptions(imageAxisOrder='row-major')

app = QtGui.QApplication([])

## Create window with ImageView widget
win = QtGui.QMainWindow()
win.resize(800,800)
imv = pg.ImageView()
win.setCentralWidget(imv)
win.show()
win.setWindowTitle('pyqtgraph example: ImageView')

## Create random 3D data set with noisy signals
img = pg.gaussianFilter(np.random.normal(size=(200, 200)), (5, 5)) * 20 + 100
img = img[np.newaxis,:,:]
decay = np.exp(-np.linspace(0,0.3,100))[:,np.newaxis,np.newaxis]
data = np.random.normal(size=(100, 200, 200))
data += img * decay
data += 2

## Add time-varying signal
sig = np.zeros(data.shape[0])
sig[30:] += np.exp(-np.linspace(1,10, 70))
sig[40:] += np.exp(-np.linspace(1,10, 60))
sig[70:] += np.exp(-np.linspace(1,10, 30))

sig = sig[:,np.newaxis,np.newaxis] * 3
data[:,50:60,30:40] += sig


## Display the data and assign each frame a time value from 1.0 to 3.0
imv.setImage(data, xvals=np.linspace(1., 3., data.shape[0]))

## Set a custom color map
colors = [
    (0, 0, 0),
    (45, 5, 61),
    (84, 42, 55),
    (150, 87, 60),
    (208, 171, 141),
    (255, 255, 255)
]
cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 6), color=colors)
imv.setColorMap(cmap)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

# -*- coding: utf-8 -*-
"""
Demonstrate a simple data-slicing task: given 3D data (displayed at top), select 
a 2D plane and interpolate data along that plane to generate a slice image 
(displayed at bottom). 


"""

## Add path to library (just for examples; you do not need this)
import initExample

import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg

app = QtGui.QApplication([])

## Create window with two ImageView widgets
win = QtGui.QMainWindow()
win.resize(800, 800)
win.setWindowTitle('pyqtgraph example: DataSlicing')
cw = QtGui.QWidget()
win.setCentralWidget(cw)
l = QtGui.QGridLayout()
cw.setLayout(l)
imv1 = pg.ImageView()
imv2 = pg.ImageView()
l.addWidget(imv1, 0, 0)
l.addWidget(imv2, 1, 0)
win.show()

roi = pg.LineSegmentROI([[10, 64], [120, 64]], pen='r')
imv1.addItem(roi)

x1 = np.linspace(-30, 10, 128)[:, np.newaxis, np.newaxis]
x2 = np.linspace(-20, 20, 128)[:, np.newaxis, np.newaxis]
y = np.linspace(-30, 10, 128)[np.newaxis, :, np.newaxis]
z = np.linspace(-20, 20, 128)[np.newaxis, np.newaxis, :]
d1 = np.sqrt(x1 ** 2 + y ** 2 + z ** 2)
d2 = 2 * np.sqrt(x1[::-1] ** 2 + y ** 2 + z ** 2)
d3 = 4 * np.sqrt(x2 ** 2 + y[:, ::-1] ** 2 + z ** 2)
data = (np.sin(d1) / d1 ** 2) + (np.sin(d2) / d2 ** 2) + (np.sin(d3) / d3 ** 2)


def update():
    global data, imv1, imv2
    d2 = roi.getArrayRegion(data, imv1.imageItem, axes=(1, 2))
    imv2.setImage(d2)


roi.sigRegionChanged.connect(update)

## Display the data
imv1.setImage(data)
imv1.setHistogramRange(-0.01, 0.01)
imv1.setLevels(-0.003, 0.003)

update()

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()



# -*- coding: utf-8 -*-
"""
This example demonstrates the ability to link the axes of views together
Views can be linked manually using the context menu, but only if they are given 
names.
"""

import initExample ## Add path to library (just for examples; you do not need this)


from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg

#QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

x = np.linspace(-50, 50, 1000)
y = np.sin(x) / x

win = pg.GraphicsWindow(title="pyqtgraph example: Linked Views")
win.resize(800,600)

win.addLabel("Linked Views", colspan=2)
win.nextRow()

p1 = win.addPlot(x=x, y=y, name="Plot1", title="Plot1")
p2 = win.addPlot(x=x, y=y, name="Plot2", title="Plot2: Y linked with Plot1")
p2.setLabel('bottom', "Label to test offset")
p2.setYLink('Plot1')  ## test linking by name


## create plots 3 and 4 out of order
p4 = win.addPlot(x=x, y=y, name="Plot4", title="Plot4: X -> Plot3 (deferred), Y -> Plot1", row=2, col=1)
p4.setXLink('Plot3')  ## Plot3 has not been created yet, but this should still work anyway.
p4.setYLink(p1)
p3 = win.addPlot(x=x, y=y, name="Plot3", title="Plot3: X linked with Plot1", row=2, col=0)
p3.setXLink(p1)
p3.setLabel('left', "Label to test offset")
#QtGui.QApplication.processEvents()


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


