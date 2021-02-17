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


def get_data(infiles, var, time_constraint, operation):
    """Get the data for a particular component"""
    
    assert operation in ['anomaly', 'mean']

    cube_list = iris.cube.CubeList([])
    for ensnum, infile in enumerate(infiles):
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
        new_aux_coord = iris.coords.AuxCoord(ensnum, long_name='ensemble_member', units='no_unit')
        cube.add_aux_coord(new_aux_coord)
        cube_list.append(cube)

    if len(cube_list) > 1:
        ens_cube = ensagg.calc_ensagg(cube_list, operator='mean')
    else:
        ens_cube = cube_list[0]
        
    return ens_cube.data[0:5], history


def main(args):
    """Run the program."""

    titles = {'precipitation_minus_evaporation_flux': 'P-E',
              'water_evapotranspiration_flux': 'evaporation',
              'precipitation_flux': 'precipitation'}

    time_constraint = gio.get_time_constraint(args.time_bounds)    
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    
    total, total_history = get_data(args.total_files, args.var, time_constraint, 'anomaly')
    flux_bar, flux_history = get_data(args.flux_bar_files, args.var, None, 'mean')
    flux_dashed_integral, flux_dashed_integral_history = get_data(args.flux_dashed_files, args.var, time_constraint, 'anomaly')
    area_bar, area_bar_history = get_data(args.area_bar_files, 'cell_area', None, 'mean')
    area_dashed_integral, area_dashed_integral_history = get_data(args.area_dashed_files, 'cell_area', time_constraint, 'anomaly')

    area_component = flux_bar * area_dashed_integral
    intensity_component = area_bar * flux_dashed_integral

    data = [['total', 'SH-P', total[0]],
            ['total', 'SH-E', total[1]],
            ['total', 'T-P', total[2]],
            ['total', 'NH-E', total[3]],
            ['total', 'NH-P', total[4]],
            ['area', 'SH-P', area_component[0]],
            ['area', 'SH-E', area_component[1]],
            ['area', 'T-P', area_component[2]],
            ['area', 'NH-E', area_component[3]],
            ['area', 'NH-P', area_component[4]],
            ['intensity', 'SH-P', intensity_component[0]],
            ['intensity', 'SH-E', intensity_component[1]],
            ['intensity', 'T-P', intensity_component[2]],
            ['intensity', 'NH-E', intensity_component[3]],
            ['intensity', 'NH-P', intensity_component[4]],
           ]

    start_year = args.time_bounds[0][0:4]
    end_year = args.time_bounds[1][0:4]
    ylabel = f"time integrated anomaly, {start_year}-{end_year} (kg)"
    df = pd.DataFrame(data, columns = ['component', 'P-E region', ylabel])
    g = sns.catplot(data=df, ax=ax, kind="bar", x="P-E region", y=ylabel, hue="component")    
    g.fig.suptitle(f"{titles[args.var]}, {args.experiment}")
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True, useOffset=False)
    ax.yaxis.major.formatter._useMathText = True

    plt.savefig(args.outfile, bbox_inches='tight')

    metadata_dict = {args.total_files[0]: total_history[0],
                     args.flux_bar_files[0]: flux_history[0],
                     args.flux_dashed_files[0]: flux_dashed_integral_history[0],
                     args.area_bar_files[0]: area_bar_history[0],
                     args.area_dashed_files[0]: area_dashed_integral_history[0]
                    }
    log_text = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    log_file = re.sub('.png', '.met', args.outfile)
    cmdprov.write_log(log_file, log_text)
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                    
    parser.add_argument("var", type=str, help="variable")
    parser.add_argument("experiment", type=str, help="experiment")
    parser.add_argument("outfile", type=str, help="output file") 

    parser.add_argument("--total_files", type=str, nargs='*', default=None,
                        help="Total cumulative anomaly (kg) files (e.g. pe-region-sum-anomaly*cumsum.nc)")
    parser.add_argument("--flux_bar_files", type=str, nargs='*', default=None,
                        help="Mean flux (kg m-2) files (e.g. pe-region-mean*.nc)")
    parser.add_argument("--flux_dashed_files", type=str, nargs='*', default=None,
                        help="Mean flux (kg m-2) cumulative anomaly files (e.g. pe-region-mean-anomaly*cumsum.nc)")
    parser.add_argument("--area_bar_files", type=str, nargs='*', default=None,
                        help="Area (m2) files")
    parser.add_argument("--area_dashed_files", type=str, nargs='*', default=None,
                        help="Area (m2) cumulative anomaly files")

    parser.add_argument("--time_bounds", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = entire]")

    args = parser.parse_args()             
    main(args)
