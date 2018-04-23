"""
Filename:     calc_ohc.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate ocean heat content

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
import dask
dask.set_options(get=dask.get)
#import dask.multiprocessing
#dask.set_options(get=dask.multiprocessing.get)

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
    import spatial_weights
    import convenient_universal as uconv
    import timeseries
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def add_metadata(temperature_cube, temperature_atts, ohc_cube, metadata_dict, inargs):
    """Add metadata to the output cube."""

    # Variable attributes
    standard_name = 'ocean_heat_content'
    long_name = 'ocean heat content'
    var_name = 'ohc'
    units = 'J'

    if not (inargs.area_file or inargs.volume_file):
        units = units + ' m-2'
    iris.std_names.STD_NAMES[standard_name] = {'canonical_units': units}

    ohc_cube.standard_name = standard_name
    ohc_cube.long_name = long_name
    ohc_cube.var_name = var_name
    ohc_cube.units = units

    # File attributes
    ohc_cube.attributes = temperature_atts
    ohc_cube.attributes['history'] = gio.write_metadata(file_info=metadata_dict)
    ohc_cube.attributes['depth_bounds'] = get_depth_text(temperature_cube, inargs.min_depth, inargs.max_depth)

    return ohc_cube


def calc_ohc_vertical_integral(temperature_cube, volume_data, density, specific_heat, coord_names, chunk=False):
    """Calculate the ohc vertical integral.

    Chunking is an option to avoid memory errors.

    """

    temperature_cube.data = temperature_cube.data * volume_data

    if chunk:
        integral = uconv.chunked_collapse_by_time(temperature_cube, 'depth', iris.analysis.SUM)
    else:
        integral = temperature_cube.collapsed('depth', iris.analysis.SUM)

    ohc = (integral * density * specific_heat) 
    ohc.remove_coord('depth')
    
    return ohc


def read_spatial_file(spatial_file):
    """Read optional areacello or volcello file."""

    if spatial_file:
        cube = iris.load_cube(spatial_file)
    else:
        cube = None

    return cube      


def get_depth_text(temperature_cube, min_depth, max_depth):
    """Set the attributes for the output cube."""

    lev_coord = temperature_cube.coord('depth')
    bounds_info = gio.vertical_bounds_text(lev_coord.points, min_depth, max_depth)
    depth_text = 'OHC integrated over %s' %(bounds_info)

    return depth_text


def get_outfile_name(temperature_file, annual=False, execute=True):
    """Define the OHC file name using the temperature file name as a template."""

    ohc_file = temperature_file.replace('thetao', 'ohc')
    ohc_file = ohc_file.replace('ua6', 'r87/dbi599')
    ohc_file = ohc_file.replace('_legacy', '')

    if annual:
        ohc_file = ohc_file.replace('/mon/', '/yr/')
        ohc_file = ohc_file.replace('Omon', 'Oyr')

    ohc_file_components = ohc_file.split('/')
    ohc_file_components.pop(-1)
    ohc_dir = "/".join(ohc_file_components)
    mkdir_command = 'mkdir -p ' + ohc_dir

    print(mkdir_command)
    if execute:
        os.system(mkdir_command)

    return ohc_file


def get_volume(volume_file, area_file, temperature_cube, metadata_dict):
    """Get the volume array"""

    if volume_file:
        volume_cube = read_spatial_file(volume_file)
        metadata_dict[volume_file] = volume_cube.attributes['history']
        volume_data = spatial_weights.volume_array(temperature_cube, volume_cube=volume_cube) 
    else:
        area_cube = read_spatial_file(area_file)
        if area_cube:
            metadata_dict[area_file] = area_cube.attributes['history']
        volume_data = spatial_weights.volume_array(temperature_cube, area_cube=area_cube) 
        
    return volume_data, metadata_dict


def main(inargs):
    """Run the program."""

    level_subset = gio.iris_vertical_constraint(inargs.min_depth, inargs.max_depth)
    for temperature_file in inargs.temperature_files:
        temperature_cube = iris.load_cube(temperature_file, inargs.temperature_var & level_subset)
        temperature_cube = gio.check_time_units(temperature_cube)
        metadata_dict = {temperature_file: temperature_cube.attributes['history']}
        temperature_atts = temperature_cube.attributes

        if inargs.annual:
            temperature_cube = timeseries.convert_to_annual(temperature_cube, chunk=inargs.chunk)

        coord_names = [coord.name() for coord in temperature_cube.dim_coords]
        assert coord_names[0] == 'time'
        assert coord_names[1] == 'depth'

        volume_data, metadata_dict = get_volume(inargs.volume_file, inargs.area_file,
                                                temperature_cube, metadata_dict)

        ohc_cube = calc_ohc_vertical_integral(temperature_cube, volume_data, inargs.density, inargs.specific_heat,
                                              coord_names, chunk=inargs.chunk)
        ohc_cube = add_metadata(temperature_cube, temperature_atts, ohc_cube, metadata_dict, inargs)
        ohc_file = get_outfile_name(temperature_file, annual=inargs.annual)    

        iris.save(ohc_cube, ohc_file)
        print(ohc_file)


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
notes:
    The default density and specific heat of seawater are from:
    Hobbs et al (2016). Journal of Climate, 29(5), 1639-1653. doi:10.1175/JCLI-D-15-0477.1

"""

    description='Calculate ocean heat content'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("temperature_files", type=str, nargs='*', help="Input temperature data files")
    parser.add_argument("temperature_var", type=str, help="Input temperature variable name (the standard_name)")

    parser.add_argument("--area_file", type=str, default=None,
                        help="Cell area file (used to make output units W instead of W m-2)")
    parser.add_argument("--volume_file", type=str, default=None,
                        help="Cell volume file (used to make output units W instead of W m-2)")

    parser.add_argument("--min_depth", type=float, default=None,
                        help="Only include data below this vertical level")
    parser.add_argument("--max_depth", type=float, default=None,
                        help="Only include data above this vertical level")

    parser.add_argument("--annual", action="store_true", default=False,
                        help="Convert data to annual timescale [default: False]")

    parser.add_argument("--density", type=float, default=1023,
                        help="Density of seawater (in kg.m-3). Default of 1023 kg.m-3 from Hobbs2016.")
    parser.add_argument("--specific_heat", type=float, default=4000,
                        help="Specific heat of seawater (in J / kg.K). Default of 4000 J/kg.K from Hobbs2016")

    parser.add_argument("--chunk", action="store_true", default=False,
                        help="Split input files on time axis to avoid memory errors [default: False]")

    args = parser.parse_args()             
    main(args)
