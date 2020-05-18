import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import scipy.optimize as opt
import os
from bluesky.plans import scan, adaptive_scan, spiral_fermat, spiral,scan_nd
from bluesky.plan_stubs import abs_set, mv
from bluesky.preprocessors import baseline_decorator, subs_decorator
# from bluesky.callbacks import LiveTable, LivePlot, CallbackBase
from pyOlog.SimpleOlogClient import SimpleOlogClient
from esm import ss_csv
from cycler import cycler
from collections import ChainMap
import math
import re
from boltons.iterutils import chunked











import re
import sys
import numpy as np
import pkg_resources
import math

from PyQt5 import uic, QtGui, QtCore


ui_path = pkg_resources.resource_filename('esmtools', 'ui/elio_gui_2.ui')

'''
def auto_redraw_factory(fnc):
    def stale_callback(fig, stale):
        if fnc is not None:
            fnc(fig, stale)
        if stale and fig.canvas:
            fig.canvas.draw_idle()

    return stale_callback
'''

class ElioGUI(*uic.loadUiType(ui_path)):

    #progress_sig = QtCore.pyqtSignal()

    def __init__(self, RE=None, motors = None, print_summary=None, scan_time=None,  scan_esm=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.scan_esm= scan_esm
        self.scan_time = scan_time
        self.print_summary = print_summary
        self.RE = RE
        self.motors = motors
        
        self.mtr_nm_ls = [i.name.replace('_', '.', 1) for i in  self.motors]
        idx =  self.mtr_nm_ls.index('EPU105.gap')
        gap_txt = str("{:.2f}".format(self.motors[idx].position))
        idx =  self.mtr_nm_ls.index('EPU105.phase')
        phase_txt = str("{:.2f}".format(self.motors[idx].position))
        self.lineEdit_EPU105.setText(gap_txt +", "+ phase_txt)
        
        idx =  self.mtr_nm_ls.index('EPU57.gap')
        gap_txt =  str("{:.2f}".format(self.motors[idx].position))
        idx =  self.mtr_nm_ls.index('EPU57.phase')
        phase_txt =  str("{:.2f}".format(self.motors[idx].position))
        self.lineEdit_EPU57.setText(gap_txt +", "+ phase_txt)

        idx =  self.mtr_nm_ls.index('FEslit.h_gap')
        self.lineEdit_FE_Hgap.setText( str("{:.2f}".format(self.motors[idx].position)))
        idx =  self.mtr_nm_ls.index('FEslit.h_center')
        self.lineEdit_FE_Hctr.setText( str("{:.2f}".format(self.motors[idx].position))) 
        
        idx =  self.mtr_nm_ls.index('FEslit.v_gap')
        self.lineEdit_FE_Vgap.setText( str("{:.2f}".format(self.motors[idx].position)))
        idx =  self.mtr_nm_ls.index('FEslit.v_center')
        self.lineEdit_FE_Vctr.setText( str("{:.2f}".format(self.motors[idx].position))) 

        idx =  self.mtr_nm_ls.index('M1.X')
        self.lineEdit_M1_x.setText( str("{:.4f}".format(self.motors[idx].position))) 
        idx =  self.mtr_nm_ls.index('M1.Ry')
        self.lineEdit_M1_Ry.setText( str("{:.4f}".format(self.motors[idx].position))) 
        idx =  self.mtr_nm_ls.index('M1.Rz')
        self.lineEdit_M1_Rz.setText( str("{:.4f}".format(self.motors[idx].position))) 


#        print(self.comboBox_motor.currentText())

        self.comboBox_scan.addItems(['scan_1D', 'scan_multi_1D', 'scan_2D']) 
        mt = [ 'EPU57.gap',  'EPU57.phase','EPU105.gap', 'EPU57.phase',\
                    'FEslit.h_center','FEslit.h_gap','FEslit.v_center','FEslit.v_gap',\
                    'M1.X','M1.Ry', 'M1.Rz',\
                    'PGM.Energy', 'PGM.Focus_Const', 'PGM.Grating_Trans',\
                    'M3Udiag.trans',\
                    'M3.X', 'M3.Y', 'M3.Z', 'M3.Rx', 'M3.Ry', 'M3.Rz',\
                    'ExitSlitA.h_gap', 'ExitSlitA.v_gap', 'ExitSlitB.h_gap', 'ExitSlitB.v_gap',
                    'BTA2diag.trans', 'BTB2diag.trans',\
                    'M4A.HFM_X', 'M4A.HFM_Z',  'M4A.HFM_Ry', 'M4A.HFM_Au_Mesh', \
                    'M4A.VFM_Y', 'M4A.VFM_Z', 'M4A.VFM_Rx', 'M4A.VFM_Au_Mesh', 'M4B.X', 'M4B.Y', 'M4B.Z', 'M4B.Rx', 'M4B.Ry', 'M4B.Rz']
         
        self.comboBox_motor.addItems(mt)
        self.comboBox_motor_2.addItems(mt)
        
        self.comboBox_detector.addItems(['xqem01', 'qem01' , 'qem02' , 'qem03', 'qem04', 'qem05', 'qem06', 'qem07', 'qem08', 'qem10',\
                                                            'qem12', 'qem13', 'qem15', 'qem16'])                                                    
        self.pushButton_startscan.clicked.connect(self.start_scan)
        self.comboBox_scan.activated.connect(self.scan_changed)
        self.timer_update_time = QtCore.QTimer(self)
        self.timer_update_time.setInterval(500)
        self.timer_update_time.timeout.connect(self.update_status)
        self.timer_update_time.start()

        



    def start_scan(self):
#        self.print_summary(self.scan_time(self.qem07))
#        mtr_name = self.comboBox_motor.currentText()
 #       mtr_nm_ls = [i.name.replace('_', '.', 1) for i in  self.motors]
        idx =  self.mtr_nm_ls.index(self.comboBox_motor.currentText())
        idx_2 =  self.mtr_nm_ls.index(self.comboBox_motor_2.currentText())
        
        scn_nm_ls = [i.__name__ for i in  self.scan_esm]
        idx_sc =  scn_nm_ls.index(self.comboBox_scan.currentText())
        
        #print(type(self.motors))
        #print(type(self.motors[0]))
        #dx = self.motors.index(mtr)
        if self.comboBox_scan.currentText() == 'scan_1D':         ### only one motor ###
            self.print_summary(self.scan_esm[idx_sc](\
                                                                            self.comboBox_detector.currentText()+'@'+self.comboBox_ch.currentText(),\
                                                                            self.motors[idx],  float(self.lineEdit_start.text()), float(self.lineEdit_stop.text()), float(self.lineEdit_step.text()) ))
        else:                                                                                   ### two motors ###
            self.print_summary(self.scan_esm[idx_sc](\
                                                                            self.comboBox_detector.currentText()+'@'+self.comboBox_ch.currentText(),\
                                                                            self.motors[idx],  float(self.lineEdit_start.text()), float(self.lineEdit_stop.text()), float(self.lineEdit_step.text()) ,\
                                                                            self.motors[idx_2],  float(self.lineEdit_start_2.text()), float(self.lineEdit_stop_2.text()), float(self.lineEdit_step_2.text()) ))
 #       self.RE(scan([qem07], num=1))
        #new_energy = float(self.lineEdit_energy.text())
        #print(str(new_energy))
        #self.RE(bps.mv(self.motors[0], new_energy))

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

        





    def set_energy_center(self):
        ses.center_en_sp.put(float(self.lineEdit_encenter))

    def set_energy_width(self):
        ses.width_en_sp.put(float(self.lineEdit_enwidth))

    def update_status(self):
        pass
        #This will poll the done PV and update the label
        #print('Hi')
        #actual_energy = (self.motors[0].energy.read()['hhm_energy']['value'])
        #self.label_actual_energy.setText(f'Actual energy is {actual_energy}')


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    esm_live = ElioGUI(print_summary=print_summary, scan_1D=scan_1D, motors=[EPU57.gap, PGM.Energy], qem07=qem07)
    esm_live.show()
    sys.exit(app.exec_())
