import os
import glob
import platform
import sys
#from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiArea, QAction, QMdiSubWindow, QTextEdit, QDockWidget, QListWidget

import numpy as np
import pyqtgraph as pg
from igor.binarywave import load as loadibw

import arpes_dlg as dlg
import util as ut


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

        load = bar.addMenu("Load")
        load.addAction("2D")
        load.addAction("3D")
        load.triggered[QAction].connect(self.dir_open)

        self.setWindowTitle("MDI Application")

        self.base_wd = QMdiSubWindow()
        self.base_wd.plt_i = pg.PlotItem(labels={'bottom': ('slits', 'degrees'), 'left': ('Kin. Energy', 'eV')})
        self.base_wd.plt_iv = pg.ImageView(view=self.base_wd.plt_i)
        self.base_wd.setWidget(self.base_wd.plt_iv)
        self.base_wd.setWindowTitle("plot window")
        self.mdi.addSubWindow(self.base_wd)
        self.base_wd.show()


        data_DockWidget =QDockWidget('data', self)
        data_DockWidget.setObjectName(('data window'))
        data_DockWidget.setAllowedAreas(Qt.RightDockWidgetArea)

        self.data_list = QListWidget()
        data_DockWidget.setWidget(self.data_list)
        self.addDockWidget(Qt.RightDockWidgetArea,data_DockWidget)

        self.data_list.itemClicked.connect(self.show_data)
        self.data_list.itemDoubleClicked.connect(self.get_data)




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
        self.current_dir = dlg.File_dlg.openDirNameDialog(self)
        print(self.current_dir)
        if p.text() == "2D":
            print('2D')
            files_ls = glob.glob(self.current_dir + '/*.ibw')
            fls = [f[len(self.current_dir) + 1:] for f in files_ls]
            print(files_ls)
            self.data_list.addItems(fls)
        if p.text() == "3D":
            zip_ls = glob.glob(self.current_dir + '/*.zip')
            zp = [f[len(self.current_dir) + 1:] for f in zip_ls]
            print(zp)
            self.data_list.addItems(zp)

    def show_data(self, s):
        file_name = s.text()
        self.data_dict = ut.ibw2dict(self.current_dir+'/'+file_name)

        e_sc = self.data_dict['E_axis'][1]-self.data_dict['E_axis'][0]
        a_sc = self.data_dict['A_axis'][1]-self.data_dict['A_axis'][0]
        e_str = self.data_dict['E_axis'][0]
        a_str = self.data_dict['A_axis'][0]
        self.base_wd.plt_i.setRange(xRange=[self.data_dict['E_axis'][0], self.data_dict['E_axis'][-1]], \
                            yRange=[self.data_dict['A_axis'][0], self.data_dict['A_axis'][-1]], update=True, padding = 0)

        self.base_wd.plt_i.getViewBox().setLimits(xMin= e_str, xMax = self.data_dict['E_axis'][-1],\
                                          yMin=self.data_dict['A_axis'][0], yMax=self.data_dict['A_axis'][-1])

        self.base_wd.plt_iv.setImage(self.data_dict['data'], pos=[self.data_dict['E_axis'][0], self.data_dict['A_axis'][0]], scale=[e_sc, a_sc])
#        self.base_wd.plt_iv.ui.histogram.hide()
        self.base_wd.plt_iv.ui.roiBtn.hide()
        self.base_wd.plt_iv.ui.menuBtn.hide()




    def get_data(self, s):
        file_name = s.text()
        self.data_dict = ut.ibw2dict(self.current_dir+'/'+file_name)

        MDIWindow.count = MDIWindow.count + 1
        sub = QMdiSubWindow()

        sub.plt_i = pg.PlotItem(labels={'bottom': ('slits', 'degrees'), 'left': ('Kin. Energy', 'eV')})
        sub.plt_iv = pg.ImageView(view=sub.plt_i)
        sub.setWidget(sub.plt_iv)
        sub.setWindowTitle(file_name)
        self.mdi.addSubWindow(sub)
        sub.show()


        e_sc = self.data_dict['E_axis'][1]-self.data_dict['E_axis'][0]
        a_sc = self.data_dict['A_axis'][1]-self.data_dict['A_axis'][0]
        e_str = self.data_dict['E_axis'][0]
        a_str = self.data_dict['A_axis'][0]
        e_end = self.data_dict['E_axis'][-1]
        a_end = self.data_dict['A_axis'][-1]
        sub.plt_i.setRange(xRange=[self.data_dict['E_axis'][0], self.data_dict['E_axis'][-1]], \
                            yRange=[self.data_dict['A_axis'][0], self.data_dict['A_axis'][-1]], update=True, padding = 0)

        sub.plt_i.getViewBox().setLimits(xMin= e_str, xMax = self.data_dict['E_axis'][-1],\
                                          yMin=self.data_dict['A_axis'][0], yMax=self.data_dict['A_axis'][-1])

        sub.plt_iv.setImage(self.data_dict['data'], pos=[self.data_dict['E_axis'][0], self.data_dict['A_axis'][0]], scale=[e_sc, a_sc])

        sub.plt_iv.ui.roiBtn.clicked.connect(lambda status, a_s = a_str,a_e = a_end,e_s = e_str,e_e = e_end, e_w = e_sc*10, a_w = a_sc*10, iv = sub.plt_iv:\
                                                 self.add_lin_ROI(status, a_s, a_e, e_s, e_e, e_w, a_w, iv))

    def add_lin_ROI(self,status, a_str,a_end,e_str,e_end,e_w, a_w, iv):

        if status:
            roi_edc = pg.LineSegmentROI([[e_str, (a_str+a_end)/2], [e_end,(a_str+a_end)/2]], pen='r',removable = True)
            iv.addItem(roi_edc)

            roi_mdc = pg.LineSegmentROI([[(e_str+e_end)/2, a_str], [(e_str+e_end)/2,a_end]], pen='b',removable = True)
            iv.addItem(roi_mdc)
        else:
            print(iv.getRoiPlot)
            iv.getRoiPlot.removeSegment()
            iv.removeItem(iv.getRoiPlot)

#        sub.plt_iv.ui.histogram.hide()
#        sub.plt_iv.ui.roiBtn.hide()
#        sub.plt_iv.ui.menuBtn.hide()




app = QApplication(sys.argv)
mdi = MDIWindow()
mdi.show()
app.exec_()

