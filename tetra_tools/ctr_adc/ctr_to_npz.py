from datetime import date
from datetime import timedelta
import tetra_analysis.timestamps.ctr_to_timestamp3 as get
import numpy as np
import os



def conv_data(box_num, start_date, end_date = None):
    """call the box number and date range to convert the ctr files to two saved
    files of lists containing the timestamp information
    """
    # start_time = time.time()
    
    if end_date == None or end_date == '': end_date = start_date
    #path0 = 'C:/Users/tetra/data/' + box_num + '/'
    path0 = 'Y:/' + box_num + '/'
    start_day, start_month, start_year = get.date_to_ints(start_date)
    end_day, end_month, end_year = get.date_to_ints(end_date)
    loop_day = date(start_year, start_month, start_day)
    loop_end = date(end_year, end_month, end_day)

    while loop_day < loop_end + timedelta(1):

        date_str = get.ints_to_date(loop_day.day, loop_day.month, loop_day.year)
        folder = date_str[5:7] + '_' + date_str[0:4] + '/'
        output_path = path0 + '/' + folder
        
        dev1_file = output_path + 'Dev1_' + date_str[8:10] + '.npy'
        dev2_file = output_path + 'Dev2_' + date_str[8:10] + '.npy'    
        if os.path.isfile(dev1_file) and os.path.isfile(dev2_file):
            
            dev1_data = np.load(dev1_file)
            dev2_data = np.load(dev2_file)
            bgo4 = np.array(dev1_data[0])
            bgo5 = np.array(dev1_data[1])
            bgo6 = np.array(dev1_data[2])
            bgo1 = np.array(dev2_data[0])
            bgo2 = np.array(dev2_data[1])
            bgo3 = np.array(dev2_data[2])
            
            file_ts = output_path + 'ts_' + date_str[8:10]
            np.savez(file_ts, bgo1=bgo1, bgo2=bgo2, bgo3=bgo3, bgo4=bgo4, bgo5=bgo5, bgo6=bgo6) 
            
            os.remove(dev1_file)
            os.remove(dev2_file)
        
        
        
        hist_file = output_path + 'hist_' + date_str[8:10] + '.npy'       
        if os.path.isfile(hist_file):
            
            hist_data = np.load(hist_file)
            bins = []
            counts = []
            for x in hist_data:
                bins.append(np.int32(x[0]/.002))
                counts.append(np.int16(x[1]))    
            bins = np.array(bins)
            counts = np.array(counts)
            
            new_hist = output_path + 'hist_' + date_str[8:10]
            np.savez(new_hist, bins=bins, counts=counts)
            
            os.remove(hist_file)
        
        loop_day = loop_day + timedelta(1)
        
        