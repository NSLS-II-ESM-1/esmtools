from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import time
import traceback, sys

class Color(QWidget):

    def __init__(self, color, *args, **kwargs):
        super(Color, self).__init__(*args, **kwargs)
        self.setAutoFillBackground(True)
        
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)



ui_path = pkg_resources.resource_filename('esmtools', 'ui/elio_gui_3.ui')
class BmlnWindow(*uic.loadUiType(ui_path)):
    
    def __init__(self, RE=None, print_summary=None, scan_time=None,  scan_esm=None, motors = None,  Beamline=None,  *args,  **kwargs):
        super().__init__(*args,  **kwargs)
        self.setupUi(self)

        self.RE = RE
        self.print_summary = print_summary
        self.scan_time = scan_time
        self.scan_esm= scan_esm
        self.motors = motors
        self.Beamline = Beamline

                                # status dictionary of motors names (keys) and their positions (values)                                   
                                # stopped at 20 but in principle would like to go to len(self.motors)
        self.mtr_status = dict( (self.motors[i].name,  self.motors[i].position) for i in range(20) )
                                # motor dictionary of motors names (keys) and EpicMotor devices (values)        
        self.mtr_dict =     dict( (self.motors[i].name,  self.motors[i]) for i in range(20) )         


        self.comboBox_scan.addItems(['scan_1D', 'scan_multi_1D', 'scan_2D']) 

 
#        self.mtr_nm_ls = [i.replace('_', '.', 1) for i in  self.mtr_status.keys()]
     
#        self.mtr_nm_ls = [i.name.replace('_', '.', 1) for i in  self.motors]

         
        self.comboBox_motor.addItems(self.mtr_dict.keys())
        self.comboBox_motor_2.addItems(self.mtr_dict.keys())
#        self.comboBox_motor.addItems(self.mtr_nm_ls)
 #       self.comboBox_motor_2.addItems(self.mtr_nm_ls)
        
        self.comboBox_detector.addItems(['xqem01', 'qem01' , 'qem02' , 'qem03', 'qem04', 'qem05', 'qem06', 'qem07', 'qem08', 'qem10',\
                                                            'qem12', 'qem13', 'qem15', 'qem16'])                                                    

      
    
        self.pushButton_startscan.clicked.connect(self.start_scan)
        self.comboBox_scan.activated.connect(self.scan_changed)

        self.timer_update_time = QtCore.QTimer(self)
        self.timer_update_time.setInterval(500)
        self.timer_update_time.timeout.connect(self.update_status)
        self.timer_update_time.start()




    def start_scan(self):

        m =  self.comboBox_motor.currentText()
        m1 =  self.comboBox_motor_2.currentText()
            
        scn_nm_ls = [i.__name__ for i in  self.scan_esm]
        idx_sc =  scn_nm_ls.index(self.comboBox_scan.currentText())
            
        if self.comboBox_scan.currentText() == 'scan_1D':         ### only one motor ###
            self.print_summary(self.scan_esm[idx_sc](\
                                                                            self.comboBox_detector.currentText()+'@'+self.comboBox_ch.currentText(),\
                                                                            self.mtr_dict[m],  float(self.lineEdit_start.text()), float(self.lineEdit_stop.text()), float(self.lineEdit_step.text()) ))

        else:                                                                                   ### two motors ###
            self.print_summary(self.scan_esm[idx_sc](\
                                             self.comboBox_detector.currentText()+'@'+self.comboBox_ch.currentText(),\
                                             self.mtr_dict[m],  float(self.lineEdit_start.text()), float(self.lineEdit_stop.text()), float(self.lineEdit_step.text()) ,\

                                             self.mtr_dict[m1],  float(self.lineEdit_start_2.text()), float(self.lineEdit_stop_2.text()), float(self.lineEdit_step_2.text()) ))
    def scan_changed(self):
        if self.comboBox_scan.currentText() == 'scan_1D':
            self.comboBox_motor_2.setDisabled(True)
            self.lineEdit_start_2.setDisabled(True)
            self.lineEdit_stop_2.setDisabled(True)
            self.lineEdit_step_2.setDisabled(True)
        else:
            self.comboBox_motor_2.setDisabled(False)
            self.lineEdit_start_2.setDisabled(False)
            self.lineEdit_stop_2.setDisabled(False)
            self.lineEdit_step_2.setDisabled(False)      
    
    def update_status(self):
        for i in range(20):             # stopped at 20 but in principle would like to go to len(self.motors)
            self.mtr_status.update({self.motors[i].name:  self.motors[i].position})        
                                                            # populate the bmln status widgets
        self.lineEdit_EPU105.setText( str("{:.2f}".format(self.mtr_status['EPU105_gap'])) +", "+  str("{:.2f}".format(self.mtr_status['EPU105_phase'])) )
        self.lineEdit_EPU57.setText( str("{:.2f}".format(self.mtr_status['EPU57_gap'])) +", "+  str("{:.2f}".format(self.mtr_status['EPU57_phase'])) )
        self.lineEdit_FE_Hgap.setText( str("{:.2f}".format(self.mtr_status['FEslit_h_gap'])))
        self.lineEdit_FE_Hctr.setText(  str("{:.2f}".format(self.mtr_status['FEslit_h_center']))) 
        self.lineEdit_FE_Vgap.setText( str("{:.2f}".format(self.mtr_status['FEslit_v_gap'])))
        self.lineEdit_FE_Vctr.setText(  str("{:.2f}".format(self.mtr_status['FEslit_v_center']))) 
        self.lineEdit_M1_x.setText(  str("{:.4f}".format(self.mtr_status['M1_X']))) 
        self.lineEdit_M1_Ry.setText(  str("{:.4f}".format(self.mtr_status['M1_Ry']))) 
        self.lineEdit_M1_Rz.setText(  str("{:.4f}".format(self.mtr_status['M1_Rz'])))
     
    




class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.setWindowTitle("My Awesome App")


        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.setTabPosition(QTabWidget.East)
        tabs.setMovable(True)

        for n, color in enumerate(['red','green','blue','yellow']):
            tabs.addTab( Color(color), color)

        self.setCentralWidget(tabs)
        self.show()


def main (RE=None, print_summary=None, scan_time=None,  scan_esm=None, motors = None,  Beamline = None):
    app = QtWidgets.QApplication([])
    wd = MainWindow(RE=RE, print_summary=print_summary, scan_time=scan_time,  scan_esm=scan_esm, motors = motors,  Beamline=Beamline)   
    app.exec_()
    
if __name__ == '__main__':
    main()

