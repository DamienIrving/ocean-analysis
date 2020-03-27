"""
Filename:     remove_drift_year_axis.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Remove drift from a data series with a year
              instead of traditional time axis.

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
import cf_units
import datetime

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
    import remove_drift
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def check_data(new_cube, orig_cube, infile):
    """Check that the new data is valid."""

    orig_max = orig_cube.data.max()
    orig_min = orig_cube.data.min()

    new_max = new_cube.data.max()
    new_min = new_cube.data.min()

    valid_max = orig_max * 1.2 if orig_max > 0.0 else orig_max * 0.8
    valid_min = orig_min * 1.2 if orig_min < 0.0 else orig_min * 0.8 

    assert new_max < valid_max, 'New data max is %f, %s' %(new_max, infile)
    assert new_min >= valid_min, 'New data min is %f, %s' %(new_min, infile)


def get_branch_year(data_cube)
    """Get the year of the branching in control run."""

    control_time_units = data_cube.attributes['parent_time_units']
    branch_time = data_cube.attributes['branch_time_in_parent']
    branch_datetime = cf_units.num2date(branch_time, control_time_units, cf_units.CALENDAR_STANDARD)
    pdb.set_trace()

    return branch_year


def main(inargs):
    """Run the program."""
    
    coefficient_a_cube = iris.load_cube(inargs.coefficient_file, 'coefficient a')
    coefficient_b_cube = iris.load_cube(inargs.coefficient_file, 'coefficient b')
    coefficient_c_cube = iris.load_cube(inargs.coefficient_file, 'coefficient c')
    coefficient_d_cube = iris.load_cube(inargs.coefficient_file, 'coefficient d')

    data_cube = iris.load_cube(inargs.data_file, gio.check_iris_var(inargs.var))
    coord_names = [coord.name() for coord in data_cube.coords(dim_coords=True)]
    assert coord_names[0] == 'year'
    
    branch_year = get_branch_year(data_cube)
    time_values = numpy.arange(branch_year, branch_year + data_cube.shape[0]) 

    drift_signal, start_polynomial = remove_drift.apply_polynomial(time_values, coefficient_a_cube.data,
                                                                   coefficient_b_cube.data, coefficient_c_cube.data,
                                                                   coefficient_d_cube.data, poly_start=None)

    new_cube = data_cube - drift_signal
    check_data(new_cube, data_cube, filename)
    new_cube.metadata = data_cube.metadata
            
    metadata_dict = {inargs.data_file: data_cube.attributes['history'], 
                     inargs.coefficient_file: coefficient_a_cube.attributes['history']}
    new_cube.attributes['history'] = gio.write_metadata(file_info=metadata_dict)
    iris.save(new_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
notes:
    Generate the polynomial coefficients first from calc_drift_coefficients.py
    
"""

    description='Remove drift from a data series'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("data_file", type=str, help="Input data file")
    parser.add_argument("var", type=str, help="Variable standard_name")
    parser.add_argument("timescale", type=str, choices=('monthly', 'annual'), help="Timescale of input data")
    parser.add_argument("outfile", type=str, help="outfile")

    args = parser.parse_args()            

    main(args)
