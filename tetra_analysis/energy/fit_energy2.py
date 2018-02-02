import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy.optimize import curve_fit

def fit_e(bin_num = 20, alpha = 2.5, constant = 110000, s = 3):
    
    energy_file='C:/Users/tetra/all_energies.npz'
    energies = np.load(energy_file)['energy']
    
    ene_edge = np.power(10, np.linspace(-2,1,51))
    ene_means = np.sqrt(ene_edge[1:] * ene_edge[:-1])
    ene_widths = ene_edge[1:] - ene_edge[:-1]
    
    n_ene = np.histogram(energies, ene_edge)[0]
    sig_ene = np.sqrt(n_ene)
    
    dndE = n_ene/ene_widths
    

    
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    
    bins = np.linspace(0, 8, bin_num + 1)
    a,b,c = ax.hist(energies, bins, histtype='step', color = 'black')
    
    
    #equation that looks (by eye) good!!  wanted x**-1.5 but -2.5 looks better
    g = lambda x: constant * (x**-alpha) * (-.0323 * np.exp(-.0477 * x) + .0309) * (1 - .0592 * np.exp(-1.185 * x) + .461)
    
    x_values = np.linspace(0,8,200)[s:]
    y_values = []
    for x in x_values:
        y_values.append(g(x))
        
    ax.plot(x_values, y_values, color = 'black', linewidth = 1.5)
    
    plt.show()
    
def chi2_e(bin_num = 50, alpha = 3.5, amp = 100000):

    energies = np.load('C:/Users/tetra/all_energies.npz')['energy']    
    
    bins = np.linspace(0, 8, bin_num + 1)
    a,b,c = plt.hist(energies, bins, histtype='step', color = 'black')
    
    ene = np.sqrt(b[1:] * b[:-1])
    ene[0] = b[1]/2.0
    
    g = lambda x: amp * (x**-alpha) * (-.0323 * np.exp(-.0477 * x) + .0309) * (1 - .0592 * np.exp(-1.185 * x) + .461)
    
    ga = []
    for x in ene:
        ga.append(g(x))
        
    sigs = np.sqrt(a)
    
    v = []
    gv = []
    vsig = []
    for x in range(len(a)):
        if a[x] != 0:
            v.append(a[x])
            gv.append(ga[x])
            vsig.append(sigs[x])
    
    (((np.array(a) - np.array(ga))**2)/np.array(sigs)).sum


def func(x, a, b):
        return scalar_data[x] * a * es_new[x]**(-b)
        
def fit_e2():
       
    energies = np.load('C:/Users/tetra/all_energies.npz')['energy']    
    
    bins = np.linspace(0, 8, 50 + 1)
    a,b,c = plt.hist(energies, bins, histtype='step', color = 'black')
    anew = a[1:]
    
    ene = np.sqrt(b[1:] * b[:-1])
    ene[0] = b[1]/2.0
    es_new = ene[1:]

    e_air = []
    u_air = []
    with open('C:/Users/tetra/air_crosssection.txt') as f:
        for line in f.readlines():
            e_air.append(float(line.split()[0]))
            u_air.append(float(line.split()[1]))
    air_exp = np.exp(-np.array(u_air)*1.225e-3*160934)
    mu_air = interpolate.interp1d(np.array(e_air), air_exp, kind = 'cubic')
    mu = mu_air(es_new)
    
    e_bgo = []
    s_bgo = []
    with open('C:/Users/tetra/bgo_crosssection.txt') as f:
        for line in f.readlines():
            e_bgo.append(float(line.split()[0]))
            s_bgo.append(float(line.split()[1]))
    bgo_exp = np.exp(-np.array(s_bgo)*7.13*2.54)
    sig_bgo = interpolate.interp1d(np.array(e_bgo), bgo_exp, kind = 'cubic')
    sig = sig_bgo(es_new)    
    
    scalar_data = mu * (1 - sig)
    
    x_values = np.arange(0,49,1)
    #popt, pcov = curve_fit(func, x_values, anew)
    
    #fit_a = scalar_data * popt[0] * es_new**-popt[1]

    fit_a = scalar_data * 1.05234519e7 * es_new**(-5.80625927)
    plt.plot(es_new, fit_a)
    
    plt.show()
    
    
    
    