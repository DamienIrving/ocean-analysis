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

ocean_names = {0: 'land', 1: 'southern_ocean', 2: 'atlantic', 
               3: 'pacific', 4: 'arctic', 5: 'indian', 
               6: 'mediterranean', 7: 'black_sea', 8: 'hudson_bay',
               9: 'baltic_sea', 10: 'red_sea'}

def get_ocean_name(ocean_num):
    return ocean_names[ocean_num]


def select_basin(df, basin_name):
    """Select basin"""

    if not basin_name == 'globe':
        df['basin'] = df['basin'].apply(get_ocean_name)
        basin_components = basin_name.split('_')
        if len(basin_components) == 1:
            ocean = basin_components[0]
            hemisphere = None
        else:
            hemisphere, ocean = basin_components

        df = df[(df.basin == ocean)]
        if hemisphere == 'north':
            df = df[(df.latitude > 0)]
        elif hemisphere == 'south':
            df = df[(df.latitude < 0)]

    return df


def create_df(tcube, scube, vcube, bcube, basin):
    """Create DataFrame"""

    tcube = gio.temperature_unit_check(tcube, 'C')
    scube = gio.salinity_unit_check(scube)

    if tcube.ndim == 3:
        lats = uconv.broadcast_array(tcube.coord('latitude').points, [1, 2], tcube.shape)
        lons = uconv.broadcast_array(tcube.coord('longitude').points, [1, 2], tcube.shape)
        levs = uconv.broadcast_array(tcube.coord('depth').points, 0, tcube.shape)
        vdata = vcube.data
        bdata = bcube.data
    elif tcube.ndim == 4:
        lats = uconv.broadcast_array(tcube.coord('latitude').points, [2, 3], tcube.shape)
        lons = uconv.broadcast_array(tcube.coord('longitude').points, [2, 3], tcube.shape)
        levs = uconv.broadcast_array(tcube.coord('depth').points, 1, tcube.shape)
        vdata = uconv.broadcast_array(vcube.data, [1, 3], tcube.shape)
        bdata = uconv.broadcast_array(bcube.data, [1, 3], tcube.shape)

    sdata = scube.data.flatten()
    tdata = tcube.data.flatten()
    vdata = vdata.flatten()
    bdata = bdata.flatten()
    lat_data = lats.flatten()
    lon_data = lons.flatten()
    depth_data = levs.flatten()

    df = pandas.DataFrame(index=range(tdata.shape[0]))
    df['temperature'] = tdata.filled(fill_value=5000)
    df['salinity'] = sdata.filled(fill_value=5000)
    df['volume'] = vdata.filled(fill_value=5000)
    df['basin'] = bdata.filled(fill_value=5000)
    df['latitude'] = lat_data
    df['longitude'] = lon_data
    df['depth'] = depth_data

    df = df[df.temperature != 5000]
    df = df[df.temperature != -273.15]

    if basin:
        df = select_basin(df, basin)

    return df


def fix_units(hist, data_shape, sstep, tstep):
    """Adjust units so they represent a single timestep and unit bin size"""

    if len(data_shape) == 4:
        hist = hist / data_shape[0]

    hist = hist / sstep
    hist = hist / tstep

    return hist


def get_bounds_list(edges):
    """Create a bounds list from edge list"""

    bounds_list = []
    for i in range(len(edges) - 1):
        interval = [edges[i], edges[i+1]]
        bounds_list.append(interval)

    return numpy.array(bounds_list)


def construct_cube(vdist, scube, tcube, x_values, y_values, x_edges, y_edges):
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

    dim_coords_list = [(scoord, 0), (tcoord, 1)]
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
    x_edges = numpy.arange(smin, smax, sstep)
    y_edges = numpy.arange(tmin, tmax, tstep)
    x_values = (x_edges[1:] + x_edges[:-1]) / 2
    y_values = (y_edges[1:] + y_edges[:-1]) / 2
    extents = [x_values[0], x_values[-1], y_values[0], y_values[-1]]

    tcube = iris.load_cube(inargs.temperature_file, 'sea_water_potential_temperature')
    scube = iris.load_cube(inargs.salinity_file, 'sea_water_salinity')
   
    df = create_df(tcube, scube, vcube, bcube, basin=inargs.basin)

    vdist, xedges, yedges = numpy.histogram2d(df['salinity'].values, df['temperature'].values,
                                              weights=df['volume'].values, bins=[x_edges, y_edges])
    vdist = fix_units(vdist, tcube.shape, sstep, tstep)
    vdist_cube = construct_cube(vdist, scube, tcube, x_values, y_values, x_edges, y_edges)

    # Metadata
    metadata_dict = {inargs.basin_file: bcube.attributes['history'],
                     inargs.volume_file: vcube.attributes['history'],
                     inargs.temperature_file: tcube.attributes['history'],
                     inargs.salinity_file: scube.attributes['history']}
    log = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    vdist_cube.attributes['history'] = log
    vdist_cube.attributes['ocean_basin'] = inargs.basin

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

    parser.add_argument("--basin", type=str, default='globe',
                        choices=('globe', 'indian', 'north_atlantic', 'south_atlantic', 'north_pacific', 'south_pacific'),
                        help='ocean basin to plot')

    parser.add_argument("--salinity_bounds", type=float, nargs=2, default=(32, 37.5),
                        help='bounds for the salinity (X) axis')
    parser.add_argument("--temperature_bounds", type=float, nargs=2, default=(-2, 30),
                        help='bounds for the temperature (Y) axis')
    parser.add_argument("--bin_size", type=float, nargs=2, default=(0.05, 0.25),
                        help='bin size: salinity step, temperature step')

    args = parser.parse_args()             

    main(args)
