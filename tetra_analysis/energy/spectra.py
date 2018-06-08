# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 11:17:05 2016
this will read in the analog tdms files containing adc information
plots the geometric mean of pmts

charged particle detector is Device 2 in LSU 01!!!!
@author: DJ
"""
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.stats.mstats import gmean
from nptdms import TdmsFile
import itertools as it

from tetra_tools.pyTDMS4 import read


def pyTDMS4_analog(file_names, pmts):
    """read in the data for a specific column in the analog file"""
    

    chs = [np.array([]) for i in range(len(pmts))]
    for f in file_names:
        data_raw = read(f)
        keys1 = data_raw[1].keys()
        for i in range(len(pmts)):
            for key in keys1:
                if str(key[-2]) == str(pmts[i]):
                    data_temp = np.array(data_raw[1].get(key))
                    chs[i] = np.concatenate([chs[i], data_temp])
    return chs
    
def nptdms_analog(file_names, dev, pmts):

    
    chs = [np.array([]) for i in range(len(pmts))]
    for f in file_names:
        tf = TdmsFile(f)
        grp = tf.groups()[0]
        for pmt in pmts:
            ch = dev + '/ai' + str(pmt)
            chs[i] = np.concatenate([chs[pmt], tf.object(grp, ch).raw_data])
    return chs


def adc_files(path0, dev):
    """get analog files for a device in a certain path"""

    file_list=[]
    path = path0 + dev + '/analog'
    for file in os.listdir(path):
        if file.endswith('.tdms'):
            file_list.append(path+'/'+file)
    return file_list


def bgo_adc(fp, dev, min_ch = 0):

    if dev == 'Dev1': keys = ['bgo4', 'bgo5', 'bgo6']
    if dev == 'Dev2': keys = ['bgo1', 'bgo2', 'bgo3']
    bgo = {}
    for d in range(len(dev)):
        files = adc_files(fp, '/'+dev)
        #chs = nptdms_analog(files, dev[d], [0,5]) NOT WORKING FOR ALL FILES!
        chs = pyTDMS4_analog(files, [0,1,2,3,4,5])
        bgo[keys[0]] = gmean(chs[0:2], min_ch)
        bgo[keys[1]] = gmean(chs[2:4], min_ch)
        bgo[keys[2]] = gmean(chs[4:6], min_ch)
    return bgo

def labr_adc(fp, box, dev , min_ch = 0):

    labr = {}

    files = adc_files(fp, '/'+dev)
    if box == 'LSU_01' and dev == 'Dev2':
        #no LaBr in LSU_01 Dev2, just charged particle detector
        return None
    else:
        chs = pyTDMS4_analog(files, [7, 8, 9])
        labr[dev + '_1'] = chs[0][np.where(chs[0] > min_ch)[0]]
        labr[dev + '_2'] = chs[1][np.where(chs[1] > min_ch)[0]]
        labr[dev + '_3'] = chs[2][np.where(chs[2] > min_ch)[0]]
    return labr

def get_cpd(fp, min_ch = 0):

    cpd = {}
    files = adc_files(fp, '/Dev2')
    cpd['pmt1'] = pyTDMS4_analog(files, [7])
    cpd['pmt2'] = pyTDMS4_analog(files, [8])
    return cpd

def plot_data(bgo, labr, cpd, ymax = 1000, xmax = 33000, xmin = 0, ymin = 0):

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