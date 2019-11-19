"""
Filename:     calc_vol_ts_dist.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate ocean volume distribution in T-S space  

"""

# Import general Python modules

import sys
import os
import re
import pdb
import argparse

import numpy
import pandas

import iris
import iris.coord_categorisation
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
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def create_df(tcube, scube, vcube, bcube):
    """Create DataFrame"""

    assert bcube.ndim == 2
    assert bcube.data.min() == 11
    assert bcube.data.max() == 17
 
    tcube = gio.temperature_unit_check(tcube, 'C')
    scube = gio.salinity_unit_check(scube)

    if tcube.ndim == 3:
        lats = uconv.broadcast_array(tcube.coord('latitude').points, [1, 2], tcube.shape)
        lons = uconv.broadcast_array(tcube.coord('longitude').points, [1, 2], tcube.shape)
        bdata = uconv.broadcast_array(bcube.data, [1, 2], tcube.shape)
        vdata = vcube.data
    elif tcube.ndim == 4:
        lats = uconv.broadcast_array(tcube.coord('latitude').points, [2, 3], tcube.shape)
        lons = uconv.broadcast_array(tcube.coord('longitude').points, [2, 3], tcube.shape)
        vdata = uconv.broadcast_array(vcube.data, [1, 3], tcube.shape)
        bdata = uconv.broadcast_array(bcube.data, [2, 3], tcube.shape)

    lats = numpy.ma.masked_array(lats, tcube.data.mask)
    lons = numpy.ma.masked_array(lons, tcube.data.mask)
    bdata.mask = tcube.data.mask

    sdata = scube.data.compressed()
    tdata = tcube.data.compressed()
    vdata = vdata.compressed()
    bdata = bdata.compressed()
    lat_data = lats.compressed()
    lon_data = lons.compressed()

    assert sdata.shape == tdata.shape
    assert sdata.shape == vdata.shape
    assert sdata.shape == bdata.shape
    assert sdata.shape == lat_data.shape
    assert sdata.shape == lon_data.shape

    df = pandas.DataFrame(index=range(tdata.shape[0]))
    df['temperature'] = tdata
    df['salinity'] = sdata
    df['volume'] = vdata
    df['basin'] = bdata
    df['latitude'] = lat_data
    df['longitude'] = lon_data

    return df, scube.units, tcube.units


def get_bounds_list(edges):
    """Create a bounds list from edge list"""

    bounds_list = []
    for i in range(len(edges) - 1):
        interval = [edges[i], edges[i+1]]
        bounds_list.append(interval)

    return numpy.array(bounds_list)


def construct_cube(vdist, scube, tcube, bcube, sunits, tunits,
                   x_values, y_values, z_values, x_edges, y_edges):
    """Create the iris cube for output"""

    x_bounds = get_bounds_list(x_edges)
    y_bounds = get_bounds_list(y_edges)

    scoord = iris.coords.DimCoord(x_values,
                                  standard_name=scube.standard_name,
                                  long_name=scube.long_name,
                                  var_name=scube.var_name,
                                  units=scube.units,
                                  bounds=x_bounds)

    tcoord = iris.coords.DimCoord(y_values,
                                  standard_name=tcube.standard_name,
                                  long_name=tcube.long_name,
                                  var_name=tcube.var_name,
                                  units=tcube.units,
                                  bounds=y_bounds)

    basin_coord = iris.coords.DimCoord(z_values,
                                       standard_name=bcube.standard_name,
                                       long_name=bcube.long_name,
                                       var_name=bcube.var_name,
                                       units=bcube.units,
                                       attributes={'flag_values': bcube.attributes['flag_values'],
                                                   'flag_meanings': bcube.attributes['flag_meanings']})

    dim_coords_list = [(scoord, 0), (tcoord, 1), (basin_coord, 2)]
    vdist_cube = iris.cube.Cube(vdist,
                                standard_name='ocean_volume',
                                long_name='Ocean Grid-Cell Volume',
                                var_name='volcello',
                                units='m3',
                                attributes=tcube.attributes,
                                dim_coords_and_dims=dim_coords_list) 

    return vdist_cube


def main(inargs):
    """Run the program."""

    vcube = iris.load_cube(inargs.volume_file)
    bcube = iris.load_cube(inargs.basin_file)

    smin, smax = inargs.salinity_bounds
    tmin, tmax = inargs.temperature_bounds
    sstep, tstep = inargs.bin_size
    x_edges = numpy.arange(smin, smax + sstep, sstep)
    y_edges = numpy.arange(tmin, tmax + tstep, tstep)
    x_values = (x_edges[1:] + x_edges[:-1]) / 2
    y_values = (y_edges[1:] + y_edges[:-1]) / 2
    z_edges = numpy.array([10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5])
    z_values = numpy.array([11, 12, 13, 14, 15, 16, 17])

    tcube = iris.load_cube(inargs.temperature_file, 'sea_water_potential_temperature')
    scube = iris.load_cube(inargs.salinity_file, 'sea_water_salinity')
   
    df, sunits, tunits = create_df(tcube, scube, vcube, bcube)

    data = numpy.array([df['salinity'].values, df['temperature'].values, df['basin'].values]).T
    vdist, edges = numpy.histogramdd(data, weights=df['volume'].values, bins=[x_edges, y_edges, z_edges])
    vdist_cube = construct_cube(vdist, scube, tcube, bcube, sunits, tunits, 
                                x_values, y_values, z_values, x_edges, y_edges)

    # Metadata
    metadata_dict = {inargs.basin_file: bcube.attributes['history'],
                     inargs.volume_file: vcube.attributes['history'],
                     inargs.temperature_file: tcube.attributes['history'],
                     inargs.salinity_file: scube.attributes['history']}
    log = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    vdist_cube.attributes['history'] = log

    iris.save(vdist_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Calculate ocean volume distribution in T-S space'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("temperature_file", type=str, help="Temperature file") 
    parser.add_argument("salinity_file", type=str, help="Salinity file")
    parser.add_argument("volume_file", type=str, help="Volume file")
    parser.add_argument("basin_file", type=str, help="Basin file")
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--salinity_bounds", type=float, nargs=2, default=(25, 40),
                        help='bounds for the salinity (X) axis')
    parser.add_argument("--temperature_bounds", type=float, nargs=2, default=(-4, 40),
                        help='bounds for the temperature (Y) axis')
    parser.add_argument("--bin_size", type=float, nargs=2, default=(0.05, 0.25),
                        help='bin size: salinity step, temperature step')

    args = parser.parse_args()             

    main(args)
