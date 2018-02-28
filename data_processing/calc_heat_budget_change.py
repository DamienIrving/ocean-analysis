"""
Filename:     calc_heat_budget_change.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the heat budget change between two time periods

"""

# Import general Python modules

import sys, os, pdb
import collections
import argparse
import numpy
import pandas
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


def get_control_time_constraint(control_cube, hist_cube, time_bounds):
    """Define the time constraints for the control data."""

    iris.coord_categorisation.add_year(control_cube, 'time')
    iris.coord_categorisation.add_year(hist_cube, 'time')

    branch_time = hist_cube.attributes['branch_time']
    
    index = 0
    for bounds in control_cube.coord('time').bounds:
        lower, upper = bounds
        if lower <= branch_time < upper:
            break
        else:
            index = index + 1

    branch_year = control_cube.coord('year').points[index]
    hist_start_year = hist_cube.coord('year').points[0]
    start_gap = int(time_bounds[0].split('-')[0]) - hist_start_year
    end_gap = int(time_bounds[1].split('-')[0]) - hist_start_year

    control_start_year = branch_year + start_gap
    control_end_year = branch_year + end_gap

    control_start_date = str(control_start_year).zfill(4)+'-01-01'
    control_end_date = str(control_end_year).zfill(4)+'-01-01'

    time_constraint = gio.get_time_constraint([control_start_date, control_end_date])

    control_cube.remove_coord('year')
    hist_cube.remove_coord('year')

    return time_constraint


def get_attributes(cube):
    """Get the model, experiment and rip information."""

    model = cube.attributes['model_id']
    experiment = cube.attributes['experiment_id']
 
    realization = cube.attributes['realization']
    initialization = cube.attributes['initialization_method']
    physics = cube.attributes['physics_version']
    
    rip = 'r%si%sp%s' %(realization, initialization, physics)

    return model, experiment, rip


def generate_results(data_dict, cube_list, time_constraint, time_bounds):
    """Generate results."""

    model, experiment, rip = get_attributes(cube_list[0])
    period = '%s-%s' %(time_bounds[0].split('-')[0], time_bounds[1].split('-')[0])

    data_dict['model'].append(model)
    data_dict['experiment'].append(experiment)
    data_dict['rip'].append(rip)
    data_dict['period'].append(period)

    for cube in cube_list:
        cube = cube.copy()
        temporal_subset = cube.extract(time_constraint)
        clim = temporal_subset.collapsed('time', iris.analysis.MEAN)
        data_dict[clim.var_name].append(float(clim.data))

    return data_dict

        
def main(inargs):
    """Run the program."""
 
    hist_cube_list = iris.load(inargs.historical_file)
    control_cube_list = iris.load(inargs.control_file)

    hist_start_constraint = gio.get_time_constraint(inargs.start_time)
    hist_end_constraint = gio.get_time_constraint(inargs.end_time)
    start_year = inargs.start_time[0].split('-')[0]
    control_start_constraint = get_control_time_constraint(control_cube_list[0], hist_cube_list[0], inargs.start_time)
    control_end_constraint = get_control_time_constraint(control_cube_list[0], hist_cube_list[0], inargs.end_time)
    
    column_headers = ['model', 'experiment', 'rip', 'period',
                      'hfds-globe-sum', 'hfds-nh-sum', 'hfds-sh-sum', 'hfds-nhext-sum', 'hfds-tropics-sum', 'hfds-shext-sum',
                      'ohc-globe-sum', 'ohc-nh-sum', 'ohc-sh-sum', 'ohc-nhext-sum', 'ohc-tropics-sum', 'ohc-shext-sum']

    data_dict = collections.OrderedDict()
    for column in column_headers:
        data_dict[column] = []

    data_dict = generate_results(data_dict, hist_cube_list, hist_start_constraint, inargs.start_time)
    data_dict = generate_results(data_dict, hist_cube_list, hist_end_constraint, inargs.end_time)

    data_dict = generate_results(data_dict, control_cube_list, control_start_constraint, inargs.start_time)
    data_dict = generate_results(data_dict, control_cube_list, control_end_constraint, inargs.end_time)

    data_df = pandas.DataFrame.from_dict(data_dict)
    data_df.to_csv(inargs.outfile)

    metadata_dict = {inargs.historical_file: hist_cube_list[0].attributes['history'],
                     inargs.control_file: control_cube_list[0].attributes['history']}
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


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
