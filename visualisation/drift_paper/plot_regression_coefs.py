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

labels = {"netTOA vs hfds regression": "cumulative netTOA ($Q_r$) vs. cumulative surface heat flux ($Q_h$)",
          "hfds vs thermal OHC regression": "cumulative surface heat flux ($Q_h$) vs. thermal OHC ($H_T$)",
          "netTOA vs thermal OHC regression": "cumulative netTOA ($Q_r$) vs. thermal OHC ($H_T$)",
          "wfo vs masso regression": "cumulative freshwater flux ($Q_m$) vs. ocean mass ($M$)",
          "wfo vs soga regression": "cumulative freshwater flux ($Q_m$) vs. ocean salinity ($S$)",
          "masso vs soga regression": "ocean mass ($M$) vs. ocean salinity ($S$)"}


def plot_energy_conservation(df):
    """Plot regression coefficients for thermal energy conservation"""
    
    comparison_list = ['netTOA vs thermal OHC regression', 'netTOA vs hfds regression', 'hfds vs thermal OHC regression']
    x = np.arange(df.shape[0])
    x0 = x - 0.2
    x1 = x + 0.2
    xlist = [x0, x, x1]
    
    plt.figure(figsize=[14, 5])
    plt.axhline(y=1.0, color='0.5', linewidth=0.5)
    plt.axvline(x=14.5, color='0.5', linewidth=2.0)
    colors = ['cadetblue', 'seagreen', 'mediumpurple']
    linestyles = ['--', '-.', ':']
    for pnum, var in enumerate(comparison_list):
        y = df[var].to_numpy()
        color = colors[pnum]
        linestyle = linestyles[pnum]
        markerline, stemlines, baseline = plt.stem(xlist[pnum], y, color, basefmt=" ", bottom=1.0, label=labels[var])
        plt.setp(stemlines, color=color, linestyle=linestyle)
        plt.setp(markerline, color=color)

    plt.axvline(x=x[0]-0.5, color='0.5', linewidth=0.5)
    for val in x:
        plt.axvline(x=val+0.5, color='0.5', linewidth=0.5)
    #plt.grid(True, axis='x')
    plt.legend()
    plt.xlim(x[0] - 0.5, x[-1] + 0.5)
    plt.xticks(x, df.index.to_list(), rotation=90)
    plt.ylabel('regression coefficient')


def plot_mass_conservation(df):
    """Plot the regression coefficient for each model"""
    
    comparison_list = ['wfo vs masso regression', 'wfo vs soga regression', 'masso vs soga regression']
    x = np.arange(df.shape[0])
    x0 = x - 0.2
    x1 = x + 0.2
    xlist = [x0, x, x1]
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(18,8), gridspec_kw={'height_ratios': [1, 5, 1]})
    ax1.spines['bottom'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax1.tick_params(axis='x', which='both', bottom=False)
    ax2.tick_params(axis='x', which='both', bottom=False)
    ax2.spines['top'].set_visible(False)
    ax3.spines['top'].set_visible(False)
    ax1.set_ylim(1.5, 3.0)
    ax2.set_ylim(-0.1, 1.4)
    ax3.set_ylim(-5.5, -1)

    ax2.axhline(y=1.0, color='0.5', linewidth=0.5)
    ax1.axvline(x=14.5, color='0.5', linewidth=2.0)
    ax2.axvline(x=14.5, color='0.5', linewidth=2.0)
    ax3.axvline(x=14.5, color='0.5', linewidth=2.0)
    colors = ['cadetblue', 'seagreen', 'mediumpurple']
    linestyles = ['--', '-.', ':']
    for pnum, var in enumerate(comparison_list):
        y = df[var].to_numpy()
        color = colors[pnum]
        linestyle = linestyles[pnum]
        markerline, stemlines, baseline = ax2.stem(xlist[pnum], y, color, basefmt=" ", bottom=1.0, label=labels[var])
        plt.setp(stemlines, color=color, linestyle=linestyle)
        plt.setp(markerline, color=color)
        
        markerline, stemlines, baseline = ax1.stem(xlist[pnum], y, color, basefmt=" ", bottom=1.0, label=labels[var])
        plt.setp(stemlines, color=color, linestyle=linestyle)
        plt.setp(markerline, color=color)
        
        markerline, stemlines, baseline = ax3.stem(xlist[pnum], y, color, basefmt=" ", bottom=1.0, label=labels[var])
        plt.setp(stemlines, color=color, linestyle=linestyle)
        plt.setp(markerline, color=color)

    ax1.axvline(x=x[0] - 0.5, color='0.5', linewidth=0.5)
    ax2.axvline(x=x[0] - 0.5, color='0.5', linewidth=0.5)
    ax3.axvline(x=x[0] - 0.5, color='0.5', linewidth=0.5)
    for val in x:
        ax1.axvline(x=val + 0.5, color='0.5', linewidth=0.5)
        ax2.axvline(x=val + 0.5, color='0.5', linewidth=0.5)
        ax3.axvline(x=val + 0.5, color='0.5', linewidth=0.5)
    #plt.grid(True, axis='x')
    ax1.legend()
    plt.xlim(x[0] - 0.5, x[-1] + 0.5)
    plt.xticks(x, df.index.to_list(), rotation=90)
    ax2.set_ylabel('regression coefficient')
    plt.subplots_adjust(hspace=0.1)


def main(inargs):
    """Run the program."""

    df = pd.read_csv(inargs.infile)
    df.set_index(df['model'] + ' (' + df['run'] + ')', drop=True, inplace=True)

    if inargs.domain == 'energy':
        plot_energy_conservation(df)
    elif inargs.domain == 'mass':
        plot_mass_conservation(df)

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

    args = parser.parse_args()  
    main(args)
