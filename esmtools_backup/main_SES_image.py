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
#import dlg_SES_image
import slicing as dlg_SES_image
    
    



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
#        self.fl_name = File_dlg.openDirNameDialog(self)
 #       self.lineEdit_dir.setText(os.path.dirname(self.fl_name))
   #     self.lineEdit_file.setText(os.path.basename(self.fl_name))
        
        w, w_of, w_dt, h, h_of, h_dt, d, d_of, d_dt, data, rgs_ls = \
                                    read_bin_multi_region('/nsls2/xf21id1/csv_files/XPS/elio',  'IT3_0043')


#                    read_bin_multi_region(os.path.dirname(self.fl_name),  os.path.splitext(os.path.basename(self.fl_name))[0])

        
        plot_dlg = dlg_SES_image.Plot3D_dlg(w, w_of, w_dt, h, h_of, h_dt, d, d_of, d_dt, data, rgs_ls,  self)    
        plot_dlg.show()
        
        
        
        
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()

