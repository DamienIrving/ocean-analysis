"""
Filename:     plot_interhemispheric_general_timeseries.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot the interhemispheric timeseries for a general input variable

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
import iris.plot as iplt
from iris.experimental.equalise_cubes import equalise_attributes
iris.FUTURE.netcdf_promote = True
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
    import timeseries
    import general_io as gio
    import convenient_universal as uconv
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


history = []

def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def get_area_weights(cube, area_file, lat_constraint):
    """Get area weights for averaging"""

    if area_file:
        area_cube = iris.load_cube(inargs.area_file, lat_constraint)
    else:
        area_cube = None

    if area_cube:
        area_weights = uconv.broadcast_array(area_cube.data, [1, 2], cube.shape)
    else:
        area_weights = spatial_weights.area_array(cube)

    return area_weights


def calc_mean(infiles, variable, lat_constraint, time_constraint, area_file):
    """Load the infiles and calculate the hemispheric mean values."""
    
    with iris.FUTURE.context(cell_datetime_objects=True):
        cube = iris.load(infiles, variable & lat_constraint & time_constraint, callback=save_history)
 
        equalise_attributes(cube)
        cube = cube.concatenate_cube()
        cube = gio.check_time_units(cube)

        cube = timeseries.convert_to_annual(cube)

    orig_units = str(cube.units)
    orig_atts = cube.attributes

    area_weights = get_area_weights(cube, area_file, lat_constraint)
    mean = cube.collapsed(['longitude', 'latitude'], iris.analysis.MEAN, weights=area_weights)

    return mean, orig_units, orig_atts
                

def get_data(infiles, variable, nh_lat_constraint, sh_lat_constraint, time_constraint, area_file):
    """Read and process the input data"""

    nh_mean, orig_units, orig_atts = calc_mean(infiles, variable, nh_lat_constraint,
                                               time_constraint, area_file)
    sh_mean, orig_units, orig_atts = calc_mean(infiles, variable, sh_lat_constraint,
                                               time_constraint, area_file)

    comparison_cube = nh_mean / sh_mean

    model = orig_atts['model_id']
    experiment = orig_atts['experiment_id']
    if experiment == 'historicalMisc':
        experiment = 'historicalAA'

    return comparison_cube, model, experiment, orig_units
    
    
def main(inargs):
    """Run the program."""

    time_constraint = gio.get_time_constraint(inargs.time)

    nh_lower, nh_upper = inargs.nh_lat_bounds
    nh_constraint = iris.Constraint(latitude=lambda cell: nh_lower <= cell < nh_upper)

    sh_lower, sh_upper = inargs.sh_lat_bounds
    sh_constraint = iris.Constraint(latitude=lambda cell: sh_lower <= cell < sh_upper)

    data_dict = {}
    plot_details_list = []
    for infiles in inargs.experiment_files:
        cube, model, experiment, orig_units = get_data(infiles, inargs.variable, nh_constraint, sh_constraint,
                                                                     time_constraint, inargs.area_file)
        iplt.plot(cube, label=experiment, color=experiment_colors[experiment])

    plt.legend()
    plt.xlabel('year')
    plt.ylabel('NH / SH')

    title = '%s interhemispheric %s comparison'  %(model, inargs.variable.replace('_', ' '))
    plt.title(title)
    #plt.subplots_adjust(top=0.90)

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info={inargs.experiment_files[0][0]: history[0]})


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot the interhemispheric timeseries for a general input variable'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                
    parser.add_argument("variable", type=str, help="Input variable")                                                 
    parser.add_argument("outfile", type=str, help="Output file")  

    parser.add_argument("--experiment_files", type=str, action='append', nargs='*', required=True,
                        help="Input files for a given experiment")

    parser.add_argument("--area_file", type=str, default=None, 
                        help="Input cell area file")

    parser.add_argument("--nh_lat_bounds", type=float, nargs=2, metavar=('LOWER', 'UPPER'), default=(0.0, 91.0),
                        help="Northern Hemisphere latitude bounds [default = entire hemisphere]")
    parser.add_argument("--sh_lat_bounds", type=float, nargs=2, metavar=('LOWER', 'UPPER'), default=(-91.0, 0.0),
                        help="Southern Hemisphere latitude bounds [default = entire hemisphere]")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = all]")

    args = parser.parse_args()             
    main(args)
