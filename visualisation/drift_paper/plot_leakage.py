"""
Filename:     plot_leakage.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Create a bar chart showing energy leakage
              in the atmosphere and ocean
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

    df['atmos energy leakage (J yr-1)'] = df['netTOA (J yr-1)'] - df['hfds (J yr-1)']
    df['ocean energy leakage (J yr-1)'] = df['hfds (J yr-1)'] - df['thermal OHC (J yr-1)']
    df['total energy leakage (J yr-1)'] = df['netTOA (J yr-1)'] - df['thermal OHC (J yr-1)']

    df_leakage = df[['total energy leakage (J yr-1)',
                     'atmos energy leakage (J yr-1)',
                     'ocean energy leakage (J yr-1)']]

    sec_in_year = 365.25 * 24 * 60 * 60
    earth_surface_area = 5.1e14
    df_leakage = (df_leakage / sec_in_year) / earth_surface_area
    df_leakage = df_leakage.rename(columns={"total energy leakage (J yr-1)": "total leakage ($dQ_r/dt - dH_T/dt$)",
                                            "ocean energy leakage (J yr-1)": "ocean leakage ($dQ_h/dt - dH_T/dt$)",
                                            "atmos energy leakage (J yr-1)": "non-ocean leakage ($dQ_r/dt - dQ_h/dt$)"})

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(18,8), gridspec_kw={'height_ratios': [1, 5, 1]})
    ax1.spines['bottom'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax1.tick_params(axis='x', which='both', bottom=False)
    ax2.tick_params(axis='x', which='both', bottom=False)
    ax2.spines['top'].set_visible(False)
    ax3.spines['top'].set_visible(False)
    ax1.set_ylim(30, 45)
    ax2.set_ylim(-1.5, 2.5)
    ax3.set_ylim(-45, -30)

    df_leakage.plot(ax=ax3, kind='bar', color=['gold', 'green', 'blue'], width=0.9, legend=False)
    df_leakage.plot(ax=ax2, kind='bar', color=['gold', 'green', 'blue'], width=0.9, legend=False)
    df_leakage.plot(ax=ax1, kind='bar', color=['gold', 'green', 'blue'], width=0.9)
    for tick in ax3.get_xticklabels():
        tick.set_rotation(90)

    plt.subplots_adjust(hspace=0.15)

    ax1.axvline(x=14.5, color='0.5', linewidth=2.0)
    ax2.axvline(x=14.5, color='0.5', linewidth=2.0)
    ax3.axvline(x=14.5, color='0.5', linewidth=2.0)
    ax2.axhline(y=-0.5, color='0.5', linewidth=0.5, linestyle='--')
    ax2.axhline(y=0.5, color='0.5', linewidth=0.5, linestyle='--')
    ax2.set_ylabel('$W \; m^{-2}$')

    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=200)
    log_file = re.sub('.png', '.met', inargs.outfile)
    log_text = cmdprov.new_log(git_repo=repo_dir)
    cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Create a bar chart showing energy leakage in the atmosphere and ocean'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("outfile", type=str, help="Output file name")

    args = parser.parse_args()  
    main(args)
