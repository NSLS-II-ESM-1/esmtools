from PyQt5 import QtWidgets,  QtCore,  QtGui ,  uic,  Qt
from PyQt5.QtWidgets import QTableWidgetItem
import pkg_resources
import sys
from bluesky.plans import count
import signal

from ui_dialog import Ui_dlg_win
from functools import partial

ui_path = pkg_resources.resource_filename('esmtools', 'ui/elio_gui_4.ui')

class WorkerSignals(QtCore.QObject):
    trigger = QtCore.pyqtSignal(object, list)

class Worker(QtCore.QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and 
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    signals = WorkerSignals()

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        #self.signals = WorkerSignals()

    @QtCore.pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        self.fn(*self.args, **self.kwargs)
        #self.signals.trigger.emit()


        
 





class MainWindow(*uic.loadUiType(ui_path)):

    def __init__(self, db=None,  RE=None, print_summary=None, scan_time=None,  scan_esm=None, motors = None, detectors=None,  Beamline=None,\
                            BeamSource=None, Eph=None,   *args,  **kwargs):
        super().__init__(*args,  **kwargs)
        self.setupUi(self)

        
        self.db = db
        self.RE = RE
        self.detectors = detectors
        self.print_summary = print_summary
        self.scan_time = scan_time
        self.scan_esm= scan_esm
        self.count= scan_esm[3]
        self.motors = motors
        self.Beamline = Beamline
        self.BeamSource = BeamSource
        self.Eph = Eph
        
        self.threadpool = QtCore.QThreadPool()
        
        
                                # status dictionary of motors names (keys) and their positions (values)                                   
                                # stopped at 20 but in principle would like to go to len(self.motors)
        self.mtr_status = dict( (self.motors[i].name,  self.motors[i].position) for i in range(len(self.motors)) )
                                # motor dictionary of motors names (keys) and EpicMotor devices (values)        
        self.mtr_dict =     dict( (self.motors[i].name,  self.motors[i]) for i in range(len(self.motors) ))         
    


#                                   Initialize the compo box of the BMLN tab
#       self.comboBox_scan.addItems(['scan_1D', 'scan_multi_1D', 'scan_2D']) 
        self.comboBox_motor.addItems(self.mtr_dict.keys())
        self.comboBox_motor_2.addItems(self.mtr_dict.keys())        
#        self.comboBox_detector.addItems(['xqem01', 'qem01' , 'qem02' , 'qem03', 'qem04', 'qem05', 'qem06', 'qem07', 'qem08', 'qem10',\
 #                                                           'qem12', 'qem13', 'qem15', 'qem16'])                                                    

      
#                                   connecting the widgets of the BMLN tab
    
        self.pushButton_PGM_set.clicked.connect(self.move_PGM)    
        self.pushButton_startscan.clicked.connect(self.start_scan)
        self.pushButton_abort.clicked.connect(self.abort)
        self.comboBox_scan.activated.connect(self.scan_changed)
        self.timer_update_time = QtCore.QTimer(self)
        self.timer_update_time.setInterval(500)
        self.timer_update_time.timeout.connect(self.update_status)
        self.timer_update_time.start()

#        pushBtn_ls = ['EPU57_gap', 'EPU57_phase',  'EPU105_gap', 'EPU105_gap'] 

#        mtr_key-ls = ['EPU57_gap', 'EPU57_phase',  'EPU105_gap', 'EPU105_gap']
        
        self.pushButton_FE_Hgap.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['FEslit_h_gap']))   
        self.pushButton_FE_Hctr.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['FEslit_h_center']))   
        self.pushButton_FE_Vgap.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['FEslit_v_gap']))   
        self.pushButton_FE_Vctr.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['FEslit_v_center']))   

        self.pushButton_M1_x.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['M1_X']))   
        self.pushButton_M1_Ry.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['M1_Ry']))   
        self.pushButton_M1_Rz.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['M1_Rz']))   

        self.pushButton_PGM_Energy.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['PGM_Energy']))   
        self.pushButton_PGM_c.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['PGM_Focus_Const']))   
        self.pushButton_PGM_grt.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['PGM_Grating_Trans']))   

        self.pushButton_M3_x.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['M3_X']))   
        self.pushButton_M3_y.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['M3_Y']))     
        self.pushButton_M3_Ry.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['M3_Ry']))   
        self.pushButton_M3_Rz.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['M3_Rz']))   

        self.pushButton_ESA_V.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['ExitSlitA_v_gap']))   
        self.pushButton_ESA_H.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['ExitSlitA_h_gap']))           
        self.pushButton_ESB_V.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['ExitSlitB_v_gap']))   
        self.pushButton_ESB_H.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['ExitSlitB_h_gap']))
        
        self.pushButton_KBH_X.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['M4A_HFM_X']))     
        self.pushButton_KBH_Z.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['M4A_HFM_Z']))     
#        self.pushButton_KBH_Ry.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['M4A_HFM_Ry']))     
  
        self.pushButton_KBV_Y.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['M4A_VFM_Y']))     
        self.pushButton_KBV_Z.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['M4A_VFM_Z']))     
#       self.pushButton_KBV_Rx.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['M4A_VFM_Rx']))     

        self.pushButton_LT_X.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['LT_X']))   
        self.pushButton_LT_Y.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['LT_Y']))     
        self.pushButton_LT_Z.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['LT_Z']))   
        self.pushButton_LT_Ry.clicked.connect(partial(self.update_single_mtr,  self.mtr_dict['LT_Ry']))   


  

###########################
#                                      PLOT PART
###########################

#                                   Initialize the dates to use for selecting the data (defaul go back 6 months)
        self.file_ls = []
        now = QtCore.QDate.currentDate()
        self.dateEdit_start.setDate(now.addMonths(-6))
        self.dateEdit_end.setDate(now)        
        self.since_date = str(self.dateEdit_start.date().year())+'-'+\
                            str(self.dateEdit_start.date().month())+'-'+ str(self.dateEdit_start.date().day())
        self.until_date = str(self.dateEdit_end.date().year())+'-'+\
                            str(self.dateEdit_end.date().month())+'-'+ str(self.dateEdit_end.date().day())
        
#                                  Make a list of scan ID within the time range and populate the data-table
        self.hdrs = list(self.db(since=self.since_date, until=self.until_date, scan_name='scan_1D'))

        self.tableWidget_data.setRowCount(len(self.hdrs))
        for indx,  i in enumerate(self.hdrs): 
#            print(i.start['scan_id'], i.start['plot_Xaxis'], i.start['plot_Yaxis'])
            self.tableWidget_data.setItem(indx, 0,  QTableWidgetItem(str(i.start['scan_id'])))
            self.tableWidget_data.setItem(indx, 1,  QTableWidgetItem(i.start['plot_Xaxis'][0]))
            self.tableWidget_data.setItem(indx, 2,  QTableWidgetItem(i.start['plot_Yaxis'][0]))
        
        self.tableWidget_data.cellClicked.connect(self.scan_selected)
        self.dateEdit_start.dateChanged.connect(self.start_datechanged)
        self.dateEdit_end.dateChanged.connect(self.end_datechanged)

        #self.timer = QTimer()
        #self.timer.setInterval(1000)
        #self.timer.timeout.connect(self.recurring_timer)
        #self.timer.start()

    def end_datechanged(self, qdate):
        self.until_date = str(qdate.year())+'-'+\
                            str(qdate.month())+'-'+ str(qdate.day())
#                                  Make a list of scan ID within the time range and populate the data-table
        self.hdrs = list(self.db(since=self.since_date, until=self.until_date, scan_name='scan_1D'))
        self.tableWidget_data.setRowCount(len(self.hdrs))
        for indx,  i in enumerate(self.hdrs): 
#            print(i.start['scan_id'], i.start['plot_Xaxis'], i.start['plot_Yaxis'])
            self.tableWidget_data.setItem(indx, 0,  QTableWidgetItem(str(i.start['scan_id'])))
            self.tableWidget_data.setItem(indx, 1,  QTableWidgetItem(i.start['plot_Xaxis'][0]))
            self.tableWidget_data.setItem(indx, 2,  QTableWidgetItem(i.start['plot_Yaxis'][0]))




    def start_datechanged(self, qdate):
        self.since_date = str(qdate.year())+'-'+\
                            str(qdate.month())+'-'+ str(qdate.day())
#                                  Make a list of scan ID within the time range and populate the data-table
        self.hdrs = list(self.db(since=self.since_date, until=self.until_date, scan_name='scan_1D'))
        self.tableWidget_data.setRowCount(len(self.hdrs))
        for indx,  i in enumerate(self.hdrs): 
#            print(i.start['scan_id'], i.start['plot_Xaxis'], i.start['plot_Yaxis'])
            self.tableWidget_data.setItem(indx, 0,  QTableWidgetItem(str(i.start['scan_id'])))
            self.tableWidget_data.setItem(indx, 1,  QTableWidgetItem(i.start['plot_Xaxis'][0]))
            self.tableWidget_data.setItem(indx, 2,  QTableWidgetItem(i.start['plot_Yaxis'][0]))
            
            
            
    def update_single_mtr(self,  mtr_dev):
        dlg_win = QtWidgets.QMainWindow(self)
        ui = Ui_dlg_win()
        ui.setupUi(dlg_win)
        #        ui.doubleSpinBox_step.setValue(1.0)         
        ui.doubleSpinBox_step.setValue(1.0)         
#        print('from dialog, {}'.format(ui.doubleSpinBox_step.value()) )
#        print(step)
        ui.pushButton_dlg_plus.clicked.connect(lambda : self.twick(ui.doubleSpinBox_step.value(),   mtr_dev) )
        ui.pushButton_dlg_minus.clicked.connect(lambda : self.twick(-ui.doubleSpinBox_step.value(),   mtr_dev) )        
        ui.doubleSpinBox_step.valueChanged[float].connect(self.set_step)
 
        dlg_win.show()    



    def set_step(self, val):
        emitter = self.sender()
        value = emitter.value()
        print(emitter,  value)
        

    def twick(self,  new_val,  mtr_dev):
#           put here the command to move the motor
            print(mtr_dev.position)
            print('New value: {}'.format(mtr_dev.position+new_val))
            print('on device: {}'.format(mtr_dev.name))
        
        
        
    def scan_selected(self):
        '''used inside plot
        '''        
        # keep a list of selected item rows
        sc_ls_rows =  [i.row() for i in self.tableWidget_data.selectedItems()]
        # initialize the plot window
        axes = self.widget_plt.canvas.ax
        axes.cla()
        
        if len(sc_ls_rows) == 1:
            sc = self.tableWidget_data.item(sc_ls_rows[0], 0).text()
    #                   bsln is a panda data frame that contain the status at the begining ([1]) and at the end ([2]) of the scan; extract with keys like ['epu105_gap']
            baseline = self.db[int(sc)].table('baseline') 
            self.initialize_plt_bsln(baseline)

        self.file_ls = [self.tableWidget_data.item(rr, 0).text() for rr in sc_ls_rows]
#        axes.cla()
        for scn in self.file_ls:
            data = self.db[int(scn)]
            x_lbl,  y_lbl = data.start['plot_Xaxis'],  data.start['plot_Yaxis']
            data_tbl = data.table(fields = x_lbl + y_lbl)
            data_tbl.plot(x=x_lbl[0], y= y_lbl[0],  label = scn,  ax=axes) 
        self.widget_plt.canvas.draw()    


    def initialize_plt_bsln(self,  bsln):
                self.lineEdit_plt_Iring.setText( str("{:.2f}".format(bsln['BeamSource_Current'][1]) ) )
                self.lineEdit_plt_Source_X.setText( str("{:.4f}".format(bsln['BeamSource_Xoffset'][1]) ) )
                self.lineEdit_plt_Source_Y.setText( str("{:.4f}".format(bsln['BeamSource_Yoffset'][1]) ) )
                self.lineEdit_plt_Source_Xangle.setText( str("{:.4f}".format(bsln['BeamSource_Xangle'][1]) ) )
                self.lineEdit_plt_Source_Yangle.setText( str("{:.4f}".format(bsln['BeamSource_Yangle'][1]) ) )


                self.lineEdit_plt_EPU57_gap.setText( str("{:.2f}".format(bsln['EPU57_gap'][1]) ) )
                self.lineEdit_plt_EPU57_phase.setText( str("{:.2f}".format(bsln['EPU57_phase'][1]) ) )
                self.lineEdit_plt_EPU105_gap.setText( str("{:.2f}".format(bsln['EPU105_gap'][1]) ) )
                self.lineEdit_plt_EPU105_phase.setText( str("{:.2f}".format(bsln['EPU105_phase'][1]) ) )
                
                feh_gap = bsln['FEslit_outboard'][1]   - bsln['FEslit_inboard'][1] 
                feh_ctr = bsln['FEslit_inboard'][1] +0.5*feh_gap
                self.lineEdit_plt_FE_Hgap.setText( str("{:.2f}".format(feh_gap )))
                self.lineEdit_plt_FE_Hctr.setText(  str("{:.2f}".format(feh_ctr ))) 
                fev_gap = bsln['FEslit_top'][1]   - bsln['FEslit_bottom'][1] 
                fev_ctr = bsln['FEslit_bottom'][1] +0.5*feh_gap
                self.lineEdit_plt_FE_Vgap.setText( str("{:.2f}".format(fev_gap )))
                self.lineEdit_plt_FE_Vctr.setText(  str("{:.2f}".format(fev_ctr ))) 

                self.lineEdit_plt_M1_x.setText(  str("{:.4f}".format(bsln['M1_X'][1]))) 
                self.lineEdit_plt_M1_Ry.setText(  str("{:.4f}".format(bsln['M1_Ry'][1]))) 
                self.lineEdit_plt_M1_Rz.setText(  str("{:.4f}".format(bsln['M1_Rz'][1])))      
                
                self.lineEdit_plt_PGM_Energy.setText(  str("{:.2f}".format(bsln['PGM_Energy'][1])))
                self.lineEdit_plt_PGM_c.setText(  str("{:.2f}".format(bsln['PGM_Focus_Const'][1])))        
                self.lineEdit_plt_PGM_grt.setText(  str("{:.2f}".format(bsln['PGM_Grating_Trans'][1])))        

#                self.lineEdit_plt_UM3_Y.setText(str("{:.4f}".format(bsln['M3Udiag_trans'][1])))

                self.lineEdit_plt_M3_x.setText(  str("{:.4f}".format(bsln['M3_X'][1]))) 
                self.lineEdit_plt_M3_y.setText(  str("{:.4f}".format(bsln['M3_Y'][1]))) 
                self.lineEdit_plt_M3_Ry.setText(  str("{:.4f}".format(bsln['M3_Ry'][1]))) 
                self.lineEdit_plt_M3_Rz.setText(  str("{:.4f}".format(bsln['M3_Rz'][1]))) 

                self.lineEdit_plt_ESA_V.setText(  str("{:.0f}".format(round(bsln['ExitSlitA_v_gap'][1])))) 
                self.lineEdit_plt_ESA_H.setText(  str("{:.0f}".format(round(bsln['ExitSlitA_h_gap'][1])))) 
                self.lineEdit_plt_ESB_V.setText(  str("{:.0f}".format(round(bsln['ExitSlitB_v_gap'][1])))) 
                self.lineEdit_plt_ESB_H.setText(  str("{:.0f}".format(round(bsln['ExitSlitB_h_gap'][1])))) 

#                self.lineEdit_plt_DES_Y.setText(str("{:.4f}".format(bsln['BTA2diag.trans'][1])))

                
                self.lineEdit_plt_KBH_X.setText(  str("{:.4f}".format(bsln['M4A_HFM_X'][1]))) 
                self.lineEdit_plt_KBH_Z.setText(  str("{:.4f}".format(bsln['M4A_HFM_Z'][1]))) 
#              self.lineEdit_plt_KBH_Ry.setText(  str("{:.4f}".format(bsln['M4A_HFM_Ry'][1]))) 

                self.lineEdit_plt_KBV_Y.setText(  str("{:.4f}".format(bsln['M4A_VFM_Y'][1]))) 
                self.lineEdit_plt_KBV_Z.setText(  str("{:.4f}".format(bsln['M4A_VFM_Z'][1]))) 
#               self.lineEdit_plt_KBV_Rx.setText(  str("{:.4f}".format(bsln['M4A_VFM_Rx'][1]))) 
        
        
        
        
        
    def start_scan(self):
        self.func_scan()

    def abort(self):
        self.RE.abort()

    def get_detector_by_name(self, name):
        for det in self.detectors:
            if det.name==name:
                return det
        return None

    def hint_channel(self, det, ch):
        for i in range(1,5):
            getattr(det, "current" + str(i)).mean_value.kind = "normal"
        getattr(det, "current" + ch).mean_value.kind = "hinted"

    def func_scan(self):
        m =  self.comboBox_motor.currentText()
        m1 =  self.comboBox_motor_2.currentText()
            
        scn_nm_ls = [i.__name__ for i in  self.scan_esm]
        idx_sc =  scn_nm_ls.index(self.comboBox_scan.currentText())
            
        if self.comboBox_scan.currentText() == 'scan_1D':         ### only one motor ###
            #self.print_summary(self.scan_esm[idx_sc](\
            #                                                                self.comboBox_detector.currentText()+'@'+self.comboBox_ch.currentText(),\
            #                                                                self.mtr_dict[m],  float(self.lineEdit_start.text()), float(self.lineEdit_stop.text()), float(self.lineEdit_step.text()) ))
            plan = self.scan_esm[idx_sc](\
                                                                            self.comboBox_detector.currentText()+'@'+self.comboBox_ch.currentText(),\
                                                                            self.mtr_dict[m],  float(self.lineEdit_start.text()), float(self.lineEdit_stop.text()), float(self.lineEdit_step.text()) )
            params = [plan]

        elif self.comboBox_scan.currentText() == 'count':         ### no motor ###
            num = int(self.lineEdit_stop.text()) - int(self.lineEdit_start.text())
            det_name = self.comboBox_detector.currentText()
            channel = self.comboBox_ch.currentText()
            det = self.get_detector_by_name(det_name)
            self.hint_channel(det, channel)
            plan = self.count([det], num=num)
            params = [plan]
        else:                                                                                   ### two motors ###
            #self.print_summary(self.scan_esm[idx_sc](\
            #                                 self.comboBox_detector.currentText()+'@'+self.comboBox_ch.currentText(),\
            #                                 self.mtr_dict[m],  float(self.lineEdit_start.text()), float(self.lineEdit_stop.text()), float(self.lineEdit_step.text()) ,\

            #                                 self.mtr_dict[m1],  float(self.lineEdit_start_2.text()), float(self.lineEdit_stop_2.text()), float(self.lineEdit_step_2.text()) ))
            plan = self.scan_esm[idx_sc](\
                                             self.comboBox_detector.currentText()+'@'+self.comboBox_ch.currentText(),\
                                             self.mtr_dict[m],  float(self.lineEdit_start.text()), float(self.lineEdit_stop.text()), float(self.lineEdit_step.text()) ,\

                                             self.mtr_dict[m1],  float(self.lineEdit_start_2.text()), float(self.lineEdit_stop_2.text()), float(self.lineEdit_step_2.text()) )
            params = [plan]

        if self.checkBox_re.isChecked():
            func = self.RE
        else:
            func = self.print_summary

        #print(dir(self.checkBox_re))
        Worker.signals.trigger.emit(func, params)

    def move_PGM(self):
        worker = Worker(self.func_PGM)
        self.threadpool.start(worker)


    def func_PGM(self):
        epu =  self.comboBox_Eph_EPU.currentText()
        branch =  self.comboBox_Eph_Branch.currentText()
        lp =  self.comboBox_Eph_LP.currentText()        
        grt =  self.comboBox_Eph_GRT.currentText()    
        energy =  self.lineEdit_Eph_Energy.text()    
#        print(self.Eph.Range)
        print(epu,  branch,  lp,  grt,  energy)
        
        self.print_summary(self.Eph.move_to( float (energy),  grating = grt,  EPU=epu,  LP=lp,  branch = branch))

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
        self.lineEdit_Iring.setText( str("{:.2f}".format(self.BeamSource.Current.value)) )
        self.lineEdit_Source_X.setText( str("{:.4f}".format(self.BeamSource.Xoffset.value)) )
        self.lineEdit_Source_Y.setText( str("{:.4f}".format(self.BeamSource.Yoffset.value)) )
        self.lineEdit_Source_Xangle.setText( str("{:.4f}".format(self.BeamSource.Xangle.value)) )
        self.lineEdit_Source_Yangle.setText( str("{:.4f}".format(self.BeamSource.Xangle.value)) )
        
        for i in range(len(self.motors)):             
            self.mtr_status.update({self.motors[i].name:  self.motors[i].position})        
                                                            # populate the bmln status widgets
        self.lineEdit_EPU57_gap.setText( str("{:.2f}".format(self.mtr_status['EPU57_gap'])) )
        self.lineEdit_EPU57_phase.setText(str("{:.2f}".format(self.mtr_status['EPU57_phase'])) )
        self.lineEdit_EPU105_gap.setText( str("{:.2f}".format(self.mtr_status['EPU105_gap'])) )
        self.lineEdit_EPU105_phase.setText(  str("{:.2f}".format(self.mtr_status['EPU105_phase'])) )
        self.lineEdit_FE_Hgap.setText( str("{:.2f}".format(self.mtr_status['FEslit_h_gap'])))
        self.lineEdit_FE_Hctr.setText(  str("{:.2f}".format(self.mtr_status['FEslit_h_center']))) 
        self.lineEdit_FE_Vgap.setText( str("{:.2f}".format(self.mtr_status['FEslit_v_gap'])))
        self.lineEdit_FE_Vctr.setText(  str("{:.2f}".format(self.mtr_status['FEslit_v_center']))) 
        self.lineEdit_M1_x.setText(  str("{:.4f}".format(self.mtr_status['M1_X']))) 
        self.lineEdit_M1_Ry.setText(  str("{:.4f}".format(self.mtr_status['M1_Ry']))) 
        self.lineEdit_M1_Rz.setText(  str("{:.4f}".format(self.mtr_status['M1_Rz'])))
        
        self.lineEdit_PGM_Energy.setText(  str("{:.2f}".format(self.mtr_status['PGM_Energy'])))
        self.lineEdit_PGM_c.setText(  str("{:.2f}".format(self.mtr_status['PGM_Focus_Const'])))        
        self.lineEdit_PGM_grt.setText(  str("{:.2f}".format(self.mtr_status['PGM_Grating_Trans'])))        
 
        self.lineEdit_UM3_Y.setText(  str("{:.2f}".format(self.mtr_status['M3Udiag_trans']))) 

        self.lineEdit_M3_x.setText(  str("{:.4f}".format(self.mtr_status['M3_X']))) 
        self.lineEdit_M3_y.setText(  str("{:.4f}".format(self.mtr_status['M3_Y']))) 
        self.lineEdit_M3_Ry.setText(  str("{:.4f}".format(self.mtr_status['M3_Ry']))) 
        self.lineEdit_M3_Rz.setText(  str("{:.4f}".format(self.mtr_status['M3_Rz']))) 

        self.lineEdit_ESA_V.setText(  str("{:d}".format(round(self.mtr_status['ExitSlitA_v_gap'])))) 
        self.lineEdit_ESA_H.setText(  str("{:d}".format(round(self.mtr_status['ExitSlitA_h_gap'])))) 
        self.lineEdit_ESB_V.setText(  str("{:d}".format(round(self.mtr_status['ExitSlitB_v_gap']))))
        self.lineEdit_ESB_H.setText(  str("{:d}".format(round(self.mtr_status['ExitSlitB_h_gap']))))

        self.lineEdit_DES_Y.setText(  str("{:.4f}".format(self.mtr_status['BTA2diag_trans']))) 

        self.lineEdit_KBH_X.setText(  str("{:.4f}".format(self.mtr_status['M4A_HFM_X']))) 
        self.lineEdit_KBH_Z.setText(  str("{:.4f}".format(self.mtr_status['M4A_HFM_Z']))) 
#        self.lineEdit_KBH_Ry.setText(  str("{:.4f}".format(self.mtr_status['M4A_HFM_Ry']))) 

        self.lineEdit_KBV_Y.setText(  str("{:.4f}".format(self.mtr_status['M4A_VFM_Y']))) 
        self.lineEdit_KBV_Z.setText(  str("{:.4f}".format(self.mtr_status['M4A_VFM_Z']))) 
        
        self.lineEdit_LT_X.setText(  str("{:.4f}".format(self.mtr_status['LT_X']))) 
        self.lineEdit_LT_Y.setText(  str("{:.4f}".format(self.mtr_status['LT_Y']))) 
        self.lineEdit_LT_Z.setText(  str("{:.4f}".format(self.mtr_status['LT_Z']))) 
        self.lineEdit_LT_Ry.setText(  str("{:.4f}".format(self.mtr_status['LT_Ry']))) 



def main (db=None,  RE=None, print_summary=None, scan_time=None,  scan_esm=None, motors = None, detectors=None,  Beamline = None,  BeamSource=None,  Eph=None):

    RE.context_managers=[]
    app = QtWidgets.QApplication(sys.argv)
    wd = MainWindow(db=db,  RE=RE, print_summary=print_summary, scan_time=scan_time,  scan_esm=scan_esm, motors = motors, detectors=detectors, Beamline=Beamline, \
                                        BeamSource=BeamSource,  Eph=Eph)   

    
    worker = Worker(wd.show)

    def call_func(func, params):
        func(*params)

    worker.signals.trigger.connect(call_func)

    threadpool = QtCore.QThreadPool()
    threadpool.start(worker)
    #wd.show()
    #sys.exit(app.exec_())
    app.exec_()

def get_detector_by_name(name, detectors):
    for det in detectors:
        if det.name==name:
            return det
    return None



#def main (db=None,  RE=None, print_summary=None, scan_time=None,  scan_esm=None, motors = None, detectors=None,  Beamline = None,  BeamSource=None,  Eph=None):
#    RE.context_managers=[]
#    main2(db,RE,print_summary,scan_time,scan_esm,motors,detectors,Beamline,BeamSource,Eph)



#if __name__ == '__main__':
#    main()
    
#  ['photon_energy', "grating='800'", "branch='A'", "EPU='57'", "LP='LH'", "c='constant'", "shutter='close'"]
