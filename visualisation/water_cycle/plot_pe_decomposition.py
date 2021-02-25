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
script_dir = repo_dir + '/data_processing'
sys.path.append(module_dir)
sys.path.append(script_dir)
try:
    import general_io as gio
    import calc_ensemble_aggregate as ensagg
except ImportError:
    raise ImportError('Script and modules in wrong directories')


def get_data(infile, var, time_constraint, operation, ref_model=None):
    """Get the data for a particular component"""
    
    assert operation in ['anomaly', 'mean']

    cube, history = gio.combine_files(infile, var, new_calendar='365_day')
    cube = cube[:, :, -1]
    cube.remove_coord('region')
    if time_constraint:
        cube = cube.extract(time_constraint)
    if operation == 'mean':
        cube = cube.collapsed('time', iris.analysis.MEAN)
    else:
        cube.data = cube.data - cube.data[0, ::]
        cube = cube[-1, ::]
    cube.remove_coord('time')

    if ref_model:
        try:
            model = cube.attributes['model_id']
        except KeyError:
            model = cube.attributes['source_id']
        assert model == ref_model, f"Model mismatch: {ref_model}, {model}"
        
    return cube, history


def plot_data(ax, df, variable, ylabel, ymax):
    """Plot data for a given variable and experiment."""
    
    titles = {'precipitation_flux': 'precipitation',
              'water_evapotranspiration_flux': 'evaporation',
              'precipitation_minus_evaporation_flux': 'P-E'}

    g = sns.barplot(data=df, ax=ax, x="P-E region", y=ylabel, hue="component") 
    #g = sns.stripplot(data=df, ax=ax, x="P-E region", y=ylabel, hue="component", dodge=True)
    if ymax:
        ax.set(ylim=(-ymax * 1e17, ymax * 1e17))  
    ax.set_title(titles[variable])
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True, useOffset=False)
    ax.yaxis.major.formatter._useMathText = True


def main(args):
    """Run the program."""

    variables = ['precipitation_flux',
                 'water_evapotranspiration_flux',
                 'precipitation_minus_evaporation_flux']

    flux_files = [[sorted(args.pr_total_files),
                   sorted(args.pr_bar_files),
                   sorted(args.pr_dashed_files),
                  ],
                  [sorted(args.evap_total_files),
                   sorted(args.evap_bar_files),
                   sorted(args.evap_dashed_files),
                  ],
                  [sorted(args.pe_total_files),
                   sorted(args.pe_bar_files),
                   sorted(args.pe_dashed_files),
                  ]]
    nfiles = len(args.pr_total_files)
    for group in flux_files:
        for subgroup in group:
            nsubfiles = len(subgroup)
            assert nsubfiles == nfiles, f"Missing {nfiles - nsubfiles} files in {subgroup}"
    print(f"Number of models = {nfiles}")

    start_year = args.time_bounds[0][0:4]
    end_year = args.time_bounds[1][0:4]
    ylabel = f"time integrated anomaly, {start_year}-{end_year} (kg)"

    time_constraint = gio.get_time_constraint(args.time_bounds)        
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    for plotnum, file_list in enumerate(flux_files): 
        total_files, flux_bar_files, flux_dashed_files = file_list
        data = []
        var = variables[plotnum]
        for modelnum in range(nfiles):
            total_cube, history = get_data(total_files[modelnum], var, time_constraint, 'anomaly', ref_model=None)
            try:
                model = total_cube.attributes['model_id']
            except KeyError:
                model = total_cube.attributes['source_id']
            print(model)
            flux_bar_cube, history = get_data(flux_bar_files[modelnum], var, None, 'mean', ref_model=model)
            flux_dashed_integral_cube, history = get_data(flux_dashed_files[modelnum], var, time_constraint, 'anomaly', ref_model=model)
            area_bar_cube, area_bar_history = get_data(args.area_bar_files[modelnum], 'cell_area', None, 'mean', ref_model=model)
            area_dashed_integral_cube, area_dashed_integral_history = get_data(args.area_dashed_files[modelnum], 'cell_area',
                                                                               time_constraint, 'anomaly', ref_model=model)
            
            area_component = flux_bar_cube.data * area_dashed_integral_cube.data
            intensity_component = area_bar_cube.data * flux_dashed_integral_cube.data

            data.append([model, 'total', 'SH-P', total_cube.data[0]])
            data.append([model, 'total', 'SH-E', total_cube.data[1]])
            data.append([model, 'total', 'T-P', total_cube.data[2]])
            data.append([model, 'total', 'NH-E', total_cube.data[3]])
            data.append([model, 'total', 'NH-P', total_cube.data[4]])
            data.append([model, 'intensity', 'SH-P', intensity_component[0]])
            data.append([model, 'intensity', 'SH-E', intensity_component[1]])
            data.append([model, 'intensity', 'T-P', intensity_component[2]])
            data.append([model, 'intensity', 'NH-E', intensity_component[3]])
            data.append([model, 'intensity', 'NH-P', intensity_component[4]])
            data.append([model, 'area', 'SH-P', area_component[0]])
            data.append([model, 'area', 'SH-E', area_component[1]])
            data.append([model, 'area', 'T-P', area_component[2]])
            data.append([model, 'area', 'NH-E', area_component[3]])
            data.append([model, 'area', 'NH-P', area_component[4]])
           
        df = pd.DataFrame(data, columns=['model', 'component', 'P-E region', ylabel])
        plot_data(axes[plotnum], df, var, ylabel, args.ymax)

    plt.suptitle(args.experiment)
    plt.savefig(args.outfile, bbox_inches='tight')

    metadata_dict = {args.area_bar_files[0]: area_bar_history[0],
                     args.area_dashed_files[0]: area_dashed_integral_history[0]}
    log_text = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    log_file = re.sub('.png', '.met', args.outfile)
    cmdprov.write_log(log_file, log_text)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                    
    parser.add_argument("experiment", type=str, help="experiment")
    parser.add_argument("outfile", type=str, help="output file") 

    parser.add_argument("--pr_total_files", type=str, nargs='*', default=None,
                        help="Total cumulative precipitation anomaly (kg) files (e.g. pr-pe-region-sum-anomaly*cumsum.nc)")
    parser.add_argument("--pr_bar_files", type=str, nargs='*', default=None,
                        help="Mean precipitation (kg m-2) files (e.g. pr-pe-region-mean*.nc)")
    parser.add_argument("--pr_dashed_files", type=str, nargs='*', default=None,
                        help="Mean precipitation (kg m-2) cumulative anomaly files (e.g. pr-pe-region-mean-anomaly*cumsum.nc)")

    parser.add_argument("--evap_total_files", type=str, nargs='*', default=None,
                        help="Total cumulative evaporation anomaly (kg) files (e.g. evspsbl-pe-region-sum-anomaly*cumsum.nc)")
    parser.add_argument("--evap_bar_files", type=str, nargs='*', default=None,
                        help="Mean evaporation (kg m-2) files (e.g. evspsbl-pe-region-mean*.nc)")
    parser.add_argument("--evap_dashed_files", type=str, nargs='*', default=None,
                        help="Mean evaporation (kg m-2) cumulative anomaly files (e.g. evspsbl-pe-region-mean-anomaly*cumsum.nc)")

    parser.add_argument("--pe_total_files", type=str, nargs='*', default=None,
                        help="Total cumulative P-E anomaly (kg) files (e.g. pe-region-sum-anomaly*cumsum.nc)")
    parser.add_argument("--pe_bar_files", type=str, nargs='*', default=None,
                        help="Mean P-E (kg m-2) files (e.g. pe-region-mean*.nc)")
    parser.add_argument("--pe_dashed_files", type=str, nargs='*', default=None,
                        help="Mean P-E (kg m-2) cumulative anomaly files (e.g. pe-region-mean-anomaly*cumsum.nc)")

    parser.add_argument("--area_bar_files", type=str, nargs='*', default=None,
                        help="Area (m2) files")
    parser.add_argument("--area_dashed_files", type=str, nargs='*', default=None,
                        help="Area (m2) cumulative anomaly files")

    parser.add_argument("--time_bounds", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = entire]")
    parser.add_argument("--ymax", type=float, default=None,
                        help="y axis maximum value (* 10^17)")

    args = parser.parse_args()             
    main(args)
