from nptdms import TdmsFile
from pyTDMS4 import read


def pyTDMS4_analog(file_name, pmt):
    """read in the data for a specific column in the analog file"""
    
    data_raw=read(file_name)
    keys1=data_raw[1].keys()
    for key in keys1:
        if str(key[-2]) == str(pmt):
            data=data_raw[1].get(key)
    return data

def pyTDMS4_ctr(file_name, trim = False):
    '''read in ctr data'''
    
    data_raw = read(file_name)
    data = data_raw[1][data_raw[1].keys()[0]]
    return data
    
def nptdms_analog(file_name, dev):
    tf = TdmsFile(file_name)
    grp = tf.groups()[0]
    
    chs = [dev+'/ai0', dev+'/ai1', dev+'/ai2', dev+'/ai3', dev+'/ai4', dev+'/ai5', dev+'/ai6']
    ch0 = tf.object(grp, chs[0]).raw_data
    # ch1 = tf.object(grp, chs[1]).raw_data
    # ch2 = tf.object(grp, chs[2]).raw_data
    # ch3 = tf.object(grp, chs[3]).raw_data
    # ch4 = tf.object(grp, chs[4]).raw_data
    # ch5 = tf.object(grp, chs[5]).raw_data
    # ch6 = tf.object(grp, chs[6]).raw_data
    return ch0
    
filename = 'E:/LSU_01/2017_12/Dev1/analog/GPGGA,00045800,302475218,N,0911072028,W,1,07,144,00024,M,-025,M,,57,3595017899.tdms'


