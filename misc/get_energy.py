# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 14:46:55 2017

make energy plots from single file from a day

needs work

@author: DJ Pleshinger
"""

from pyTDMS4 import read
import numpy as np
import sys
import os
import get_info as get
import datetime

##############################################################################
def check_gps(ctr1_file,ctr2_file,ctr3_file,adc_file):
    ctr1_gps_check=ctr1_file[-77:-71]
    ctr2_gps_check=ctr2_file[-77:-71]
    ctr3_gps_check=ctr3_file[-77:-71]
    adc_gps_check=adc_file[-77:-71]
    if not str.isdigit(ctr1_gps_check):
        print 'ctr1 has no gps lock'
        sys.exit()
    if not str.isdigit(ctr2_gps_check):
        print 'ctr2 has no gps lock'
        sys.exit()
    if not str.isdigit(ctr3_gps_check):
        print 'ctr3 has no gps lock'
        sys.exit()
    if not str.isdigit(adc_gps_check):
        print 'adc file has no gps lock'
        sys.exit()
    del ctr1_gps_check
    del ctr2_gps_check
    del ctr3_gps_check
    del adc_gps_check

def get_date(filename):
    statinfo = os.stat(filename)
    timestamp = statinfo.st_mtime
    date = datetime.datetime.fromtimestamp(timestamp)
    
    return date.day, date.month, date.year
##############################################################################

    
##############################################################################

 
##############################################################################
def get_idx(ctr1_times, ctr2_times, ctr3_times, ctr1_pps_idx):
    
    idx=[]


    j=0
    count=0
    ctr1_times_arr=np.array(ctr1_times)    
    ctr2_times_arr=np.array(ctr2_times)
    ctr3_times_arr=np.array(ctr3_times)
    
    
    for line in ctr1_times_arr:
        if count == ctr1_pps_idx[j]:
            idx.append('pps')
            j=j+1
            if j>len(ctr1_pps_idx)-1:
                j=j-1
            count=count+1
            continue
        ctr2_diff = np.abs(ctr2_times_arr - line)
        ctr3_diff = np.abs(ctr3_times_arr - line)
        ctr2_matches = np.where(ctr2_diff <= 0.0000002)[0]
        ctr3_matches = np.where(ctr3_diff <= 0.0000002)[0]
        n2_matches = len(ctr2_matches)
        n3_matches = len(ctr3_matches)
        if n2_matches==n3_matches==1:
            idx.append('both')
        elif n2_matches!=0:
            idx.append('bgo2')
        elif n3_matches!=0:
            idx.append('bgo3')
        elif n2_matches==n3_matches==0:
            idx.append('bgo1')
        count=count+1
    del ctr1_times_arr
    del ctr2_times_arr
    del ctr3_times_arr
        
    return idx
            
############################################################################## 
############################################################################## 
############################################################################## 
##############################################################################
############################################################################## 
############################################################################## 
############################################################################## 
##############################################################################










array = 'pr'
box_num = 'PR_02'
dev = 'Dev1'

path0='C:/Users/tetra/array/'+array+'/data/'+box_num+'/'+dev+'/'
filename = 'GPGGA,18073300,181524705,N,0664325439,W,1,08,092,00198,M,-043,M,,5E,3557153251.tdms'

   
adc_file=path0+'analog/'+filename
ctr1_file=path0+'ctr1/'+filename
ctr2_file=path0+'ctr2/'+filename
ctr3_file=path0+'ctr3/'+filename
       
check_gps(ctr1_file, ctr2_file, ctr3_file, adc_file)
day, month, year = get_date(adc_file) #does not matter which file used

##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
ctr1_times=[]
ctr2_times=[]
ctr3_times=[]

pps_idx, pps_ctr1, clks = get.get_pps(ctr1_file)

ctr2_times.extend(get.get_times(ctr2_file,pps_ctr1,clks))
ctr3_times.extend(get.get_times(ctr3_file,pps_ctr1,clks))
ctr1_times.extend(get.get_times(ctr1_file,pps_ctr1,clks))



'''###################################################################'''
'''get idx and see how many of each triggers we see'''
idx = get_idx(ctr1_times, ctr2_times, ctr3_times, pps_idx)

idx_arr=np.array(idx)
pps_idx_len=(idx_arr == 'pps').sum()
bgo1_idx_len=(idx_arr == 'bgo1').sum()
bgo2_idx_len=(idx_arr == 'bgo2').sum()
bgo3_idx_len=(idx_arr == 'bgo3').sum()
both_idx_len=(idx_arr == 'both').sum()

