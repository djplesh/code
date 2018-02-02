import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import date
from datetime import timedelta
import sys

from tetra_tools.tools import *
import lightning




class Tetra(object):

    def __init__(self, loc, box_list):
        self.loc = fix_loc(loc)
        boxes = []
        if box_list == 'all' or box_list == 0:
            box_list = box_numbers(self.loc)
        for b in box_list:
            boxes.append(fix_num(b))
        self.box = boxes

    def date_str(self, day, month, year):

        day = fix_num(day)
        month = fix_num(month)
        year = fix_num(year)
        self.ts_date = year + '_' + month + '_' + day

    def get_ts(self, day, month, year):

        day = fix_num(day)
        month = fix_num(month)
        year = fix_num(year)
        self.ts_date = year + '_' + month + '_' + day
        all_data = np.array([])
        for b in self.box:
            fp = 'Y:/' + self.loc + '_' + b + '/' + year + '_' + month + '/ts_' + day + '.npz'
            if not os.path.exists(fp): continue
            ts_file = np.load(fp)
            for key in ts_file.keys():
                all_data = np.concatenate([all_data, ts_file[key]])
        self.ts = all_data

    def hist(self, bin_size):

        self.bin_size = bin_size
        if bin_size < .1:
            all_counts = np.array([])
            all_bins = np.array([])
            for i in range(24):
                ts_1hr = self.ts[np.where(np.logical_and(self.ts < 3600 * (i+1), self.ts > 3600 * i))[0]]
                bins = np.linspace(0, 3600, 3600/bin_size + 1) + 3600 * i
                counts = np.histogram(ts_1hr, bins)[0]
                all_counts = np.concatenate([all_counts, counts])
                if i != 23:
                    all_bins = np.concatenate([all_bins, bins[:-1]])
                else:
                    all_bins = np.concatenate([all_bins, bins[:]])
        else:
            all_bins = np.linspace(0, 86400, (86400/bin_size) + 1)
            all_counts = np.histogram(self.ts, all_bins)[0]
        bin_mid = all_bins[:-1] + bin_size/2

        self.counts = all_counts
        self.bin_mid = bin_mid
        self.average = np.average(all_counts)
        self.stddev = np.std(all_counts)

    def nearby_lightning(self, source = 'entln'):

        if not hasattr(self, 'source'): self.source = source
        self.strikes_8km = lightning.nearby(self.loc, self.ts_date, self.source)

    def event_search(self, sigma, source = 'entln', time_window = 5):

        if not hasattr(self, 'source'): self.source = source
        if not hasattr(self, 'strikes_8km'): self.strikes_8km = lightning.nearby(self.loc, self.ts_date, self.source)
        if not hasattr(self, 'time_window'): self.time_window = time_window
        self.min_counts = np.ceil(self.average + sigma * self.stddev)
        ec = np.where(self.counts > self.min_counts)[0]
        ec_num = len(ec)
        if ec_num != 0:
            #self.strikes_8km = lightning.nearby(self.loc, self.ts_date, source)
            num_strikes = len(self.strikes_8km[0])
            if ec_num < 100 and len(self.strikes_8km[0]) > 0:
                #print str(ec_num) + ' events above ' + str(sigma) + ' sigma on ' + str(self.ts_date)
                for x in ec:
                    ec_time_sec = x * self.bin_size
                    ec_lightning = lightning.recent(self.strikes_8km, ec_time_sec, self.time_window)
                    if len(ec_lightning[0]) != 0:
                        soonest = min(np.abs(ec_lightning[0] - ec_time_sec))
                        d = np.where(np.logical_or(ec_lightning[0] == ec_time_sec + soonest, ec_lightning[0] == ec_time_sec - soonest))[0][0]
                        nearest = min(ec_lightning[1])
                        n = np.where(ec_lightning[1] == nearest)[0][0]
                        print str(ec_time_sec) + ' on ' + str(self.ts_date)
                        print str(len(ec_lightning[0])) + ' lightning strikes within ' + str(self.time_window) + ' seconds of event'
                        print str('%.6f'%(soonest)) + ' seconds apart ' + str('%.3f'%(ec_lightning[1][d])) + ' kilometers away'
                        print str('%.3f'%(min(ec_lightning[1]))) + ' kilometers away ' +str('%.6f'%(np.abs(ec_lightning[0][n] - ec_time_sec))) + ' seconds apart'
                        print '\n'

    def plot_hist(self):

        plt.plot(self.bin_mid,self.counts)
        plt.ylabel('Counts (' + str(self.bin_size) + ' second bins)')
        plt.xlabel('Time (seconds) on ' + str(self.ts_date))
        plt.xlim([0,86400])
        plt.show()

    def plot_strikes(self):

        f, ax = plt.subplots(1)
        ax.plot(self.bin_mid,self.counts)
        ax.set_ylabel('Counts (' + str(self.bin_size) + ' second bins)')
        ax.set_xlim([0,86400])
        plt.xlabel('Time (seconds)')
        ax2 = ax.twinx()
        ax2.plot(self.strikes_8km[0], self.strikes_8km[1], lw = 0, marker = 'o', color = 'g', alpha = 0.8)
        ax2.set_ylabel('kilometers to lightning')
        plt.show()

    def loop_days(self, start_d, start_m, start_y, duration, bin_size, sigma, source = 'entln', window = 5):

        self.time_window = window
        self.source = source
        loop_day = date(start_y, start_m, start_d)
        n = duration/np.abs(duration)
        for loop_day in [loop_day + timedelta(x) for x in range(0, duration, n)]:

            self.date_str(loop_day.day, loop_day.month, loop_day.year)
            self.nearby_lightning(source)
            if len(self.strikes_8km[0]) == 0: continue
            try:
                self.get_ts(loop_day.day, loop_day.month, loop_day.year)
            except IOError:
                continue
            #print loop_day
            self.hist(bin_size)
            self.event_search(sigma)
