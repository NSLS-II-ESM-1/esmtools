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


ui_path = pkg_resources.resource_filename('esmtools', 'ui/elio_gui.ui')

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

    def __init__(self, RE=None, motors = None,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.RE = RE
        self.motors = motors
        self.pushButton_startscan.clicked.connect(self.start_scan)
        self.timer_update_time = QtCore.QTimer(self)
        self.timer_update_time.setInterval(500)
        self.timer_update_time.timeout.connect(self.update_status)
        self.timer_update_time.start()


    def start_scan(self):
 #       print("print_summary(scan_1D(qem07@01, PGM.Energy, 20, 25,1))")
        self.RE(scan([qem07], num=1))
        #new_energy = float(self.lineEdit_energy.text())
        #print(str(new_energy))
        #self.RE(bps.mv(self.motors[0], new_energy))

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


