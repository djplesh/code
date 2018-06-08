import os
import numpy as np
import glob
import datetime as dt

import tetra_tools.tools as tool







def tetra_check():



    boxlist = tool.box_list('all')
    devices = ['Dev1', 'Dev2']
    ftype = ['analog', 'ctr1', 'ctr2', 'ctr3']
    today = dt.date.today()
    folder = today.strftime('%Y_%m')
    
    for b in boxlist:
        for dev in devices:
            for f in ftype:
            
                fpath = 'E:/{0}/{1}/{2}/{3}/*'.format(b, folder, dev, f)
                flist = glob.glob(fpath)
                latestfile = max(flist, key=os.path.getctime)
                
                ftime = os.path.getctime(latestfile)
                ftime = dt.datetime.fromtimestamp(int(ftime)).strftime('%Y-%m-%d_%H:%M:%S')
                
                fsize = os.path.getsize(latestfile)
                
                try:
                    gps_lock = latestfile.split(',')[6]
                    if gps_lock == '0': 
                        gps_lock = 'no gps lock'
                    else
                        gps_lock = 'gps lock'
                except IndexError:
                    gps_lock = 'no GPGGA string'