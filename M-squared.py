#%% Importing libraries

import glob
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rc
from scipy.special import erfc as erfc
from scipy.misc import derivative as der
from scipy.optimize import curve_fit

#%% Setting a "LaTeX-like" plotting style

plt.style.use('default')
rc('font', **{'family': 'DejaVu Sans', 'serif': ['Computer Modern']})
rc('text', usetex=True)

#%% For loop to generate all P vs x plots with custom erfc fitting

sets = glob.glob('Data*.txt')
sets.sort()
j    = 1 # custom index for saving plots without overwriting them

# Initializing for loop

for i in sets:
    Data = np.loadtxt(i, comments = '#')

# Defining variables and functions

    z    = Data[0, 0] # [mm]
    x    = Data[:, 1] # [um]
    P    = Data[:, 2] # [W]
    dx   = Data[:, 3] # [um]
    dP   = Data[:, 4] # [W]
    P0   = np.amin(P) # [W]
    Pmax = np.amax(P) # [W]

    def fit(x, x0, w):
        return P0+Pmax/2*erfc(np.sqrt(2)*(x-x0)/w) # [W]

    xfit = np.linspace(np.amin(x), np.amax(x), 300) # [um]
    pi   = [(np.amax(x)-np.amin(x))/2, 1800]

# Fitting

    popt, pcov = curve_fit(fit, x, P, pi)
    sigma = np.sqrt([pcov[0, 0], pcov[1, 1]])
    fit_values = fit(xfit, popt[0], popt[1])   # [W]

    w  = popt[1]  # [um]
    dw = sigma[1] # [um]

# Plotting erfc

    plt.figure()
    plt.errorbar(x, P, xerr = dx, yerr = dP, color = 'b', marker = 'd', linestyle = 'None', label = 'Dati sperimentali', zorder = 1)
    plt.plot(xfit, fit_values, '-r', label = 'Fit', zorder = 2)

    plt.legend(loc = 'best', fontsize = 12, fancybox = False, edgecolor = 'k')

    plt.xlabel('$x$ ($\mu$m)')
    plt.ylabel('$P$ (W)')

    plt.savefig('Plot%d.png' % j, dpi = 300)

# Saving results

    f = open('Waists', 'a')
    f.write('%.2f\t%.2f\t0.3\t%.2f\n' % (z, w, dw))
    f.close()

# Manually incrementing j

    j = j+1

#%% Finding w0 and M2

# Defining variables and functions

Waists = np.loadtxt('Waists', comments = '#')

z  = Waists[:, 0] # [mm]
w  = Waists[:, 1] # [um]
dz = Waists[:, 2] # [mm]
dw = Waists[:, 3] # [um]
wl = 1030         # [nm]
D  = 7            # [mm]
dD = 1            # [mm]
F  = 300          # [mm]

def fit(z, w0, z1, zR):
    return w0*np.sqrt(1+((z-z1)/zR)**2) # [um]

xfit = np.linspace(np.amin(z), np.amax(z), 300) # [mm]
pi   = [100, 250, 30]

# Fitting

popt, pcov = curve_fit(fit, z, w, sigma = dw, absolute_sigma = False, p0 = pi)
sigma = np.sqrt([pcov[0, 0], pcov[1, 1], pcov[2, 2]])
fit_values = fit(xfit, popt[0], popt[1], popt[2]) # [mm]

w0  = popt[0]  # [um]
dw0 = sigma[0] # [um]
zR  = -popt[2]  # [mm]
dzR = sigma[2] # [mm]

# Calculating ideal beam

w0_th  = 2*wl*F/np.pi/D/1000 # [um]
dw0_th = dD/D*w0_th          # [um]

zR_th  = 8*wl*F**2/np.pi/D**2/1000/1000 # [mm]
dzR_th = dD/D*zR_th

th_up = fit(xfit, w0_th+dw0, popt[1], zR_th+dzR) # [um]
th_lo = fit(xfit, w0_th-dw0, popt[1], zR_th-dzR) # [um]
th_ct = fit(xfit, w0_th, popt[1], zR_th)         # [um]

# Plotting

plt.figure()

plt.errorbar(z, w, xerr = dz, yerr = dw, color = 'b', marker = 'd', linestyle = 'None', label = 'Dati sperimentali', zorder = 1)
plt.plot(xfit, fit_values, '-r', label = 'Fit', zorder = 2)
plt.plot(xfit, th_ct, '-g', label = 'Fascio ideale ($M^2=1.0$)', zorder = 3)
plt.fill_between(xfit, th_up, th_lo, facecolor = 'g', edgecolor = 'g', linestyle = '--', alpha = 0.3)

plt.legend(loc = 'best', fontsize = 12, fancybox = False, edgecolor = 'k')

plt.xlabel('$z$ (mm)')
plt.ylabel('$w$ ($\mu$m)')

plt.savefig('Plot%d.png' % j, dpi = 300)

# Calculating O0

O0  = w0/zR
dO0 = (np.abs(dw0/w0)+np.abs(dzR/zR))*O0

# Calculating M2

M2  = w0**2/zR*np.pi/wl
dM2 = (np.abs(2*dw0/w0)+np.abs(dzR/zR))*M2

# Saving results

f = open('Results', 'a')
f.write('%.3f\t%.3f\t%.3f\t%.3f\n%.3f\t%.3f\t%.3f\t%.3f\n\n' % (w0, zR, M2, O0, dw0, dzR, dM2, dO0))
f.close()
