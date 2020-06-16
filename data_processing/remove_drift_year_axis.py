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
import cmdline_provenance as cmdprov

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

def get_branch_year(data_cube, control_time_units):
    """Get the year of the branching in control run."""

    if not control_time_units:
        control_time_units = gio.fix_time_descriptor(data_cube.attributes['parent_time_units'])
    else:
        control_time_units = control_time_units.replace("_", " ")
    branch_time = data_cube.attributes['branch_time_in_parent']
    branch_datetime = cf_units.num2date(branch_time, control_time_units, cf_units.CALENDAR_STANDARD)
    branch_year = branch_datetime.year
    print(f"Branch year: {branch_year}")

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
    if not inargs.branch_year == None:
        branch_year = inargs.branch_year
    else:
        branch_year = get_branch_year(data_cube, inargs.control_time_units)
    time_values = numpy.arange(branch_year, branch_year + data_cube.shape[0]) 
    drift_signal, start_polynomial = remove_drift.apply_polynomial(time_values, coefficient_a_cube.data,
                                                                   coefficient_b_cube.data, coefficient_c_cube.data,
                                                                   coefficient_d_cube.data, poly_start=None)

    new_cube = data_cube - drift_signal
    #remove_drift.check_data(new_cube, data_cube, inargs.data_file)
    new_cube.metadata = data_cube.metadata
            
    metadata_dict = {inargs.data_file: data_cube.attributes['history'], 
                     inargs.coefficient_file: coefficient_a_cube.attributes['history']}
    new_cube.attributes['history'] = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
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
    parser.add_argument("coefficient_file", type=str, help="Drift coefficient file")
    parser.add_argument("outfile", type=str, help="outfile")

    parser.add_argument("--branch_year", type=int, default=None, help="override metadata")
    parser.add_argument("--control_time_units", type=str, default=None, help="override metadata (e.g. days_since_1850-01-01)")

    args = parser.parse_args()            

    main(args)
