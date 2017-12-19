from get_energy import get_pmt
from ctr_to_timestamp3 import get_pps
from ctr_to_timestamp3 import get_times

import numpy as np


def comp(filenames):


    adc_file = path0 + 'analog/' + filename
    ctr1_file = path0 + 'ctr1/' + filename

    gps = get_pmt(filenames[3], 'gps')
    gps_pos = np.where(np.array(gps) > 2500)
    
    pos, pps_ctrs, clks = get.get_pps(filenames[0])
    ctr1_times = get.get_times(filenames[0], pps_ctrs, clks, 1)
    
    times_clean = []
    for x in range(len(ctr1_times)-1):
        if np.abs(ctr1_times[x] - ctr1_times[x+1]) > .000004:
            times_clean.append(ctr1_times[x])
    times_clean.append(ctr1_times[-1])
    times_clean = np.array(times_clean)
    
    test1 = []
    for x in range(len(pos)):
        test1.append(np.where(times_clean == ctr1_times[pos[x]]))
    clean_pos=[]
    for x in test1:
        clean_pos.append(x[0][0])
    clean_pos2 = clean_pos[:-1]
    
    gps_pos = np.array(gps_pos)
    diff2 = clean_pos2 - gps_pos
    
    return  diff2
    