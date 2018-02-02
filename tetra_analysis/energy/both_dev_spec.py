# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 11:17:05 2016
this will read in the analog tdms files containing adc information 
plots the geometric mean of pmts
@author: DJ
"""
import numpy as np
import matplotlib.pyplot as plt
from tetra_tools.pyTDMS4 import read
import os
from scipy.stats.mstats import gmean


def get_gmean(pmt_a, pmt_b):     
    """take geometric mean of each pair in two lists"""
    
    bgo = []
    for i in range(len(pmt_a) - 1):
        pmts = []
        if pmt_a[i] > 0 and pmt_b[i] > 0:
            pmts.append(pmt_a[i])
            pmts.append(pmt_b[i])
            bgo.append(gmean(pmts))            
    return bgo


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
    #path = path0
    for file in os.listdir(path):
        if file.endswith('.tdms'):
            file_list.append(path+'/'+file)              
    return file_list


def labr_data(files):
    """get final 3 columns of data from analog file
    possibly used for 3 labr detectors
    """
    
    labr = [[],[],[]]
    for f in files:
        labr[0].extend(get_pmt(f,7))
        labr[1].extend(get_pmt(f,8))
        labr[2].extend(get_pmt(f,9))        
    return labr

def bgo_data(files):
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
    pmt0b, pmt1b, pmt2b, pmt3b, pmt4b, pmt5b = ([] for i in range(6))
    
    #use this block to search for pmt triggers above a minimum threshold, min_ch
    min_ch = 800
    for x in range(len(pmt0)):
        if pmt0[x] > min_ch and pmt1[x] > min_ch:
            pmt0b.append(pmt0[x])
            pmt1b.append(pmt1[x])
        if pmt2[x] > min_ch and pmt3[x] > min_ch:
            pmt2b.append(pmt2[x])
            pmt3b.append(pmt3[x])
        if pmt4[x] > min_ch and pmt5[x] > min_ch:
            pmt4b.append(pmt4[x])
            pmt5b.append(pmt5[x])
#            
    bgo = [[], [], []]
    bgo[0] = get_gmean(pmt0b, pmt1b)
    bgo[1] = get_gmean(pmt2b, pmt3b)
    bgo[2] = get_gmean(pmt4b, pmt5b)   
    return bgo


##############################################################################
def make_plots(path0 = None, y_max = None, bins = 1000): 
    if not path0:
        path0='C:/Users/tetra/calibrations/LSU/misc/LSU_01/20171127_bkgd/'
    
    
    bin_num=np.linspace(0,32769,bins)
    
    if not y_max:
        y_max=3000
    
    
    file_list = adc_files(path0, 'Dev1')
    dev1_bgo = bgo_data(file_list)
    #dev1_labr = labr_data(file_list)
    file_list = adc_files(path0, 'Dev2')
    dev2_bgo = bgo_data(file_list)
    #dev1_labr = labr_data(file_list)
    
    f,axes = plt.subplots(3,2,sharex=True,sharey=True)
    
    ax1,ax2,ax3,ax4,ax5,ax6 = axes.flatten()
    
    ax1.hist(dev1_bgo[0],bin_num,histtype='step',color='blue',alpha=0.7)
    ax2.hist(dev1_bgo[1],bin_num,histtype='step',color='red',alpha=0.7)
    ax3.hist(dev1_bgo[2],bin_num,histtype='step',color='green',alpha=0.7)
    ax4.hist(dev2_bgo[0],bin_num,histtype='step',color='black',alpha=0.7)
    ax5.hist(dev2_bgo[1],bin_num,histtype='step',color='teal',alpha=0.7)
    ax6.hist(dev2_bgo[2],bin_num,histtype='step',color='purple',alpha=0.7)
    
    plt.ylim(0,y_max)
    #plt.xticks((0,5000,10000,15000,20000,25000,30000,35000),('0','5','10','15','20','25','30','35'))
    f.text(0.3,0.04, 'channel x1000',ha='center')
    f.text(0.723,0.04, 'channel x1000',ha='center')
    f.text(0.02,0.25,'bgo3 counts',va='center',rotation='vertical')
    f.text(0.02,0.53,'bgo2 counts',va='center',rotation='vertical')
    f.text(0.02,0.803,'bgo1 counts',va='center',rotation='vertical')
    
    #plt.hist(dev1_bgo[0], bin_num, histtype='step')
    plt.show()

