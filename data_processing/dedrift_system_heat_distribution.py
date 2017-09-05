"""
Filename:     dedrift_system_heat_distribution.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot the system heat distribution

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris


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


def select_segment(control_cube, ploynomial_data, branch_time, nyears):
    """Select the right time segment of the control run.

    Assumes annual timescale data (and that the branch times are expressed in months)

    The branch time represents the start of the year, while the first data time mid-year.
      Hence the adjustment by 182.5

    """

    assert control_cube.attributes['experiment_id'] == 'piControl'
    time_values = control_cube.coord('time').points - 182.5 
    start_index, error = uconv.find_nearest(time_values, branch_time, index=True)

    return polynomial_data[start_index : int(start_index + nyears)]


def remove_drift(experiment_cube, control_cube, var):
    """Remove drift from the experiment cube.
    
    polyfit returns [d, c, b, a] corresponding to y = a + bt + ct^2 + dt^3
    
    """
    
    pdb.set_trace()
    
    branch_time = experiment_cube.attributes['branch_time']

    time_axis = control_cube.coord('time').points
    
    coef_d, coef_c, coef_b, coef_a = numpy.polyfit(time_axis, control_cube.data, 3)
    control_polynomial = coef_a + (coef_b * time_axis) + (coef_c * time_axis**2) + (coef_d * time_axis**3)
    drift_data = control_polynomial - control_polynomial[0]
    drift_data = select_segment(drift_data, branch_time, experiment_cube.shape[0])

    new_experiment_cube = experiment_cube.copy()
    new_experiment_cube.data = new_experiment_cube.data - drift_data 
    
    return new_experiment_cube
    

def main(inargs):
    """Run the program."""

    experiment_cube = iris.load(inargs.experiment_file)
    control_cube = iris.load(inargs.control_file)

    for hemisphere in ['sh', 'nh']:
        hfbasin_var = 'Northward Ocean Heat Transport ' + hemisphere + ' ocean sum'
        ohc_var = 'ocean heat content ' + hemisphere + ' sum'
    
        new_hfbasin_cube = remove_drift(experiment_cube.extract(hfbasin_var),
                                        control_cube.extract(hfbasin_var))
        new_ohc_cube = remove_drift(experiment_cube.extract(ohc_var),
                                    control_cube.extract(ohc_var))
        
        
    

if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot the system heat distribution'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                     
    parser.add_argument("experiment_file", type=str, 
                        help="Input experiment file generated from calc_system_heat_distribution.py")
    parser.add_argument("control_file", type=str, 
                        help="Input control file generated from calc_system_heat_distribution.py")
                                           
    parser.add_argument("outfile", type=str, help="Output file")                                     

    args = parser.parse_args()             
    main(args)
