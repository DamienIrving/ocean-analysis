"""
Filename:     plot_zonal_ensemble.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot zonal mean for an ensemble of models  

"""

# Import general Python modules

import sys, os, pdb
import argparse
from itertools import groupby
from  more_itertools import unique_everseen
import numpy
import iris
from iris.experimental.equalise_cubes import equalise_attributes
import iris.plot as iplt
import matplotlib.pyplot as plt
from matplotlib import gridspec
import seaborn

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
    import timeseries
    import grids
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def make_zonal_grid():
    """Make a dummy cube with desired grid."""
    
    lat_values = numpy.arange(-90, 91.5, 1.5)   
    latitude = iris.coords.DimCoord(lat_values,
                                    standard_name='latitude',
                                    units='degrees_north',
                                    coord_system=iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS))

    dummy_data = numpy.zeros((len(lat_values)))
    new_cube = iris.cube.Cube(dummy_data, dim_coords_and_dims=[(latitude, 0),])

    new_cube.coord('latitude').guess_bounds()

    return new_cube


def calc_trend_cube(cube):
    """Calculate trend and put into appropriate cube."""
    
    trend_array = timeseries.calc_trend(cube, per_yr=True)
    new_cube = cube[0,:].copy()
    new_cube.remove_coord('time')
    new_cube.data = trend_array
    
    return new_cube


def get_colors(family_list):
    """Define a color for each model/physics combo"""

    nfamilies = len(family_list)
    cm = plt.get_cmap('nipy_spectral')
    colors = [cm(1. * i / (nfamilies + 1)) for i in range(nfamilies + 1)]
    color_dict = {}
    count = 1  # skips the first color, which is black
    for family in family_list:
        color_dict[family] = colors[count]
        count = count + 1

    return color_dict


def get_ylabel(cube, inargs):
    """get the y axis label"""

    ylabel = '$%s' %(str(cube.units))
    if inargs.perlat:
        ylabel = ylabel + ' \: lat^{-1}'
    if inargs.time_agg == 'trend':
        ylabel = ylabel + ' \: yr^{-1}'
    ylabel = ylabel + '$'

    return ylabel


def get_line_width(realization, model):
    """Get the line width"""

    if model == 'FGOALS-g2':
        lw = 2.0
    else:
        lw = 2.0 if realization == 'r1' else 0.5

    return lw


def plot_individual(data_dict, color_dict):
    """Plot the individual model data"""

    for key, cube in data_dict.items():
        model, physics, realization = key
        if (realization == 'r1') or (model == 'FGOALS-g2'):
            label = model + ', ' + physics
        else:
            label = None
        lw = 0.5   #get_line_width(realization, model)
        iplt.plot(cube, label=label, color=color_dict[(model, physics)], linewidth=lw)


def plot_ensmean(data_dict, time_period, ntimes, single_run=False):
    """Plot the ensemble mean.

    If single_run is true, the ensemble is calculated using
      only the first run from each model/physics family.

    """

    target_grid = make_zonal_grid()
    regridded_cube_list = iris.cube.CubeList([])
    count = 0
    for key, cube in data_dict.items():
        model, physics, realization = key
        if not single_run or ((realization == 'r1') or (model == 'FGOALS-g2')):
            regridded_cube = grids.regrid_1D(cube, target_grid, 'latitude')
            new_aux_coord = iris.coords.AuxCoord(count, long_name='ensemble_member', units='no_unit')
            regridded_cube.add_aux_coord(new_aux_coord)
            regridded_cube.cell_methods = None
            regridded_cube_list.append(regridded_cube)
            count = count + 1

    equalise_attributes(regridded_cube_list)
    ensemble_cube = regridded_cube_list.merge_cube()
   
    label, color = get_ensemble_label_color(time_period, ntimes, single_run)
    ensemble_mean = ensemble_cube.collapsed('ensemble_member', iris.analysis.MEAN)
    iplt.plot(ensemble_mean, label=label, color=color, linewidth=2.0)

    return ensemble_mean


def get_ensemble_label_color(time_period, ntimes, single_run):
    """Get the line label and color."""

    ensemble_colors = ['blue', 'red', 'green']

    label = 'ensemble mean (r1)' if single_run else 'ensemble mean (all runs)'
    color = 'black' 
    if ntimes > 1:
        label = '%s, %s-%s' %(label, time_period[0][0:4], time_period[1][0:4]) 
        color=None

    return label, color


def group_runs(data_dict):
    """Find unique model/physics groups"""

    all_info = data_dict.keys()

    model_physics_list = []
    for key, group in groupby(all_info, lambda x: x[0:2]):
        model_physics_list.append(key)

    family_list = list(unique_everseen(model_physics_list))

    return family_list


def read_data(inargs, time_constraint):
    """Read data."""

    data_dict = {}
    for infile in inargs.infiles:
        with iris.FUTURE.context(cell_datetime_objects=True):
            cube = iris.load_cube(infile, gio.check_iris_var(inargs.var) & time_constraint)
        
        if inargs.perlat:
            grid_spacing = grids.get_grid_spacing(cube) 
            cube.data = cube.data / grid_spacing
 
        if inargs.time_agg == 'trend':
            agg_cube = calc_trend_cube(cube)
            plot_name = 'linear trend'
        elif inargs.time_agg == 'climatology':
            agg_cube = cube.collapsed('time', iris.analysis.MEAN)
            agg_cube.remove_coord('time')
            plot_name = 'climatology'

        model = cube.attributes['model_id']
        realization = 'r' + str(cube.attributes['realization'])
        physics = 'p' + str(cube.attributes['physics_version'])

        data_dict[(model, physics, realization)] = agg_cube
    
    experiment = cube.attributes['experiment_id']    
    ylabel = get_ylabel(cube, inargs)
    metadata_dict = {infile: cube.attributes['history']}
    
    return data_dict, plot_name, experiment, ylabel, metadata_dict


def get_title(plot_name, time_list, experiment):
    """Get the plot title"""

    experiment_text = 'historicalAA' if experiment == "historicalMisc" else experiment 
    ntimes = len(time_list) 
    if ntimes == 1:
        title = '%s, %s-%s (%s experiment)' %(plot_name, time_list[0][0][0:4], time_list[0][1][0:4], experiment_text)
    else:
        title = '%s,%s experiment' %(plot_name, experiment_text)

    return title


def correct_y_lim(ax, data_cube):   
   """Adjust the y limits after changing x limit 

   x: data for entire x-axes
   y: data for entire y-axes

   """

   x_data = data_cube.coord('latitude').points
   y_data = data_cube.data

   lims = ax.get_xlim()
   i = numpy.where( (x_data > lims[0]) & (x_data < lims[1]) )[0]

   plt.ylim( y_data[i].min(), y_data[i].max() ) 


def main(inargs):
    """Run the program."""
    
    fig, ax = plt.subplots(figsize=[14, 7])
    ntimes = len(inargs.time) 
    for time_period in inargs.time:
        time_constraint = gio.get_time_constraint(time_period)
        data_dict, plot_name, experiment, ylabel, metadata_dict = read_data(inargs, time_constraint)
    
        model_family_list = group_runs(data_dict)
        color_dict = get_colors(model_family_list)

        if ntimes == 1:
            plot_individual(data_dict, color_dict)
        ensemble_mean = plot_ensmean(data_dict, time_period, ntimes, single_run=inargs.single_run)

    title = get_title(plot_name, inargs.time, experiment)
    plt.title(title)
    plt.xticks(numpy.arange(-75, 90, 15))
    plt.xlim(inargs.xlim[0], inargs.xlim[1])
    if not inargs.xlim == [-90, 90]:
        correct_y_lim(ax, ensemble_mean)

    plt.ylabel(ylabel)
    plt.xlabel('latitude')
    plt.axhline(y=0, color='0.5', linestyle='--')

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot zonal ensemble'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input files")
    parser.add_argument("var", type=str, help="Variable")
    parser.add_argument("time_agg", type=str, choices=('trend', 'climatology'), help="Temporal aggregation")
    parser.add_argument("outfile", type=str, help="Output file")                                     
    
    parser.add_argument("--time", type=str, action='append', nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")
    parser.add_argument("--perlat", action="store_true", default=False,
                        help="Scale per latitude [default=False]")
    parser.add_argument("--single_run", action="store_true", default=False,
                        help="Only use run 1 in the ensemble mean [default=False]")

    parser.add_argument("--xlim", type=float, nargs=2, metavar=('SOUTHERN_LIMIT', 'NORTHERN LIMIT'), default=(-90, 90),
                        help="x-axis limits [default = entire]")

    args = parser.parse_args()             
    main(args)
