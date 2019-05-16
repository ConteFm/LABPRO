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

# Initializing 3D frame

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1, projection = '3d')
ax.view_init(20, 140)

ax.set_xlabel('$x$ ($\mu$m)')
ax.set_ylabel('$z$ (mm)')
ax.set_zticklabels([])

cmap = mpl.cm.get_cmap('plasma')
norm = mpl.colors.Normalize(vmin=0, vmax=10)

# Initializing data sets

sets = glob.glob('Data*.txt')
sets.sort()

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

# Plotting static 3D gaussian profile

    k = np.max(g)
    rgba = cmap(norm(k))
    ax.plot3D(x, z, g, color = rgba)

sm = plt.cm.ScalarMappable(cmap = cmap, norm = norm)
sm.set_array([])
cb = fig.colorbar(sm, shrink = 0.6, aspect = 13)
cb.ax.set_title('$\partial P$ (u.a.)')

plt.savefig('Profile.png', dpi = 300)

# Generating frames for gif of rotating beam profile

for angle in range(0, 360):
    ax.view_init(20, angle)
    plt.savefig('./frames/%d.png' % angle, dpi = 150)

#%% Converting frames into a gif

gif_name = 'Profile_Rotation'
frames = glob.glob('./frames/*.png')
list.sort(frames, key = lambda x: int(x.split('./frames/')[1].split('.png')[0]))

with open('frames.txt', 'w') as file:
    for i in frames:
        file.write("%s\n" % i)

os.system('convert @frames.txt {}.gif'.format(gif_name))
