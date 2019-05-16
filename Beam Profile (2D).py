#%% Importing libraries

import os
import glob
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import rc
from mpl_toolkits.mplot3d import Axes3D
from scipy.special import erfc as erfc
from scipy.optimize import curve_fit

#%% Setting a "LaTeX-like" plotting style

plt.style.use('default')
rc('font', **{'family': 'DejaVu Sans', 'serif': ['Computer Modern']})
rc('text', usetex=True)

#%% For loop to reconstruct beam profile

# Initializing data sets

sets = glob.glob('Data*.txt')
sets.sort()
j    = 1 # custom index for saving plots without overwriting them

# Initializing for loop

for i in sets:
    Data = np.loadtxt(i, comments = '#')

# Defining variables and functions

    z    = Data[:, 0] # [mm]
    x    = Data[:, 1] # [um]
    P    = Data[:, 2] # [W]
    dx   = Data[:, 3] # [um]
    dP   = Data[:, 4] # [W]
    P0   = np.amin(P)
    Pmax = np.amax(P)

    def fit(x, x0, w):
        return P0+Pmax/2*erfc(np.sqrt(2)*(x-x0)/w) # [W]

    xfit = np.linspace(np.amin(x), np.amax(x), 300) # [um]
    pi   = [(np.amax(x)-np.amin(x))/2, 1800]

# Fitting

    popt, pcov = curve_fit(fit, x, P, pi)
    sigma = np.sqrt([pcov[0, 0], pcov[1, 1]])
    fit_values = fit(xfit, popt[0], popt[1])

    w  = popt[1]  # [um]
    dw = sigma[1] # [um]

# Calculating derivative

    def prime(f, a, h):
        return (f(a+h)-f(a-h))/(2*h)

    def fun(x):
        return fit(x, popt[0], w)

    g = -prime(fun, x, 0.001)*1000

# Plotting 2D gaussian profile

    fig = plt.figure()
    grid = plt.GridSpec(2, 8)

    ax1 = fig.add_subplot(grid[1, :4])
    ax2 = fig.add_subplot(grid[1, 4:5])

    ax1.plot(x, g, '-r')
    ax1.set_xlim(2000, 11000)
    ax1.set_ylim(0, 8)
    ax1.set_xlabel('$x$ ($\mu$m)')
    ax1.set_ylabel('$\partial P$ (u.a.)')

    ax2.axhline(z[j-1], color = 'r')
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 450)
    ax2.set_ylabel('$z$ (mm)')
    ax2.set_xticks([])
    ax2.yaxis.set_label_position('right')
    ax2.yaxis.set_ticks_position('right')
    plt.savefig('./frames/%d.png' % j, dpi = 300)

# Manually incrementing j

    j = j+1

#%% Converting plots into a gif

gif_name = 'Profile_Evolution'
frames = glob.glob('./frames/*.png')
list.sort(frames, key = lambda x: int(x.split('./frames/')[1].split('.png')[0]))

with open('frames.txt', 'w') as file:
    for i in frames:
        file.write("%s\n" % i)

os.system('convert -delay 60 @frames.txt {}.gif'.format(gif_name))
