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


def get_data(infile, variable, nh_lat_constraint, sh_lat_constraint, time_constraint, area_file):
    """Read the input data"""

    with iris.FUTURE.context(cell_datetime_objects=True):
        nh_cube = iris.load_cube(infile, variable & nh_lat_constraint & time_constraint)
        sh_cube = iris.load_cube(infile, variable & sh_lat_constraint & time_constraint)

        nh_cube = timeseries.convert_to_annual(nh_cube)
        sh_cube = timeseries.convert_to_annual(sh_cube)

    orig_units = str(nh_cube.units)

    nh_area_weights = get_area_weights(nh_cube, area_file, nh_lat_constraint)
    sh_area_weights = get_area_weights(sh_cube, area_file, sh_lat_constraint)

    nh_mean = nh_cube.collapsed(['longitude', 'latitude'], iris.analysis.MEAN, weights=nh_area_weights)
    sh_mean = sh_cube.collapsed(['longitude', 'latitude'], iris.analysis.MEAN, weights=sh_area_weights)

    comparison_cube = nh_mean / sh_mean

    history = sh_cube.attributes['history']
    model = sh_cube.attributes['model_id']
    experiment = sh_cube.attributes['experiment_id']
    if experiment == 'historicalMisc':
        experiment = 'historicalAA'
    run = 'r' + str(sh_cube.attributes['realization'])

    return comparison_cube, history, model, experiment, run, orig_units
    
    
def main(inargs):
    """Run the program."""

    time_constraint = gio.get_time_constraint(inargs.time)

    nh_lower, nh_upper = inargs.nh_lat_bounds
    nh_constraint = iris.Constraint(latitude=lambda cell: nh_lower <= cell < nh_upper)

    sh_lower, sh_upper = inargs.sh_lat_bounds
    sh_constraint = iris.Constraint(latitude=lambda cell: sh_lower <= cell < sh_upper)

    data_dict = {}
    plot_details_list = []
    for infile in inargs.infiles:
        cube, history, model, experiment, run, orig_units = get_data(infile, inargs.variable, nh_constraint, sh_constraint,
                                                                     time_constraint, inargs.area_file)
        iplt.plot(cube, label=experiment, color=experiment_colors[experiment])

    plt.legend()
    plt.xlabel('year')
    plt.ylabel('NH / SH')

    title = '%s interhemispheric %s comparison'  %(model, inargs.variable.replace('_', ' '))
    plt.title(title)
    #plt.subplots_adjust(top=0.90)

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info={inargs.infiles[-1]: history})


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
               
    parser.add_argument("infiles", type=str, nargs='*', help="Input files")   
    parser.add_argument("variable", type=str, help="Input variable")                                                 
    parser.add_argument("outfile", type=str, help="Output file")  

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
