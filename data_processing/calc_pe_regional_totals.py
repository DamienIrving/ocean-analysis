"""
Filename:     calc_pe_regional_totals.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate precipitation minus evaporation regional totals
"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy as np
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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def get_boundary_indexes(xintercept_indexes, lat_coord):
    """Find boundary indexes in x-intercepts"""
    
    sh_south_bound = None
    sh_north_bound = None
    for index in xintercept_indexes:
        lat = lat_coord[index]
        if (lat < -25) and (lat > -50) and not sh_south_bound:
            sh_south_bound = index
        if (lat < -7) and (lat > -25) and not sh_north_bound:
            sh_north_bound = index
        if sh_south_bound and sh_north_bound:
            break

    nh_south_bound = None
    nh_north_bound = None
    for index in reversed(xintercept_indexes):
        lat = lat_coord[index]
        if (lat > 25) and (lat < 50) and not nh_north_bound:
            nh_north_bound = index
        if (lat > 7) and (lat < 25) and not nh_south_bound:
            nh_south_bound = index
        if nh_south_bound and nh_north_bound:
            break

    assert (lat_coord[sh_south_bound] < -25) and (lat_coord[sh_south_bound] > -50)
    assert (lat_coord[sh_north_bound] < -7) and (lat_coord[sh_north_bound] > -25)
    assert (lat_coord[nh_south_bound] > 7) and (lat_coord[nh_south_bound] < 25)
    assert (lat_coord[nh_north_bound] > 25) and (lat_coord[nh_north_bound] < 50)
    
    print(lat_coord[sh_south_bound], lat_coord[sh_north_bound],
          lat_coord[nh_south_bound], lat_coord[nh_north_bound])

    return sh_south_bound, sh_north_bound, nh_south_bound, nh_north_bound


def get_regional_totals(pe_data, lat_coord):
    """Calculate the P-E zonally integrated regional totals.
    
    pe_data (numpy.array) - one dimensional (latitude) data array
    
    """

    pair_products = pe_data[0:-1] * pe_data[1:]
    xintercept_indexes = np.where(pair_products < 0)[0] + 1
    boundary_indexes = get_boundary_indexes(xintercept_indexes, lat_coord)
    
    sh_precip = pe_data[0:boundary_indexes[0]].sum()
    sh_evap = pe_data[boundary_indexes[0]:boundary_indexes[1]].sum()
    tropical_precip = pe_data[boundary_indexes[1]:boundary_indexes[2]].sum()
    nh_evap = pe_data[boundary_indexes[2]:boundary_indexes[3]].sum()
    nh_precip = pe_data[boundary_indexes[3]:].sum()

    return sh_precip, sh_evap, tropical_precip, nh_evap, nh_precip


def create_region_coord():
    """Create a dimension for the P-E regions"""
    
    flag_values = '1 2 3 4 5'
    flag_meanings = 'SH precip, SH evap, tropical precip, NH evap, NH precip'
    region_coord = iris.coords.DimCoord(np.array([1, 2, 3, 4, 5]),
                                        standard_name='region',
                                        long_name='region',
                                        var_name='region',
                                        units=1,
                                        attributes={'flag_values': flag_values,
                                                    'flag_meanings': flag_meanings})
    return region_coord


def main(inargs):
    """Run the program."""

    pe_cube, pe_history = gio.combine_files(inargs.pe_files, 'precipitation minus evaporation flux')
    lat_coord = pe_cube.coord('latitude').points
    
    region_data = np.apply_along_axis(get_regional_totals, 1, pe_cube.data, lat_coord)
    if inargs.cumsum:
        region_data = np.cumsum(region_data, axis=0)    

    region_coord = create_region_coord()
    time_coord = pe_cube.coord('time')

    iris.std_names.STD_NAMES['precipitation_minus_evaporation_flux'] = {'canonical_units': pe_cube.units}
    dim_coords_list = [(time_coord, 0), (region_coord, 1)]
    out_cube = iris.cube.Cube(region_data,
                              standard_name='precipitation_minus_evaporation_flux',
                              long_name=pe_cube.long_name,
                              var_name=pe_cube.var_name,
                              units=pe_cube.units,
                              attributes=pe_cube.attributes,
                              dim_coords_and_dims=dim_coords_list) 

    out_cube.attributes['history'] = cmdprov.new_log(infile_history={inargs.pe_files[0]: pe_history[0]},
                                                     git_repo=repo_dir)
    iris.save(out_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
    
"""

    description='Calculate precipitation minus evaporation regional totals'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("pe_files", type=str, nargs='*', help="P-E zonal sum files")
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--cumsum", action="store_true", default=False,
                        help="Output the cumulative sum [default: False]")

    args = parser.parse_args()            
    main(args)
