import numpy as np
import matplotlib.pyplot as plt
import time

from tools import *



class Tetra(object):

    def __init__(self, loc, box):
        self.loc = fix_loc(loc)
        self.box = fix_num(box)
        
    def get_ts(self, day, month, year):
    
        day = fix_num(day)
        month = fix_num(month)
        year = fix_num(year)    
        fp = 'Y:/' + self.loc + '_' + self.box + '/' + year + '_' + month + '/ts_' + day + '.npz'
        
        ts_file = np.load(fp)
        all_data = np.array([])
        for key in ts_file.keys():
            all_data = np.concatenate([all_data, ts_file[key]])
        self.ts = all_data
        
    
    def hist(self, bin_size):
    
        start_time = time.time()
        
        if bin_size < .1:
            all_counts = np.array([])
            all_bins = np.array([])
            for i in range(24):
                ts_1hr = self.ts[np.where(np.logical_and(self.ts < 3600 * (i+1), self.ts > 3600 * i))[0]]
                bins = np.linspace(0, 3600, 3600/bin_size + 1) + 3600 * i
                counts = np.histogram(ts_1hr, bins)[0]
                all_counts = np.concatenate([all_counts, counts])
                all_bins = np.concatenate([all_bins, bins[:-1]])         
        else:
            all_bins = np.linspace(0, 86400, (86400/bin_size) + 1)
            all_counts = np.histogram(self.ts, all_bins)[0]       
        bin_mid = all_bins[:-1] + bin_size/2
        
        self.counts = all_counts
        self.bin_mid = bin_mid
        self.average = np.average(all_counts)
        self.stddev = np.std(all_counts)
        print time.time() - start_time   
        #return all_counts, bin_mid
        
    def plot_hist(self):
    
        plt.plot(self.bin_mid,self.counts)
        plt.xlim([0,86400])
        plt.show()
        
    def threshold(self, sigma):
    
        self.min_counts = np.ceil(self.average + sigma * self.stddev)