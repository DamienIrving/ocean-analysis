"""
Filename:     plot_regression_coefs.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot regression coefficients from drift analysis  

"""

# Import general Python modules

import sys
import os
import re
import pdb
import argparse

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import cmdline_provenance as cmdprov

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'ocean-analysis':
        break

import matplotlib as mpl
mpl.rcParams['axes.labelsize'] = 'large'
mpl.rcParams['axes.titlesize'] = 'x-large'
mpl.rcParams['xtick.labelsize'] = 'medium'
mpl.rcParams['ytick.labelsize'] = 'medium'
mpl.rcParams['legend.fontsize'] = 'large'


# Define functions 

labels = {"netTOA vs hfdsgeou regression": "$Q_r$ vs. $Q_h$",
          "hfdsgeou vs thermal OHC regression": "$Q_h$ vs. $H_T$",
          "netTOA vs thermal OHC regression": "$Q_r$ vs. $H_T$",
          "wfo vs masso regression": "$Q_m$ vs. $M$",
          "wfo vs soga regression": "$Q_m$ vs. $S$",
          "masso vs soga regression": "$M$ vs. $S$",
          "wfa vs massa regression": "$M_a$ vs. $Q_{ep}$"}


def plot_energy_conservation(df, cmip_line):
    """Plot regression coefficients for thermal energy conservation"""
    
    comparison_list = ['netTOA vs thermal OHC regression', 'netTOA vs hfdsgeou regression', 'hfdsgeou vs thermal OHC regression']
    df = df[comparison_list]
    df = df.dropna(axis=0, how='all')
    
    x = np.arange(df.shape[0])
    x0 = x - 0.2
    x1 = x + 0.2
    xlist = [x0, x, x1]
    
    plt.figure(figsize=[14, 5])
    plt.axhline(y=1.0, color='0.5', linewidth=0.5)
    if cmip_line:
        plt.axvline(x=cmip_line, color='0.5', linewidth=2.0)
    colors = ['cadetblue', 'seagreen', 'mediumpurple']
    linestyles = ['--', '-.', ':']
    for pnum, var in enumerate(comparison_list):
        y = df[var].to_numpy()
        color = colors[pnum]
        linestyle = linestyles[pnum]
        markerline, stemlines, baseline = plt.stem(xlist[pnum], y, color, basefmt=" ", bottom=1.0, label=labels[var])
        plt.setp(stemlines, color=color, linestyle=linestyle)
        plt.setp(markerline, color=color)

    plt.axvline(x=x[0]-0.5, color='0.5', linewidth=0.1)
    for val in x:
        plt.axvline(x=val+0.5, color='0.5', linewidth=0.1)
    #plt.grid(True, axis='x')
    plt.legend()
    plt.xlim(x[0] - 0.5, x[-1] + 0.5)
    plt.xticks(x, df.index.to_list(), rotation=90)
    plt.ylabel('regression coefficient')


def plot_mass_conservation(df, cmip_line):
    """Plot the regression coefficient for each model"""
    
    comparison_list = ['wfo vs masso regression', 'wfo vs soga regression',
                       'masso vs soga regression', 'wfa vs massa regression']
    df = df[comparison_list]
    df = df.dropna(axis=0, how='all')
    
    x = np.arange(df.shape[0])
    x0 = x - 0.3
    x1 = x - 0.1
    x2 = x + 0.1
    x3 = x + 0.3
    xlist = [x0, x1, x2, x3]
    
    fig, (ax1) = plt.subplots(1, 1, figsize=(18,6))
    ax1.set_ylim(-0.2, 1.5)
    ax1.axhline(y=1.0, color='0.5', linewidth=0.5)
    if cmip_line:
        ax1.axvline(x=cmip_line, color='0.5', linewidth=2.0)
    colors = ['cadetblue', 'seagreen', 'mediumpurple', 'peachpuff']
    linestyles = ['--', '-.', ':', '-']
    for pnum, var in enumerate(comparison_list):
        y = df[var].to_numpy()
        color = colors[pnum]
        linestyle = linestyles[pnum]        
        markerline, stemlines, baseline = ax1.stem(xlist[pnum], y, color, basefmt=" ", bottom=1.0, label=labels[var])
        plt.setp(stemlines, color=color, linestyle=linestyle)
        plt.setp(markerline, color=color)
        
    ax1.axvline(x=x[0] - 0.5, color='0.5', linewidth=0.1)
    for val in x:
        ax1.axvline(x=val + 0.5, color='0.5', linewidth=0.1)
    #plt.grid(True, axis='x')
    ax1.legend()
    plt.xlim(x[0] - 0.5, x[-1] + 0.5)
    plt.xticks(x, df.index.to_list(), rotation=90)
    ax1.set_ylabel('regression coefficient')
    plt.subplots_adjust(hspace=0.1)


def main(inargs):
    """Run the program."""

    df = pd.read_csv(inargs.infile)
    df.set_index(df['model'] + ' (' + df['run'] + ')', drop=True, inplace=True)
    
    if inargs.domain == 'energy':
        plot_energy_conservation(df, inargs.cmip_line)
    elif inargs.domain == 'mass':
        plot_mass_conservation(df, inargs.cmip_line)

    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=200)
    log_file = re.sub('.png', '.met', inargs.outfile)
    log_text = cmdprov.new_log(git_repo=repo_dir)
    cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot regression coefficients from drift analysis'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("domain", type=str, choices=("energy", "mass"),
                        help="Plot energy or mass conservation")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--cmip_line", type=float, default=None,
                        help="Add a vertical line at this x value to should CMIP5/6 boundary")

    args = parser.parse_args()  
    main(args)
