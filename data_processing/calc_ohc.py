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
    import spatial_weights
    import convenient_universal as uconv
    import timeseries
    import grids
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def add_metadata(temperature_cube, temperature_atts, ohc_cube, inargs):
    """Add metadata to the output cube."""

    # Variable attributes
    standard_name = 'ocean_heat_content'
    long_name = 'ocean heat content'
    var_name = 'ohc'
    units = 'J'

    iris.std_names.STD_NAMES[standard_name] = {'canonical_units': units}

    ohc_cube.standard_name = standard_name
    ohc_cube.long_name = long_name
    ohc_cube.var_name = var_name
    ohc_cube.units = units

    # File attributes
    ohc_cube.attributes = temperature_atts
    ohc_cube.attributes['depth_bounds'] = get_depth_text(temperature_cube, inargs.min_depth, inargs.max_depth)

    return ohc_cube


def ohc(temperature_cube, volume_data, density, specific_heat, coord_names, vertical_integral=False, chunk=False):
    """Calculate the ocean heat content.

    Chunking is an option to avoid memory errors.

    """

    temperature_cube.data = temperature_cube.data * volume_data

    if vertical_integral:
        if chunk:
            tv = uconv.chunked_collapse_by_time(temperature_cube, 'depth', iris.analysis.SUM)
        else:
            tv = temperature_cube.collapsed('depth', iris.analysis.SUM)
        tv.remove_coord('depth')
    else:
        tv = temperature_cube

    ohc = (tv * density * specific_heat) 
    
    return ohc


def read_area_file(area_file):
    """Read optional areacello file."""

    if area_file:
        cube = iris.load_cube(area_file)
    else:
        cube = None

    return cube      


def get_depth_text(temperature_cube, min_depth, max_depth):
    """Set the attributes for the output cube."""

    lev_coord = temperature_cube.coord('depth')
    bounds_info = gio.vertical_bounds_text(lev_coord.points, min_depth, max_depth)
    depth_text = 'OHC integrated over %s' %(bounds_info)

    return depth_text


def get_volume(volume_file, temperature_cube, level_constraint, metadata_dict):
    """Get the volume array"""

    volume_cube = iris.load_cube(volume_file, 'ocean_volume' & level_constraint)
    metadata_dict[volume_file] = volume_cube.attributes['history']
    volume_data = spatial_weights.volume_array(temperature_cube, volume_cube=volume_cube) 
        
    return volume_data, metadata_dict


def main(inargs):
    """Run the program."""

    temperature_cube, history = gio.combine_files(inargs.temperature_files, inargs.var)

    temperature_atts = temperature_cube.attributes
    metadata_dict = {inargs.temperature_files[0]: history[0]}

    level_subset = gio.iris_vertical_constraint(inargs.min_depth, inargs.max_depth)
    temperature_cube = temperature_cube.extract(level_subset)

    if inargs.annual:
        temperature_cube = timeseries.convert_to_annual(temperature_cube, chunk=inargs.chunk)

    if inargs.regrid:
        area_cube = read_area_file(inargs.regrid)
        temperature_cube, coord_names, regrid_status = grids.curvilinear_to_rectilinear(temperature_cube, weights=area_cube.data)
        volume_data = spatial_weights.volume_array(temperature_cube)
        grid = 'y72x144'
    else:
        assert inargs.volume_file, "Must provide volume file if not regridding data"
        volume_data, metadata_dict = get_volume(inargs.volume_file, temperature_cube, level_subset, metadata_dict)
        coord_names = [coord.name() for coord in temperature_cube.dim_coords]
        grid = None

    ohc_cube = ohc(temperature_cube, volume_data, inargs.density, inargs.specific_heat,
                   coord_names, vertical_integral=inargs.vertical_integral, chunk=inargs.chunk)

    ohc_cube = add_metadata(temperature_cube, temperature_atts, ohc_cube, inargs)
    log = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir) 
    ohc_cube.attributes['history'] = log

    iris.save(ohc_cube, inargs.outfile)


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
    parser.add_argument("var", type=str, help="Input temperature variable name (the standard_name)")
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--regrid", type=str, default=None,
                        help="Regrid data using this area weighting file.")
    parser.add_argument("--volume_file", type=str, default=None,
                        help="Cell volume file (required if not regridding)")

    parser.add_argument("--min_depth", type=float, default=None,
                        help="Only include data below this vertical level")
    parser.add_argument("--max_depth", type=float, default=None,
                        help="Only include data above this vertical level")

    parser.add_argument("--annual", action="store_true", default=False,
                        help="Convert data to annual timescale [default: False]")
    parser.add_argument("--vertical_integral", action="store_true", default=False,
                        help="Calculate the vertically integrated OHC [default: False]")
    
    parser.add_argument("--density", type=float, default=1023,
                        help="Density of seawater (in kg.m-3). Default of 1023 kg.m-3 from Hobbs2016.")
    parser.add_argument("--specific_heat", type=float, default=4000,
                        help="Specific heat of seawater (in J / kg.K). Default of 4000 J/kg.K from Hobbs2016")

    parser.add_argument("--chunk", action="store_true", default=False,
                        help="Split input files on time axis to avoid memory errors [default: False]")

    args = parser.parse_args()             
    main(args)
