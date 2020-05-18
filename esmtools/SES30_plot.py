import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PyQt5 import QtWidgets,  QtCore,  QtGui ,  uic,  Qt
from PyQt5.QtWidgets import QWidget,  QFileDialog
from PyQt5.QtWidgets import QApplication,  QTableWidgetItem,  QMainWindow,  QToolBar,  QAction,  QLabel,  QCheckBox,  QStatusBar
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
import pkg_resources
import sys,  os,  glob
import pyqtgraph as pg
# Interpret image data as row-major instead of col-major
pg.setConfigOptions(imageAxisOrder='row-major')



from ui_dialog import Ui_dlg_win
from functools import partial
from zipfile import ZipFile


    
    



class File_dlg(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 file dialogs - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.openFileNameDialog()
        self.openFileNamesDialog()
        self.saveFileDialog()
        
        self.show()

    def openDirNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        dirName = QFileDialog.getExistingDirectory(self,"Open Directory", "/nsls2/xf21id1/csv_files/XPS/elio",  options=options)
        print(dirName)
        return(dirName)

    
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "/nsls2/xf21id1/csv_files/XPS","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName)
            return(fileName)
    
    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
        if files:
            print(files)
    
    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)










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




ui_path = pkg_resources.resource_filename('esmtools', 'ui/SES_plot_GUI.ui')


class MainWindow(*uic.loadUiType(ui_path)):
    def __init__(self, *args,  **kwargs):
        super().__init__(*args,  **kwargs)
        self.setupUi(self)
  
        self.actionLoad.triggered.connect(self.file_open)
  
    def file_open(self):
        self.fl_name = File_dlg.openDirNameDialog(self)
        self.lineEdit_dir.setText(os.path.dirname(self.fl_name))
        self.lineEdit_file.setText(os.path.basename(self.fl_name))
        
#        print(os.path.splitext(os.path.basename(self.fl_name))[0])
#        loader(os.path.splitext(os.path.basename(self.fl_name))[0], os.path.dirname(self.fl_name))
        w, w_of, w_dt, h, h_of, h_dt, d, d_of, d_dt, data, rgs_ls = \
                    read_bin_multi_region(os.path.dirname(self.fl_name),  os.path.splitext(os.path.basename(self.fl_name))[0])
        
        print(np.shape(data))                        
                        
        en =w_of+w_dt*np.arange(0,w)
        ang =h_of+h_dt*np.arange(0,h)
        ang_s=d_of+d_dt*np.arange(0,d)


        E0, E1 = (en[0], en[-1])
        A0, A1 = (ang[0], ang[-1])
        AS0,AS1 = (ang_s[0],ang_s[-1])
        asscale, ascale, escale = (AS1-AS0) / data.shape[0], (A1-A0) / data.shape[1], (E1-E0) / data.shape[2] 
        print(E0,E1,A0,A1,AS0,AS1)
        print(asscale,  ascale,  escale)

        data = np.transpose(data,axes=(2,1,0))
        a_max = np.max(np.abs(np.array([A0,A1,AS0,AS1]))) 
        print(np.shape(data),  a_max)                        
        plt1 = pg.PlotItem(labels={'bottom': ('slits', 'degrees'), 'left': ('deflector', 'degrees')})
        plt1.setAspectLocked(True)
        plt1.invertY(False)
        plt1.invertX(False)
        plt1.setRange(xRange=[-a_max,a_max], yRange=[-a_max,a_max], padding = 0)

        plt2 = pg.PlotItem(labels={'bottom': ('slits', 'degrees'), 'left': ('Kin. Energy', 'eV')})
        plt2.setAspectLocked(False)
        plt2.invertY(False)
        plt2.invertX(False)
        plt2.setRange(xRange=[E0,E1], yRange=[-a_max,a_max])

        plt3 = pg.PlotItem(labels={'bottom': ('Kin. Energy', 'eV'), 'left': ('deflector', 'degrees')})
        plt3.setAspectLocked(False)
        plt3.invertY(False)
        plt3.invertX(False)
        plt3.setRange(xRange=[E0,E1], yRange=[-a_max,a_max])

        self.gv_00.view=plt2
        self.gv_10.view=plt1
        self.gv_10.view.setLabel('bottom',  text = 'slits', units = 'degrees')
        self.gv_11.view=plt3
        print(self.gv_10.view.getLabel('bottom'))

        roi2 = pg.LineSegmentROI([[A0, (AS0+AS1)/2], [A1,(AS0+AS1)/2]], pen='r')
        self.gv_10.addItem(roi2)

        roi3 = pg.LineSegmentROI([[(A0+A1)/2, AS0], [(A0+A1)/2,AS1]], pen='b')
        self.gv_10.addItem(roi3)

        def update2():            
#            global data, self.gv_10, self.gv_00, E0,A0,escale,ascale
            d2 = roi2.getArrayRegion(data, self.gv_10.imageItem, axes=(1,2))
            self.gv_00.setImage(np.transpose(d2),pos=[A0, E0], scale=[ascale, escale])
            self.gv_00.ui.histogram.hide()
            self.gv_00.ui.roiBtn.hide()
            self.gv_00.ui.menuBtn.hide()
        roi2.sigRegionChanged.connect(update2)
        
        def update3():
#            global data, self.gv_10,self.gv_11, E0,AS0,escale,asscale
            d3 = roi3.getArrayRegion(data, self.gv_10.imageItem, axes=(1,2))
            self.gv_11.setImage(d3,pos=[E0, AS0], scale=[escale, asscale])
            self.gv_11.ui.histogram.hide()
            self.gv_11.ui.roiBtn.hide()
            self.gv_11.ui.menuBtn.hide()
        roi3.sigRegionChanged.connect(update3)


        ## Display the data
        self.gv_10.setImage(data, xvals=np.linspace(en[0], en[-1], data.shape[0]),\
                                          pos=[A0, AS0], scale=[ascale, asscale])
        self.gv_10.ui.histogram.hide()
        self.gv_10.ui.roiBtn.hide()
        self.gv_10.ui.menuBtn.hide()
        #imv1.setImage(data)
        #imv1.setHistogramRange(-0.01, 0.01)
        #imv1.setLevels(-0.003, 0.003)


        update2()
        update3()

        
       ## Display the data and assign each frame a time value from 1.0 to 3.0
#        self.graphicsView.setImage(data1)
        # set position and scale of image
                
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
        self.gv_11.setColorMap(cmap)
                
        
        
        
        
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()

