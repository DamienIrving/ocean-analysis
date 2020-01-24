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

def main(inargs):
    """Run the program."""

    df = pd.read_csv(inargs.infile)
    df.set_index(df['model'] + ' (' + df['run'] + ')', drop=True, inplace=True)
    ncmip5 = df['project'].value_counts()['cmip5']

    df_ohc = df[['OHC (J yr-1)', 'thermal OHC (J yr-1)', 'barystatic OHC (J yr-1)']]

    sec_in_year = 365.25 * 24 * 60 * 60
    earth_surface_area = 5.1e14
    df_ohc = (df_ohc / sec_in_year) / earth_surface_area
    df_ohc = df_ohc.rename(columns={"OHC (J yr-1)": "change in OHC ($dH/dt$)",
                                    "thermal OHC (J yr-1)": "change in thermal OHC ($dH_T/dt$)",
                                    "barystatic OHC (J yr-1)": "change in barystatic OHC ($dH_m/dt$)"})
    
    df_ohc.plot.bar(figsize=(18,6), color=['black', 'red', 'blue'], width=0.9)
    plt.axvline(x=ncmip5 - 0.5, color='0.5', linewidth=2.0)
    plt.axhline(y=0.5, color='0.5', linewidth=0.5, linestyle='--')
    plt.ylabel('$W \; m^{-2}$')

    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=200)
    log_file = re.sub('.png', '.met', inargs.outfile)
    log_text = cmdprov.new_log(git_repo=repo_dir)
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
