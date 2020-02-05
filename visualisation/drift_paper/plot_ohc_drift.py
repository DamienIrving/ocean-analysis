"""
Filename:     plot_ohc_drift.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Create a bar chart showing drift in ocean heat content
              and its thermal and barystatic components  

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
mpl.rcParams['ytick.labelsize'] = 'large'
mpl.rcParams['legend.fontsize'] = 'large'


# Define functions 

def get_quartiles(df, column_name, df_project, units):
    """Get the ensemble quartiles"""

    quartiles = ['# ' + column_name + ' quartiles']
    for project in ['cmip6', 'cmip5']:
        df_subset = df[df_project == project]
        
        upper_quartile = df_subset[column_name].abs().quantile(0.75)
        median = df_subset[column_name].abs().quantile(0.5)
        lower_quartile = df_subset[column_name].abs().quantile(0.25)
        
        upper_quartile_text = "%s upper quartile: %f %s" %(project, upper_quartile, units)
        median_text = "%s median: %f %s" %(project, median, units)
        lower_quartile_text = "%s lower quartile: %f %s" %(project, lower_quartile, units)
        
        quartiles.append(upper_quartile_text)
        quartiles.append(median_text)
        quartiles.append(lower_quartile_text)

    return quartiles


def main(inargs):
    """Run the program."""

    df = pd.read_csv(inargs.infile)
    df.set_index(df['model'] + ' (' + df['run'] + ')', drop=True, inplace=True)
    x = np.arange(df.shape[0])
    ncmip5 = df['project'].value_counts()['cmip5']

    df_ohc = df[['OHC (J yr-1)', 'thermal OHC (J yr-1)', 'barystatic OHC (J yr-1)']]

    sec_in_year = 365.25 * 24 * 60 * 60
    earth_surface_area = 5.1e14
    df_ohc = (df_ohc / sec_in_year) / earth_surface_area
    df_ohc = df_ohc.rename(columns={"OHC (J yr-1)": "change in OHC ($dH/dt$)",
                                    "thermal OHC (J yr-1)": "change in OHC temperature component ($dH_T/dt$)",
                                    "barystatic OHC (J yr-1)": "change in OHC barystatic component ($dH_m/dt$)"})
    
    df_ohc.plot.bar(figsize=(18,6), color=['#272727', 'tab:red', 'tab:blue'], width=0.9)
    plt.axvline(x=ncmip5 - 0.5, color='0.5', linewidth=2.0)
    plt.axhline(y=0.5, color='0.5', linewidth=0.5, linestyle='--')
    units = '$W \; m^{-2}$'
    plt.ylabel(units)
    plt.axvline(x=x[0]-0.5, color='0.5', linewidth=0.1)
    for val in x:
        plt.axvline(x=val+0.5, color='0.5', linewidth=0.1)
    
    quartiles = get_quartiles(df_ohc, "change in OHC ($dH/dt$)", df['project'], units)

    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=200)
    log_file = re.sub('.png', '.met', inargs.outfile)
    log_text = cmdprov.new_log(git_repo=repo_dir, extra_notes=quartiles)
    cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Create a bar chart showing drift in ocean heat content'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("outfile", type=str, help="Output file name")

    args = parser.parse_args()  
    main(args)
