"""
Filename:     calc_pe_spatial_totals.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate precipitation minus evaporation spatial totals
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
    import spatial_weights
    import timeseries
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

basin_names = ['atlantic', 'pacific', 'indian', 'arctic', 'marginal seas', 'land']
pe_names = ['SH precip', 'SH evap', 'tropical precip', 'NH evap', 'NH precip']

def create_basin_coord():
    """Create a dimension for the basins."""

    flag_values = "11.5 13.5 15 16 17 18"
    flag_meanings = "atlantic pacific indian arctic marginal_seas land"
    basin_coord = iris.coords.DimCoord(np.array([11.5, 13.5, 15, 16, 17, 18]),
                                       standard_name='region',
                                       long_name='Region Selection Index',
                                       var_name='basin',
                                       units=1,
                                       attributes={'flag_values': flag_values,
                                                   'flag_meanings': flag_meanings})

    return basin_coord
 

def create_pe_region_coord():
    """Create a dimension for the P-E regions"""
    
    flag_values = '1 2 3 4 5'
    flag_meanings = 'SH precip, SH evap, tropical precip, NH evap, NH precip'
    standard_name = 'precipitation_minus_evporation_region'
    iris.std_names.STD_NAMES[standard_name] = {'canonical_units': 1}
    pe_region_coord = iris.coords.DimCoord(np.array([1, 2, 3, 4, 5]),
                                           standard_name=standard_name,
                                           long_name='precipitation minus evaporation region',
                                           var_name='pereg',
                                           units=1,
                                           attributes={'flag_values': flag_values,
                                                       'flag_meanings': flag_meanings})
    return pe_region_coord


def get_regional_totals(var_data, pe_data, lats, basins):
    """Calculate the regional totals

    Basin definitions:
      north atlantic = 11
      south atlantic = 12
      north pacific = 13
      south pacific = 14
      indian = 15
      arctic = 16
      marginal seas = 17
      land = 18

    """

    basin_selection = {'atlantic': (basins >=11) & (basins <= 12),
                       'pacific': (basins >= 13) & (basins <= 14),
                       'indian': basins == 15,
                       'arctic': basins == 16,
                       'marginal seas': basins == 17,
                       'land': basins == 18}

    pe_selection = {'SH precip': (pe_data >= 0) & (lats < -20),
                    'SH evap': (pe_data < 0) & (lats < 0),
                    'tropical precip': (pe_data >= 0) & (lats <= 20) & (lats >= -20),
                    'NH evap': (pe_data < 0) & (lats >= 0),
                    'NH precip': (pe_data >= 0) & (lats > 20)}
    
    output = np.zeros([5, 6])
    for pe_num, pe_name in enumerate(pe_names):
        for basin_num, basin_name in enumerate(basin_names): 
            selection = pe_selection[pe_name] & basin_selection[basin_name]
            output[pe_num, basin_num] = var_data[selection].sum()

    assert np.allclose(var_data.sum(), output.sum())

    return output 


def read_data(infiles, var, annual=False):
    """Read the input data."""    

    cube, history = gio.combine_files(infiles, var)

    if annual:
        cube = timeseries.convert_to_annual(cube)

    cube = uconv.flux_to_magnitude(cube)
    cube = spatial_weights.multiply_by_area(cube)

    coord_names = [coord.name() for coord in cube.coords(dim_coords=True)]
    assert cube.ndim == 3
    lat_pos = coord_names.index('latitude')
    lats = uconv.broadcast_array(cube.coord('latitude').points, lat_pos - 1, cube.shape[1:])

    return cube, lats, history
    

def main(inargs):
    """Run the program."""

    pe_cube, pe_lats, pe_history = read_data(inargs.pe_files, 'precipitation minus evaporation flux', annual=inargs.annual)   
    basin_cube = iris.load_cube(inargs.basin_file, 'region')  

    if inargs.data_var == 'cell_area':   
        data_cube = iris.load_cube(inargs.data_files[0], 'cell_area')
        data_history = [data_cube.attributes['history']]
        assert data_cube.shape == pe_cube.shape[1:]
    elif inargs.data_files:
        data_cube, data_lats, data_history = read_data(inargs.data_files, inargs.data_var, annual=inargs.annual)
        assert data_cube.shape == pe_cube.shape
    else:
        data_cube = pe_cube.copy()
        data_var = 'precipitation minus evaporation flux'

    region_data = np.zeros([pe_cube.shape[0], 5, 6])
    tstep = 0
    ntimes = pe_cube.shape[0]
    for tstep in range(ntimes):
        var_data = data_cube.data if inargs.data_var == 'cell_area' else data_cube[tstep, ::].data
        region_data[tstep, :] = get_regional_totals(var_data, pe_cube[tstep, ::].data, pe_lats, basin_cube.data)
        
    if inargs.cumsum:
        region_data = np.cumsum(region_data, axis=0)    

    pe_region_coord = create_pe_region_coord()
    basin_coord = create_basin_coord()
    time_coord = pe_cube.coord('time')

    if inargs.data_var:
        standard_name = data_cube.standard_name
    else:
        iris.std_names.STD_NAMES['precipitation_minus_evaporation_flux'] = {'canonical_units': pe_cube.units}
        standard_name = 'precipitation_minus_evaporation_flux'
    atts = pe_cube.attributes if inargs.data_var == 'cell_area' else data_cube.attributes
    dim_coords_list = [(time_coord, 0), (pe_region_coord, 1), (basin_coord, 2)]
    out_cube = iris.cube.Cube(region_data,
                              standard_name=standard_name,
                              long_name=data_cube.long_name,
                              var_name=data_cube.var_name,
                              units=data_cube.units,
                              attributes=atts,
                              dim_coords_and_dims=dim_coords_list) 

    metadata = {inargs.pe_files[0]: pe_history[0],
                inargs.basin_file: basin_cube.attributes['history']}
    if inargs.data_files:
        metadata[inargs.data_files[0]] = data_history[0]
    out_cube.attributes['history'] = cmdprov.new_log(infile_history=metadata, git_repo=repo_dir)
    iris.save(out_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
    
"""

    description='Calculate precipitation minus evaporation zonal sum regional totals'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("pe_files", type=str, nargs='*', help="P-E files")
    parser.add_argument("basin_file", type=str, help="Basin file")
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--data_files", type=str, nargs='*', default=[],
                        help="Data files (if none, use pe_files)")
    parser.add_argument("--data_var", type=str, default=None,
                        help="Data variable")

    parser.add_argument("--annual", action="store_true", default=False,
                        help="Output annual mean [default=False]")
    parser.add_argument("--cumsum", action="store_true", default=False,
                        help="Output the cumulative sum [default: False]")

    args = parser.parse_args()            
    main(args)
