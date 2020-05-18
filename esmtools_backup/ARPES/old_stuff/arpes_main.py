import os
import glob
import platform
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import numpy as np
import pyqtgraph as pg
from igor.binarywave import load as loadibw

import arpes_dlg as dlg

def flatten(lst):
    """Completely flatten an arbitrarily-deep list"""
    return list(_flatten(lst))

def _flatten(lst):
    """Generator for flattening arbitrarily-deep lists"""
    for item in lst:
        if isinstance(item, (list, tuple)):
            yield from _flatten(item)
        elif item not in (None, "", b''):
            yield item


def from_repr(s):
    """Get an int or float from its representation as a string"""
    # Strip any outside whitespace
    s = s.strip()
    # "NaN" and "inf" can be converted to floats, but we don't want this
    # because it breaks in Mathematica!
    if s[1:].isalpha():  # [1:] removes any sign
        rep = s
    else:
        try:
            rep = int(s)
        except ValueError:
            try:
                rep = float(s)
            except ValueError:
                rep = s
    return rep



def fill_blanks(lst):
    """Convert a list (or tuple) to a 2 element tuple"""
    try:
        return (lst[0], from_repr(lst[1]))
    except IndexError:
        return (lst[0], "")


def process_notes(notes):
    """Splits a byte string into an dict"""
    # Decode to UTF-8, split at carriage-return, and strip whitespace
    note_list = list(map(str.strip, notes.decode(errors='ignore').split("\r")))
    note_dict = dict(map(fill_blanks, [p.split(":") for p in note_list]))

    # Remove the empty string key if it exists
    try:
        del note_dict[""]
    except KeyError:
        pass
    return note_dict




def ibw2dict(filename):
    """Extract the contents of an *ibw to a dict"""
    data = loadibw(filename)
    wave = data['wave']
    wave_h = wave['wave_header']

    dim = wave_h['nDim'][0:2]
    scale_values = wave_h['sfA'][0:2]
    start_values = wave_h['sfB'][0:2]
    end_values = start_values + np.multiply(dim,scale_values)

    # Get the labels and tidy them up into a list
    labels = list(map(bytes.decode,
                      flatten(wave['labels'])))

    # Get the notes and process them into a dict
    notes = process_notes(wave['note'])

    # Get the data numpy array and convert to a simple list and then to a numpy array properly shaped
    Data = np.nan_to_num(wave['wData']).tolist()
    wData = np.array(Data).reshape(dim[0],dim[1])
    E_axis = np.linspace(start_values[0],end_values[0], dim[0])
    A_axis = np.linspace(start_values[1],end_values[1], dim[1])
    # Get the filename from the file - warn if it differs
    fname = wave['wave_header']['bname'].decode()
    input_fname = os.path.splitext(os.path.basename(filename))[0]
    if input_fname != fname:
        print("Warning: stored filename differs from input file name")
        print("Input filename: {}".format(input_fname))
        print("Stored filename: {}".format(str(fname) + " (.ibw)"))

    return {"filename": fname, "dimensions": dim, "E_axis":E_axis , "A_axis":A_axis , "labels": labels, "notes": notes, "data": wData}









class MainWindow(QMainWindow):

    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)


        self.setWindowTitle('controls')
        self.resize(950,950)

        self.twoD_list = QListWidget()
        self.threeD_list = QListWidget()
        self.mul_chk = QCheckBox()
        self.mul_lbl = QLabel("Multiple")
        self.mul_lbl.setBuddy(self.mul_chk)

        self.current_dir = None
        self.data_dict = None

        optionLayout = QHBoxLayout()
        optionLayout.addStretch()
        optionLayout.addWidget((self.mul_lbl))
        optionLayout.addWidget(self.mul_chk)
        grid = QGridLayout()
        grid.addWidget(self.twoD_list, 0, 0)
        grid.addWidget(self.threeD_list, 0, 1)
        grid.addLayout(optionLayout, 1, 0, 1, 2)

        central_wdg = QWidget()
        central_wdg.setLayout(grid)
        self.setCentralWidget(central_wdg)


        plt_DockWidget =QDockWidget('plot', self)
        plt_DockWidget.setObjectName(('plot window'))
        plt_DockWidget.setAllowedAreas(Qt.RightDockWidgetArea)

        self.plt_i = pg.PlotItem(labels={'bottom': ('slits', 'degrees'), 'left': ('Kin. Energy', 'eV')})
        self.plt_iv = pg.ImageView(view=self.plt_i)
        plt_DockWidget.setWidget(self.plt_iv)
        self.addDockWidget(Qt.RightDockWidgetArea,plt_DockWidget)



        toolbar = QToolBar()
        self.addToolBar(toolbar)


        actionLoadDir = QAction(QIcon("/home2/xf21id1/Repos/esmtools/esmtools/icons/address-book--plus.png"), '&Load', self)
        actionLoadDir.triggered.connect(self.dir_open)
        toolbar.addAction(actionLoadDir)

        self.twoD_list.itemClicked.connect(self.get_data)




    def dir_open(self):
        self.current_dir = dlg.File_dlg.openDirNameDialog(self)
        files_ls = glob.glob(self.current_dir+'/*.ibw')
        zip_ls = glob.glob(self.current_dir+'/*.zip')
        print(zip_ls)
        fls = [f[len(self.current_dir)+1:] for f in files_ls]
        zip = [f[len(self.current_dir)+1:] for f in zip_ls]
        self.twoD_list.addItems(fls)
        self.threeD_list.addItems(zip)
#        self.lineEdit_dir.setText(os.path.dirname(self.fl_name))
#        self.lineEdit_file.setText(os.path.basename(self.fl_name))

    def get_data(self, s):
        file_name = s.text()
        self.data_dict = ibw2dict(self.current_dir+'/'+file_name)

        print(self.data_dict['filename'])
#            print(self.data_dict['labels'])
#            print(self.data_dict['dimensions'])
        print(len(self.data_dict['E_axis']))
        print(len(self.data_dict['A_axis']))
        e_sc = self.data_dict['E_axis'][1]-self.data_dict['E_axis'][0]
        a_sc = self.data_dict['A_axis'][1]-self.data_dict['A_axis'][0]
        print(e_sc, a_sc)
        e_str = self.data_dict['E_axis'][0]
        a_str = self.data_dict['A_axis'][0]
        print(e_str, a_str)
#            print(self.data_dict['data'][:1])
#        self.plt_iv.view = pg.PlotItem(labels={'bottom': ('slits', 'degrees'), 'left': ('Kin. Energy', 'eV')})
        self.plt_i.setRange(xRange=[self.data_dict['E_axis'][0], self.data_dict['E_axis'][-1]], \
                            yRange=[self.data_dict['A_axis'][0], self.data_dict['A_axis'][-1]], update=True, padding = 0)

        self.plt_i.getViewBox().setLimits(xMin= e_str, xMax = self.data_dict['E_axis'][-1],\
                                          yMin=self.data_dict['A_axis'][0], yMax=self.data_dict['A_axis'][-1])
#        self.plt_i.enableAutoRange()
        self.plt_iv.setImage(self.data_dict['data'], pos=[self.data_dict['E_axis'][0], self.data_dict['A_axis'][0]], scale=[e_sc, a_sc])
        self.plt_iv.ui.histogram.hide()
        self.plt_iv.ui.roiBtn.hide()
        self.plt_iv.ui.menuBtn.hide()



def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("NSLS II")
    app.setOrganizationDomain("bnl.gov")
    app.setApplicationName("ARPES_viewer")
    form = MainWindow()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()