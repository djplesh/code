import subprocess as sp
from monthdelta import monthdelta
from datetime import timedelta
from datetime import date
import urllib
import os

from tetra_tools.tools import box_list


def get_tetra2():

    boxes = box_list('all')
    d = date.today() - timedelta(1)
    month_dir = '/' + d.strftime("%Y_%m") + '/'
    old = date(d.year, d.month, 1)
    oldest = old.strftime("%Y%m%d")
    new = old + monthdelta(1)
    newest = new.strftime("%Y%m%d")
    for box in boxes:
        x = sp.Popen('robocopy Z:\\' + box + '\\ ' + ' E:/' + box + month_dir + ' *.* ' + '/MAXAGE:' + oldest + ' /MINAGE:' + newest + ' /E')
        x.wait() #wait for each box to complete before starting next



def get_wwlln(year = None, month = None, day = None):
    #default is one week prior, files are uploaded a week delayed
    
    if day == None: d = date.today() - timedelta(7)
    else: d = date(year, month, day)
    folder = d.strftime("%Y_%m")
    output_path = 'C:/Users/tetra/lightning/WWLLN/' + folder
    if not os.path.exists(output_path): os.makedirs(output_path)
    for i in range(1, d.day+1):
        x = date(d.year, d.month, i)
        path = output_path + '/A' + x.strftime("%Y%m%d") + '.loc'
        if not os.path.isfile(path):
            url = 'http://LSU:deirdreWWLLN17@wwlln.net/hostdata/A' + x.strftime("%Y%m%d") + '.loc'
            urllib.urlretrieve(url, filename = path)
