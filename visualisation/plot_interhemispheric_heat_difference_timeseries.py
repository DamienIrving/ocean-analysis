"""
Filename:     plot_interhemispheric_heat_difference_timeseries.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot ensemble interhemispheric heat difference timeseries for OHC, hfds and rndt

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
from iris.experimental.equalise_cubes import equalise_attributes
import iris.plot as iplt
import matplotlib.pyplot as plt
from matplotlib import gridspec
import seaborn
seaborn.set_context('talk')

# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'ocean-analysis':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)
try:
    import general_io as gio
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

colors = {'ohc': 'blue', 'hfds': 'orange', 'netTOA': 'red'}

names = {'ohc': 'ocean heat content',
         'hfds': 'Downward Heat Flux at Sea Water Surface',
         'netTOA': 'TOA Incoming Net Radiation'}


def equalise_time_axes(cube_list):
    """Make all the time axes the same."""

    iris.util.unify_time_units(cube_list)
    reference_cube = cube_list[0]
    new_cube_list = iris.cube.CubeList([])
    for cube in cube_list:
        assert len(cube.coord('time').points) == len(reference_cube.coord('time').points)
        cube.coord('time').points = reference_cube.coord('time').points
        cube.coord('time').bounds = reference_cube.coord('time').bounds
        cube.coord('time').units = reference_cube.coord('time').units
        cube.coord('time').attributes = reference_cube.coord('time').attributes
        new_cube_list.append(cube)
    
    return new_cube_list


def ensemble_aggregation(cube_list, operator):
    """Calculate the ensemble mean."""

    aggregators = {'mean': iris.analysis.MEAN, 'median': iris.analysis.MEDIAN}

    if len(cube_list) > 1:
        equalise_attributes(cube_list)
        equalise_time_axes(cube_list)
        ensemble_cube = cube_list.merge_cube()
        ensemble_agg = ensemble_cube.collapsed('ensemble_member', aggregators[operator])
    else:
        ensemble_agg = cube_list[0]

    return ensemble_agg


def calc_anomaly(cube):
    """Calculate the anomaly."""
    
    anomaly = cube.copy()
    anomaly.data = anomaly.data - anomaly.data[0]
    
    return anomaly


def get_simulation_attributes(cube):
    """Get model. experiment and mip information."""

    model = cube.attributes['model_id']
    experiment = cube.attributes['experiment_id']
    physics = cube.attributes['physics_version']
    run = cube.attributes['realization']
    mip = 'r%si1p%s' %(run, physics)

    if experiment == 'historicalMisc':
        experiment = 'historicalAA'

    return model, experiment, mip


def calc_interhemispheric_diff(nh_file, sh_file, var, time_constraint, ensemble_number):
    """Calculate the interhemispheric difference timeseries."""

    nh_name = names[var] + ' nh sum'
    nh_cube = iris.load_cube(nh_file, nh_name & time_constraint)
    nh_attributes = get_simulation_attributes(nh_cube)
    nh_anomaly = calc_anomaly(nh_cube)

    sh_name = names[var] + ' sh sum'
    sh_cube = iris.load_cube(sh_file, sh_name & time_constraint)
    sh_attributes = get_simulation_attributes(sh_cube)
    sh_anomaly = calc_anomaly(sh_cube)

    assert nh_attributes == sh_attributes 

    diff = nh_cube.copy()
    diff.data = nh_anomaly.data - sh_anomaly.data

    new_aux_coord = iris.coords.AuxCoord(ensemble_number, long_name='ensemble_member', units='no_unit')
    diff.add_aux_coord(new_aux_coord)

    diff.cell_methods = ()

    return diff


def calc_transport_tendency(upper, lower):
    """ """

    tendency = upper[1:].copy()
    diff = upper.data - lower.data
    tendency.data = numpy.diff(diff)

    return tendency


def main(inargs):
    """Run the program."""

    time_constraint = gio.get_time_constraint(inargs.time)
    #metadata_dict = {}
    #plt.axvline(x=0, color='0.5', linestyle='--')
    
    fig = plt.figure()
    gs = gridspec.GridSpec(2, 1)

    infiles = {}
    infiles['netTOA'] = inargs.rndt_files
    infiles['hfds'] = inargs.hfds_files
    infiles['ohc'] = inargs.ohc_files
    ensemble_dict = {}
    for var in ['netTOA', 'hfds', 'ohc']:
        cube_list = iris.cube.CubeList([])
        for file_num, file_pair in enumerate(infiles[var]):
            nh_file, sh_file = file_pair
            diff = calc_interhemispheric_diff(nh_file, sh_file, var, time_constraint, file_num)
            cube_list.append(diff)
        ensemble_dict[var] = ensemble_aggregation(cube_list, 'median')
        ax = plt.subplot(gs[0])
        plt.sca(ax)
        iplt.plot(ensemble_dict[var], label=var, color=colors[var])

    #plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0), useMathText=True)
    #ax.xaxis.major.formatter._useMathText = True
    ax.set_ylabel('NH minus SH (Joules)')
    plt.legend()
    plt.title('interhemispheric difference in accumulated heat')

    atmos_transport_tendency = calc_transport_tendency(ensemble_dict['hfds'], ensemble_dict['netTOA'])
    ocean_transport_tendency = calc_transport_tendency(ensemble_dict['ohc'], ensemble_dict['hfds'])
    ax = plt.subplot(gs[1])
    plt.sca(ax)
    iplt.plot(atmos_transport_tendency.rolling_window('time', iris.analysis.MEAN, 20), color='green', label='atmos transport tendency')
    iplt.plot(ocean_transport_tendency.rolling_window('time', iris.analysis.MEAN, 20), color='purple', label='ocean transport tendency')
    plt.legend()

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot ensemble interhemispheric heat difference boxplot for OHC, hfds and rndt'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("outfile", type=str, help="output file")                               
    
    parser.add_argument("--rndt_files", type=str, nargs=2, action='append', 
                        help="NH and SH integrated netTOA file, in that order (dedrifted)")
    parser.add_argument("--hfds_files", type=str, nargs=2, action='append', 
                        help="NH and SH integrated hfds file, in that order (dedrifted)")
    parser.add_argument("--ohc_files", type=str, nargs=2, action='append', 
                        help="NH and SH OHC file, in that order (dedrifted)")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=['1861-01-01', '2005-12-31'], help="Time bounds")

    args = parser.parse_args()             
    main(args)
