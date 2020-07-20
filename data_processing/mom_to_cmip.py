"""
Filename:     mom_to_cmip.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  convert MOM data files to be like ACCESS-CM2 CMIP6 files

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy as np
import xarray as xr
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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def xr_to_cube(dset, ref_cube, inargs):
    """Create iris cube from xarray dataset"""

    assert dset[inargs.mom_var].units[0] == 'W'
    new_units = 'W m-2'

    mom_ndim = dset[inargs.mom_var].ndim
    assert mom_ndim == ref_cube.ndim, \
        "MOM and reference data do not have same number of dimensions"

    assert np.allclose(ref_cube.coord('latitude').points, dset['geolat_t'].values)
    mom_lons = np.where(dset['geolon_t'].values < 0.0, dset['geolon_t'].values + 360, dset['geolon_t'].values)
    assert np.allclose(ref_cube.coord('longitude').points, mom_lons)

    time_coord = iris.coords.DimCoord(dset['time'].values,
                                      standard_name='time',
                                      long_name='time',
                                      var_name='time',
                                      units=cf_units.Unit(dset['time'].units,
                                                          calendar=dset['time'].calendar.lower()))
    dim_coord_list = [(time_coord, 0)]
    for index, coord in enumerate(ref_cube.dim_coords[1:]):
        dim_coord_list.append((coord, index + 1))

    new_data = dset[inargs.mom_var].to_masked_array()
        
    new_cube = iris.cube.Cube(new_data,
                              long_name=dset[inargs.mom_var].long_name,
                              var_name=dset[inargs.mom_var].name,
                              units=new_units,
                              attributes=ref_cube.attributes,
                              dim_coords_and_dims=dim_coord_list,
                              aux_coords_and_dims=[(ref_cube.aux_coords[0], (mom_ndim - 2, mom_ndim - 1)),
                                                   (ref_cube.aux_coords[1], (mom_ndim - 2, mom_ndim - 1))])
    if 'standard_name' in dset[inargs.mom_var].attrs:
        new_cube.standard_name = dset[inargs.mom_var].standard_name

    return new_cube


def main(inargs):
    """Run the program."""
    
    ref_cube = iris.load_cube(inargs.ref_file, inargs.ref_var)
    if inargs.single:
        cube_list = iris.cube.CubeList([])
        for mom_file in inargs.mom_files:
            print(mom_file)
            dset = xr.open_dataset(mom_file, decode_times=False)
            cube = xr_to_cube(dset, ref_cube, inargs)
            cube_list.append(cube)
        outcube = gio.combine_cubes(cube_list) 
    else:
        dset = xr.open_mfdataset(inargs.mom_files, decode_times=False, combine='by_coords')
        outcube = xr_to_cube(dset, ref_cube, inargs)
    
    outcube.attributes['history'] = cmdprov.new_log(git_repo=repo_dir)
    iris.save(outcube, inargs.outfile)
        

if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'convert MOM data files to be like ACCESS-CM2 CMIP6 files'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                     
    parser.add_argument("mom_files", type=str, nargs='*', help="Input MOM files")
    parser.add_argument("mom_var", type=str, help="variable name")
    parser.add_argument("ref_file", type=str, help="reference file")
    parser.add_argument("ref_var", type=str, help="reference variable")
    parser.add_argument("outfile", type=str, help="output file")

    parser.add_argument("--single", action="store_true", default=False,
                        help="Process each mom_file separately before merging")

    args = parser.parse_args()
    main(args)
