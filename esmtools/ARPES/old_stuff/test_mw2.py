#!/usr/bin/env python3

import os
import glob
import platform
import sys
#from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiArea, QAction, QMdiSubWindow, QTextEdit, QDockWidget, \
    QListWidget, QWidget, QGridLayout, QListWidgetItem, QToolBar

import numpy as np
import pyqtgraph as pg
from igor.binarywave import load as loadibw

import arpes_dlg as dlg
import util as ut


class MDIWindow(QMainWindow):
    count = 0

    def __init__(self):
        super().__init__()

        self.data_dict = {}
        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)
#        self.mdi.resize(950,950)

        bar = self.menuBar()

        self.current_dir = None
        self.opened_wd_names = []
        file = bar.addMenu("File")
        file.addAction("New")
        file.addAction("cascade")
        file.addAction("Tiled")
        file.triggered[QAction].connect(self.WindowTrig)

        load = bar.addMenu("Load")
        load.addAction("2D")
        load.addAction("3D")
        load.triggered[QAction].connect(self.dir_open)

        toolbar = QToolBar()
        self.addToolBar(toolbar)

        bw_button_action = QAction('base_wnd', self)
        bw_button_action.setStatusTip('base window button')
        bw_button_action.triggered.connect(self.onclicktb)
        toolbar.addAction(bw_button_action)

        self.setWindowTitle("MDI Application")

        self.base_wd = QMdiSubWindow()
        self.base_wd.setAttribute(Qt.WA_DeleteOnClose, False)
        self.base_wd.resize(400, 400)
        self.base_wd.plt_i = pg.PlotItem(labels={'left': ('slits', 'degrees'), 'bottom': ('Kin. Energy', 'eV')})
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
        self.mdi.subWindowActivated.connect(self.get_data)



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
        print('show data')
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
        print('get data')
        if isinstance (s,QMdiSubWindow) and str(s.objectName()) in self.opened_wd_names:
            sub = self.mdi.currentSubWindow()
            self.data_dict = ut.ibw2dict(self.current_dir+'/'+str(s.objectName()))
        elif isinstance (s,QListWidgetItem):
            file_name = s.text()
            self.opened_wd_names.append(file_name)
            MDIWindow.count = MDIWindow.count + 1
            sub = QMdiSubWindow()
            sub.resize(550, 550)
            sub.setWindowTitle(file_name)
            sub.setObjectName(file_name)
            self.data_dict = ut.ibw2dict(self.current_dir+'/'+file_name)
        else:
            print(isinstance (s,QMdiSubWindow), isinstance (s,QListWidgetItem))
            print(type(s))
            return
        e_sc = self.data_dict['E_axis'][1]-self.data_dict['E_axis'][0]
        a_sc = self.data_dict['A_axis'][1]-self.data_dict['A_axis'][0]
        e_rg = self.data_dict['E_axis'][-1] - self.data_dict['E_axis'][0]
        a_rg = self.data_dict['A_axis'][-1] - self.data_dict['A_axis'][0]

        e_str = self.data_dict['E_axis'][0]
        a_str = self.data_dict['A_axis'][0]
        e_end = self.data_dict['E_axis'][-1]
        a_end = self.data_dict['A_axis'][-1]
        print(e_str,a_str)
        print(e_end, a_end)
        print(e_rg, a_rg)
        print(e_sc, a_sc)


        gr_v = pg.GraphicsView()
        l = pg.GraphicsLayout()
        gr_v.setCentralWidget(l)
        sub.setWidget(gr_v)
        self.mdi.addSubWindow(sub)
        sub.show()

        p1 = l.addPlot(x=[1,2], y=[1,2], name="Plot1", title="EDC",pen="r",row=0, col=0)
 #       label1 = pg.LabelItem(justify='right')
#        p1.addItem(label1)

        plt_i = pg.PlotItem( labels={'left': ('slits', 'degrees'), 'bottom': ('Kin. Energy', 'eV')})
        plt_i.setRange(xRange=[e_str, e_end], yRange=[a_str, a_end], update=True, padding = 0)

        vb = plt_i.getViewBox()
        vb.setLimits(xMin= e_str, xMax = e_end, yMin=a_str, yMax=a_end)

        l.addItem(plt_i, row=1, col=0)
        img_i = pg.ImageItem(self.data_dict['data'] , border=None)
        qrect = vb.viewRect()
        img_i.setRect(qrect)
        vb.addItem(img_i)
        vb.autoRange()
#        vb.invertX()
        vb.invertY()



        p2 = l.addPlot(x=[1,2], y=[2,1], name="Plot2", title="MDC", pen="g",row=1, col=1)
#        label2 = pg.LabelItem(justify='left')
#        plt_i.addItem(label2)

        # cross hair
        vLine = pg.InfiniteLine(angle=90, movable=False)
        hLine = pg.InfiniteLine(angle=0, movable=False)
        p1.addItem(vLine, ignoreBounds=False)
        p1.addItem(hLine, ignoreBounds=False)

        vb1 = p1.vb

        pcv = plt_i.addLine(x = e_end, pen='r')
        pch = plt_i.addLine(y=a_str, pen='r')
#        lROI = pg.ROI(((e_str+e_end)/2,a_str), size=(5*e_sc,a_rg))
#        vb.addItem(lROI)
#        slice, coor = lROI.getArrayRegion(self.data_dict['data'], img_i ,returnMappedCoords = True)

#        print('slice')
#        sl_sum=np.sum(slice, axis=0)
#        print(sl_sum[0:10])
#        print(type(slice), slice.shape)
#        print(type(coor), coor.shape)
#        print(coor[1,0,0:10])
#        p2.invertY()
#        p2.setYLink(plt_i)
#        p2.plot(y=coor[1,0,:], x=sl_sum)

        def onMouseMoved(point):
            p =vb.mapSceneToView(point)
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

            vROI = pg.ROI((p.x(),a_str), size=(5*e_sc, a_rg))
            vb.addItem(vROI)
            vROI.hide()
            slc, coo = vROI.getArrayRegion(self.data_dict['data'], img_i ,returnMappedCoords = True)
            sl_sum=np.sum(slc, axis=0)
            p2.invertY()
            p2.setYLink(plt_i)
            p2.plot(y=coo[1,0,:], x=sl_sum, clear=True)




#            label2.setText("{}-{}".format(p.x(), p.y()))

        img_i.scene().sigMouseMoved.connect(onMouseMoved)

    def onclicktb(self):
        self.base_wd.plt_i = pg.PlotItem(labels={'left': ('slits', 'degrees'), 'bottom': ('Kin. Energy', 'eV')})
        self.base_wd.plt_iv = pg.ImageView(view=self.base_wd.plt_i)
        self.base_wd.setWidget(self.base_wd.plt_iv)
        self.base_wd.show()



'''   
        print(len(self.mdi.subWindowList()))
        self.base_wd = QMdiSubWindow()
        self.base_wd.resize(400, 400)
        self.base_wd.setWindowTitle("plot window")
        self.mdi.addSubWindow(self.base_wd)




        def mouseMoved(evt):
            print(type(evt[0]))
            pos = evt[0]  ## using signal proxy turns original arguments into a tuple
            if p1.sceneBoundingRect().contains(pos):
                mousePoint = vb1.mapSceneToView(pos)
                index = int(mousePoint.x())
                if index > 0 and index < len(data1):
                    label.setText(
                        "<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (
                        mousePoint.x(), data1[index], data2[index]))
                vLine.setPos(mousePoint.x())
                hLine.setPos(mousePoint.y())

        #proxy = pg.SignalProxy(p1.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)
        p1.scene().sigMouseMoved.connect(mouseMoved)

        
        
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


'''

app = QApplication(sys.argv)
mdi = MDIWindow()
mdi.resize(1500,900)
mdi.show()
app.exec_()

