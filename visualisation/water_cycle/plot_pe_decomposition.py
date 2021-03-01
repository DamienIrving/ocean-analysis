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


def plot_data(ax, df, exp, ylabel, ymax, model_dots=False):
    """Plot data for a given variable and experiment."""

    g = sns.barplot(data=df, ax=ax, x="P-E region", y=ylabel, hue="component", estimator=np.mean) 
    if model_dots:
        g = sns.stripplot(data=df, ax=ax, x="P-E region", y=ylabel, hue="component", dodge=True)
    if ymax:
        ax.set(ylim=(-ymax * 1e17, ymax * 1e17))  
    ax.set_title(exp)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True, useOffset=False)
    ax.yaxis.major.formatter._useMathText = True


def sort_files(args):
    """Sort the input files."""

    flux_bar_files = sorted(args.flux_bar_files)
    area_bar_files = sorted(args.area_bar_files)

    file_dict = {}
    file_dict['GHG-only'] = [sorted(args.ghg_total_files),
                             sorted(args.ghg_flux_dashed_files),
                             sorted(args.ghg_area_dashed_files)]
    file_dict['AA-only'] =  [sorted(args.aa_total_files),
                             sorted(args.aa_flux_dashed_files),
                             sorted(args.aa_area_dashed_files)]
    file_dict['historical'] =  [sorted(args.hist_total_files),
                                sorted(args.hist_flux_dashed_files),
                                sorted(args.hist_area_dashed_files)]

    nfiles = len(args.ghg_total_files)
    for exp, group in file_dict.items():
        for subgroup in group:
            nsubfiles = len(subgroup)
            assert nsubfiles == nfiles, f"Missing {nfiles - nsubfiles} file of {nfiles} in {subgroup}"
    assert len(area_bar_files) == nfiles
    assert len(flux_bar_files) == nfiles
    print(f"Number of models = {nfiles}")

    return area_bar_files, flux_bar_files, file_dict, nfiles


def main(args):
    """Run the program."""

    experiments = ['GHG-only', 'AA-only', 'historical']
    area_bar_files, flux_bar_files, file_dict, nfiles = sort_files(args)

    start_year = args.time_bounds[0][0:4]
    end_year = args.time_bounds[1][0:4]

    var_names = {'precipitation_flux': 'precipitation',
                 'water_evapotranspiration_flux': 'evaporation',
                 'precipitation_minus_evaporation_flux': 'P-E'}
    var_name = var_names[args.var]
    ylabel = f"time integrated {var_name} anomaly, {start_year}-{end_year} (kg)"

    time_constraint = gio.get_time_constraint(args.time_bounds)        
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    for plotnum, exp in enumerate(experiments): 
        total_files, flux_dashed_files, area_dashed_files = file_dict[exp]
        data = []
        for modelnum in range(nfiles):
            total_cube, history = get_data(total_files[modelnum], args.var, time_constraint, 'anomaly', ref_model=None)
            try:
                model = total_cube.attributes['model_id']
            except KeyError:
                model = total_cube.attributes['source_id']
            flux_bar_cube, history = get_data(flux_bar_files[modelnum], args.var, None, 'mean', ref_model=model)
            flux_dashed_integral_cube, history = get_data(flux_dashed_files[modelnum], args.var, time_constraint, 'anomaly', ref_model=model)
            area_bar_cube, area_bar_history = get_data(area_bar_files[modelnum], 'cell_area', None, 'mean', ref_model=model)
            area_dashed_integral_cube, area_dashed_integral_history = get_data(area_dashed_files[modelnum], 'cell_area',
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
        plot_data(axes[plotnum], df, exp, ylabel, args.ymax, model_dots=args.dots)

    plt.savefig(args.outfile, bbox_inches='tight')

    metadata_dict = {area_bar_files[0]: area_bar_history[0],
                     area_dashed_files[0]: area_dashed_integral_history[0]}
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

    parser.add_argument("--ghg_total_files", type=str, nargs='*', default=None,
                        help="Total cumulative flux anomaly (kg) files for hist-GHG experiment (e.g. pe-region-sum-anomaly*cumsum.nc)")
    parser.add_argument("--ghg_flux_dashed_files", type=str, nargs='*', default=None,
                        help="Mean flux (kg m-2) cumulative anomaly files for hist-GHG experiment (e.g. pe-region-mean-anomaly*cumsum.nc)")
    parser.add_argument("--ghg_area_dashed_files", type=str, nargs='*', default=None,
                        help="Area (m2) cumulative anomaly files for hist-GHG experiment (e.g. areacella-pe-region-sum-anomaly*cumsum.nc")

    parser.add_argument("--aa_total_files", type=str, nargs='*', default=None,
                        help="Total cumulative flux anomaly (kg) files for hist-aer experiment (e.g. pe-region-sum-anomaly*cumsum.nc)")
    parser.add_argument("--aa_flux_dashed_files", type=str, nargs='*', default=None,
                        help="Mean flux (kg m-2) cumulative anomaly files for hist-aer experiment (e.g. pe-region-mean-anomaly*cumsum.nc)")
    parser.add_argument("--aa_area_dashed_files", type=str, nargs='*', default=None,
                        help="Area (m2) cumulative anomaly files for hist-aer experiment (e.g. areacella-pe-region-sum-anomaly*cumsum.nc")

    parser.add_argument("--hist_total_files", type=str, nargs='*', default=None,
                        help="Total cumulative flux anomaly (kg) files for historical experiment (e.g. pe-region-sum-anomaly*cumsum.nc)")
    parser.add_argument("--hist_flux_dashed_files", type=str, nargs='*', default=None,
                        help="Mean flux (kg m-2) cumulative anomaly files for historical experiment (e.g. pe-region-mean-anomaly*cumsum.nc)")
    parser.add_argument("--hist_area_dashed_files", type=str, nargs='*', default=None,
                        help="Area (m2) cumulative anomaly files for historical experiment (e.g. areacella-pe-region-sum-anomaly*cumsum.nc")

    parser.add_argument("--flux_bar_files", type=str, nargs='*', default=None,
                        help="Mean flux (kg m-2) files for piControl experiment (e.g. pe-region-mean*.nc)")
    parser.add_argument("--area_bar_files", type=str, nargs='*', default=None,
                        help="Area (m2) files for piControl experiment (e.g. areacella-pe-region-sum*.nc)")

    parser.add_argument("--time_bounds", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = entire]")
    parser.add_argument("--ymax", type=float, default=None,
                        help="y axis maximum value (* 10^17)")
    parser.add_argument("--dots", action="store_true", default=False,
                        help="Plot each model result as a dot [default: False]")

    args = parser.parse_args()             
    main(args)
