"""Plot P-E (or P or E) decomposition into area and intensity components"""

import sys
script_dir = sys.path[0]
import os
import pdb
import re
import argparse

import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import iris
import cmdline_provenance as cmdprov

repo_dir = '/'.join(script_dir.split('/')[:-2])
module_dir = repo_dir + '/modules'
sys.path.append(module_dir)
try:
    import general_io as gio
except ImportError:
    raise ImportError('Script and modules in wrong directories')


def plot_data(ax, df, xcoord, ylabel, title, model_dots=False):
    """Plot data for a given variable and experiment."""

    g = sns.barplot(data=df, ax=ax, x=xcoord, y=ylabel, color='grey', estimator=np.mean, ci=95) 
    if model_dots:
        g = sns.stripplot(data=df, ax=ax, x=xcoord, y=ylabel, dodge=True) 
    ax.set_title(title)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True, useOffset=False)
    ax.yaxis.major.formatter._useMathText = True


def main(args):
    """Run the program."""

    infiles = sorted(args.infiles)

    var_names = {'precipitation_flux': 'precipitation',
                 'water_evapotranspiration_flux': 'evaporation',
                 'precipitation_minus_evaporation_flux': 'P-E'}
    var_name = var_names[args.var]
    ylabel = f"annual mean {var_name} (kg)"
       
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
 
    region_data = []
    basin_data = []
    nfiles = len(infiles)
    print(f"Number models: {nfiles}")
    for modelnum in range(nfiles):
        cube, history = gio.combine_files(infiles[modelnum], args.var)
        cube = cube.collapsed('time', iris.analysis.MEAN)
        cube.remove_coord('time')
        try:
            model = cube.attributes['model_id']
        except KeyError:
            model = cube.attributes['source_id']
        
        # cube(time, pereg, basin)
        #  pereg: SH_precip SH_evap tropical_precip NH_evap NH_precip globe
        #  basin: atlantic pacific indian arctic marginal_seas land ocean globe
        
        region_data.append([model, 'SH-P', cube.data[0, -1]])
        region_data.append([model, 'SH-E', cube.data[1, -1]])
        region_data.append([model, 'T-P', cube.data[2, -1]])
        region_data.append([model, 'NH-E', cube.data[3, -1]])
        region_data.append([model, 'NH-P', cube.data[4, -1]])

        basin_data.append([model, 'Atlantic', cube.data[-1, 0]])
        basin_data.append([model, 'Indian', cube.data[-1, 2]])
        basin_data.append([model, 'Pacific', cube.data[-1, 1]])
        basin_data.append([model, 'Land', cube.data[-1, 5]])
           
    region_df = pd.DataFrame(region_data, columns=['model', 'P-E region', ylabel])
    basin_df = pd.DataFrame(basin_data, columns=['model', 'basin', ylabel])
    plot_data(axes[0], region_df, 'P-E region', ylabel,
              '(a) meridional climatology', model_dots=args.dots)
    plot_data(axes[1], basin_df, 'basin', ylabel,
              '(b) zonal climatology', model_dots=args.dots)

    plt.savefig(args.outfile, bbox_inches='tight')

    metadata_dict = {infiles[-1]: history[0]}
    log_text = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    log_file = re.sub('.png', '.met', args.outfile)
    cmdprov.write_log(log_file, log_text)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    valid_variables = ['precipitation_flux',
                       'water_evapotranspiration_flux',
                       'precipitation_minus_evaporation_flux']
    
    parser.add_argument("infiles", type=str, nargs='*', help="input files") 
    parser.add_argument("var", type=str, choices=valid_variables, help="variable")
    parser.add_argument("outfile", type=str, help="output file") 

    parser.add_argument("--dots", action="store_true", default=False,
                        help="Plot each model result as a dot [default: False]")

    args = parser.parse_args()             
    main(args)

