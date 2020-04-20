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
mpl.rcParams['xtick.labelsize'] = 'large'
mpl.rcParams['ytick.labelsize'] = 'large'
mpl.rcParams['legend.fontsize'] = 'large'


# Define functions 

def get_quartiles(df, column_names, df_project, units):
    """Get the ensemble quartiles"""

    assert len(df) == len(df_project)

    quartiles = []
    for column_name in column_names:
        quartiles.append('# ' + column_name + ' quartiles')
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
    if inargs.cmip_line:
        cmip_line = inargs.cmip_line
    else:
        ncmip5 = df['project'].value_counts()['cmip5']
        cmip_line = ncmip5 - 0.5
        print('x-value for CMIP dividing line:', cmip_line)

    df['atmos energy leakage (J yr-1)'] = df['netTOA (J yr-1)'] - df['hfdsgeou (J yr-1)']
    df['ocean energy leakage (J yr-1)'] = df['hfdsgeou (J yr-1)'] - df['thermal OHC (J yr-1)']
    df['total energy leakage (J yr-1)'] = df['netTOA (J yr-1)'] - df['thermal OHC (J yr-1)']

    df_leakage = df[['total energy leakage (J yr-1)',
                     'atmos energy leakage (J yr-1)',
                     'ocean energy leakage (J yr-1)']]
    df_leakage = df_leakage.dropna(axis=0, how='all')
    x = np.arange(df_leakage.shape[0])

    sec_in_year = 365.25 * 24 * 60 * 60
    earth_surface_area = 5.1e14
    df_leakage = (df_leakage / sec_in_year) / earth_surface_area
    df_leakage = df_leakage.rename(columns={"total energy leakage (J yr-1)": "total leakage ($dQ_r/dt - dH_T/dt$)",
                                            "ocean energy leakage (J yr-1)": "ocean leakage ($dQ_h/dt - dH_T/dt$)",
                                            "atmos energy leakage (J yr-1)": "non-ocean leakage ($dQ_r/dt - dQ_h/dt$)"})

    if inargs.split_axes:
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

        df_leakage.plot(ax=ax3, kind='bar', color=['tab:olive', 'tab:green', 'tab:blue'], width=0.9, legend=False)
        df_leakage.plot(ax=ax2, kind='bar', color=['tab:olive', 'tab:green', 'tab:blue'], width=0.9, legend=False)
        df_leakage.plot(ax=ax1, kind='bar', color=['tab:olive', 'tab:green', 'tab:blue'], width=0.9)
        for tick in ax3.get_xticklabels():
            tick.set_rotation(90)

        plt.subplots_adjust(hspace=0.15)

        ax1.axvline(x=cmip_line, color='0.5', linewidth=2.0)
        ax2.axvline(x=cmip_line, color='0.5', linewidth=2.0)
        ax3.axvline(x=cmip_line, color='0.5', linewidth=2.0)
        ax2.axhline(y=-0.5, color='0.5', linewidth=0.5, linestyle='--')
        ax2.axhline(y=0.5, color='0.5', linewidth=0.5, linestyle='--')
        ax2.set_ylabel('$W \; m^{-2}$')

        ax1.axvline(x=x[0]-0.5, color='0.5', linewidth=0.1)
        ax2.axvline(x=x[0]-0.5, color='0.5', linewidth=0.1)
        ax3.axvline(x=x[0]-0.5, color='0.5', linewidth=0.1)
        for val in x:
            ax1.axvline(x=val+0.5, color='0.5', linewidth=0.1)
            ax2.axvline(x=val+0.5, color='0.5', linewidth=0.1)
            ax3.axvline(x=val+0.5, color='0.5', linewidth=0.1)

    else:
    
        df_leakage.plot.bar(figsize=(18,6), color=['tab:olive', 'tab:green', 'tab:blue'], width=0.9)
        plt.axvline(x=cmip_line, color='0.5', linewidth=2.0)
        plt.axhline(y=0.5, color='0.5', linewidth=0.5, linestyle='--')
        plt.axhline(y=-0.5, color='0.5', linewidth=0.5, linestyle='--')
        units = '$W \; m^{-2}$'
        plt.ylabel(units)
        plt.axvline(x=x[0]-0.5, color='0.5', linewidth=0.1)
        for val in x:
            plt.axvline(x=val+0.5, color='0.5', linewidth=0.1)
        plt.ylim(-1.5, 2.5)

    column_names = ["total leakage ($dQ_r/dt - dH_T/dt$)",
                    "ocean leakage ($dQ_h/dt - dH_T/dt$)",
                    "non-ocean leakage ($dQ_r/dt - dQ_h/dt$)"]
    quartiles = get_quartiles(df_leakage, column_names, df['project'], units)

    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=400)
    log_file = re.sub('.png', '.met', inargs.outfile)
    log_text = cmdprov.new_log(git_repo=repo_dir, extra_notes=quartiles)
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

    parser.add_argument("--cmip_line", type=float, default=None,
                        help="Override default CMIP line, which can be wrong if nan models")
    parser.add_argument("--split_axes", action="store_true", default=False,
                        help="Split the axes to accommodate outliers")

    args = parser.parse_args()  
    main(args)
