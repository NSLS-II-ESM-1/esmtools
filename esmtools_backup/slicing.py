"""
Demonstrate a simple data-slicing task: given 3D data (displayed at top), select 
a 2D plane and interpolate data along that plane to generate a slice image 
(displayed at bottom). 

"""



## Add path to library (just for examples; you do not need this)

#import initExample



#import matplotlib

import numpy as np
import os
import sys
#import glob

#from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
#import  QtGui,   QtCore
import pyqtgraph as pg

#from matplotlib import cm
from zipfile import ZipFile



def loader(fl_nm, base_path):
    path_to_file = os.path.join(base_path, fl_nm)
                                #### check if it is a file folder to unzip
    if os.path.isfile(path_to_file+'.zip') and not os.path.isdir(path_to_file): # the folder has still not been unzipped
        with ZipFile(path_to_file+'.zip',  'r') as zipObj:
            zipObj.extractall(path_to_file)


                #### READ VIEWER.INI FILE to find the regions
# the file has been already unzipped; form the list of spectra
    specta_nm_ls = [f for f in os.listdir(path_to_file) if (('Spectrum_' in f)and('.ini' in f))]
    specta_nm_ls = [os.path.splitext(each)[0] for each in specta_nm_ls]
    rg_nm_ls = [w[9:] for w in specta_nm_ls]

    info_ls = []
    for rn in rg_nm_ls: 
        path_to_file = os.path.join(base_path, fl_nm,rn+'.ini')
#        path_to_file = os.path.join(base_path, fl_nm,rn)
        fd = open(path_to_file , 'r')
        lst = fd.readlines()     #python list: every element is a line
        info_ls.append(lst[3]+lst[4]+lst[5]+lst[6]+lst[21]+lst[27]+lst[28]+lst[29]+lst[30]+lst[34])
#    print(specta_nm_ls)
 #   print( info_ls)
    return specta_nm_ls, info_ls
    



def read_bin_multi_region(base_path, fl_nm,  rg = 0):
    path_to_file = os.path.join(base_path, fl_nm)
    rgs_ls, rgs_info_ls = loader(fl_nm, base_path) # unzip and create .dat files and return the list of regions
    #### READ INI FILE for the region (default is rg = 0)
    path_to_file = os.path.join(base_path, fl_nm,rgs_ls[rg]+'.ini')
    fd = open(path_to_file , 'r')
    lst = fd.readlines()     #python list: every element is a line
    w = int(lst[1].split('=')[1][:-1])
    h = int(lst[2].split('=')[1][:-1])
    d = int(lst[3].split('=')[1][:-1])
    w_of = float(lst[7].split('=')[1][:-1])
    w_dt = float(lst[8].split('=')[1][:-1])
    h_of = float(lst[9].split('=')[1][:-1])
    h_dt = float(lst[10].split('=')[1][:-1])
    d_of = float(lst[11].split('=')[1][:-1])
    d_dt = float(lst[12].split('=')[1][:-1])
    w_lb = str(lst[13].split('=')[1][:-1])
    h_lb = str(lst[14].split('=')[1][:-1])
    d_lb = str(lst[15].split('=')[1][:-1])
    nm = str(lst[16].split('=')[1][:-1])
    

    #### READ-IN from .bin the data and form a 3D-matrix to return

    path_to_file = os.path.join(base_path, fl_nm,rgs_ls[rg]+'.bin')
    fh = open(path_to_file , 'rb')
    data = np.fromfile(fh, np.float32)
    data.shape = (d,  h,  w)
    return w, w_of, w_dt, h, h_of, h_dt, d, d_of, d_dt, data, rgs_ls










class MainWindow(QMainWindow):
    def __init__(self, *args,  **kwargs):
        super(MainWindow, self).__init__(*args,  **kwargs)

        self.E0, self.E1 = 0.0,  1.0
        self.A0, self.A1 = -1.0,  1.0
        self.AS0,self.AS1 = -1.0,  1.0
        self.data = np.array([0, 0, 0])
        self.rgs_ls = []
        self.a_max = 1.0
        self.setWindowTitle('DA30 - viewer')
        self.resize(900,900)

        plt00 = pg.PlotItem(labels={'bottom': ('slits', 'degrees'), 'left': ('Kin. Energy', 'eV')})
        plt00.setAspectLocked(False)
        plt00.invertY(False)
        plt00.invertX(False)

        plt10 = pg.PlotItem(labels={'bottom': ('slits', 'degrees'), 'left': ('deflector', 'degrees')})
        plt10.setAspectLocked(True)
        plt10.invertY(False)
        plt10.invertX(False)


        plt11 = pg.PlotItem(labels={'bottom': ('Kin. Energy', 'eV'), 'left': ('deflector', 'degrees')})
        plt11.setAspectLocked(False)
        plt11.invertY(False)
        plt11.invertX(False)

        plt00.setRange(xRange=[self.E0,self.E1], yRange=[-self.a_max,self.a_max])
        plt10.setRange(xRange=[-self.a_max,self.a_max], yRange=[-self.a_max,self.a_max], padding = 0)
        plt11.setRange(xRange=[self.E0,self.E1], yRange=[-self.a_max,self.a_max])


        imv00 = pg.ImageView(view=plt00)
        imv10 = pg.ImageView(view=plt10)
        imv11 = pg.ImageView(view=plt11)

        grid = QGridLayout()

        grid.addWidget(imv00, 0, 0)
        grid.addWidget(imv10, 1, 0)
        grid.addWidget(imv11, 1, 1)



        cw = QWidget()
        cw.setLayout(grid)
        self.setCentralWidget(cw)

        toolbar = QToolBar("ToolBar")
        self.addToolBar(toolbar)
        
        load_action_button = QAction("Load",  self)
        load_action_button.triggered.connect(self.file_open)
        toolbar.addAction(load_action_button)
        
  
    def file_open(self):
#        self.fl_name = File_dlg.openDirNameDialog(self)
 #       self.lineEdit_dir.setText(os.path.dirname(self.fl_name))
   #     self.lineEdit_file.setText(os.path.basename(self.fl_name))
        print('in')
        w, w_of, w_dt, h, h_of, h_dt, d, d_of, d_dt, data, rgs_ls = \
                                read_bin_multi_region("/nsls2/xf21id1/csv_files/XPS/elio", "IT3_0043")

        en =w_of+w_dt*np.arange(0,w)
        ang =h_of+h_dt*np.arange(0,h)
        ang_s=d_of+d_dt*np.arange(0,d)

        self.E0, self.E1 = (en[0], en[-1])
        self.A0, self.A1 = (ang[0], ang[-1])
        self.AS0,self.AS1 = (ang_s[0],ang_s[-1])

#        self.asscale, self.ascale, self.escale = (self.AS1-AS0) / data.shape[0], (A1-A0) / data.shape[1], (E1-E0) / data.shape[2] 
#        a_max = np.max(np.abs(np.array([A0,A1,AS0,AS1]))) 

        self.data = np.transpose(data,axes=(2,1,0))
        print(self.A0)

        imv10.setImage(data, xvals=np.linspace(en[0], en[-1], data.shape[0]), pos=[A0, AS0], scale=[ascale, asscale])
        imv10.setCurrentIndex(data.shape[0]//2)
        imv10.ui.histogram.hide()

        imv10.ui.roiBtn.hide()
        imv10.ui.menuBtn.hide()
    








'''
app = QtGui.QApplication([])



## Create window with two ImageView widgets



win.show()

roi2 = pg.LineSegmentROI([[A0, (AS0+AS1)/2], [A1,(AS0+AS1)/2]], pen='r')
imv1.addItem(roi2)
roi3 = pg.LineSegmentROI([[(A0+A1)/2, AS0], [(A0+A1)/2,AS1]], pen='b')
imv1.addItem(roi3)


def update2():
    global data, imv1, imv2, E0,A0,escale,ascale
    d2 = roi2.getArrayRegion(data, imv1.imageItem, axes=(1,2))
    imv2.setImage(np.transpose(d2),pos=[A0, E0], scale=[ascale, escale])
    imv2.ui.histogram.hide()
    imv2.ui.roiBtn.hide()
    imv2.ui.menuBtn.hide()
roi2.sigRegionChanged.connect(update2)



def update3():
    global data, imv1, imv3, E0,AS0,escale,asscale
    d3 = roi3.getArrayRegion(data, imv1.imageItem, axes=(1,2))
    imv3.setImage(d3,pos=[E0, AS0], scale=[escale, asscale])
    imv3.ui.histogram.hide()
    imv3.ui.roiBtn.hide()
    imv3.ui.menuBtn.hide()
roi3.sigRegionChanged.connect(update3)



## Display the data

imv1.setImage(data, xvals=np.linspace(en[0], en[-1], data.shape[0]), pos=[A0, AS0], scale=[ascale, asscale])
imv1.setCurrentIndex(data.shape[0]//2)
imv1.ui.histogram.hide()

imv1.ui.roiBtn.hide()
imv1.ui.menuBtn.hide()

#imv1.setImage(data)

#imv1.setHistogramRange(-0.01, 0.01)

#imv1.setLevels(-0.003, 0.003)



update2()

update3()



## Start Qt event loop unless running in interactive mode.

if __name__ == '__main__':

    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):

        QtGui.QApplication.instance().exec_()



'''

app = QApplication(sys.argv)
win = MainWindow()
win.show()
app.exec_()
