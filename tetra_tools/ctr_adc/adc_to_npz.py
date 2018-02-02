# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 11:17:05 2016
this will read in the analog tdms files containing adc information 
and save the information in a .npz file
@author: DJ
"""
import numpy as np
import matplotlib.pyplot as plt
from pyTDMS4 import read
import os
from scipy.stats.mstats import gmean
import tools as tool




def get_pmt(file_name,pmt):
    """read in the data for a specific column in the analog file"""
    
    data_raw=read(file_name)
    keys1=data_raw[1].keys()
    for key in keys1:
        if str(key[-2]) == str(pmt):
            data=data_raw[1].get(key)
    return data

def adc_files(path0, dev):
    """get analog files for a device in a certain path"""
    
    file_list=[]
    path = path0 + dev + '/analog'
    for file in os.listdir(path):
        if file.endswith('.tdms'):
            file_list.append(path+'/'+file)              
    return file_list


def pmt_data(files):
    """get first 6 columns of data from analog file
    used for 6 pmts attached to the 3 bgo of a single device
    """
    
    pmt0, pmt1, pmt2, pmt3, pmt4, pmt5 = ([] for i in range(6))
    for f in files:
        pmt0.extend(get_pmt(f,0))
        pmt1.extend(get_pmt(f,1))
        pmt2.extend(get_pmt(f,2))
        pmt3.extend(get_pmt(f,3))
        pmt4.extend(get_pmt(f,4))
        pmt5.extend(get_pmt(f,5))

    return pmt0, pmt1, pmt2, pmt3, pmt4, pmt5
    

##############################################################################
def get_pmt_adc(box_num, run_type, folder1, folder2=None, file_list=None, file_list2=None, output_path=None): 
    """set run type to source name or bkgd"""

    if not file_list:
        loc = tool.loc_name(box_num)
        path0='C:/Users/tetra/calibrations/' + loc + '/' + folder1 + '/' + box_num + '/' + folder2 + '/'

            
        output_path = 'Y:/' + box_num + '/calibrations/'
        if not os.path.exists(output_path):
            os.makedirs(output_path)
       
        file_list = adc_files(path0, 'Dev1')
        file_list2 = adc_files(path0, 'Dev2')        
    
    dev1_data = pmt_data(file_list)

    pmt0 = np.array(dev1_data[0])
    pmt1 = np.array(dev1_data[1])
    pmt2 = np.array(dev1_data[2])
    pmt3 = np.array(dev1_data[3])
    pmt4 = np.array(dev1_data[4])
    pmt5 = np.array(dev1_data[5])

    file_ts = output_path + 'dev1_pmts_' + run_type
    np.savez(file_ts, pmt0=pmt0, pmt1=pmt1, pmt2=pmt2, pmt3=pmt3, pmt4=pmt4, pmt5=pmt5)
        

    dev2_data = pmt_data(file_list2)

    pmt0 = np.array(dev2_data[0])
    pmt1 = np.array(dev2_data[1])
    pmt2 = np.array(dev2_data[2])
    pmt3 = np.array(dev2_data[3])
    pmt4 = np.array(dev2_data[4])
    pmt5 = np.array(dev2_data[5])

    file_ts = output_path + 'dev2_pmts_' + run_type
    np.savez(file_ts, pmt0=pmt0, pmt1=pmt1, pmt2=pmt2, pmt3=pmt3, pmt4=pmt4, pmt5=pmt5)