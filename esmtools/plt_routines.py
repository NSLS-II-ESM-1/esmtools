
from databroker import get_table, get_fields, get_events, get_images
from databroker import Broker

#%matplotlib nbagg
#%matplotlib inline
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import datetime
import time

from scipy.interpolate import interp1d
from scipy.special import wofz


db = Broker.named('arpes')


#########################################
####### Utility Routine #################
#########################################



def channel_list_unpack(DETS_str):
        ''' 
        This function is used to unpack the detector input string and return a list of channels

        This function is used to unpack the detector list string used as an input into our "scans" 
        and "notebook" routines and returns a list of channels that it relates to for plotting and/
        or data analysis.

        PARAMETERS
        ----------
        
        DETS_str : str
            The input string that is to be "unpacked" into a channel list. This needs to have the 
                format definitions: 
                    - DETX is the name of 'Xth' detector.
                    - every '@' symbol defines a new channel number for the preceeding detector.
                    - ChX is the channel number of the 'Xth' channel.
                    -    if ChX is 0 then it returns no channels for this detector.
                    -    if ChX is -1 then it returns all channels for this detector.
                    - every '-' symbol defines a new value for the preceeding channel number.
                    - ValX is the name of the 'Xth' value, and can be 'total', 'max' or 'min'.

                format1:  'DET1@Ch1-Val1-Val2-...@Ch2-Val1-...., DET2@Ch1-Val1-...@.... ,....'
                    If no '@' is present for a detector then it reverts to the default of channel 1.
                    If no '-' is present it reverts to the default 'Total'.

                format2: 'DET1,    DET2    ,......,   @Ch1-val1-val2-...@Ch2-val2-...@...'
                    This returns The channels and values defined by the last list entry for all 
                    detectors.
                    If no '-' is present it reverts to the default 'Total'.               


                            
 
        name_list : list, output
            The output list of channels.
        '''
        name_list=[]
        #define the empty output list

        #split the detectors str into a list of detector strs
        DET_list=DETS_str.split(',')

        # check if format 1 or format 2 is being used.

        if  DET_list[-1].startswith('@'):
            #If format 2 is used
            Channel_list=DET_list[-1][1:].split('@')    
            DET_list=DET_list[:-1]
            Format = 2
        else:
            Format = 1
            
        for i,DET_str in enumerate(DET_list):
            DET=DET_str.partition('@')[0]
            if Format == 1:
            #If format 1 is used
                Channel_list=DET_str.partition('@')[2].split('@')
   
            if len(Channel_list[0]) == 0:
                #if no channels are defined for this detector.
                name_list.append(format_channel_name(DET,1,Value='total'))

            elif '-1' in Channel_list:
                #if all channels are defined. for this detector.
                name_list+= format_channel_name(DET,-1).split(',')
                    
            elif '0' not in Channel_list:
                #if some channels are defined for this detector. 
                for j,Channel_str in enumerate(Channel_list):
                    Channel=Channel_str.partition('-')[0]
                    Value_list=Channel_str.partition('-')[2].split('-')

                    if len(Value_list[0]) == 0:
                        #if no valuess are defined for this detector.
                        name_list.append(format_channel_name(DET,Channel))
                    else:
                        #if there are values listed for this channel.
                        for k,Value in enumerate(Value_list):
                            name_list.append(format_channel_name(DET,Channel,Value))
                            


        return name_list
    
    
def format_channel_name(DET,Channel,Value='total'):
        ''' 
        This function formats the channel name for a given detector type.
        
        This function takes in the detctor name, channel number, and an optional channel value
        and returns a formated channel name string for this type of detector. If 'Channel' is -1 
        then it returns a string containg all the possible channel names for the detector, 
        seperated by commas.

        PARAMETERS
        ----------
        DET: str
            The name of the detector for which the channel is to be formatted        

        Channel: integer
            The channel number for the  channel to be formatted

        Value: str,optional
            The optional "value" for the channel number. 

        channel_name : str
            The output string that is the formatted channel name.
        '''


        if 'qem' in DET.lower():
            #if the detector is a qem.
            if Channel == -1:
                channel_name=''
                for i in range(1,5):
                    if i > 1: channel_name+=','
                    channel_name+=DET+'_current'+str(i)+'_mean_value'

            else:        
                channel_name=DET+'_current'+str(Channel)+'_mean_value'
            
        elif 'cam' in DET.lower():
            #if the detctor is a camera.
            if Channel == -1:
                channel_name=''
                for i in range(1,5):
                    if i > 1: channel_name+=','
                    channel_name+=DET+'_stats'+str(i)+'_total,'
                    channel_name+=DET+'_stats'+str(i)+'_max_value,'
                    channel_name+=DET+'_stats'+str(i)+'_min_value'
            else:
                if 'max' in Value or 'min' in Value:
                    Value+='_value'
                channel_name=DET+'_stats'+str(Channel)+'_'+Value

        else:
            #If the detcor type has not been determined.
            raise ValueError("Detector type not recognised, name must contain 'qem' or 'cam'.")

        return channel_name
    

        
def scan_info(scan_id_list,Baseline=False,Detector=False):
    '''
    This routine is used to return a formatted string containing the relevant information from the
    for the scan defined by scan_id.

    This scan looks up metadata and prints out some relevant info from this, it can also optionally
    include the baseline state stream from scan_id and removes everything but the readback
    values. It then returns a formatted string containing these values to make finding the information
    required easier.

    Parameters
    ----------
    scan_id_list : number
        This is a list of the uid, scan id or previous scan number (-1,-2 etc.) used to extract the
        data from the databroker.

     Baseline : Boolean, optional
            Used to include baseline readings (i.e. data recorded that is not directly part of the
            scan). to include baseline data use Baseline=True)

     detector : Boolean, optional
            Used to include detectro configuration readings (i.e. detector settings that is not directly
            part ofset prior to the scan). to include detector settings use Baseline=True)

     f_string : str
         Possible output string for formatting.

    '''

    #define the output string
    f_string=''

    for scan_id in scan_id_list:
        #Load up the baseline data stream and extract out the list of keys that are not setpoints or
        #done indicators
        data = db[scan_id].table(stream_name='baseline')
        key_list=[key for key in data.keys() if '_setpoint' not in key and '_done' not in key ]

        #Extract out a list of devices from the list of keys.
        temp_list=key_list
        if 'time' in temp_list: temp_list.remove('time')
        device_dict={}
        exit_val=0

        #continue looping over the list of remaining axes until none exist.
        while len(temp_list)>0 and exit_val<=200:
            device_name,_,channel = temp_list[0].partition('_')
            axis_list=list(key for key in temp_list if key.startswith(device_name))
            temp_device_dict = {key:data[key] for  key in axis_list}
            device_dict[device_name]=temp_device_dict

            temp_list = list(dev for dev in temp_list if not dev.startswith(device_name) )
            exit_val+=1

        # calculate how long the scan took
        scan_time=(db[scan_id].stop['time']-db[scan_id].start['time'])

        #create the formatted string heading
        f_string+='\n\n************************************************************\n'
        f_string+='Scan id '+str(db[scan_id].start['scan_id'])+' ,  '
        f_string+=datetime.datetime.fromtimestamp(int(db[scan_id].start['time'])).strftime('%Y-%m-%d %H:%M:%S') +'\n'
        f_string+='************************************************************\n\n'

        f_string+='***** Scan Data *****\n\n'
        f_string+='Scan type : '+str(db[scan_id].start['scan_type'])
        f_string+=' , Scan name : '+str(db[scan_id].start['scan_name'])
        f_string+=' , Plan name : '+str(db[scan_id].start['plan_name'])+'\n'
        f_string+='Detector(s) : '+str(db[scan_id].start['detectors'])+'\n'
        f_string+='num_points : '+str(db[scan_id].start['num_points'])
        f_string+=', scan time : '+time.strftime("%H:%M:%S", time.gmtime(scan_time))
        f_string+=', time/point : '+time.strftime("%H:%M:%S", time.gmtime(scan_time/db[scan_id].start['num_points']))+'\n'

        if db[scan_id].start['scan_name'].endswith('_2D'):
            f_string+='Plotted channel(s) : '+str(db[scan_id].start['plot_Zaxis'])+'\n'
            f_string+='X axis : '+str(db[scan_id].start['plot_Xaxis'])+'( '
            f_string+= str(db[scan_id].start['X_start'])+' , '+str(db[scan_id].start['X_stop'])
            f_string+=' , '+str(db[scan_id].start['X_delta'])+' )'+'\n'
            f_string+='Y axis : '+str(db[scan_id].start['plot_Yaxis'])+' ( '
            f_string+= str(db[scan_id].start['Y_start'])+' , '+str(db[scan_id].start['Y_stop'])
            f_string+=' , '+str(db[scan_id].start['Y_delta'])+' )'+'\n\n'
        elif db[scan_id].start['scan_name'].endswith('_1D'):
            f_string+='Plotted channel(s) : '+str(db[scan_id].start['plot_Yaxis'])+'\n'
            f_string+='X axis : '+str(db[scan_id].start['plot_Xaxis'])+' ( '
            f_string+= str(db[scan_id].start['plan_args']['args'][-2])+' , '
            f_string+= str(db[scan_id].start['plan_args']['args'][-1])+' , '
            f_string+= str(db[scan_id].start['delta'])+' ) '+'\n\n'


        if Detector is True:
            #If the user asked for detector info
            dets=db[scan_id].start['detectors']
            f_string+='***** Detector Settings *****\n\n'
            hdr=db[scan_id]

            for det in dets:
                f_string+='    '+det+':\n'
                keys=list(hdr.config_data(det)['primary'][0].keys())
                #extract out the list of configuration items for this detector and step through them.
                for key in keys:
                    set_list = key.split('_')
                    del set_list[0]
                    f_string+='\t '
                    n_string=''
                    for set in set_list:
                            n_string+=set+' '
                    f_string+=n_string.ljust(25)
                    f_string+=':\t '+ str(hdr.config_data(det)['primary'][0][key])+'\n'

            f_string+='\n\n'


        if Baseline is True:
            f_string+='***** Baseline Readings *****\n\n'
            #step through each of the 'devices' and print out the axes associated with it
            device_list=list(device_dict.keys())
            device_list.sort()

            for dev in device_list:
                f_string+='    '+dev+':\n'
                axis_dict = device_dict[dev]
                for axis in axis_dict:
                    f_string+='\t '+axis.ljust(30)+':  start = %f\t , end = %f\n ' % (axis_dict[axis][1],axis_dict[axis][2])

                f_string+='\n'



    print (f_string)

    


def csv_conv(scan_id, sav_dir = '/home/vescovo/Downloads/'):
    """
    Convert qem data into csv files.
    
    Parameters
    ------------------------------
    scan_id: a 'list' of id-numbers or (start, stop) tuple of integers for consecutive runs
    sav-dir: directory where to save files with name 'element_of_scan_id.csv'
  
    """
    
    if type(scan_id) == str:
                            # transform the 'string' into a list
        (start, stop)=scan_id.split(',')
        scan_id = [i for i in range(eval(start),eval(stop)+1)]
        
    for ids in scan_id:
        x_list = db[ids].start['plot_Xaxis']  # list of name(s) of x-axis that were plot on the screen
        y_list = db[ids].start['plot_Yaxis']  # list of name(s) of y-axis that were plot on the screen
        scan = db[ids].table(fields=x_list+y_list)
        scan.to_csv(sav_dir+str(ids)+'.csv', index=False, columns=x_list+y_list)



def read_in(fl_nmb=''):
    import os

    base_path = "/home/xf21id1/Downloads/"
    filename = fl_nmb
    path_to_file = os.path.join(base_path, filename)
    fd = open(path_to_file , 'r')
    lst = fd.readlines()      #python list: every element is a line
    X = np.linspace(float((lst[1].split('#'))[1].split('#')[0]),
                    float((lst[2].split('#'))[1].split('#')[0]),
                    int((lst[3].split('#'))[1].split('#')[0]),
                    endpoint=True)
    
    Y = np.array([float(i) for i in lst[10:]])
    return X, Y


def SiQY(ph_en, i):
    ''' Given the photon energy (in eV) and the XUV Si-diode current (in Amp), 
        returns the flux (ph/sec). It uses the QY for a typical XUV Si-diode. 
        Usage: Sic2f(hv(eV), i(A))
    '''
    from decimal import Decimal

    
        # XUV QY data: number of electrons per 1 photons of a given photon energy
    E_eV = [1,1.25,2,2.75,3,4,5,6,7,8,9,10,20,40,60,80,100,120,140,160,180,200,220,240,260,
            280,300,320,340,360,380,400,420,440,460,480,500, 520, 540,560,580,600,620,640,
            740,760,780,800,820,840,860,880,900,920,940,960,980,1000,1200,1400,1600,1800,2000,
            2200,2400,2600,2800, 3000,3200,3400,3600,3800,4000,4200,4400,4600,4800,5000,5200,
            5400,5600,5800,6000]
    
    QY = [0.023, 0.32 ,0.64,0.57,0.49,0.432,0.45,0.5,0.7,1,1.05,1.1,3.25,8.38,12.18,17.85,22.72,
          26.42,31.37,33.5,42.95,50.68,60.61,66.12,71.63,77.13, 82.64,88.15,93.66,99.17,104.68,110.19,
          115.7,121.21,126.72,132.23,137.74,143.25,148.76,154.27,159.78,165.29,170.8,176.31,203.86,209.37, 
          214.88,220.39,225.9,231.41,236.91,242.42,247.94,253.44,258.95,264.46,269.97,275.48,330.58,385.67,
          440.77,495.87,550.96,606.06,661.18,716.35, 771.35,826.45,881.54,936.64,991.74,1046.83,1101.93,
          1157.02,1212.12,1267.22,1322.31,1377.41,1432.51,1487.6,1542.7,1597.8,1652.89]

    Sictof = interp1d(E_eV, QY)
    flux =  (i)/(1.6E-19)/Sictof(ph_en)
    return '%.2E' % Decimal(flux)




######################################
####### Plot Routine #################
######################################


def XY_1(scan_id, x_r=0,x_l=0 ,norm=False):
    """ 
    service routing, called by others;
    read-in a 1D data (scan_id & channel) and return the corresponding X, Y and their labels
    X and Y are panda-structure; can be treated as arrays but start from index 1 instead of 0.
    """

    x_list = db[scan_id].start['plot_Xaxis']  # list of name(s) of x-axis that were plot on the screen
    y_list = db[scan_id].start['plot_Yaxis']  # list of name(s) of y-axis that were plot on the screen
    scan = db[scan_id].table(fields=x_list+y_list)
    X = scan[x_list[0]]  
    Y = scan[y_list[0]]
    
    if norm == True:
        Y = Y - min(Y)
        Y = Y/max(Y)
    N=len(X)
    return X[x_r:N-x_l], Y[x_r:N-x_l], x_list[0], y_list[0]                   






def esm_plt(ids, norm = False, stack = None, ch = None , lw = 2, lb = True, mk = '-'):

    '''
    Plots the data taken by the qems.
    
        esm_plt(ids, norm = False, stack = None, ch = None , lw = 2, lb = True, mk = '-')

    Parameters:
    ----------------------------
        ids = a 'list' of id-numbers or (start, stop) tuple of integers for consecutive runs
        norm = from 0 to 100
        stack = equal offsets
        ch = 1,2,3 or 4 is the current number of the qem
        lw = integer, linewidth
        lb = True/False, print/not print the legend
        mk = '.-' or 'o-' or '*--' etc, etc
    
    '''    
    
    
    if type(ids) == str:
                            # transform the 'string' into a list
        (start, stop)=ids.split(',')
        ids = [i for i in range(eval(start),eval(stop)+1)]
    if type(ids) == dict:
        print('dictionary')
    elif type(ids) == list:
        id_ls = ids
        x = db[id_ls[0]].start['plot_Xaxis']
        y = db[id_ls[0]].start['plot_Yaxis']
        det_num = len(y)
        
        
        fig,ax = plt.subplots(det_num, sharex=True, figsize=(8, 5*det_num), dpi=80, facecolor='w', edgecolor='k')
        if det_num == 1: 
            for index, id in enumerate(id_ls):
                x_list = db[id].start['plot_Xaxis']
                if x_list != x:
                    print('data '+str(id) + ' has different x')
                    return 
                y_list = db[id].start['plot_Yaxis']
                if y_list != y:
                    print('data '+str(id) + ' has different y')
                    return             
                
                if ch != None:
                    for i, obj in enumerate(y_list):
                        split_ls = obj.split('_')
                        split_ls[1] = 'current'+ str(ch)
                        y_list[i] = '_'.join(split_ls)

                scan = db[id].table(fields=x_list+y_list)
                X = scan[x_list[0]]    

#                for i in range(det_num):  
                Y = scan[y_list[0]]

                if hasattr(db[id].start, 'scan_name') and  db[id].start['scan_name'] == 'scan_multi_1D':
                    lbl = str(id) + ','\
                                      + str(round(db[id].start['multi_start'] + (db[id].start['multi_pos']-1)*db[id].start['multi_delta'],3))
                    tlt = 'scan_multi_1D: axis = '+ db[id].start['multi_axis']
                    fig.suptitle(tlt)
                else:
                    lbl = str(id)

                if norm == True:
                     #   print(Y.min(), Y.max())
                    Y = 100*(Y-Y.min())/(Y.max()-Y.min()) 
                
                if stack != None:
                    Y = Y+(stack*index)
                
                ax.plot(X,Y, mk, label = lbl, linewidth = lw)
                if lb == True:
                    ax.legend()          
                ax.set_xlabel(X.name)
                ax.set_ylabel(Y.name)
        else:    
            for id in id_ls:
                x_list = db[id].start['plot_Xaxis']
                if x_list != x:
                    print('data '+str(id) + ' has different x')
                    return 
                y_list = db[id].start['plot_Yaxis']
                if y_list != y:
                    print('data '+str(id) + ' has different y')
                    return             

                scan = db[id].table(fields=x_list+y_list)
                X = scan[x_list[0]]    

                for i in range(det_num):  
                    Y = scan[y_list[i]]

                    if hasattr(db[id].start, 'scan_name') and  db[id].start['scan_name'] == 'scan_multi_1D':
                        lbl = str(id) + ','\
                                      + str(round(db[id].start['multi_start'] + (db[id].start['multi_pos']-1)*db[id].start['multi_delta'],3))
                        tlt = 'scan_multi_1D: axis = '+ db[id].start['multi_axis']
                        fig.suptitle(tlt)
                    else:
                        lbl = str(id)
                    ax[i].plot(X,Y, label = lbl)
                    ax[i].legend()          

                    if i == det_num-1: ax[i].set_xlabel(X.name)
                    ax[i].set_ylabel(Y.name)
    return fig,ax                
       

    
def esm_plt_2D(scan_id):
    """
    Plot for 2D scans

    Parameters:
    --------------------------------
    scan_id = integer, scan number    
    """
    
    scan = db[scan_id]
    try:
        dataZ = scan.table(fields= scan.start['plot_Zaxis'])
    except:
        print("This is not a 2D data")
        return
    del dataZ['time']

    Idata = np.ones(scan.start['shape']) * np.nan
    I, J = np.shape(Idata)
    idx = -1
    for i in range(I):
        for j in range(J):
            idx = idx+1        
            Idata[i][j] = dataZ.values[idx]
    
    fig, ax = plt.subplots()
    im_extent=[scan.start['X_start'],scan.start['X_stop'], scan.start['Y_start'],scan.start['Y_stop']]
    im_aspect=abs((scan.start['X_start']-scan.start['X_stop'])/(scan.start['Y_start']-scan.start['Y_stop']))
    
    ax.set_xlabel(scan.start['plot_Xaxis'][0])
    ax.set_ylabel(scan.start['plot_Yaxis'][0])
    
    
    im = ax.imshow(Idata,extent=im_extent, aspect = im_aspect, 
                   cmap='viridis', interpolation='none', origin='lower')

    cb = ax.figure.colorbar(im)
    cb.set_label(scan.start['plot_Zaxis'])    
    
    
######################################
####### Fitting Routine ##############
######################################

def G(x, alpha):
    """ Return Gaussian line shape at x with HWHM alpha """
    return np.sqrt(np.log(2) / np.pi) / alpha\
                             * np.exp(-(x / alpha)**2 * np.log(2))


def L(x, gamma):
    """ Return Lorentzian line shape at x with HWHM gamma """
    return gamma / np.pi / (x**2 + gamma**2)


def V(x, alpha, gamma):
    """
    Return the Voigt line shape at x with Lorentzian component HWHM gamma
    and Gaussian component HWHM alpha.

    """
    sigma = alpha / np.sqrt(2 * np.log(2))
    return np.real(wofz((x + 1j*gamma)/sigma/np.sqrt(2))) / sigma\
                                                           /np.sqrt(2*np.pi)


def Fano(x, x_0, q, fwhm):
    '''x is energy 
       x_0 is the center of the peak
       fwhm is the line width
       q is asymmetry parameter
    '''
    eps=2*(x-x_0)/fwhm
    return 1-(eps+q)*(eps+q)/(eps*eps+1)

def model_fano(x, x_0, q_f, fwhm_l, fwhm_g):
    '''covolution with Gaussian'''
    YG = G(x-x_0, fwhm_g/2.0)
    YF = Fano(x, x_0, q_f, fwhm_l)
    YC = np.convolve(YG, YF, mode='same')
    return YC

def He_fit(scn_ls, display = True, n_r=0, n_l=0 , asy=-2.6, \
           fwhm_l = 4.5E-3, lin_bk=0, axes = None):
    """
    Routine to fit He gas line. Parameter of the inrinsic Fanao from PRL66, 1306 (1991). It returns the 
    list of corresponding FWHM of the gaussian convolved to the Fano profile. 
    The result of the fitting is displayed by default if there is only one file in the list but can be 
    suppressed by setting display = False.

    Parameters
    -------------------------------------
    scn_ls: list of scans-ids or a list of one string with ['first, last'] scan for consecutive scans
    display: True/False, display the results in a figure 
    n_r=0, n_l=0: crop the left and right number of data-points
    asy: Fano asymmetry
    fwhm_l: Lorenzian width 
    lin_bk: integer number of point used at the edges to calculate the average intensity 
    axes: if not None, it can be used to call the routine with a matplotlib "ax" of a figure 

    
    """
                        ### handles the scan_ls for consecutive scans: ['1,4'] becomes [1,2,3,4]
    if type(scn_ls[0]) == str:    
        (start, stop)=scn_ls[0].split(',')
        scn_ls = [i for i in range(eval(start),eval(stop)+1)]
    
                        ### array to contain the Gauss FWHM results of the fittings
    FWHM_g = np.array([0.0]*len(scn_ls))
    FWHM_l = np.array([0.0]*len(scn_ls))
    asym = np.array([0.0]*len(scn_ls))
    X_pos = np.array([0.0]*len(scn_ls))
    I = np.array([0.0]*len(scn_ls))
    
    
    from scipy.optimize import curve_fit
    def mod_f(x, *fit_guess):
        '''The model function is the sum of Voigt (= Gauss_convolved_Lorentz)
                    Parameters are the peak intensities, their locations and the gaussian FWHM (all in array fit_guess)
                    The Lorenzian FWHM (gamma) is kept fixed in the fitting'''
        return fit_guess[0]*model_fano(x, fit_guess[1], asy,fwhm_l, fit_guess[2])+fit_guess[3]

#    f, ax = plt.subplots(figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
    
    i = 0                        ### loop to perform the fitting for every scan_id
    for scan_id in scn_ls:            
        X,Y, x_lbl, y_lbl = XY_1(scan_id, x_r=n_r, x_l=n_l )  ## read-in data
        if lin_bk != 0:
            x1,x2 = X.values[0],X.values[-1]
            n = lin_bk
            y1,y2 = sum(Y.values[0:n])/n, sum(Y.values[-(n+1):-1])/n
            x_ln_bk = X
            y_ln_bk = ((y2-y1)/(x2-x1))*(x_ln_bk-x1)+y1
            Y = Y-y_ln_bk
        else:
            x_ln_bk, y_ln_bk = 0.0*X, 0.0*Y # no background

        i = i+1    
        m,M = min(Y),max(Y)        
#        Xm,XM = X[Y.argmin()],X[Y.argmax()]        
        Xm,XM = X[Y.idxmin()],X[Y.idxmax()]        
        n_margin = 20
        bkg = 0.5*(sum(Y[0:n_margin])/len(Y[0:n_margin])+sum(Y[-n_margin:-1])/len(Y[-n_margin:-1]))
        fw_g = abs((XM-Xm)/2)
        fit_guess = [M, XM, fw_g , bkg]         # list of all fitting parameters: initial guess

        popt, pcov = curve_fit(mod_f, X, Y, p0 = fit_guess) ## popt is the list of optimal parameter

        Y_fit = popt[0]*model_fano(X, popt[1], asy, fwhm_l,popt[2])+popt[3]

                                        ### print scan_id and corresponding Gaussian FWHM 
        ind = scn_ls.index(scan_id)
        FWHM_g[ind] = popt[2]
        X_pos[ind] = popt[1]
        I[ind] = popt[0]
        print('scan = %d, X_0 = %f, FWHM_g = %e,FWHM_l = %e; q_f = %e ' 
                  %(scan_id, X_pos[ind], FWHM_g[ind], fwhm_l, asy))

                                               ### plot: only if there is a single file         
        if (display == True):
            f, ax = plt.subplots(figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
            Y_fit = popt[0]*model_fano(X, popt[1], asy, fwhm_l, popt[2])+popt[3]
            ax.plot(X,Y+y_ln_bk,'o', label ='He gas ',zorder =10)
            if lin_bk != 0: ax.plot(X,y_ln_bk,'--', label ='bkg',zorder =10)
            ax.plot(X,Y_fit+y_ln_bk,'-', label ='fit', linewidth =2, zorder =1)
            ax.legend(bbox_to_anchor=(0.7, 1.0), loc='upper left', ncol=1)
            ax.set_xlabel("Photon Energy (eV)", fontsize=14, weight ='bold')
            ax.set_ylabel("Intensity (arb. units)", fontsize=14, weight ='bold')
            ax.set_yticks([])

        if (axes != None):    
            Y_fit = popt[0]*model_fano(X, popt[1], asy, fwhm_l, popt[2])+popt[3]
            line1, = axes.plot(X,Y,'o', label =gas+' gas ', markersize =2,zorder =10)
            if lin_bk != 0: axes.plot(X,y_ln_bk,'--', label ='bkg',zorder =10)
            axes.plot(X,Y_fit,'-', label ='fit', linewidth =1, zorder =1)
#            axes.legend(bbox_to_anchor=(0.7, 1.0), loc='upper left', ncol=1)
#            axes.set_xlabel("Photon Energy (eV)", fontsize=14, weight ='bold')
#            axes.set_ylabel("Intensity (arb. units)", fontsize=14, weight ='bold')
#            axes.set_yticks([])

#    if (display == False): 
    if axes == None:
        return FWHM_g, X_pos
    else:
        return line1

def gas_fit(scn_ls, gas = 'N2', display = True, n_r = 10, n_l=10):
    """
    Fitting for  N2 and O2 gas spectra. Takes-in a scan_ls and the 
    choice of gas (either 'N2' or 'O2') and returns the list of corresponding FWHM of the gaussian.
    The result of the fitting is displayed by default if there is only one file in the list but can be 
    suppressed by setting display = False
    
    Parameters
    -----------------------------------
    scn_ls: a list of scan names or a signle string item containing first and last scan-id for sequential spectra
    gas = 'N2' or 'O2' 
    display = True/False (only for single fitting) 
    n_r, n_l: used to crop the edges    
    """
    
                        ### handles the scan_ls for consecutive scans: ['1,4'] becomes [1,2,3,4]
    if type(scn_ls[0]) == str:    
        (start, stop)=scn_ls[0].split(',')
        scn_ls = [i for i in range(eval(start),eval(stop)+1)]
            
            
            
                        ### array to contain the Gauss FWHM results of the fittings
    FWHM = np.array([0.0]*len(scn_ls))
    X_pos = np.array([0.0]*len(scn_ls))
    
                        ### loop to perform the fitting for every scan_id
    for scan_id in scn_ls:    
        X,YY, x_lbl, y_lbl = XY_1(scan_id, x_r=n_r, x_l=n_l, norm=True)  ## read-in data, crop the edges and normalize        
        
                                                  ## arrays (x and y) to contain the fitting (Voigt) curve
        x = np.linspace(min(X),max(X),1000)
        Y_V_tot = np.array([0.0]*len(x))

        
        #        res = np.array([0.0]*len(x))

                                                #### construct the initial guess
        if gas == 'N2':
            alpha, gamma = 0.5*40e-3, 0.5*117e-3  # HWHM for gaussian and Lorentzian (note HALF WIDTH)
                                                  
                                        # identify position of first peak of N2 spectra
            first_max = np.min(YY.idxmax())
            X_fm = X[first_max]

            n_peaks =6
            Y_V = [[0.0]]*n_peaks

            a_0 = [0.19, 0.175, 0.105, 0.04, 0.01,0.008]
            x_0 =[i+X_fm for i in [0, 0.23, 0.45, 0.67, 0.85, 1.05]]

            Y_V = [a_0[p]*V(x-x_0[p], alpha, gamma) for p in range(len(Y_V))]

            Y_V_tot = np.sum([Y_V[p] for p in range(len(Y_V))],axis=0)

        if gas == 'O2':
            alpha, gamma = 0.5*40e-3, 0.5*169e-3  # HWHM for gaussian and Lorentzian (note HALF WIDTH)

            YY = YY + 0.0

            X_fm = X[YY.idxmax()]                ## identify the maximum of the O2 spectra

            n_peaks = 12                          #### original 11
            Y_V = [[0.0]]*n_peaks

            a_0 = [0.05, 0.125, 0.15, 0.15, 0.125, 0.1, 0.075, 0.055, 0.025, 0.01, 0.0075, 0.005, 0.004]
            a_0 = a_0[0:n_peaks]                ## use this to reduce the number of used fitting peaks
            
            
                                                ### peaks are positioned around the maximum (learned by try and error)
            x_0 = [X_fm]*n_peaks
            x_0 =[x_0[i]+i*0.125 for i in range(-len(x_0)//2+3,len(x_0)//2+3,1 )]
            
            Y_V = [a_0[p]*V(x-x_0[p], alpha, gamma) for p in range(len(Y_V))]

            Y_V_tot = np.sum([Y_V[p] for p in range(len(Y_V))],axis=0)

                                                #### fitting proper    
        from scipy.optimize import curve_fit
        fit_guess = a_0 + x_0 + [alpha]         # list of all fitting parameters: initial guess

        def mod_f(x, *fit_guess):
            '''The model function is the sum of Voigt (= Gauss_convolved_Lorentz)
            Parameters are the peak intensities, their locations and the gaussian FWHM (all in array fit_guess)
            The Lorenzian FWHM (gamma) is kept fixed in the fitting'''
            return sum([fit_guess[i]*V(x-fit_guess[i+n_peaks], fit_guess[2*n_peaks], gamma) for i in range(n_peaks)])

        popt, pcov = curve_fit(mod_f, X, YY, p0 = fit_guess) ## popt is the list of optimal parameter

                                        ### print scan_id and corresponding Gaussian FWHM 
        ind = scn_ls.index(scan_id)
        FWHM[ind] = 2*popt[[2*n_peaks]]*1E3
        if gas == 'N2': X_pos[ind] = popt[[n_peaks]]
        if gas == 'O2': X_pos[ind] = popt[[n_peaks+3]]
        print('scan = %d, FWHM = %f, X_0 = %f' %(scan_id, FWHM[ind], X_pos[ind]))

        
                                       ### plot: only if there is a single file         
    if (display == True and len(scn_ls) == 1) :
        Y_fit = sum(\
                    [popt[i]*V(x-popt[i+n_peaks], popt[2*n_peaks], gamma) for i in range(n_peaks)]\
                    )
        YY_int = interp1d(X, YY)

        res = -0.1 +(YY_int(x) - sum([popt[i]*V(x-popt[n_peaks+i], popt[2*n_peaks], gamma) for i in range(n_peaks)]) )

        plt.figure(figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
#            plt.text(min(X)+0.01*(max(X)-min(X)), 0.8*max(YY), ' scan = %d' %(scan_id), fontsize=12)
        plt.plot(X,YY,'ro', label =gas+' gas ',zorder =10)
        plt.plot(x,Y_fit,'b-', label ='fit', linewidth =2, zorder =1)
        for i in range(0,n_peaks):
            plt.plot(x, popt[i]*V(x-popt[n_peaks+i], popt[2*n_peaks], gamma), 'k:', 
                     label=(r'(%.2f, %.2f)' %(popt[n_peaks+i], popt[i])))
        plt.plot(x,res,'g', linewidth =2, label ='residual')
        plt.plot([min(X),max(X)],[-0.1,-0.1],'k--', linewidth =1, label ='res.-zero')
        plt.title('scan = %d -- Voigt: FWHM_G = %.1f meV, FWHM_L = %.1f meV' 
                  %(scn_ls[0], 2*popt[2*n_peaks]*1e3, 2*gamma*1e3),fontsize=12, fontweight='bold')
            #pylab.legend()
        plt.legend(bbox_to_anchor=(0.7, 1.0), loc='upper left', ncol=1)
        plt.xlabel("Photon Energy (eV)", fontsize=14, weight ='bold')
        plt.ylabel("Intensity (arb. units)", fontsize=14, weight ='bold')
#            pylab.show()
#            pylab.savefig(f_nm+'.pdf')
        
    return FWHM, X_pos


#######################################################################
######### PGM CALIBRATION ROUTINES ####################################
#######################################################################

def off_adjust(grt_lines, e_display_eV, cff_display, e_real_eV):
    '''Fitting Procedure to determine the PGM offset mirror/ grating angles
       Returns the M2 and GRT offset corrections in degrees 
        
        Parameters:
        -----------------------
        grt_lines: string, grating line density
        e_display_eV: np_array, measured values of the gas lines; if multiple gas lines, just contatenate  
        cff_display: np_array, used c-values during measuraments of the gas lines; if multiple gas, just contatenate
        e_real_eV: np.array of target values, must have the same dimension of the other two arrays
        
        typical arrays:
            for Nitrogen: e_real_ev = np.array([400.8]*len(e_display_eV))
            for Oxygen:  e_real_ev = np.array([530.8]*len(e_display_eV))
            for He4+:  e_real_ev = np.array([64.45]*len(e_display_eV))
    '''


    ## Basic PGM equations

    ## grating equations

    #grating_density_mm=1200 #in l/mm
    def f_grating_density_mm(x):    # x should be small fraction of the unity
    #    return grating_density_mm*(1-x);    # use this line if want to valy the l/mm
         return grating_density_mm;          # use this line for fixed l/mm
    def f_energy_eV(x,y,z):         # in eV; x=incident angle(rad,positive) y=diffraction angle(rad, negative) 
        return 1239.852/(10**6/f_grating_density_mm(z)*(np.sin(x)+np.sin(y))) 
    def f_cff(x,y):                 # dimensionless; x=incident angle(rad,positive) y=diffraction angle(rad, negative)
        return np.cos(y)/np.cos(x) 

    #inverted grating equation (first (internal) order)
    def f_alfa_rad(x,y):  # in rad
        return np.arcsin((x-np.sqrt(x**2-(x**2+y**2-1)*(1-y**2)))/(1-y**2))
    def f_beta_rad(x,y):  # in rad
        return np.arcsin((x*y**2-np.sqrt(x**2*y**4-(y**2-1)*(y**2*x**2+1-y**2)))/(y**2-1))
    #where y=Cff,x=grating_density*0.001239852./energy_eV;

    #pgm scanning mechnism
    def f_mirror_deg(x,y):
        return 90*(np.pi-x+y)/np.pi      #in deg
    def f_grating_deg(y):
        return (np.pi/2+y)*180.0/np.pi     #in deg
    #where x=incident angle(rad,pos),y=diffraction angle(rad, neg)

    def f_pgm_alfa_rad(x,y): 
        return np.pi/2+np.pi/180.0*(y-2*x)
    def f_pgm_beta_rad(y):
        return y/180.0*np.pi-np.pi/2.0;
    #where x=mirror(deg),y=grating(deg)


    



                        ##################################################
                        ############## CODE ##############################
                        ##################################################
                                # Fit      
                                # the expected position of the peak (calibration standard);



    grating_density_mm=eval(grt_lines)

    mirror_deg=np.array([f_mirror_deg(f_alfa_rad(f_grating_density_mm(0)*0.001239852/i,j),\
                                f_beta_rad(f_grating_density_mm(0)*0.001239852/i,j))\
                                    for (i,j) in zip(e_display_eV, cff_display)])
    mirror_offset_deg=0.0
    grating_deg=np.array([f_grating_deg(f_beta_rad(f_grating_density_mm(0)*0.001239852/i,j))
                 for (i,j) in zip(e_display_eV, cff_display)])
    grating_offset_deg=0.0

    ## visialize initial calibration
    alfa_rad=np.array([f_alfa_rad(f_grating_density_mm(0)*0.001239852/i,j) for (i,j) in zip(e_display_eV, cff_display)])
    beta_rad=np.array([f_beta_rad(f_grating_density_mm(0)*0.001239852/i,j) for (i,j) in zip(e_display_eV, cff_display)])
    a=np.array([f_mirror_deg(i,j) for (i,j) in zip(alfa_rad,beta_rad)])
    b=np.array([f_grating_deg(i) for i in beta_rad]) 

    fig = plt.figure(figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
    fig.add_subplot(1,2,1)
    plt.plot(cff_display, mirror_deg-mirror_offset_deg, 'bo', cff_display, a, 'ro')
    plt.xlabel('Cff')
    plt.ylabel('Rotation(deg)') 
    plt.title('Mirror Offset(deg)= '+str(mirror_offset_deg))
    fig.add_subplot(1,2,2)  
    plt.plot(cff_display,grating_deg-grating_offset_deg,'bo',cff_display,b,'g*')
    plt.xlabel('Cff')
    plt.ylabel('Rotation(deg)') 
    plt.title('Grating Offset(deg)='+ str(grating_offset_deg))

    ## fitting procedure
    def f(x,y,x0):
               return np.array([f_energy_eV(f_pgm_alfa_rad(i-x0[0],j-x0[1]),f_pgm_beta_rad(j-x0[1]),x0[2]) 
                                for (i,j) in zip(x,y)])


    # define fitting function, same as energy fit but with explicit offset parameters (x0)
    # extend function to a set of equations to be minimized


    def F(x):
        return  f(mirror_deg,grating_deg,x) - e_real_eV 


    #initial 
    x0 = [mirror_offset_deg, grating_offset_deg, 0]

    #performleast square fit
    from scipy.optimize import least_squares

    res_lsq = least_squares(F, x0)
    x = res_lsq.x

    # predict new calibration using new mirror/ grating offsets

    e_fit_eV=f_energy_eV(f_pgm_alfa_rad(mirror_deg-x[0],grating_deg-x[1]),f_pgm_beta_rad(grating_deg-x[1]),x[2]);

    cff_fit=f_cff(f_pgm_alfa_rad(mirror_deg-x[0],grating_deg-x[1]),f_pgm_beta_rad(grating_deg-x[1]));

    fig1 = plt.figure(figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
    fig1.add_subplot(1,1,1)
    plt.plot(cff_display,e_display_eV,'bo', label='starting')
    plt.plot(cff_fit,e_real_eV,'yo', label = 'target')
    plt.plot(cff_fit,e_fit_eV,'g+', label = 'fit with offsets')
    plt.legend()
    plt.xlabel('Cff')
    plt.ylabel('Energy(eV)') 
    plt.title('PGM Fit for ' + str(f_grating_density_mm(x[2])) + ' l/mm using He and N$_2$ gas lines')
    #plt.title('PGM Fit for ' + str(f_grating_density_mm(x[2])) + ' l/mm using N$_2$ and O$_2$ gas lines')
    l,r,t,b = plt.axis()
    plt.text(l+0.05*(r-l),b+0.7*(t-b), 
             ' GRT_density = ' + str(f_grating_density_mm(x[2])) +'\n\n Moff(deg)=' + str(x[0]) + '\n\n Goff(deg)=' + str(x[1]),
             fontsize = 14, fontweight ='bold')
#    print(x)
    #disp(['Calibration Energy Deviation (RMS,eV)=',num2str(std(e_real_eV-e_fit_eV))]);           
    #print(l,r,t,b)

    return x[0], x[1]


def new_off(grt_lines,  m2_off_corr, grt_off_corr, branch='A',):
    '''
    For a certain grating, calculates the new offsets, starting from the current values (for branch A or Branch B)
    and adding the corrections previously calculated vy the off_adjust procedure 
    
    Parameters:
    ----------------------------------------------
    grt_lines: string
    branch: string, 'A' or 'B'
    m2_off_corr, grt_off_corr: calculated with Kon routine
    '''
    import pandas as pd

    if branch == 'A':
        df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/Grt_Offset_A.csv',dtype='str') #you wanted float datatype
        ESM_Grt_Offset_A = df.to_dict(orient='records')[0] #the[0] extract the dictionary

        df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/M2_Offset_A.csv', dtype='str') #string  datatype
        ESM_M2_Offset_A = df.to_dict(orient='records')[0] #the[0] extract the dictionary
    else:
        df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/Grt_Offset_B.csv',dtype='str') #you wanted float datatype
        ESM_Grt_Offset_A = df.to_dict(orient='records')[0] #the[0] extract the dictionary

        df = pd.read_csv('/home2/xf21id1/.ipython/profile_collection/startup/motion_definition_files/M2_Offset_B.csv', dtype='str') #string  datatype
        ESM_M2_Offset_A = df.to_dict(orient='records')[0] #the[0] extract the dictionary
        
    lines = grt_lines


    new_M2 = eval(ESM_M2_Offset_A[lines]) + m2_off_corr
    new_GRT = eval(ESM_Grt_Offset_A[lines]) + grt_off_corr


    print("### GRT: {} ###".format(lines))
    print(' M2 from {:3f}  to {:3f} (correction = {:3f})'.format(eval(ESM_M2_Offset_A[lines]), new_M2, m2_off_corr))
    print('GRT from {:3f}  to {:3f} (correction = {:3f})'.format(eval(ESM_Grt_Offset_A[lines]), new_GRT, grt_off_corr))





functions = [name for (name, thing) in locals().items() if callable(thing)]
print(functions)