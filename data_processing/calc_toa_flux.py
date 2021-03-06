"""
Filename:     calc_toa_flux.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the net TOA incoming flux

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
from iris.experimental.equalise_cubes import equalise_attributes
import dask
dask.set_options(get=dask.get)

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
    import grids
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def add_metadata(rndt_cube, atts):
    """Add metadata to the output cube."""

    standard_name = 'toa_incoming_net_flux'
    long_name = 'TOA Incoming Net Radiation'
    var_name = 'rndt'
    units = 'W m-2'

    iris.std_names.STD_NAMES[standard_name] = {'canonical_units': units}

    rndt_cube.standard_name = standard_name
    rndt_cube.long_name = long_name
    rndt_cube.var_name = var_name
    rndt_cube.units = units

    rndt_cube.attributes = atts
    rndt_cube.attributes['history'] = gio.write_metadata()

    return rndt_cube


def get_data(filename, var, time_constraint):
    """Read data."""
    
    cube = iris.load_cube(filename, gio.check_iris_var(var) & time_constraint)
    cube = gio.check_time_units(cube)
    cube = iris.util.squeeze(cube)

    return cube


def calc_rndt(cube_dict):
    """Calculate the TOA incoming net radiation."""

    assert cube_dict['rsdt'].data.min() >= 0.0
    assert cube_dict['rsut'].data.min() >= 0.0  
    assert cube_dict['rlut'].data.min() >= 0.0

    cube_dict['rndt'] = cube_dict['rsdt'].copy()
    cube_dict['rndt'].data = cube_dict['rsdt'].data - cube_dict['rsut'].data - cube_dict['rlut'].data  

    return cube_dict


def equalise_time_axes(cube_dict):
    """Make all the time axes the same."""

    iris.util.unify_time_units(cube_dict.values())
    reference_cube = list(cube_dict.values())[0]
    new_data_dict = {}
    for key, cube in cube_dict.items():
        assert len(cube.coord('time').points) == len(reference_cube.coord('time').points)
        cube.coord('time').points = reference_cube.coord('time').points
        cube.coord('time').bounds = reference_cube.coord('time').bounds
        new_data_dict[key] = cube
    
    return new_data_dict
    

def check_inputs(inargs):
    """Check for the correct number of input files"""

    nfiles = len(inargs.rsdt_files)
    for files in [inargs.rsut_files, inargs.rlut_files]:
        assert len(files) == nfiles 

    return nfiles
       

def get_outfile_name(rsdt_file):
    """Define the output file name using the rsdt file name as a template."""

    rsdt_components = rsdt_file.split('/')

    rsdt_filename = rsdt_components[-1]  
    rsdt_components.pop(-1)
    rsdt_dir = "/".join(rsdt_components)

    rndt_filename = rsdt_filename.replace('rsdt', 'rndt')
    rndt_dir = rsdt_dir.replace('rsdt', 'rndt')
    rndt_dir = rndt_dir.replace('ua6', 'r87/dbi599')

    mkdir_command = 'mkdir -p ' + rndt_dir

    print(mkdir_command)
    os.system(mkdir_command)

    return rndt_dir + '/' + rndt_filename


def main(inargs):
    """Run the program."""

    time_constraint = gio.get_time_constraint(inargs.time)
    nfiles = check_inputs(inargs)
    for fnum in range(nfiles):
        cube_dict = {}
        cube_dict['rsdt'] = get_data(inargs.rsdt_files[fnum], 'toa_incoming_shortwave_flux', time_constraint)
        cube_dict['rsut'] = get_data(inargs.rsut_files[fnum], 'toa_outgoing_shortwave_flux', time_constraint)
        cube_dict['rlut'] = get_data(inargs.rlut_files[fnum], 'toa_outgoing_longwave_flux', time_constraint)
                         
        cube_dict = equalise_time_axes(cube_dict)
        cube_dict = calc_rndt(cube_dict)
        add_metadata(cube_dict['rndt'], cube_dict['rsdt'].attributes)   

        if inargs.outfile:
            rndt_file = inargs.outfile  
        else:
            assert inargs.time == None
            rndt_file = get_outfile_name(inargs.rsdt_files[fnum])
        print(rndt_file)
        iris.save(cube_dict['rndt'], rndt_file)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Calculate the net TOA incoming flux'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("--rsdt_files", type=str, nargs='*', required=True,
                        help="TOA incoming shortwave flux files")
    parser.add_argument("--rsut_files", type=str, nargs='*', required=True,
                        help="TOA outgoing shortwave flux files")
    parser.add_argument("--rlut_files", type=str, nargs='*', required=True,
                        help="TOA outgoing longwave flux files")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = entire]")
    parser.add_argument("--outfile", type=str, default=None,
                        help="Override automatic outfile name")

    args = parser.parse_args()             
    main(args)
