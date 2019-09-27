"""
Filename:     plot_conservation_scatter.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Create a scatterplot showing energy, mass and salt conservation  

"""

# Import general Python modules

import sys
import os
import re
import pdb
import argparse
import copy

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import pandas as pd
from brokenaxes import brokenaxes

import cmdline_provenance as cmdprov

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'ocean-analysis':
        break

ocean_model_colors = {'MOM': 'red',
                      'GOLD': 'gold',
                      'NEMO': 'blue',
                      'OPA': 'green',
                      'COCO': 'chocolate',
                      'MPI-OM': 'purple',
                      'MICOM-HAMOCC': 'teal',
                      'POP': 'lime'}

markers = ['o', '<', '^', '>', 'v', 's', 'p', 'D',
           'o', '<', '^', '>', 'v', 's', 'p', 'D',
           'o', '<', '^', '>', 'v', 's', 'p', 'D']


# Define functions 

def plot_abline(ax, slope, intercept, static_bounds=True):
    """Plot a line from slope and intercept"""

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    if type(xlim[0]) in (list, tuple):
        for lims in xlim:
            x_vals = np.array(lims)
            y_vals = intercept + slope * x_vals
            ax.plot(x_vals, y_vals, linestyle='--', c='0.5')
    else:
        x_vals = np.array(xlim)
        y_vals = intercept + slope * x_vals
        ax.plot(x_vals, y_vals, linestyle='--', c='0.5')

    if static_bounds:
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
    

def plot_shading(ax):
    """Plot shading to indicate dominant source of drift."""
    
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    
    x_vals = np.array(xlim)
    y_vals = x_vals * 2
    ax.fill_between(x_vals, 0, y_vals, alpha=0.3, color='0.5')

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    
    
def plot_eei_shading(ax):
    """Plot shading to indicate netTOA / OHC valid range."""
    
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    
    x_vals = np.array(xlim)
    y_vals = x_vals * 0.8
    ax.fill_between(x_vals, x_vals, y_vals, alpha=0.3, color='0.5')
                      
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    
                      
def format_axis_label(orig_label, units, scale_factor):
    """Put LaTeX math into axis labels"""
    
    label = orig_label.split('(')[0] + '(' + units + ')'
    label = label.replace('(', '($').replace(')', '$)')
    label = label.replace('s-1', '\; s^{-1}')
    label = label.replace('m-2', '\; m^{-2}')
    label = label.replace('yr-1', '\; yr^{-1}')
    if scale_factor:
        scale_factor = int(scale_factor) * -1
        label = label.replace('($', '($10^{%s} \;' %(str(scale_factor)))
    
    return label 


def plot_aesthetics(ax, yvar, xvar, units, scinotation, shading, scale_factor,
                    xpad=None, ypad=None, non_square=True):
    """Set the plot aesthetics"""
    
    if shading:
        plot_shading(ax)
    if 'netTOA' in xvar:
        plot_eei_shading(ax)
    else:
        plot_abline(ax, 1, 0, static_bounds=non_square)
    ax.axhline(y=0, color='0.5', linewidth=1.0)
    ax.axvline(x=0, color='0.5', linewidth=1.0)
    #ax.yaxis.major.formatter._useMathText = True
    #ax.xaxis.major.formatter._useMathText = True

    ylabel = format_axis_label(yvar, units, scale_factor)
    if ypad:
        ax.set_ylabel(ylabel, labelpad=ypad)
    else:
        ax.set_ylabel(ylabel)
    xlabel = format_axis_label(xvar, units, scale_factor)
    if xpad:
        ax.set_xlabel(xlabel, labelpad=xpad)
    else:
        ax.set_xlabel(xlabel)
    ax.set_xlabel(xlabel, labelpad=xpad)
    #plt.sca(ax)
    if scinotation:
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True)
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0), useMathText=True)
    
    # Shrink current axis by 20%
   #box = ax.get_position()
   #ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])


def get_units(column_header):
    """Get the units from the column header."""
    
    units = column_header.split('(')[-1].split(')')[0]
    
    return units
    
    
def convert_units(value, start_units, end_units, ocean_area=None):
    """Convert units."""
    
    sec_in_year = 365.25 * 24 * 60 * 60
    
    if start_units == end_units:
        new_value = value
    else:    
        assert start_units in ['J yr-1', 'm yr-1', 'kg yr-1', 'g/kg yr-1', 'm yr-1']
        assert end_units in ['PW', 'W m-2', 'mm yr-1', 'kg s-1', 'g/kg s-1', 'm s-1']

        if start_units == 'J yr-1':
            new_value = value / sec_in_year 
            if end_units == 'W m-2':
                earth_surface_area = 5.1e14
                new_value = new_value / earth_surface_area
            elif end_units == 'PW':
                new_value = new_value / 1e15
                
        elif (start_units == 'm yr-1') and (end_units == 'mm yr-1'):
            new_value = value * 1000

        elif (start_units == 'kg yr-1') and (end_units == 'mm yr-1'):
            assert ocean_area
            new_value = value / ocean_area
            
        elif (start_units == 'kg yr-1') and (end_units == 'kg s-1'):
            new_value = value / sec_in_year 
            
        elif (start_units == 'g/kg yr-1') and (end_units == 'g/kg s-1'):
            new_value = value / sec_in_year
            
        elif (start_units == 'm yr-1') and (end_units == 'm s-1'):
            new_value = value / sec_in_year
            
    return new_value


def plot_broken_comparison(df, title, xvar, yvar, plot_units, scale_factor=0,
                           scinotation=False, shading=False, outfile=None,
                           xlims=None, ylims=None, xpad=None, ypad=None,
                           hspace=0.04, wspace=0.04):
    """Plot comparison for given x and y variables.
    
    Data are multiplied by 10^scale_factor.
    
    """
    
    fig = plt.figure(figsize=[10, 8])
    if xlims and ylims:
        bax = brokenaxes(xlims=xlims, ylims=ylims, hspace=hspace, wspace=wspace)
    else:
        bax = fig.add_subplot(1, 1, 1)
    
    x_input_units = get_units(xvar) 
    y_input_units = get_units(yvar)
    for dotnum in range(len(df['model'])):
        area = df['ocean area (m2)'][dotnum]
        x = convert_units(df[xvar][dotnum], x_input_units, plot_units, ocean_area=area) * 10**scale_factor
        y = convert_units(df[yvar][dotnum], y_input_units, plot_units, ocean_area=area) * 10**scale_factor
        marker = markers[dotnum]
        label = df['model'][dotnum] + ' (' + df['run'][dotnum] + ')'
        ocean_model = df['ocean model'][dotnum]
        color = ocean_model_colors[ocean_model]
        if df['project'][dotnum] == 'cmip6':
            facecolors = color
            edgecolors ='none'
        else:
            facecolors = 'none'
            edgecolors = color
        bax.scatter(x, y, label=label, s=130, linewidth=1.2, marker=marker,
                    facecolors=facecolors, edgecolors=edgecolors)

    if xlims:
        non_square = False
    else:
        non_square = True
        bax.spines["top"].set_visible(False)
        bax.spines["right"].set_visible(False)
    plot_aesthetics(bax, yvar, xvar, plot_units, scinotation, shading, scale_factor,
                    xpad=xpad, ypad=ypad, non_square=non_square)
    plt.title(title)
    bax.legend(loc='center left', bbox_to_anchor=(1, 0.5))


def main(inargs):
    """Run the program."""

    df = pd.read_csv(inargs.infile)
    df.set_index(df['model'] + ' (' + df['run'] + ')', drop=True, inplace=True)

    plot_broken_comparison(df, 'thermal energy conservation', 'hfds (J yr-1)', 'thermal OHC (J yr-1)', 'W m-2',
                           xlims=[(-41.05, -40.82), (-0.35, 0.3)], ylims=[(-0.3, 0.25), (0.55, 0.65)],
                           wspace=0.08, hspace=0.08, xpad=20)

    plt.savefig(inargs.outfile, bbox_inches='tight')  # dpi=400
    log_file = re.sub('.png', '.met', inargs.outfile)
    log_text = cmdprov.new_log(git_repo=repo_dir)
    cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Create a scatterplot showing energy, mass and salt conservation'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, default=None, help="Output file name")
    parser.add_argument("outfile", type=str, default=None, help="Output file name")

    args = parser.parse_args()  
    main(args)
