# -*- coding: utf-8 -*-
"""
Created on Mon May 16 10:53:20 2016

@author: DJ
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 11:17:05 2016
this will read in the analog tdms files containing adc information 
for a source and background run

after plotting both histograms they will be subtracted and a bar graph will be made
this is done for a single pvc at a time currently

plots
@author: DJ Pleshinger
"""

import os
from tetra_tools.pyTDMS4 import read
import numpy as np
import matplotlib.pyplot as plt


#########################################################################
'''get data for background files'''

adc_dev1_list=[]

for file in os.listdir('C:/Users/DJ Pleshinger/Documents/pr_may_trip/box8_dev2/analog_bkgd_night'):
    if file.endswith('.tdms'):
        adc_dev1_list.append('C:/Users/DJ Pleshinger/Documents/pr_may_trip/box8_dev2/analog_bkgd_night/'+file)

num_files=len(adc_dev1_list)
time_elapsed=num_files*10/60  #each file has 10minutes of data, this gives hours
print str(num_files)+' 10min files combined of background data'
        
          
pmt0_bkgd=[]
pmt1_bkgd=[]
pmt2_bkgd=[]
pmt3_bkgd=[]
pmt4_bkgd=[]
pmt5_bkgd=[]
gps_bkgd=[]
unk_bkgd=[]


for filename in adc_dev1_list:
    adc_dev1_data=read(filename)
    keys1=adc_dev1_data[1].keys()
    temp=[]
    #print keys1
    for key in keys1:
        temp=adc_dev1_data[1].get(key)
        x=key[-2]
        #print key
        #print x
        #print type(x)
        for line in temp:
            if x=='0':
                pmt0_bkgd.append(line)
            elif x=='1':
                pmt1_bkgd.append(line)
            elif x=='2':
                pmt2_bkgd.append(line)
            elif x=='3':
                pmt3_bkgd.append(line)
            elif x=='4':
                pmt4_bkgd.append(line)
            elif x=='5':
                pmt5_bkgd.append(line)
            elif x=='6':
                gps_bkgd.append(line)
            elif x=='7':
                unk_bkgd.append(line)
    
    

sz0=len(pmt0_bkgd)
sz1=len(pmt1_bkgd)
sz2=len(pmt2_bkgd)
sz3=len(pmt3_bkgd)
sz4=len(pmt4_bkgd)
sz5=len(pmt5_bkgd)
szg_1=len(gps_bkgd)
szu_1=len(unk_bkgd)
print sz0
#print sz1
#print sz2
#print sz3
#print sz4
#print sz5
#print szg_1

'''put an error check in here in case different sizes'''

sz_1=sz0-1             

bgo1_bkgd=[]
bgo2_bkgd=[]
bgo3_bkgd=[]

#print pmt4_bkgd[0:10]
#print pmt5_bkgd[0:10]

for i in range(0,sz_1):
    if(float(pmt0_bkgd[i])>0 and float(pmt1_bkgd[i])>0):
        bgo1_bkgd.append(np.sqrt(float(pmt0_bkgd[i])*float(pmt1_bkgd[i])))
for i in range(0,sz_1):
    if(float(pmt2_bkgd[i])>0 and float(pmt3_bkgd[i])>0):
        bgo2_bkgd.append(np.sqrt(float(pmt2_bkgd[i])*float(pmt3_bkgd[i])))
for i in range(0,sz_1):
    if(float(pmt4_bkgd[i])>0 and float(pmt5_bkgd[i])>0):
        bgo3_bkgd.append(np.sqrt(float(pmt4_bkgd[i])*float(pmt5_bkgd[i])))
        
bgo1_num_b=len(bgo1_bkgd)
bgo2_num_b=len(bgo2_bkgd)
bgo3_num_b=len(bgo3_bkgd)
print str(bgo1_num)+' events in bgo1 background'
print str(bgo2_num)+' events in bgo2 background'
print str(bgo3_num)+' events in bgo3 background'



################################################################
'''get spectra data with source'''

adc_dev1_list_s=[]

for file in os.listdir('C:/Users/DJ Pleshinger/Documents/pr_may_trip/box8_dev2/analog_th_night/'):
    if file.endswith('.tdms'):
        adc_dev1_list_s.append('C:/Users/DJ Pleshinger/Documents/pr_may_trip/box8_dev2/analog_th_night/'+file)

num_files=len(adc_dev1_list_s)
time_elapsed=num_files*10/60  #each file has 10minutes of data, this gives hours
print str(num_files)+' 10min files combined of source data'
        
          
pmt0_s=[]
pmt1_s=[]
pmt2_s=[]
pmt3_s=[]
pmt4_s=[]
pmt5_s=[]
gps_s=[]
unk_s=[]

for filename in adc_dev1_list_s:
    adc_dev2_data=read(filename)
    keys2=adc_dev2_data[1].keys()
    temp=[]
    for key in keys2:
        temp=adc_dev2_data[1].get(key)
        x=key[-2]
        for line in temp:
            if x=='0':
                pmt0_s.append(line)
            elif x=='1':
                pmt1_s.append(line)
            elif x=='2':
                pmt2_s.append(line)
            elif x=='3':
                pmt3_s.append(line)
            elif x=='4':
                pmt4_s.append(line)
            elif x=='5':
                pmt5_s.append(line)
            elif x=='6':
                gps_s.append(line)
            elif x=='7':
                unk_s.append(line)
    
sz0=len(pmt0_s)
sz1=len(pmt1_s)
sz2=len(pmt2_s)
sz3=len(pmt3_s)
sz4=len(pmt4_s)
sz5=len(pmt5_s)
szg_2=len(gps_s)
szu_2=len(unk_s)
'''put an error check in here in case different sizes'''

sz_2=sz0-1             

bgo1_s=[]
bgo2_s=[]
bgo3_s=[]

for i in range(0,sz_2):
    if(float(pmt0_s[i])>0 and float(pmt1_s[i])>0):
        bgo1_s.append(np.sqrt(float(pmt0_s[i])*float(pmt1_s[i])))
for i in range(0,sz_2):
    if(float(pmt2_s[i])>0 and float(pmt3_s[i])>0):
        bgo2_s.append(np.sqrt(float(pmt2_s[i])*float(pmt3_s[i])))
for i in range(0,sz_2):
    if(float(pmt4_s[i])>0 and float(pmt5_s[i])>0):
        bgo3_s.append(np.sqrt(float(pmt4_s[i])*float(pmt5_s[i])))
        
bgo1_num=len(bgo1_s)
bgo2_num=len(bgo2_s)
bgo3_num=len(bgo3_s)
print str(bgo1_num)+' events in bgo1 source'
print str(bgo2_num)+' events in bgo2 source'
print str(bgo3_num)+' events in bgo3 source'
print str(sz2)


###########################################################################
'''plot one pvc at a time'''
a,b,p1=plt.hist(bgo3_bkgd, alpha=0.5, bins=1000,histtype='step',color='white')
c,d,p2=plt.hist(bgo3_s, alpha=0.5, bins=1000,histtype='step',color='white')

bgo3_sub=c-a
#print bgo1_sub
#print c
#print a

bins=1000
ind=np.arange(bins)

plt.bar(ind,bgo3_sub,edgecolor='black',color='w')
plt.axis([0,1000,0,25000])
plt.annotate('bgo6 subtracted', xy=(400,20000))
plt.annotate(str(num_files)+' 10min files', xy=(400,15000))
plt.annotate(str(bgo3_num)+' events in bgo6 th file', xy=(400,10000))
plt.annotate(str(bgo3_num_b)+' events in bgo6 bkgd file', xy=(400,8000))
#plt.savefig('box8_bgo6_th_night.pdf')


############################################################################
'''plot one dev in 3 plots vertically, subtract background'''
'''bgo1'''
#plt.subplot(3,1,1)
#a,b,p1=plt.hist(bgo1_bkgd, alpha=0.5, bins=1000,histtype='step',color='white')
#c,d,p2=plt.hist(bgo1_s, alpha=0.5, bins=1000,histtype='step',color='white')
#
#bgo1_sub=c-a
##print bgo1_sub
##print c
##print a
#
#bins=1000
#ind=np.arange(bins)
#
#plt.bar(ind,bgo1_sub,color='red')
#plt.axis([0,1000,0,50000])
#
#
#'''bgo2'''
#plt.subplot(3,1,2)
#a,b,p1=plt.hist(bgo2_bkgd, alpha=0.5, bins=1000,histtype='step',color='white')
#c,d,p2=plt.hist(bgo2_s, alpha=0.5, bins=1000,histtype='step',color='white')
#
#bgo2_sub=c-a
##print bgo1_sub
##print c
##print a
#
#bins=1000
#ind=np.arange(bins)
#
#plt.bar(ind,bgo2_sub,color='red')
#plt.axis([0,1000,0,50000])
#
#
#'''bgo3'''
#plt.subplot(3,1,3)
#a,b,p1=plt.hist(bgo3_bkgd, alpha=0.5, bins=1000,histtype='step',color='white')
#c,d,p2=plt.hist(bgo3_s, alpha=0.5, bins=1000,histtype='step',color='white')
#
#bgo3_sub=c-a
##print bgo1_sub
##print c
##print a
#
#bins=1000
#ind=np.arange(bins)
#
#plt.bar(ind,bgo3_sub,color='red')
#plt.axis([0,1000,0,50000])

#plt.savefig('test2.pdf')

#############################################################################