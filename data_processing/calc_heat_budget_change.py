"""
Filename:     calc_heat_budget_change.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the heat budget change between two time periods

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
import iris.coord_categorisation

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
    import spatial_weights
    import timeseries
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

history = []


def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def convert_to_joules(cube):
    """Convert units to Joules"""

    assert 'W' in str(cube.units)
    assert 'days' in str(cube.coord('time').units)
    
    time_span_days = cube.coord('time').bounds[:, 1] - cube.coord('time').bounds[:, 0]
    time_span_seconds = time_span_days * 60 * 60 * 24
    
    cube.data = cube.data * uconv.broadcast_array(time_span_seconds, 0, cube.shape)
    cube.units = str(cube.units).replace('W', 'J')
    
    return cube
    

def get_data(infile):
     """Get the data."""

    data_dict = {}
    cube_list = iris.load(infile)

    cube_list = iris.load(infile)


def get_control_time_constraints(control_cube, hist_cube):
    """ """

    branch_time = hist_cube.attributes['branch_time']

    iris.coord_categorisation.add_year(control_cube, 'time')
    iris.coord_categorisation.add_year(hist_cube, 'time')
    
    index = 0
    for bounds in control_cube.coord('time').bounds:
        lower, upper = bounds
        if lower <= branch_time < upper:
            break
        else:
            index = index + 1

    branch_year = control_cube.coord('year').points[index]
    hist_start_year = hist_cube.coord('year').points[0]

    time_constraint = get_time_constraint([str(81).zfill(4)+'-01-01', str(100).zfill(4)+'-12-31'])

    ## To do = account for the fact that the selected historical time period might not start at 1850.

        
def main(inargs):
    """Run the program."""
 
    hist_start_constraint = gio.get_time_constraint(inargs.start_time)
    hist_end_constraint = gio.get_time_constraint(inargs.end_time)

    hist_cube_list = iris.load(inargs.historical_file)
   
    control_cube_list = iris.load(inargs.control_file)
    control_start_constraint, control_end_constraint = get_control_time_constraints(control_cube_list[0], hist_cube_list[0])
    



if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com
 
"""

    description = 'Calculate the heat budget change between two time periods'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                
    parser.add_argument("historical_file", type=str,
                        help="historical experiment heat budget file from calc_heat_budget_timeseries.py")  
    parser.add_argument("control_file", type=str,
                        help="control experiment heat budget file from calc_heat_budget_timeseries.py")
    parser.add_argument("outfile", type=str, help="Output .csv file")  
    
    parser.add_argument("--start_time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=('1861-01-01', '1880-12-31'), help="Start time period")
    parser.add_argument("--end_time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=('1986-01-01', '2005-12-31'), help="End time period")

    args = parser.parse_args()             
    main(args)
