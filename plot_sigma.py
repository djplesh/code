# -*- coding: utf-8 -*-
"""
Created on Wed Mar 08 17:27:01 2017

read in timestamp files from get_timestamps, sum over boxes if desired
in 2ms time bins, plot histogram of values above various sigma

@author: DJ Pleshinger
"""


#import cPickle
import numpy as np
import matplotlib.pyplot as plt

from nearby_lightning2 import nearby_lightning



##############################################################################
##############################################################################    
def get_bins(c, min_bin):    
    """return bins with at least min threshold counts"""
    
    b2a = np.where(c > min_bin)
    b2b = np.where(c < 500)  #elsiminates periodic noise trigger ~900
    b2c = np.intersect1d(b2a, b2b)    
    return b2c

def get_nearest(array, value):    
    '''find the nearest value in an array'''
    
    idx = (np.abs(array - value)).argmin()
    return idx

def get_focus(data, mi, ma):    
    """obtain data between a min and max value or time"""
    
    focus = []
    for line in data:
        if line > mi and line < ma:
            focus.append(line)            
    return focus
       
##############################################################################
##############################################################################        
##############################################################################
##############################################################################        
##############################################################################        
def rates(box_num, date_str, path0 = None):
    """search bgo data for candidate events above user defined threshold"""
   
    folder = date_str[5:7] + '_' + date_str[0:4] + '/'
   

    if not path0: 
        path = 'D:/rates/' + box_num + '/' + folder
    else:
        path = path0 + box_num + '/' + folder
        
        
#    dev1_file =  path + 'Dev1_' + date_str[8:] + '.npy'
#    dev2_file =  path + 'Dev2_' + date_str[8:] + '.npy'  
#    dev1_data = np.load(dev1_file)
#   
#    dev2_data = np.load(dev2_file)
#    sum_data = np.array(dev1_data[0] + dev1_data[1] + dev1_data[2] + \
#                        dev2_data[0] + dev2_data[1] + dev2_data[2])
#    strikes_5mi = nearby_lightning(box_num, date_str)
#    
#    dists = []
#    near_data = []
#    far_data = []
#    for line in sum_data:
#        x = get_nearest(strikes_5mi, line)
#        if np.abs(line - strikes_5mi[x]) < 7:
#            near_data.append(line)
#            dists.append([line, strikes_5mi[x]])
#        else:
#            far_data.append(line)
    
#    bins_num = np.linspace(0, 86400, 3600*500*24 + 1, dtype = np.float64)        
#    bgo, bins = np.histogram(sum_data, bins=bins_num)
    
    hist_file = path + 'hist_' + date_str[8:] + '.npy'
    hist_data = np.load(hist_file)
    bgo = hist_data[:,1]
    
    ave = np.sum(hist_data, axis=0)[1]/43200000
    std_counts = np.sqrt((np.sum((hist_data-ave)**2, axis = 0)[1] \
    + (43200000 - len(hist_data))*ave**2)/(43200000-1))
#    sigma = [i*std_counts + ave_counts for i in range(100)]
    above = bgo - ave
    above[above < 0] = 0
    bin_sig = above / std_counts
    bin_sig = np.floor(bin_sig).astype(np.int32)
    bin_sig = bin_sig[bin_sig >= 0]
    n_bin = np.bincount(bin_sig)
    plt.plot(n_bin, lw = 0, marker = 'o')
    plt.yscale('log', noposy = 'clip')
    plt.axis([0,100,0,max(n_bin)+10000000])

#    near, bins = np.histogram(near_data,bins_num)
#    far, bins = np.histogram(far_data,bins_num)
#    
#    print len(near_data)
#    print len(far_data)

#    plt.hist(bgo, sigma, histtype = 'bar')
#    plt.hist(near, sigma, histtype = 'bar', color = 'blue', alpha = 0.5, label = 'near')
#    plt.hist(far, sigma, histtype = 'bar', color = 'red', alpha = 0.5, label = 'far')
#    plt.legend(loc = 'upper right')
#    plt.yscale('log', nonposy = 'clip')
    plt.show()

 #   return bgo, bin_sig  , ave, std_counts                         

                



        

