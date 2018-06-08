# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 11:17:05 2016
this will read in the analog tdms files containing adc information 
plots the geometric mean of pmts
@author: DJ
"""
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.stats.mstats import gmean
from nptdms import TdmsFile

def plot_data(filename, ymax = 1000, xmax = 33000, xmin = 0, ymin = 0):
    files = adc_files(filename,'/Dev1')
    files2 = adc_files(filename,'/Dev2')
    chs = nptdms_analog(files, 'Dev1')
    chs2 = nptdms_analog(files2, 'Dev2')
    bin_num = np.linspace(0,32769,1000)
    
    for i in range(10):
        y = plt.hist(chs[i],bin_num)
        plt.ylim(ymin,ymax)
        plt.xlim(xmin, xmax)
        plt.show()
        if i == 6:
            print np.sum(np.array(y[0][100:]))
    for i in range(10):
        y = plt.hist(chs2[i],bin_num)
        plt.ylim(ymin, ymax)
        plt.xlim(xmin, xmax)
        plt.show()
        if i == 6:
            print np.sum(np.array(y[0][100:]))

def plot_data(filename, ymax = 1000, xmax = 33000, xmin = 0, ymin = 0):
    files = adc_files(filename,'/Dev1')
    files2 = adc_files(filename,'/Dev2')
    chs = nptdms_analog(files, 'Dev1')
    chs2 = nptdms_analog(files2, 'Dev2')
    bin_num = np.linspace(0,32769,1000)
    
    bgo_dev1 = bgo_data(chs[:6], 0)
    bgo_dev2 = bgo_data(chs2[:6], 0)
    labr_dev1 = labr_data(chs[7:], 0)
    labr_dev2 = labr_data(chs2[7:], 0)
    
    
    for i in range(10):
        y = plt.hist(chs[i],bin_num)
        plt.ylim(ymin,ymax)
        plt.xlim(xmin, xmax)
        plt.show()
        if i == 6:
            print np.sum(np.array(y[0][100:]))
    for i in range(10):
        y = plt.hist(chs2[i],bin_num)
        plt.ylim(ymin, ymax)
        plt.xlim(xmin, xmax)
        plt.show()
        if i == 6:
            print np.sum(np.array(y[0][100:]))

def nptdms_analog(file_name, dev):

    ch_data = [[] for i in range(10)]
    for f in file_name:
        tf = TdmsFile(file_name)
        grp = tf.groups()[0]
        
        for i in range(10):
            ch = dev + '/ai' + str(i)
            ch_data[i].extend(tf.object(grp, ch).raw_data)
            
    # tf = TdmsFile(file_name)
    # grp = tf.groups()[0]
    
    # ch_data = []
    # for i in range(10):
        # ch = dev + '/ai' + str(i)
        # ch_data.append(tf.object(grp, ch).raw_data)
    
    return ch_data
            
            
            
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




def adc_files(path0, dev):
    """get analog files for a device in a certain path"""
    
    file_list=[]
    path = path0 + dev + '/analog'
    for file in os.listdir(path):
        if file.endswith('.tdms'):
            file_list.append(path+'/'+file)              
    return file_list


def labr_data(pmts, min_ch):
    """get final 3 columns of data from analog file
    possibly used for 3 labr detectors
    """
    
    labr = [[],[],[]]
    labr[0] = pmts[0] > min_ch
    labr[1] = pmts[1] > min_ch
    labr[2] = pmts[2] > min_ch
    # for i in range(len(pmts)):
        # labr[0].append(pmts[0][i])
        # labr[1].append(pmts[1][i])
        # labr[2].append(pmts[2][i])        
    return labr

def bgo_data(pmts, min_ch):
    """get first 6 columns of data from analog file
    used for 6 pmts attached to the 3 bgo of a single device
    """
    pmts_thr = [[],[],[],[],[],[],[]]
    for i in range(len(pmts[0])):
        if pmts[0][i] > min_ch and pmts[1][i] > min_ch:
            pmts_thr[0].append(pmts[0][i])
            pmts_thr[1].append(pmts[1][i])
        if pmt2[x] > min_ch and pmt3[x] > min_ch:
            pmts_thr[2].append(pmts[2][i])
            pmts_thr[3].append(pmts[3][i])
        if pmt4[x] > min_ch and pmt5[x] > min_ch:
            pmts_thr[4].append(pmts[4][i])
            pmts_thr[5].append(pmts[5][i])
#            
    bgo = [[], [], []]
    bgo[0] = get_gmean(pmts_thr[0], pmts_thr[1])
    bgo[1] = get_gmean(pmts_thr[2], pmts_thr[3])
    bgo[2] = get_gmean(pmts_thr[4], pmts_thr[5])
    return bgo

