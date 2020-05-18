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
from matplotlib import cm
from zipfile import ZipFile

import arpes_dlg as dlg

def flatten(lst):
    """Completely flatten an arbitrarily-deep list"""
    return list(_flatten(lst))
#
def _flatten(lst):
    """Generator for flattening arbitrarily-deep lists"""
    for item in lst:
        if isinstance(item, (list, tuple)):
            yield from _flatten(item)
        elif item not in (None, "", b''):
            yield item
#
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
#
def fill_blanks(lst):
    """Convert a list (or tuple) to a 2 element tuple"""
    try:
        return (lst[0], from_repr(lst[1]))
    except IndexError:
        return (lst[0], "")
#
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
#
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
#
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
#
def read_bin_multi_region(base_path, fl_nm, rg=0):
    #    import os

    path_to_file = os.path.join(base_path, fl_nm)
    rgs_ls, rgs_info_ls = loader(fl_nm, base_path)  # unzip and create .dat files and return the list of regions
    #### READ INI FILE for the region (default is rg = 0)
    path_to_file = os.path.join(base_path, fl_nm, rgs_ls[rg] + '.ini')
    fd = open(path_to_file, 'r')
    lst = fd.readlines()  # python list: every element is a line
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

    #### READ-IN from junk1.dat the data and for a 3D-matrix to return

    #    path_to_file = os.path.join(base_path, fl_nm,rgs_ls[rg]+'.dat')
    #    fd = open(path_to_file , 'r')
    #    data = fd.readlines()                                 #python list: every element is a line
    #    I = np.empty([d, h, w])
    #   for j in range(d):
    #      for k in range(h):
    #       I[j,k,:]=data[j*h+k].split()

    path_to_file = os.path.join(base_path, fl_nm, rgs_ls[rg] + '.bin')
    fh = open(path_to_file, 'rb')
    data = np.fromfile(fh, np.float32)
    if data.shape[0] != d*h*w:
        print('d*h*w = {}'.format(d*h*w))
        print('shape = {}'.format(data.shape[0]))
#        pad = np.zeros(d*h*w-data.shape)
        data = np.pad(data,(d*h*w-data.shape[0]))
        print('shape padded = {}'.format(data.shape[0]))
    data.shape = (d, h, w)
    data = np.transpose(data, axes=(2, 1, 0))   #transposed for use in pg.Imageview


#    return w, w_of, w_dt, h, h_of, h_dt, d, d_of, d_dt, data, rgs_ls
    return  {"filename": path_to_file, "dimensions": data.shape,\
             "w":w, "w_of":w_of, "w_dt":w_dt,\
             "h":h, "h_of":h_of, "h_dt":h_dt,\
             "d":d, "d_of":d_of, "d_dt":d_dt,\
             "data":data, "rgs_ls": rgs_ls}
