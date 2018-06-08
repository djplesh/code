import numpy as np
import matplotlib.pyplot as plt
import time
import datetime as dt
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

        
    def get_ts(self, day, month, year, keys = 'all'):

        day = fix_num(day)
        month = fix_num(month)
        year = fix_num(year)
        if keys == 'all': keys = ['bgo1','bgo2','bgo3','bgo4','bgo5','bgo6']
        #date_str = year + '_' + month + '_' + day
        timestamps = np.array([])
        for b in self.box:
            #fp = 'Y:/' + self.loc + '_' + b + '/' + year + '_' + month + '/ts_' + day + '.npz'
            fp = 'Y:/{0}_{1}/{2}_{3}/ts_{4}.npz'.format(self.loc, b, year, month, day)
            if not os.path.exists(fp): continue
            ts_file = np.load(fp)
            for key in ts_file.keys():
                if key in keys:
                    timestamps = np.concatenate([timestamps, ts_file[key]])
        return timestamps
        
    def hist(self, bin_size, ts):

        self.bin_size = bin_size
        if bin_size < .1:
            all_counts = np.array([])
            all_bins = np.array([])
            for i in range(24):
                ts_1hr = ts[np.where(np.logical_and(ts < 3600 * (i+1), ts > 3600 * i))[0]]
                bins = np.linspace(0, 3600, 3600/bin_size + 1) + 3600 * i
                counts = np.histogram(ts_1hr, bins)[0]
                all_counts = np.concatenate([all_counts, counts])
                if i != 23:
                    all_bins = np.concatenate([all_bins, bins[:-1]])
                else:
                    all_bins = np.concatenate([all_bins, bins[:]])
        else:
            all_bins = np.linspace(0, 86400, (86400/bin_size) + 1)
            all_counts = np.histogram(ts, all_bins)[0]
        bin_mid = all_bins[:-1] + bin_size/2

        return all_counts, bin_mid

    def sig_search(self, counts, sigma, d_str):

        ave_rate = np.average(counts)
        stddev = np.std(counts)
        min_counts = np.ceil(ave_rate + sigma * stddev)
        ec = np.where(counts > min_counts)[0]
        ec_num = len(ec)
        self.trigs = ec * self.bin_size
        if ec_num > 0:
            print d_str, ec_num

    def event_search(self, counts, bin_mid, strikes_8km, d_str, bin_size = .002, sigma = 20, f_out = None, source = 'entln', window = 5):

        ave_rate = np.average(counts)
        stddev = np.std(counts)
        min_counts = np.ceil(ave_rate + sigma * stddev)
        ec = np.where(counts > min_counts)[0]
        ec_num = len(ec)
        ec_ts = []
        if ec_num != 0:
            num_strikes = len(strikes_8km[0])
            if ec_num < 1000 and len(strikes_8km[0]) > 0:
                for x in ec:
                    ec_time = x * bin_size
                    ec_light = lightning.recent(strikes_8km, ec_time, window)
                    if len(ec_light[0]) != 0:
                        ec_ts.append(ec_time)
                        soonest = min(np.abs(ec_light[0] - ec_time))
                        t = np.where(np.logical_or(ec_light[0] == ec_time + soonest, ec_light[0] == ec_time - soonest))[0][0]
                        nearest = min(ec_light[1])
                        n = np.where(ec_light[1] == nearest)[0][0]
                        line1 = str(ec_time) + ' on ' + d_str
                        line2 = str(len(ec_light[0])) + ' lightning strikes within ' + str(window) + ' sec of event'
                        line3 = str('%.6f'%(soonest)) + ' sec apart ' + str('%.3f'%(ec_light[1][t])) + ' kms away'
                        line4 = str('%.3f'%(min(ec_light[1]))) + ' kms away ' +str('%.6f'%(np.abs(ec_light[0][n] - ec_time))) +' sec apart'
                        if not f_out:
                            print line1, '\n', line2, '\n', line3, '\n', line4, '\n'
                        else:
                            with open(f_out, 'a') as f:
                                f.write(line1 + '\n' + line2 + '\n' + line3 + '\n' + line4 + '\n' + '\n')
        self.ecs = ec_ts

    def plot_hist(self, counts, bin_mid, bin_size, date_str):

        plt.plot(bin_mid,counts)
        plt.ylabel('Counts (' + str(bin_size) + ' second bins)')
        plt.xlabel('Time (seconds) on ' + date_str)
        plt.xlim([0,86400])
        plt.show()


    def plot_ec(self, ts, bin_size, time_window):
    
        for x in self.ecs:
            print x
            max_t = x + time_window
            min_t = x - time_window
            ec_ts = ts[np.logical_and(ts > min_t, ts < max_t)]
            bin_num = np.linspace(min_t, max_t, (max_t - min_t)/bin_size)
            counts = np.histogram(ec_ts, bin_num)[0]
            bin_mid = bin_num[:-1] + bin_size/2
            plt.plot(bin_mid, counts)
            plt.xlim([min_t,max_t])
            plt.ylim([0,max(counts)+5])
            plt.show()

    def loop_days(self, d_str, duration = 1, bin_size = .002, sigma = 20, window = 5, source = 'wwlln', f_out = None):
        
        loop_day = dt.datetime.strptime(d_str, "%Y_%m_%d").date()
        n = duration/np.abs(duration)
        if f_out:
            f_out = 'C:/Users/tetra/analysis/' + f_out + '.txt'
            with open(file_out, 'a') as f:
                f.write(self.loc + ' ' + str(self.box) + '\n')
                f.write('from ' + str(loop_day) + ' until ' + str(loop_day + dt.timedelta(duration)) + '\n')
                f.write(str(bin_size) + ' second bins at ' + str(sigma) + ' sigma above daily background rate' + '\n')
                f.write('using ' + source + ' to search for lightning strikes within ' + str(window) + ' seconds of event' + '\n' + '\n')
        
        for loop_day in [loop_day + dt.timedelta(x) for x in range(0, duration, n)]:
            d_str = ints_to_date(loop_day.day, loop_day.month, loop_day.year)
            strikes_8km = lightning.nearby(self.loc, loop_day, source)
            if len(strikes_8km[0]) == 0: continue
            try:
                timestamps = self.get_ts(loop_day.day, loop_day.month, loop_day.year)
            except IOError:
                continue
            counts, bin_mid = self.hist(bin_size, timestamps)
            self.event_search(counts, bin_mid, strikes_8km, d_str, bin_size, sigma, f_out, source, window)
            
            
    def loop_days2(self, d_str, duration = 1, bin_size = .002, sigma = 20):
        
        loop_day = dt.datetime.strptime(d_str, "%Y_%m_%d").date()
        n = duration/np.abs(duration)

        for loop_day in [loop_day + dt.timedelta(x) for x in range(0, duration, n)]:
            d_str = ints_to_date(loop_day.day, loop_day.month, loop_day.year)
            try:
                timestamps = self.get_ts(loop_day.day, loop_day.month, loop_day.year)
            except IOError:
                continue
            counts, bin_mid = self.hist(bin_size, timestamps)

            self.sig_search(counts, sigma, d_str)


