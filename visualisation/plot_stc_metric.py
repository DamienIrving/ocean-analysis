"""
Filename:     plot_stc_metric.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot metrics for the subtropical cells

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
import iris.plot as iplt
from iris.experimental.equalise_cubes import equalise_attributes
import matplotlib.pyplot as plt
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
    import spatial_weights
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

experiment_colors = {'historical': 'orange',
                     'historicalGHG': 'red',
                     'historicalAA': 'blue',
                     'rcp26': '#16DB65',
                     'rcp45': '#058C42',
                     'rcp60': '#04471C',
                     'rcp85': '#0D2818'}

basin_index = {'pacific': 1,
               'atlantic': 0,
               'globe': 2}

history = []

def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history']) 


def plot_hemispheres(ax, nmetric, smetric, experiment, basin):
    """Plot interhemispheric comparison."""
    
    plt.sca(ax)

    iplt.plot(smetric * -1, label=experiment + ', SH',
              color=experiment_colors[experiment], linestyle='--')
    if not basin == 'atlantic':
        iplt.plot(nmetric, label=experiment + ', NH',
                  color=experiment_colors[experiment], linestyle='-')

    plt.legend()
    plt.ylabel(str(nmetric.units))
    plt.xlabel('Year')
    plt.title(basin.title() + ' hemispheric values')


def plot_comparison(ax, nmetric, smetric, experiment, basin):
    """Plot interhemispheric comparison."""
    
    plt.sca(ax)

    data = nmetric / (-1 * smetric)
    ylabel = 'NH / SH'

    iplt.plot(data, label=experiment, color=experiment_colors[experiment])

    plt.legend()
    plt.ylabel(ylabel)
    plt.xlabel('Year')
    plt.title(basin.title() + ' hemisphere comparison')


def calc_metrics(sh_cube, nh_cube):
    """Calculate the metrics."""

    dim_coord_names = [coord.name() for coord in sh_cube.dim_coords]
    nh_vert_extents = spatial_weights.calc_vertical_weights_1D(nh_cube.coord('depth'),
                                                               dim_coord_names,
                                                               nh_cube.shape)
    sh_vert_extents = spatial_weights.calc_vertical_weights_1D(sh_cube.coord('depth'),
                                                              dim_coord_names,
                                                              sh_cube.shape)
    
    nh_cube.data = numpy.where(nh_cube.data > 0, nh_cube.data, 0)
    sh_cube.data = numpy.where(sh_cube.data < 0, sh_cube.data, 0)
    
    nh_metric = nh_cube.collapsed(['depth', 'latitude'], iris.analysis.SUM, weights=nh_vert_extents)
    sh_metric = sh_cube.collapsed(['depth', 'latitude'], iris.analysis.SUM, weights=sh_vert_extents)

    return sh_metric, nh_metric
    

def load_data(infile, basin):
    """Load, temporally aggregate and spatially slice input data"""
    
    try:
        with iris.FUTURE.context(cell_datetime_objects=True):
            cube = iris.load(infile, 'ocean_meridional_overturning_mass_streamfunction', callback=save_history)
            equalise_attributes(cube)
            cube = cube.concatenate_cube()
            cube = gio.check_time_units(cube)

            cube = cube[:, basin_index[basin], : ,:]
            cube = timeseries.convert_to_annual(cube)

        experiment = cube.attributes['experiment_id']
        if experiment == 'historicalMisc':
            experiment = 'historicalAA'
    
        depth_constraint = iris.Constraint(depth=lambda cell: cell <= 250)
        sh_constraint = iris.Constraint(latitude=lambda cell: -30.0 <= cell < 0.0)
        nh_constraint = iris.Constraint(latitude=lambda cell: 0.0 < cell <= 30.0)

        sh_cube = cube.extract(depth_constraint & sh_constraint)
        nh_cube = cube.extract(depth_constraint & nh_constraint)
    except OSError:
        sh_cube = nh_cube = experiment = None

    return sh_cube, nh_cube, experiment

    
def main(inargs):
    """Run the program."""

    time_constraints = {}
    time_constraints['historical'] = gio.get_time_constraint(inargs.hist_time)
    time_constraints['rcp'] = gio.get_time_constraint(inargs.rcp_time)

    width=10
    height=20
    fig = plt.figure(figsize=(width, height))
    ax_dict = {}
    ax1 = fig.add_subplot(3, 1, 1)
    ax2 = fig.add_subplot(3, 1, 2)
    ax3 = fig.add_subplot(3, 1, 3)
    valid_files = []
    for infiles in inargs.experiment_files:
        spacific_cube, npacific_cube, experiment = load_data(infiles, 'pacific')
        satlantic_cube, natlantic_cube, experiment = load_data(infiles, 'atlantic')
        if experiment:
            spacific_metric, npacific_metric = calc_metrics(spacific_cube, npacific_cube)
            satlantic_metric, natlantic_metric = calc_metrics(satlantic_cube, natlantic_cube)
            plot_hemispheres(ax1, npacific_metric, spacific_metric, experiment, 'pacific')
            plot_comparison(ax2, npacific_metric, spacific_metric, experiment, 'pacific')
            plot_hemispheres(ax3, natlantic_metric, satlantic_metric, experiment, 'atlantic')
            model = spacific_cube.attributes['model_id']
            valid_files.append(infiles)

    title = 'Annual Mean Meridional Overturning Mass Streamfunction, %s'  %(model)
    plt.suptitle(title, size='large')
#    plt.subplots_adjust(top=0.90)

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info={valid_files[0][0]: history[0]})


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot a summary of the system heat distribution'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                                            
    parser.add_argument("outfile", type=str, help="Output file")  
    parser.add_argument("--experiment_files", type=str, action='append', nargs='*', required=True, 
                        help="Input msftmyz files for a given experiment")

    parser.add_argument("--hist_time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = all]")
    parser.add_argument("--rcp_time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = all]")

    args = parser.parse_args()             
    main(args)
