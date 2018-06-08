# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 14:46:55 2017

make energy plots from single file from a day

needs work

@author: DJ Pleshinger
"""


import numpy as np
import datetime
import numpy.ma as ma
from numba import jit
from scipy.stats.mstats import gmean
import csv

import tetra_analysis.timestamps.ctr_to_timestamp3 as get
from tetra_tools.pyTDMS4 import read
import tetra_tools.tools as tool

##############################################################################
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


def bgo_adc(fp, dev, keys, min_ch = 0):

    bgo = {}
    #files = adc_files(fp, '/'+dev[d])
    chs = pyTDMS4_analog([fp], [0,1,2,3,4,5])
    bgo[keys[0]] = gmean(chs[0:2])
    bgo[keys[1]] = gmean(chs[2:4])
    bgo[keys[2]] = gmean(chs[4:6])
    return bgo

def gps_adc(fp, dev):
    
    gps = pyTDMS4_analog([fp], [6])[0]
    return gps

def get_times2(f):

    pps_idx, pps_ctr1, clks = get.get_pps(f)
    ctr_times = get.get_times(f, pps_ctr1, clks, 1)
    ctr1_clean = []
    ctr1_clean.append(ctr_times[0])
    for i in range(1,len(ctr_times)):
        if ctr_times[i] - ctr1_clean[-1] > .000013:
            ctr1_clean.append(ctr_times[i])
    ctr1_times = ctr1_clean
    return ctr1_times, pps_idx


def get_filename(path0, date_str, time_sec, dev):
    files = {}

    d, m, y = tool.date_to_ints(date_str)
    date = datetime.date(y, m, d)

    path = path0 + dev + '/'
    file_type = ['ctr1', 'analog']
    file_list = [[],[]]
    for x in file_type:
        file_list = get.day_files(path, x, date)
        file_names = []
        for f in file_list:
            file_name = f[f.rfind('\\'):]
            file_time = file_name.split(',')[1]
            try:
                file_time = 3600*int(file_time[0:2]) + 60*int(file_time[2:4]) \
                + int(file_time[4:6])
            except ValueError as e:
                continue
            if file_time < time_sec:
                good_file = f
            else:
                break
        files[x] = good_file

    return files

    
def trim(c1times, adc_file, pps_idx, event_time, duration, box_num, dev):

    if dev == 'Dev1': keys = ['bgo4', 'bgo5', 'bgo6', 'gps1']
    if dev == 'Dev2': keys = ['bgo1', 'bgo2', 'bgo3', 'gps2']
    adc = bgo_adc(adc_file, dev, keys, min_ch = 0)
    adc[keys[3]] = gps_adc(adc_file, dev)

    gps_1pos = np.where(adc[keys[3]] > 2500)[0][0]
    for k in adc.keys():
        adc[k] = adc[k][gps_1pos:]
    gps_pos = np.where(adc[keys[3]] > 2500)[0]
    c1times = c1times[pps_idx[0]:]
    pps_idx = np.array(pps_idx) - pps_idx[0]
    
    x = np.where(np.array(c1times) == np.floor(event_time))[0][0]
    sec_in_file = int(c1times[x] - c1times[0]) #number of seconds passed in file, use to find pps in analog
    y = np.where(np.array(c1times) == np.ceil(event_time))[0][0]
    c1times = c1times[x:y+1]
    
    gps_pos = gps_pos[sec_in_file:sec_in_file+2]
    
    for k in adc.keys():
        adc[k] = adc[k][gps_pos[0]:gps_pos[1]+1]

    c = 0
    event_times = []
    event_adc = {}
    #print event_time
    for t in c1times:
        #print t
        if t < (event_time + duration) and t > (event_time):
            event_times.append(t)
            event_pmts.append(pmts_new[c])
            event_gps.append(gps_new[c])
            c0 = c + 1
        c = c + 1
    for x in range(len(pmts_new) - len(c1times)):
        event_pmts.append(pmts_new[c0])
        event_gps.append(gps_new[c0])
        c0 = c0 + 1

    event = [event_times, event_pmts, event_gps]
    return event
    

def get_cals():

    slopes = []
    y_ints = []
    cal_file = 'C:/Users/tetra/calibrations/cal_eqns.csv'
    with open(cal_file, 'r') as infile:
        for line in infile:
            csv_input = csv.reader(infile, delimiter = ',')
            for cols in csv_input:
                slopes.append(float(cols[0]))
                y_ints.append(float(cols[1]))
    return slopes, y_ints
    
    
def adc_to_energy(pmts, box_num, idx, dev):

    
    g = lambda x: m*x + b
    
    lookup = {'LSU_01':0, 'LSU_02':1, 'PAN_01':2, 'PAN_02':3, 'PAN_03':4,
    'PAN_04':5, 'PAN_05':6, 'PR_01':7, 'PR_02':8, 'PR_03':9, 'PR_04':10, 
    'PR_05':11, 'PR_06':12, 'PR_07':13, 'PR_08':14, 'PR_09':15, 'PR_10':16,
    'UAH_01':17, 'UAH_18':18}
    box = lookup[box_num]
    
    if dev == 'Dev1':
        lookup_idx = {1:0, 2:1, 3:2}
    if dev == 'Dev2':
        lookup_idx = {1:3, 2:4, 3:5}
    f = np.zeros(shape = (19, 6, 2))
    slopes, y_ints = get_cals()

    c = 0
    for i in range(19):
        for j in range(6):
            f[i][j][0] = slopes[c]
            f[i][j][1] = y_ints[c]
            c = c + 1
    bgo = []
    c = 0
    for x in idx:

        m = f[box][lookup_idx[x]][0]
        b = f[box][lookup_idx[x]][1]
        pmt1 = g(pmts[c][0])
        pmt2 = g(pmts[c][1])
        bgo.append(gmean([pmt1,pmt2]))
        c = c + 1
    return bgo
##############################################################################
##############################################################################
##############################################################################


def energy(box_num, date_str, time_sec, duration = None, path0=None):
    #if duration = None use the entire 10 minute file
    if not path0: path0 = 'E:/' + box_num + '/'
    folder = date_str[:4] + '_' + date_str[5:7] + '/'
    path = path0 + folder
    
    try:
        d1_files = get_filename(path, date_str, time_sec, 'Dev1')
        d1_times, pps_idx1 = get_times2(d1_files['ctr1'])
        d1_event = trim(d1_times, d1_files['analog'], pps_idx1, time_sec, duration, box_num, 'Dev1')
    except IndexError as e:
        d1_event = [[],[],[]]
    
    try:
        d2_files = get_filename(path, date_str, time_sec, 'Dev2')
        d2_times, pps_idx2 = get_times2(d2_files['ctr1'])
        d2_event = trim(d2_times, d2_files['analog'], pps_idx2, time_sec, duration, box_num, 'Dev2')
    except IndexError as e:
        d2_event = [[],[],[]]

    
    event = []
    c = 0
    for x in d1_event[1]:
        if x == 1.0:
            d1_event[1][c] = 4.0
        if x == 2.0:
            d1_event[1][c] = 5.0
        if x == 3.0:
            d1_event[1][c] = 6.0
        c = c + 1
    event = [d1_event[0] + d2_event[0], d1_event[1] + d2_event[1], d1_event[2] + d2_event[2]]

    return event

    
def loop_energy(box_list, date_str, time_sec, duration, path0=None):

    boxes = [list() for _ in range(len(box_list))]
    
    b = 0
    for box in box_list:
        boxes[b] = energy(box, date_str, time_sec, duration, path0)
        b = b + 1
    return boxes
    












