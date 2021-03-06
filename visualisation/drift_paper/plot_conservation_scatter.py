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
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
from matplotlib.gridspec import GridSpec
from brokenaxes import brokenaxes

import cmdline_provenance as cmdprov

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'ocean-analysis':
        break

import matplotlib as mpl
mpl.rcParams['axes.labelsize'] = 'xx-large'
mpl.rcParams['axes.titlesize'] = 20
mpl.rcParams['xtick.labelsize'] = 'x-large'
mpl.rcParams['ytick.labelsize'] = 'x-large'
mpl.rcParams['legend.fontsize'] = 'xx-large'

# From https://sashat.me/2017/01/11/list-of-20-simple-distinct-colors/
# '#800000' Maroon
# '#a9a9a9' Grey
# '#808000' Olive
# '#469990' Teal
# '#000075' Navy
# '#e6194B' Red
# '#f58231' Orange
# '#fabebe' Pink
# '#ffe119' Yellow
# '#bfef45' Lime
# '#3cb44b' Green
# '#42d4f4' Cyan
# '#4363d8' Blue
# '#911eb4' Purple
# '#f032e6' Magenta


institution_colors = {'BCC': '#800000',
                      'BNU': '#a9a9a9',
                      'CMCC': '#808000',
                      'CNRM-CERFACS': '#469990',
                      'CSIRO': '#000075',
                      'E3SM-Project': '#e6194B',
                      'EC-Earth-Consortium': '#f58231',
                      'HAMMOZ-Consortium': '#fabebe',
                      'IPSL': '#ffe119',
                      'MIROC': '#bfef45',
                      'MOHC': '#3cb44b',
                      'MPI-M': '#42d4f4',
                      'NASA-GISS': '#4363d8',
                      'NCC': '#911eb4',
                      'NOAA-GFDL': '#f032e6'
                      }

markers = ['o', '^', 's', '<', '>', 'v', 'p', 'D', 'd', 'h', 'H', 'X']

axis_labels = {'thermal OHC': 'change in OHC temperature component \n $dH_T/dt$',
               'masso': 'change in ocean mass \n $dM/dt$',
               'massa': 'change in mass of atmospheric water vapor \n $dM_a/dt$',
               'netTOA': 'time-integrated netTOA \n $dQ_r/dt$',
               'hfdsgeou': 'time-integrated heat flux into ocean \n $dQ_h/dt$',
               'soga': 'change in ocean salinity \n $dS/dt$',
               'wfo': 'time-integrated freshwater flux into ocean \n $dQ_m/dt$',
               'wfa': 'time-integrated moisture flux into atmosphere \n $dQ_{ep}/dt$'}

stats_done = []
quartiles = []

cmip6_data_points = {}
cmip5_data_points = {}

# Define functions 

def record_quartiles(variable, data, project):
    """Get the ensemble quartiles"""

    quartiles.append('# ' + variable + ' quartiles') 
    
    abs_data = np.abs(data)
    clean_abs_data = abs_data[np.logical_not(np.isnan(abs_data))]
        
    upper_quartile = np.percentile(clean_abs_data, 75)
    median = np.percentile(clean_abs_data, 50)
    lower_quartile = np.percentile(clean_abs_data, 25)
    nmodels = len(data)
    valid_nmodels = len(clean_abs_data)
        
    upper_quartile_text = "%s upper quartile: %f" %(project, upper_quartile)
    median_text = "%s median: %f" %(project, median)
    lower_quartile_text = "%s lower quartile: %f" %(project, lower_quartile)
    nmodels_text = "%s number of models: %i (%i not nan)" %(project, nmodels, valid_nmodels)
        
    quartiles.append(upper_quartile_text)
    quartiles.append(median_text)
    quartiles.append(lower_quartile_text)
    quartiles.append(nmodels_text)


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
    label = label.replace('s-1', 's$^{-1}$')
    label = label.replace('m-2', 'm$^{-2}$')
    label = label.replace('yr-1', 'yr$^{-1}$')
    if scale_factor:
        scale_factor = int(scale_factor) * -1
        label = label.replace('(', '(10$^{%s}$ ' %(str(scale_factor)))
    
    for var in axis_labels.keys():
        if var in label:
            label = label.replace(var, axis_labels[var])

    return label 


def plot_two_var_aesthetics(ax, yvar, xvar, units, scinotation, shading, scale_factor,
                            xpad=None, ypad=None, non_square=True):
    """Set the plot aesthetics"""
    
    plot_abline(ax, 1, 0, static_bounds=non_square)
    ax.axhline(y=0, color='black', linewidth=1.0)
    ax.axvline(x=0, color='black', linewidth=1.0)

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
    
    if 'W m$^{-2}$' in ylabel:
        ax.axhspan(0.4, 1.0, color='0.95', zorder=1)
        ax.axhspan(-0.4, -1.0, color='0.95', zorder=1)
        ax.axvspan(0.4, 1.0, color='0.95', zorder=1)
        ax.axvspan(-0.4, -1.0, color='0.95', zorder=1)
#        ax.axhline(y=-0.5, color='0.5', linewidth=0.5, linestyle='--')
#        ax.axhline(y=0.5, color='0.5', linewidth=0.5, linestyle='--')
#        ax.axvline(x=-0.5, color='0.5', linewidth=0.5, linestyle='--')
#        ax.axvline(x=0.5, color='0.5', linewidth=0.5, linestyle='--')
    elif 'kg yr-1' in xvar:
        ref = convert_units(1.8, 'mm yr-1', 'kg yr-1')
        ref = ref * 10**scale_factor
        ax.axhline(y=-1 * ref, color='0.5', linewidth=0.5, linestyle='--')
        ax.axhline(y=ref, color='0.5', linewidth=0.5, linestyle='--')
        ax.axvline(x=-1 * ref, color='0.5', linewidth=0.5, linestyle='--')
        ax.axvline(x=ref, color='0.5', linewidth=0.5, linestyle='--')

    return xlabel, ylabel


def plot_one_var_aesthetics(ax, yvar, units, scinotation, scale_factor, ypad=None):
    """Set the plot aesthetics"""
    
    ax.axhline(y=0, color='black', linewidth=1.0)

    ylabel = format_axis_label(yvar, units, scale_factor)
    if ypad:
        ax.set_ylabel(ylabel, labelpad=ypad)
    else:
        ax.set_ylabel(ylabel)
        
    if scinotation:
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True)

    ax.set_yscale('symlog')
    ax.grid(axis='y')
    #ax.get_xaxis().set_visible(False)
    ax.get_xaxis().set_ticks([])
    ax.set_xlabel('CMIP5/CMIP6 model')

    ax.axhline(y=-1.68e13 * 10**scale_factor, color='0.5', linewidth=0.5, linestyle='--')
    ax.axhline(y=1.68e13 * 10**scale_factor, color='0.5', linewidth=0.5, linestyle='--')

    return ylabel


def get_units(column_header):
    """Get the units from the column header."""
    
    units = column_header.split('(')[-1].split(')')[0]
    
    return units
    
    
def convert_units(value, start_units, end_units):
    """Convert units."""
    
    sec_in_year = 365.25 * 24 * 60 * 60
    ocean_density = 1026  # kg m-3
    ocean_area = 3.6e14  #m2
    
    if start_units == end_units:
        new_value = value
    else:    
        assert start_units in ['J yr-1', 'm yr-1', 'kg yr-1', 'g/kg yr-1', 'm yr-1', 'mm yr-1']
        assert end_units in ['PW', 'W m-2', 'mm yr-1', 'kg s-1', 'g/kg s-1', 'm s-1', 'kg yr-1']

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
            volume_trend = value / ocean_density
            new_value = (volume_trend / ocean_area) * 1000
        
        elif (start_units == 'mm yr-1') and (end_units == 'kg yr-1'):
            new_value = (value / 1000) * ocean_area * ocean_density
        
        elif (start_units == 'kg yr-1') and (end_units == 'kg s-1'):
            new_value = value / sec_in_year 
            
        elif (start_units == 'g/kg yr-1') and (end_units == 'g/kg s-1'):
            new_value = value / sec_in_year
            
        elif (start_units == 'm yr-1') and (end_units == 'm s-1'):
            new_value = value / sec_in_year
            
    return new_value


def plot_broken_comparison(ax, df, title, xvar, yvar, plot_units,
                           scale_factor=0, scinotation=False, shading=False,
                           xpad=None, ypad=None, broken=False, legend=False):
    """Plot comparison for given x and y variables.
    
    Data are multiplied by 10^scale_factor.
    
    """

    cmip5_institution_counts = {}
    for institution in institution_colors.keys():
        cmip5_institution_counts[institution] = 0
    cmip6_institution_counts = cmip5_institution_counts.copy()
    cmip6_xdata = []
    cmip6_ydata = []
    cmip5_xdata = []
    cmip5_ydata = []

    x_input_units = get_units(xvar) 
    y_input_units = get_units(yvar)
    for dotnum in range(len(df['model'])):       
        x = convert_units(df[xvar][dotnum], x_input_units, plot_units) * 10**scale_factor
        y = convert_units(df[yvar][dotnum], y_input_units, plot_units) * 10**scale_factor
        label = df['model'][dotnum]
        #label = df['model'][dotnum] + ' (' + df['run'][dotnum] + ')'
        institution = df['institution'][dotnum]
        color = institution_colors[institution]
        if df['project'][dotnum] == 'cmip6':
            facecolors = color
            edgecolors ='none'
            marker_num = cmip6_institution_counts[institution]
            cmip6_institution_counts[institution] = cmip6_institution_counts[institution] + 1
            cmip6_xdata.append(x)
            cmip6_ydata.append(y)
        else:
            facecolors = 'none'
            edgecolors = color
            marker_num = cmip5_institution_counts[institution]
            cmip5_institution_counts[institution] = cmip5_institution_counts[institution] + 1
            cmip5_xdata.append(x)
            cmip5_ydata.append(y)
        marker = markers[marker_num]
        x_for_plot = dotnum + 1 if 'massa' in xvar else x
        ax.scatter(x_for_plot, y, label=label, s=130, linewidth=1.2, marker=marker,
                   facecolors=facecolors, edgecolors=edgecolors, zorder=2) 
        if dotnum == 0:
            xmin = x
            xmax = x
            ymin = y
            ymax = y
        else:
            xmin = min(x, xmin)
            xmax = max(x, xmax)
            ymin = min(y, ymin)
            ymax = max(y, ymax)
    
    print(title)
    print(f'x-axis: {xmin} to {xmax}')
    print(f'y-axis: {ymin} to {ymax}')
    
    if broken:
        non_square = False
    else:
        non_square = True
        if not 'massa' in xvar:
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
    ax.set_title(title)
    if 'massa' in xvar:
        ylabel = plot_one_var_aesthetics(ax, yvar, plot_units, scinotation, scale_factor, ypad=ypad)
        xlabel = format_axis_label(xvar, plot_units, scale_factor)
    else:
        xlabel, ylabel = plot_two_var_aesthetics(ax, yvar, xvar, plot_units, scinotation, shading, scale_factor,
                                                 xpad=xpad, ypad=ypad, non_square=non_square)

    if not xlabel in stats_done:
        cmip6_data_points[xlabel] = cmip6_xdata
        cmip5_data_points[xlabel] = cmip5_xdata
    if not ylabel in stats_done:
        cmip6_data_points[ylabel] = cmip6_ydata
        cmip5_data_points[ylabel] = cmip5_ydata
    stats_done.append(xlabel)
    stats_done.append(ylabel)


def get_legend_info(ax, df_subset):
    """Get the legend handles and labels.
    
    df_subset should only contain rows plotted in ax
    
    """

    legend_info = ax.get_legend_handles_labels()
    if len(legend_info[0]) == 2:
        legend_info = legend_info[0]
    assert len(legend_info) == 2
    handles = legend_info[0]
    labels = legend_info[1]
    
    for index, model in enumerate(labels):
        if df_subset.loc[model].isnull().values.any():
            handles[index] = None    
    
    return handles, labels
    

def update_legend_info(ax, df_subset, handles, labels):
    """Update legend information.
    
    df_subset should only contain rows plotted in ax
    
    """
    
    new_handles, new_labels = get_legend_info(ax, df_subset)
    assert len(handles) == len(new_handles)
    
    for index, handle in enumerate(handles):
        if not handle:
            handles[index] = new_handles[index] 
    
    return handles, labels  
    
    
def main(inargs):
    """Run the program."""

    df = pd.read_csv(inargs.infile)
    #df.set_index(df['model'] + ' (' + df['run'] + ')', drop=True, inplace=True)
    df.set_index(df['model'], drop=True, inplace=True)
    fig = plt.figure(figsize=[18.5, 21])  # width, height
    gs = GridSpec(3, 2)

    # EEI conservation
    eei_ax = fig.add_subplot(gs[0, 0])
    plot_broken_comparison(eei_ax, df, '(a) planetary energy imbalance', 'netTOA (J yr-1)',
                           'thermal OHC (J yr-1)', 'W m-2', legend=True)
    handles, labels = get_legend_info(eei_ax, df[['netTOA (J yr-1)', 'thermal OHC (J yr-1)']])

    # Ocean energy conservation
    xlims=[(-41.05, -40.82), (-0.55, 0.71)]
    ylims=[(-0.55, 0.66)]
    wspace = hspace = 0.08
    ocean_energy_ax = brokenaxes(xlims=xlims, ylims=ylims, hspace=hspace, wspace=wspace,
                                 subplot_spec=gs[0, 1], d=0.0)
    #ocean_energy_ax = fig.add_subplot(gs[0, 1])
    plot_broken_comparison(ocean_energy_ax, df, '(b) ocean energy conservation', 'hfdsgeou (J yr-1)',
                           'thermal OHC (J yr-1)', 'W m-2', xpad=25, ypad=45, broken=True)
    handles, labels = update_legend_info(ocean_energy_ax, df[['hfdsgeou (J yr-1)', 'thermal OHC (J yr-1)']],
                                         handles, labels)

    # Ocean mass conservation
    xlims=[(-7, 4), (472, 474), (492, 495)]
    ylims=[(-0.7, 0.25)]
    hspace = 0.1
    ocean_mass_ax = brokenaxes(xlims=xlims, ylims=ylims, hspace=hspace, subplot_spec=gs[1, 0], d=0.0)
    #ocean_mass_ax = fig.add_subplot(gs[1, 0])
    plot_broken_comparison(ocean_mass_ax, df, '(c) ocean mass conservation', 'wfo (kg yr-1)', 'masso (kg yr-1)',
                           'kg yr-1', scale_factor=-15, broken=True, xpad=30, ypad=50)
    handles, labels = update_legend_info(ocean_mass_ax, df[['wfo (kg yr-1)', 'masso (kg yr-1)']],
                                         handles, labels)

    # Salt conservation
    xlims=[(-0.73, 0.35), (3.55, 3.7)]
    ylims=[(-0.8, 3.1)]
    hspace = wspace = 0.1
    salt_ax = brokenaxes(xlims=xlims, ylims=ylims, hspace=hspace, wspace=wspace, subplot_spec=gs[1, 1], d=0.0)
    #salt_ax = fig.add_subplot(gs[1, 1])
    plot_broken_comparison(salt_ax, df, '(d) salt conservation', 'masso (kg yr-1)', 'soga (kg yr-1)',
                           'kg yr-1', scale_factor=-15, xpad=30, ypad=40, broken=True)
    handles, labels = update_legend_info(salt_ax, df[['masso (kg yr-1)', 'soga (kg yr-1)']],
                                         handles, labels)

    # Atmosphere mass conservation
    atmos_mass_ax = fig.add_subplot(gs[2, :])
    plot_broken_comparison(atmos_mass_ax, df, '(e) atmospheric mass conservation', 'massa (kg yr-1)', 'wfa (kg yr-1)',
                           'kg yr-1', scale_factor=-12, ypad=20)
    handles, labels = update_legend_info(atmos_mass_ax, df[['wfa (kg yr-1)']], handles, labels)

    fig.legend(handles, labels, loc='center left', bbox_to_anchor=(0.815, 0.5))
    plt.tight_layout(rect=(0, 0, 0.8, 1))

    for variable, data in cmip6_data_points.items():
        record_quartiles(variable, data, 'cmip6')
    for variable, data in cmip5_data_points.items():
        record_quartiles(variable, data, 'cmip5')
    
    plt.savefig(inargs.outfile, dpi=400)
    log_file = re.sub('.png', '.met', inargs.outfile)
    log_text = cmdprov.new_log(git_repo=repo_dir, extra_notes=quartiles)
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

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("outfile", type=str, help="Output file name")

    args = parser.parse_args()  
    main(args)
