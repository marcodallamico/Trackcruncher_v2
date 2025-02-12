 
"""
SX PANEL:               DX PANEL:

COSTA TRACKS            NGUYEN TRACKS
- tracks                - tracks
- trackcruncher table       xxx
- my table              - My table
- sevn tables
"""


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd

pd.set_option('display.float_format', '{:.8f}'.format)

def table_2_array(pathtable, masstrack, tab):

    masstable = pathtable + 'mass.dat'
    table     = pathtable + tab

    df = pd.read_fwf(masstable, header=None)
    index = df[df[0] == masstrack].index[0]

    df   = pd.read_fwf(table, header=None)
    line = df.iloc[index].to_numpy()
    return line[~np.isnan(line)]


def compute_effective_temperature(luminosity, radius):
    # Stefan-Boltzmann constant in SI units (W m^-2 K^-4)
    sigma = 5.670374419e-8

    # Convert luminosity in solar units (L_sun) to watts (1 L_sun = 3.828e26 W)
    luminosity_solar = luminosity * 3.828e26

    # Convert radius in solar radii (R_sun) to meters (1 R_sun = 6.9634e8 m)
    radius_solar = radius * 6.9634e8

    # Compute the effective temperature using the Stefan-Boltzmann equation
    temperature = (luminosity_solar / (4 * np.pi * radius_solar**2 * sigma))**0.25

    return temperature


def tracks_2_array(path, masstrack, skiprow):

    if skiprow==4:
        dat = path + 'Z0.017Y0.279O_IN0.00OUTA1.74_F7_M{}.00.TAB'.format(masstrack)
    else:
        dat = path + 'Z0.017Y0.279O_IN0.00OUTA1.74_F7_M{}0.TAB'.format(masstrack)


    df = pd.read_csv(
        dat,
        sep=r"\s+",
        skiprows=skiprow,
        skipfooter=1,
        engine="python",
        usecols=['LOG_L','RSTAR']
    )
    # df.columns = df.columns.str.lower()
    L = 10 ** (df['LOG_L'].to_numpy())
    print('L',min(L),max(L))
    R = df['RSTAR'].to_numpy()
    R = R/6.96e10
    print('R',min(R),max(R))
    T = compute_effective_temperature(L,R)
    return L,T

###############
# NGUYEN 2022 #
###############

# TRACKS
path  = '/home/marco/Desktop/tracks_nguyen/VAR_ROT0.00_SH_Z0.017_Y0.279/'
La,Ta = tracks_2_array(path,2,4)
print('T',min(Ta),max(Ta))

# NEW TABLES
path = '/home/marco/Desktop/Trackcruncher_cutomized/tables_Nguyen/0017/'
Lb    = table_2_array(path, 2., 'lumi.dat')
R    = table_2_array(path, 2., 'radius.dat')
Tb    = compute_effective_temperature(Lb,R)
print('L',min(Lb),max(Lb))
print('R',min(R),max(R))
print('T',min(Tb),max(Tb))
###############
# COSTA 2025  #
###############

# TRACKS
path  = '/home/marco/Desktop/tracks_costa/Z0.017/'
L1,T1 = tracks_2_array(path,2.2,0)


# NEW TABLES
path = '/home/marco/Desktop/Trackcruncher_cutomized/tables_Costa_filtertracks/0017/'
L2    = table_2_array(path, 2.2, 'lumi.dat')
R    = table_2_array(path, 2.2, 'radius.dat')
T2    = compute_effective_temperature(L2,R)

# Trackcruncher TABLES
path = '/home/marco/Desktop/tables_costa/0017/'
L3    = table_2_array(path, 2.2, 'lumi.dat')
R    = table_2_array(path, 2.2, 'radius.dat')
T3    = compute_effective_temperature(L3,R)

# SEVN TABLES
path = '/home/marco/Desktop/sevn/tables/SEVNtracks_parsec_ov05_AGB/0017/'
L4    = table_2_array(path, 2.2, 'lumi.dat')
R    = table_2_array(path, 2.2, 'radius.dat')
T4    = compute_effective_temperature(L4,R)



lw = 5.

# Create figure and gridspec layout
fig = plt.figure(figsize=(10, 5))
gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])  # Two equally sized panels

# First HR diagram
ax1 = plt.subplot(gs[0])

ax1.plot(Ta, La, c='darkred',linewidth=lw,label='Nguyen2022')
ax1.plot(Tb, Lb, linestyle='-', marker='o', c='black', linewidth=0.5,label='newtab')

ax1.set_xlabel(r'$\log_{10}(T_{\rm eff})$')
ax1.set_ylabel(r'$\log_{10}(L)$')
ax1.invert_xaxis()  # Traditional HR diagram convention
ax1.legend()

# Second HR diagram
ax2 = plt.subplot(gs[1])

ax2.plot(T1, L1, c='darkred',linewidth=lw,label='Costa2025')
ax2.plot(T2, L2, linestyle='-', marker='o', c='black', linewidth=0.5,label='newtab')
# ax2.plot(T3, L3, linestyle='-', marker='o', c='blue', linewidth=0.5,label='trackcruncher')
# ax2.plot(T4, L4, linestyle='-', marker='o', c='gold', linewidth=0.5,label='sevntab')

ax2.set_xlabel(r'$\log_{10}(T_{\rm eff})$')
ax2.invert_xaxis()
ax2.legend()

# Adjust layout
plt.tight_layout()
plt.show()
