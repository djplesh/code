import numpy as np
import matplotlib.pyplot as plt


def fit_e(energy_file='C:/Users/tetra/all_energies.npz', x=160934):
    
    energies = np.load(energy_file)['energy']
    
    ene_edge = np.power(10, np.linspace(-2,1,51))
    ene_means = np.sqrt(ene_edge[1:] * ene_edge[:-1])
    ene_widths = ene_edge[1:] - ene_edge[:-1]
    
    n_ene = np.histogram(energies, ene_edge)[0]
    sig_ene = np.sqrt(n_ene)
    
    dndE = n_ene/ene_widths
    
    # fig = plt.figure()
    # ax = fig.add_subplot(1,1,1)
    
    # ax.plot(ene_means, dndE, marker='s', linewidth=0)
    # ax.set_yscale('log')
    # ax.set_xscale('log')
    
    # y_values = dndE[35:45]
    # x_values = ene_means[35:45]
    # np.polyfit(np.log10(x_values),np.log10(y_values),1)
    
    e_air = []
    u_air = []
    
    with open('C:/Users/tetra/nist_mu_air.txt') as f:
        for line in f.readlines():
            e_air.append(float(line.split()[0]))
            u_air.append(float(line.split()[0]))
    p_air = 1.225e-3
    u = []
    for i in u_air:
        u.append(i * p_air)
    u_air = u
    del u 
    
    atten_effect = []
    for u in u_air:
        atten_effect.append(np.exp(-1*u*x))
    
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    
    ax.plot(e_air, atten_effect, marker='s', linewidth=0)
    plt.show()
    
    
    #equation that looks (by eye) good!!  wanted x**-1.5 but -2.5 looks better
    g2 = lambda x: (x**-2.5) * (-.0323 * np.exp(-.0477 * x) + .0309) * (1 - .0592 * np.exp(-1.185 * x) + .461)
    