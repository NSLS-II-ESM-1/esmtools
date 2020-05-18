__author__ = 'Elio Vescovo'
__version__ = '0.0.1'

# import python standard modules
import sys
import os
import glob
import platform

# import 3rd party libraries
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import numpy as np
import pyqtgraph as pg
from igor.binarywave import load as loadibw

# import local python
import arpes_dlg as dlg
import util as ut

from ui.ui_main_window import Ui_MDIWindow
from ui.ui_dock_widget import Ui_DockWidget

class MDIWindow(QMainWindow):
    count = 0

    def __init__(self, parent=None):
        super(MDIWindow, self).__init__(parent)
        self.setWindowTitle("ARPES Viewer")
        #
        self.ui = Ui_MDIWindow()
        self.ui.setupUi(self)
        #
        self.mbar = self.setMenuBar(self.ui.ui_menubar.ui_menubar)
        self.ui.ui_menubar.exit_action.triggered.connect(self.close)
        self.ui.ui_menubar.file_menu.triggered[QAction].connect(self.WindowTrig)
        self.ui.ui_menubar.load_menu.triggered[QAction].connect(self.dir_open)
#
        self.tbar = self.addToolBar(self.ui.ui_toolbar.ui_toolbar)
        self.ui.ui_toolbar.bw_button_action.triggered.connect(self.onclicktb)

        #
        self.dck_widget = Ui_DockWidget()
        self.dck_widget.setupUi(self)
        self.addDockWidget(Qt.RightDockWidgetArea,self.dck_widget.ui_datalist_DockWidget)

        self.data_dict = {}
        self.data3D_dict = {}
        self.current_dir = None
        self.opened_wd_names = []
        self.opened3D_wd_names = []


        self.dck_widget.data_list.itemClicked.connect(self.show_data)
        self.dck_widget.data_list.itemDoubleClicked.connect(self.get_data)
        self.ui.mdi.subWindowActivated.connect(self.refresh_wnd)
        self.dck_widget.data3D_list.itemDoubleClicked.connect(self.get_data3D)


    def onclicktb(self):
        self.ui.base_wd.plt_i = pg.PlotItem(labels={'left': ('slits', 'degrees'), 'bottom': ('Kin. Energy', 'eV')})
        self.ui.base_wd.plt_iv = pg.ImageView(view=self.ui.base_wd.plt_i)
        self.ui.base_wd.setWidget(self.ui.base_wd.plt_iv)
        self.ui.base_wd.show()

    def refresh_wnd(self,s):
        try:
            if str(s.objectName()) in self.opened_wd_names:
                self.data_dict = ut.ibw2dict(self.current_dir + '/' + str(s.objectName()))
            elif str(s.objectName()) in self.opened3D_wd_names:
                self.data3D_dict = ut.read_bin_multi_region(self.current_dir, str(s.objectName())[:-4])
        except AttributeError as e:
            print('Error: {}'.format(e))

    def WindowTrig(self, p):
        if p.text() == "&New":
            MDIWindow.count = MDIWindow.count + 1
            sub = QMdiSubWindow()
            sub.setWidget(QTextEdit())
            sub.setWindowTitle("Sub Window" + str(MDIWindow.count))
            self.ui.mdi.addSubWindow(sub)
            sub.show()

        if p.text() == "&Cascade":
            self.ui.mdi.cascadeSubWindows()

        if p.text() == "&Tiled":
            self.ui.mdi.tileSubWindows()

    def dir_open(self, p):
        self.current_dir = dlg.File_dlg.openDirNameDialog(self)
        if p.text() == "2D" or p.text() == "3D":
            files_ls = glob.glob(self.current_dir + '/*.ibw')
            fls = [f[len(self.current_dir) + 1:] for f in files_ls]
            self.dck_widget.data_list.addItems(fls)
#        if p.text() == "3D":
            zip_ls = glob.glob(self.current_dir + '/*.zip')
            zp = [f[len(self.current_dir) + 1:] for f in zip_ls]
            self.dck_widget.data3D_list.addItems(zp)

    def show_data(self, s):
        file_name = s.text()
        self.data_dict = ut.ibw2dict(self.current_dir+'/'+file_name)

        e_sc = self.data_dict['E_axis'][1]-self.data_dict['E_axis'][0]
        a_sc = self.data_dict['A_axis'][1]-self.data_dict['A_axis'][0]
        e_rg = self.data_dict['E_axis'][-1] - self.data_dict['E_axis'][0]
        a_rg = self.data_dict['A_axis'][-1] - self.data_dict['A_axis'][0]
        e_str = self.data_dict['E_axis'][0]
        a_str = self.data_dict['A_axis'][0]
        e_end = self.data_dict['E_axis'][-1]
        a_end = self.data_dict['A_axis'][-1]

        self.ui.base_wd.plt_i.setRange(xRange=[e_str, e_end], yRange=[a_str, a_end], update=True, padding = 0)
        self.ui.base_wd.plt_i.getViewBox().setLimits(xMin= e_str, xMax = e_end, yMin=a_str, yMax=a_end)
        self.ui.base_wd.plt_iv.setImage(self.data_dict['data'], pos=[e_str, a_str], scale=[e_sc, a_sc])

        self.ui.base_wd.plt_iv.ui.roiBtn.hide()
        self.ui.base_wd.plt_iv.ui.menuBtn.hide()

    def get_data(self, s):
        file_name = s.text()
        MDIWindow.count = MDIWindow.count + 1
        sub = QMdiSubWindow()
        sub.resize(600, 600)
        sub.setWindowTitle(file_name)
        sub.setObjectName(file_name)
        if 'ibw' in file_name:
            self.opened_wd_names.append(file_name)
            self.data_dict = ut.ibw2dict(self.current_dir + '/' + file_name)
        elif 'zip' in file_name:
            self.opened3D_wd_names.append(file_name)
            self.data3D_dict = ut.read_bin_multi_region(self.current_dir, file_name[:-4])

        e_sc = self.data_dict['E_axis'][1] - self.data_dict['E_axis'][0]
        a_sc = self.data_dict['A_axis'][1] - self.data_dict['A_axis'][0]
        e_rg = self.data_dict['E_axis'][-1] - self.data_dict['E_axis'][0]
        a_rg = self.data_dict['A_axis'][-1] - self.data_dict['A_axis'][0]

        e_str = self.data_dict['E_axis'][0]
        a_str = self.data_dict['A_axis'][0]
        e_end = self.data_dict['E_axis'][-1]
        a_end = self.data_dict['A_axis'][-1]

        gr_v = pg.GraphicsView()
        l = pg.GraphicsLayout()
        gr_v.setCentralWidget(l)
        sub.setWidget(gr_v)
        self.ui.mdi.addSubWindow(sub)
        sub.show()

        p1 = l.addPlot(x=[1, 2], y=[1, 2], name="Plot1", title="EDC", pen="r", row=0, col=0)
        #       label1 = pg.LabelItem(justify='right')
        #        p1.addItem(label1)

        plt_i = pg.PlotItem(labels={'left': ('slits', 'degrees'), 'bottom': ('Kin. Energy', 'eV')})
        plt_i.setRange(xRange=[e_str, e_end], yRange=[a_str, a_end], update=True, padding=0)

        vb = plt_i.getViewBox()
        vb.setLimits(xMin=e_str, xMax=e_end, yMin=a_str, yMax=a_end)
        vb.setMouseMode(vb.RectMode)

        l.addItem(plt_i, row=1, col=0)
        img_i = pg.ImageItem(self.data_dict['data'], border=None)
        qrect = vb.viewRect()
        img_i.setRect(qrect)
        vb.addItem(img_i)
        vb.autoRange()
        #        vb.invertX()
        vb.invertY()
        hist = pg.HistogramLUTItem(image=img_i)

        l.addItem(hist, row=0, col=1)

        p2 = l.addPlot(x=[1, 2], y=[2, 1], name="Plot2", title="MDC", pen="g", row=1, col=1)
        #        label2 = pg.LabelItem(justify='left')
        #        plt_i.addItem(label2)

        # cross hair
        vLine = pg.InfiniteLine(angle=90, movable=False)
        hLine = pg.InfiniteLine(angle=0, movable=False)
        p1.addItem(vLine, ignoreBounds=False)
        p1.addItem(hLine, ignoreBounds=False)

        vb1 = p1.vb

        pcv = plt_i.addLine(x=e_end, pen='r')
        pch = plt_i.addLine(y=a_str, pen='r')

        def onMouseMoved(point):
            p = vb.mapSceneToView(point)
            pcv.setValue(p.x())
            pch.setValue(p.y())
            #            print(p.x(), p.y())

            hROI = pg.ROI((e_str, p.y()), size=(e_rg, 5 * a_sc))
            vb.addItem(hROI)
            hROI.hide()
            sl, co = hROI.getArrayRegion(self.data_dict['data'], img_i, returnMappedCoords=True)
            sl_sum = np.sum(sl, axis=1)
            p1.setXLink(plt_i)
            p1.plot(x=co[0, :, 0], y=sl_sum, clear=True)
            p1.setTitle('EDC, angle ={:.2f}'.format(p.y()))

            vROI = pg.ROI((p.x(), a_str), size=(5 * e_sc, a_rg))
            vb.addItem(vROI)
            vROI.hide()
            slc, coo = vROI.getArrayRegion(self.data_dict['data'], img_i, returnMappedCoords=True)
            sl_sum = np.sum(slc, axis=0)
            p2.invertY()
            p2.setYLink(plt_i)
            p2.plot(y=coo[1, 0, :], x=sl_sum, clear=True)
            p2.setTitle('MDC, energy ={:.2f}'.format(p.x()))

        #            label2.setText("{}-{}".format(p.x(), p.y()))

        img_i.scene().sigMouseMoved.connect(onMouseMoved)

    def get_data3D(self, s):
        file_name = s.text()
        self.opened3D_wd_names.append(file_name)
        MDIWindow.count = MDIWindow.count + 1
        sub = QMdiSubWindow()
        sub.resize(800, 800)
        sub.setWindowTitle(file_name)
        sub.setObjectName(file_name)
        self.data3D_dict = ut.read_bin_multi_region(self.current_dir, file_name[:-4])

        E_axis = np.array(
            [self.data3D_dict['w_of'], self.data3D_dict['w_of']+self.data3D_dict['w']*self.data3D_dict['w_dt']])
        A_axis = np.array(
            [self.data3D_dict['h_of'], self.data3D_dict['h_of'] + self.data3D_dict['h'] * self.data3D_dict['h_dt']])
        D_axis = np.array(
            [self.data3D_dict['d_of'], self.data3D_dict['d_of'] + self.data3D_dict['d'] * self.data3D_dict['d_dt']])
        a_max = np.max(np.abs(np.concatenate((A_axis,  D_axis), axis=None)))
        asscale, ascale, escale = self.data3D_dict['d_dt'],self.data3D_dict['h_dt'],self.data3D_dict['w_dt']


        cw = QWidget()
        l = QGridLayout()
        cw.setLayout(l)
        sub.setWidget(cw)
        self.ui.mdi.addSubWindow(sub)
        sub.show()

        plt1 = pg.PlotItem(labels={'bottom': ('slits', 'degrees'), 'left': ('deflector', 'degrees')})
        imv1 = pg.ImageView(view=plt1)
        plt1.setAspectLocked(False)
        plt1.setRange(xRange=[-a_max, a_max], yRange=[-a_max, a_max], padding=0)
        vb1 = plt1.getViewBox()
        vb1.setMouseMode(vb1.RectMode)

        print('vb1 rectg: {}'.format(vb1.screenGeometry()))

        histo1 = vb1.menu.addAction('histogram')
        no_histo1 = vb1.menu.addAction('no histogram')
        no_histo1.triggered.connect(imv1.ui.histogram.hide)
        histo1.triggered.connect(imv1.ui.histogram.show)

        plt2 = pg.PlotItem(labels={'bottom': ('slits', 'degrees'), 'left': ('Kin. Energy', 'eV')})
        imv2 = pg.ImageView(view=plt2)
        plt2.setAspectLocked(False)
        plt2.invertY(False)
        plt2.setRange(xRange=[-a_max, a_max], yRange=[E_axis[0], E_axis[-1]])
        vb2 = plt2.getViewBox()
        vb2.setMouseMode(vb2.RectMode)

        histo2 = vb2.menu.addAction('histogram')
        no_histo2 = vb2.menu.addAction('no histogram')
        no_histo2.triggered.connect(imv2.ui.histogram.hide)
        histo2.triggered.connect(imv2.ui.histogram.show)


        plt3 = pg.PlotItem(labels={'bottom': ('Kin. Energy', 'eV'), 'left': ('deflector', 'degrees')})
        imv3 = pg.ImageView(view=plt3)
        plt3.setAspectLocked(False)
        plt3.setRange(xRange=[E_axis[0], E_axis[-1]], yRange=[-a_max, a_max])
        vb3 = plt3.getViewBox()
        vb3.setMouseMode(vb3.RectMode)

        histo3 = vb3.menu.addAction('histogram')
        no_histo3 = vb3.menu.addAction('no histogram')
        no_histo3.triggered.connect(imv3.ui.histogram.hide)
        histo3.triggered.connect(imv3.ui.histogram.show)


        hlayout =QHBoxLayout()
        hlayout.addWidget(imv1.ui.histogram)
        hlayout.addWidget(imv2.ui.histogram)
        hlayout.addWidget(imv3.ui.histogram)

        hist_wdg = QWidget()
        hist_wdg.setLayout(hlayout)

        l.addWidget(imv2, 0, 0)
        l.addWidget(imv1, 1, 0)
        l.addWidget(imv3, 1, 1)
        l.addWidget(hist_wdg, 0, 1)


        roi2 = pg.LineSegmentROI([[A_axis[0], (D_axis[0]+D_axis[-1])/2], [A_axis[-1],(D_axis[0]+D_axis[-1])/2]], pen='r')
        imv1.addItem(roi2)

        roi3 = pg.LineSegmentROI([[(A_axis[0]+A_axis[1])/2, D_axis[0]], [(A_axis[0]+A_axis[-1])/2,D_axis[-1]]], pen='b')
        imv1.addItem(roi3)

        def update2():
            d2 = roi2.getArrayRegion(self.data3D_dict['data'], imv1.imageItem, axes=(1,2))
            imv2.setImage(np.transpose(d2),pos=[A_axis[0], E_axis[0]], scale=[ascale, escale],autoHistogramRange = False)
#            imv2.ui.histogram.hide()
            imv2.ui.roiBtn.hide()
            imv2.ui.menuBtn.hide()
        roi2.sigRegionChanged.connect(update2)

        def update3():
            d3 = roi3.getArrayRegion(self.data3D_dict['data'], imv1.imageItem, axes=(1,2))
            imv3.setImage(d3,pos=[E_axis[0], D_axis[0]], scale=[escale, asscale], autoHistogramRange=False)
#            imv3.ui.histogram.hide()
            imv3.ui.roiBtn.hide()
            imv3.ui.menuBtn.hide()
        roi3.sigRegionChanged.connect(update3)

        ## Display the data
        imv1.setImage(self.data3D_dict['data'], xvals=np.linspace(E_axis[0], E_axis[-1], self.data3D_dict['data'].shape[0]),\
                                          pos=[A_axis[0], D_axis[0]], scale=[ascale, asscale])
        imv1.setCurrentIndex(self.data3D_dict['data'].shape[0]//2)
#        imv1.ui.histogram.hide()
        imv1.ui.roiBtn.hide()
        imv1.ui.menuBtn.hide()
        #imv1.setImage(data)
        #imv1.setHistogramRange(-0.01, 0.01)
        #imv1.setLevels(-0.003, 0.003)
        update2()
        update3()
