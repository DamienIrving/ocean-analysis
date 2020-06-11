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

def create_region_coord():
    """Create a dimension for the P-E regions"""
    
    flag_values = '1 2 3 4 5 6 7'
    flag_meanings = 'SH precip, SH evap, tropical precip, NH evap, NH precip, global precip, global evap'
    region_coord = iris.coords.DimCoord(np.array([1, 2, 3, 4, 5, 6, 7]),
                                        standard_name='region',
                                        long_name='region',
                                        var_name='region',
                                        units=1,
                                        attributes={'flag_values': flag_values,
                                                    'flag_meanings': flag_meanings})
    return region_coord


def get_regional_totals(pe_data, lats):
    """Calculate the regional totals"""

    sh_precip = pe_data[(pe_data > 0) & (lats < -20)].sum()
    sh_evap = pe_data[(pe_data < 0) & (lats < 0)].sum()
    tropical_precip = pe_data[(pe_data > 0) & (lats <= 20) & (lats >= -20)].sum()
    nh_evap = pe_data[(pe_data < 0) & (lats >= 0)].sum()
    nh_precip = pe_data[(pe_data > 0) & (lats > 20)].sum()
    global_precip = pe_data[pe_data >= 0].sum()
    global_evap = pe_data[pe_data < 0].sum()

    net_pe = sh_precip + sh_evap + tropical_precip + nh_evap + nh_precip
    assert np.allclose(pe_data.sum(), net_pe)

    output = numpy.array([sh_precip, sh_evap, tropical_precip, nh_evap,
                          nh_precip, global_precip, global_evap])

    return output 


def main(inargs):
    """Run the program."""

    pe_cube, pe_history = gio.combine_files(inargs.pe_files, 'precipitation minus evaporation flux')

    if inargs.annual:
        pe_cube = timeseries.convert_to_annual(pe_cube)
    pe_cube = uconv.flux_to_magnitude(pe_cube)
    pe_cube = spatial_weights.multiply_by_area(pe_cube)

    coord_names = [coord.name() for coord in pe_cube.coords(dim_coords=True)]
    assert pe_cube.ndim == 3
    lat_pos = coord_names.index('latitude')
    lats = uconv.broadcast_array(pe_cube.coord('latitude').points, lat_pos - 1, pe_cube.shape[1:])

    region_data = np.zeros([pe_cube.shape[0], 7])
    tstep = 0
    pdb.set_trace()
    for yx_slice in pe_cube.slices(coord_names[1:]):
        region_data[tstep, :] = get_regional_totals(yx_slice, lats)
        
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

    description='Calculate precipitation minus evaporation zonal sum regional totals'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("pe_files", type=str, nargs='*', help="P-E zonal sum files")
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--annual", action="store_true", default=False,
                        help="Output annual mean [default=False]")
    parser.add_argument("--cumsum", action="store_true", default=False,
                        help="Output the cumulative sum [default: False]")

    args = parser.parse_args()            
    main(args)
