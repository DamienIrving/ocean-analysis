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


def get_data(infile, var, time_constraint):
    """Get the data for a particular component"""

    cube, history = gio.combine_files(infile, var, new_calendar='365_day')
    cube = cube[:, -1, :]
    cube.remove_coord('precipitation minus evaporation region')
    if time_constraint:
        cube = cube.extract(time_constraint)
    cube.data = cube.data - cube.data[0, ::]
    cube = cube[-1, ::]
    cube.remove_coord('time')
        
    return cube, history


def plot_data(ax, df, title, ylabel, model_dots=False):
    """Plot data for a given variable and experiment."""

    g = sns.barplot(data=df, ax=ax, x="basin", y=ylabel, color='grey', estimator=np.mean, ci=95) 
    if model_dots:
        g = sns.stripplot(data=df, ax=ax, x="basin", y=ylabel, hue="model", dodge=True) 
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True, useOffset=False)
    if not '(a)' in title:
        g.set(ylabel=None)
    ax.set_title(title)
    ax.set_ylim(-2e17, 3e17)
    ax.yaxis.major.formatter._useMathText = True


def sort_files(args):
    """Sort the input files."""

    file_dict = {}
    file_dict['GHG-only'] = sorted(args.ghg_files)
    file_dict['AA-only'] = sorted(args.aa_files)
    file_dict['historical'] = sorted(args.hist_files)
                              
    nfiles = len(file_dict['GHG-only'])
    assert len(file_dict['AA-only']) == nfiles
    assert len(file_dict['historical']) == nfiles
    print(f"Number of models = {nfiles}")

    return file_dict, nfiles


def main(args):
    """Run the program."""

    experiments = ['GHG-only', 'AA-only', 'historical']
    letters = ['(a) ', '(b) ', '(c) ']
    file_dict, nfiles = sort_files(args)

    start_year = args.time_bounds[0][0:4]
    end_year = args.time_bounds[1][0:4]

    var_names = {'precipitation_flux': 'precipitation',
                 'water_evapotranspiration_flux': 'evaporation',
                 'precipitation_minus_evaporation_flux': 'P-E'}
    var_name = var_names[args.var]
    ylabel = f"time integrated {var_name} anomaly, {start_year}-{end_year} (kg)"

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    time_constraint = gio.get_time_constraint(args.time_bounds)        
    for plotnum, exp in enumerate(experiments):
        data = [] 
        for modelnum, infile in enumerate(file_dict[exp]):
            cube, history = get_data(infile, args.var, time_constraint)
            try:
                model = cube.attributes['model_id']
            except KeyError:
                model = cube.attributes['source_id']
            data.append([model, 'Atlantic', cube.data[0]])
            data.append([model, 'Indian', cube.data[2]])
            data.append([model, 'Pacific', cube.data[1]])
            data.append([model, 'Land', cube.data[5]])
        df = pd.DataFrame(data, columns=['model', 'basin', ylabel])
        title = letters[plotnum] + exp
        plot_data(axes[plotnum], df, title, ylabel, model_dots=args.dots)

    plt.savefig(args.outfile, bbox_inches='tight')

    metadata_dict = {file_dict['historical'][-1]: history}
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
                                    
    parser.add_argument("var", type=str, choices=valid_variables, help="variable")
    parser.add_argument("outfile", type=str, help="output file") 

    parser.add_argument("--ghg_files", type=str, nargs='*', default=None,
                        help="Cumulative flux anomaly (kg) files for hist-GHG experiment (e.g. pe-region-sum-anomaly*cumsum.nc)")
    parser.add_argument("--aa_files", type=str, nargs='*', default=None,
                        help="Cumulative flux anomaly (kg) files for hist-aer experiment (e.g. pe-region-sum-anomaly*cumsum.nc)")
    parser.add_argument("--hist_files", type=str, nargs='*', default=None,
                        help="Cumulative flux anomaly (kg) files for historical experiment (e.g. pe-region-sum-anomaly*cumsum.nc)")
   
    parser.add_argument("--time_bounds", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = entire]")
    parser.add_argument("--dots", action="store_true", default=False,
                        help="Plot each model result as a dot [default: False]")

    args = parser.parse_args()             
    main(args)

