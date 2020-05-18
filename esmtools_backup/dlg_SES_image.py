import numpy as np
from PyQt5 import  QtGui
from PyQt5.QtWidgets import  QDialog
import pyqtgraph as pg

class Plot3D_dlg(QDialog):
    def __init__(self, w, w_of, w_dt, h, h_of, h_dt, d, d_of, d_dt, data, rgs_ls,  parent=None):
        super(Plot3D_dlg,  self).__init__(parent)
        self.setFixedSize(950, 950)
        
        self.en_pnts, self.en_of, self.en_dt = w, w_of, w_dt
        self.ang_pnts, self.ang_of, self.ang_dt =h, h_of, h_dt
        self.defl_pnts, self.defl_of, self.defl_dt = d, d_of, d_dt
        self.data = data 
        self.rgs_ls = rgs_ls
        

        E_range = np.array([self.en_of, self.en_of +self.en_pnts*self.en_dt])
        A_range = np.array([self.ang_of, self.ang_of +self.ang_pnts*self.ang_dt])
        D_range = np.array([self.defl_of, self.defl_of +self.defl_pnts*self.defl_dt])
        a_max = np.max(np.abs(np.concatenate((A_range,  D_range), axis=None))) 
        a_max_range = np.array([-a_max,  a_max])    

#        E0, E1 = np.array([self.en_of, self.en_of +self.en_pnts*self.en_dt])
 #       A0, A1 = np.array([self.ang_of, self.ang_of +self.ang_pnts*self.ang_dt])
 #       AS0, AS1 = np.array([self.defl_of, self.defl_of +self.defl_pnts*self.defl_dt])
        asscale, ascale, escale = self.defl_dt,  self.ang_dt,  self.en_dt                                                                    
        
    #    print(E0, E1)
        self.data = np.transpose(self.data,axes=(2,1,0))
        print(self.data.shape)
        ## Create window with two ImageView widgets
        plt1 = pg.PlotItem(labels={'bottom': ('slits', 'degrees'), 'left': ('deflector', 'degrees')})
        plt1.getViewBox().setAspectLocked(lock = True,  ratio = None)
        plt1.getViewBox().setRange(xRange=a_max_range, yRange=a_max_range, padding = 0,   disableAutoRange = True)
        
       # print('pl1:', a_max_range,  a_max_range)
       # print('pl2:', a_max_range,  E_range)
        #print('pl3:', E_range,  a_max_range)


        plt2 = pg.PlotItem(labels={'bottom': ('slits', 'degrees'), 'left': ('Kin. Energy', 'eV')})
        plt2.getViewBox().invertY(False)
        plt2.getViewBox().setYRange(E_range[0],  E_range[1],  padding = 0)
        

        plt3 = pg.PlotItem(labels={'bottom': ('Kin. Energy', 'eV'), 'left': ('deflector', 'degrees')})
        plt3.getViewBox().setXRange(E_range[0],  E_range[1],   padding = 0)
        
        
        
        plt2.getViewBox().setXLink(plt1)
        plt3.getViewBox().setYLink(plt1)
        
        self.imv1 = pg.ImageView(view = plt1)
        self.imv2 = pg.ImageView(view = plt2)        
        self.imv3 = pg.ImageView(view = plt3)

        self.setWindowTitle('SES30 - DataSlicing')

        grid = QtGui.QGridLayout(self)        
        grid.addWidget(self.imv2, 0, 0)
        grid.addWidget(self.imv1, 1, 0)
        grid.addWidget(self.imv3, 1, 1)
        self.setLayout(grid)

        ## Display the data



        self.imv1.setImage(self.data, autoRange= False,  xvals=np.linspace(E_range[0], E_range[1], self.data.shape[0]),\
                                        pos=(A_range[0], D_range[0]), scale=(asscale, ascale))
        self.imv1.setCurrentIndex(self.data.shape[0]//2)                                
        self.imv1.ui.histogram.hide()
        self.imv1.ui.roiBtn.hide()
        self.imv1.ui.menuBtn.hide()
        



        roi2 = pg.LineSegmentROI([[A_range[0], (D_range[0]+D_range[1])/2], [A_range[1],(D_range[0]+D_range[1])/2]], pen='r')
        self.imv1.addItem(roi2)

        roi3 = pg.LineSegmentROI([[(A_range[0]+A_range[1])/2, D_range[0]], [(A_range[0]+A_range[1])/2, D_range[1]]], pen='b')
        self.imv1.addItem(roi3)
        

        def update2():
#            global self.data, self.imv1, self.imv2
            print(self.data.shape)
            d2 = roi2.getArrayRegion(self.data, self.imv1.imageItem, axes=(1,2))
#            print(A0,  E0)
            print(d2.shape)
            self.imv2.setImage(np.transpose(d2), autoRange= False, pos=(A_range[0], E_range[0]), scale=(ascale, escale))
            self.imv2.ui.histogram.hide()
            self.imv2.ui.roiBtn.hide()
            self.imv2.ui.menuBtn.hide()
        roi2.sigRegionChanged.connect(update2)

        def update3():
 #           global self.data, self.imv1, self.imv3
            d3 = roi3.getArrayRegion(self.data,  self.imv1.imageItem, axes=(1,2))
            self.imv3.setImage(d3, autoRange= False, pos=(E_range[0], D_range[0]), scale=(escale, asscale))
            self.imv3.ui.histogram.hide()
            self.imv3.ui.roiBtn.hide()
            self.imv3.ui.menuBtn.hide()
        roi3.sigRegionChanged.connect(update3)

        update2()
        update3()
