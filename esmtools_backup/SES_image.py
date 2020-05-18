# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 19:17:14 2018

@author: vescovo
"""

# -*- coding: utf-8 -*-
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
import glob
from PyQt5 import  QtGui,   QtCore
#from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
from matplotlib import cm
import sys

    
def loader(fl_nm, base_path):
    path_to_file = os.path.join(base_path, fl_nm)
                                #### check if it is a file folder to unzip
    if os.path.isfile(path_to_file+'.zip') and not os.path.isdir(path_to_file): # the folder has still not been unzipped
   #     ! unzip -d {path_to_file} {path_to_file+'.zip'};
                #### READ VIEWER.INI FILE to find the regions
        path_to_file = os.path.join(base_path, fl_nm,'viewer.ini')
        fd = open(path_to_file , 'r')
        lst = fd.readlines()     #python list: every element is a line
        for ln in lst:           # find the regions list
            if ln.split('=')[0] == 'region_list': rg_ls = ln.split('=')[1][:-1].split(';')

        specta_nm_ls, rg_nm_ls = [], []

        for rg in rg_ls: # for each region
            k = lst.index('[viewer.'+rg+']\n')             # find region name
            rg_nm_ls.append(str(lst[k+1].split('=')[1][:-1])) 
            i = lst.index('[viewer.'+rg+'.channel_0]\n')   # find the index where the info for the region start
            w = int(lst[i+1].split('=')[1][:-1])
            rg_nm = str(lst[i+4].split('=')[1][:-1])
            specta_nm_ls.append('Spectrum_'+rg_nm)
            pth = str(lst[i+5].split('=')[1][:-1])


                    #### TRANSFORM BINARY INTO TEXT FILE        
            n_lines = "'" + str(w) + '/4 "%f "' + "'"
            file_in = base_path+'/'+fl_nm+'/'+pth
            file_out = base_path+'/'+fl_nm+'/'+'Spectrum_'+rg_nm+'.dat'
#            print('rg_nm={}, pth={}'.format(rg_nm, pth))
#            print('file_in={}'.format(file_in))
            file_in = file_in.replace(' ', '\ ')
            file_out = file_out.replace(' ', '\ ')
#            print('file_in={}'.format(file_out))
    #        ! hexdump -v -e {n_lines} -e '"\n"' {file_in} > {file_out}; 
        rg_nm_ls = [os.path.splitext(each)[0] for each in rg_nm_ls]
    else:  # the file has been already unzipped; form the list of spectra
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
    return specta_nm_ls, info_ls
    


def read_bin_multi_region(base_path, fl_nm,  rg = 0):
#    import os

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
    

    #### READ-IN from junk1.dat the data and for a 3D-matrix to return

#    path_to_file = os.path.join(base_path, fl_nm,rgs_ls[rg]+'.dat')
#    fd = open(path_to_file , 'r')
#    data = fd.readlines()                                 #python list: every element is a line
#    I = np.empty([d, h, w])
 #   for j in range(d):
  #      for k in range(h):
     #       I[j,k,:]=data[j*h+k].split()

    path_to_file = os.path.join(base_path, fl_nm,rgs_ls[rg]+'.bin')
    fh = open(path_to_file , 'rb')
    data = np.fromfile(fh, np.float32)
    data.shape = (d,  h,  w)


    return w, w_of, w_dt, h, h_of, h_dt, d, d_of, d_dt, data, rgs_ls
#    return w, w_of, w_dt, h, h_of, h_dt, d, d_of, d_dt, I
    

w, w_of, w_dt, h, h_of, h_dt, d, d_of, d_dt, data, rgs_ls = \
                        read_bin_multi_region("/nsls2/xf21id1/csv_files/XPS/elio", "IT3_0043")
                        

print(np.shape(data))                        
                        
en =w_of+w_dt*np.arange(0,w)
ang =h_of+h_dt*np.arange(0,h)
ang_s=d_of+d_dt*np.arange(0,d)


E0, E1 = en[0], en[-1]
A0, A1 = ang[0], ang[-1]
AS0,AS1 = ang_s[0],ang_s[-1]
asscale, ascale, escale = (AS1-AS0) / data.shape[0], (A1-A0) / data.shape[1], (E1-E0) / data.shape[2] 

print(E0,E1,A0,A1,AS0,AS1)
print(asscale,  ascale,  escale)
data = np.transpose(data,axes=(2,1,0))
print(np.shape(data))                        
a_max = np.max(np.abs(np.array([A0,A1,AS0,AS1]))) 
print(a_max)
print(data[500, 200, 10],  data[600, 200, 20], data[500, 300, 30])


#data_en = np.transpose(data, axes=(2,1,0))
#print(np.shape(data))                        

#data_s = np.transpose(data, axis=(1,3,0))

#data_d = np.transpose(data, axis=(0,3,1))


app = QtGui.QApplication([])

## Create window with two ImageView widgets
win = QtGui.QMainWindow()
win.resize(950,950)
win.setWindowTitle('pyqtgraph example: DataSlicing')
cw = QtGui.QWidget()
win.setCentralWidget(cw)
l = QtGui.QGridLayout()
cw.setLayout(l)

plt1 = pg.PlotItem(labels={'bottom': ('slits', 'degrees'), 'left': ('deflector', 'degrees')})
imv1 = pg.ImageView(view=plt1)
plt1.setAspectLocked(False)
#plt1.invertY(False)
#plt1.invertX(False)
#plt1.setRange(xRange=[AS0,AS1], yRange=[A0,A1], padding = 0)
plt1.setRange(xRange=[-a_max,a_max], yRange=[-a_max,a_max], padding = 0)


#imv1 = pg.ImageView()
plt2 = pg.PlotItem(labels={'bottom': ('slits', 'degrees'), 'left': ('Kin. Energy', 'eV')})
imv2 = pg.ImageView(view=plt2)
#imv2.setImage(np.transpose(data[:,:,0]))
plt2.setAspectLocked(False)
plt2.invertY(False)
#plt2.invertX(False)
#plt2.setRange(xRange=[E0,E1], yRange=[A0,A1],padding = 0)
plt2.setRange(xRange=[-a_max,a_max],  yRange=[E0,E1])


plt3 = pg.PlotItem(labels={'bottom': ('Kin. Energy', 'eV'), 'left': ('deflector', 'degrees')})
imv3 = pg.ImageView(view=plt3)
#imv2.setImage(np.transpose(data[:,:,0]))
plt3.setAspectLocked(False)
#plt3.invertY(False)
#plt3.invertX(False)
#plt3.setRange(xRange=[E0,E1], yRange=[AS0,AS1],padding = 0)
plt3.setRange(xRange=[E0,E1], yRange=[-a_max,a_max])


l.addWidget(imv2, 0, 0)
l.addWidget(imv1, 1, 0)
l.addWidget(imv3, 1, 1)

win.show()

roi2 = pg.LineSegmentROI([[A0, (AS0+AS1)/2], [A1,(AS0+AS1)/2]], pen='r')
imv1.addItem(roi2)

roi3 = pg.LineSegmentROI([[(A0+A1)/2, AS0], [(A0+A1)/2,AS1]], pen='b')
imv1.addItem(roi3)

def update2():
#    global data, imv1, imv2, E0,A0,escale,ascale
    d2 = roi2.getArrayRegion(data, imv1.imageItem, axes=(1,2))
    imv2.setImage(np.transpose(d2),pos=[A0, E0], scale=[asscale, escale])
    imv2.ui.histogram.hide()
    imv2.ui.roiBtn.hide()
    imv2.ui.menuBtn.hide()
roi2.sigRegionChanged.connect(update2)

def update3():
 #   global data, imv1, imv3, E0,AS0,escale,asscale
    d3 = roi3.getArrayRegion(data, imv1.imageItem, axes=(1,2))
    imv3.setImage(d3,pos=[E0, AS0], scale=[escale, ascale])
    imv3.ui.histogram.hide()
    imv3.ui.roiBtn.hide()
    imv3.ui.menuBtn.hide()
roi3.sigRegionChanged.connect(update3)

## Display the data
imv1.setImage(data, xvals=np.linspace(E0, E1, data.shape[0]),\
                                  pos=[A0, AS0], scale=[ascale, asscale])
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






















