"""
Filename:     calc_water_mass_components.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate volume, volume*salinity and
              volume*temperature binned by temperature
              for each ocean basin  

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
from iris.experimental.equalise_cubes import equalise_attributes
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


def construct_cube(vdata, vsdata, vtdata, vcube, bcube, scube, tcube, sunits,
                   tunits, years, x_values, x_edges, y_values, log):
    """Create the iris cube for output"""

    year_coord = iris.coords.DimCoord(years,
                                      standard_name=scube.coord('year').standard_name,
                                      long_name=scube.coord('year').long_name,
                                      var_name=scube.coord('year').var_name,
                                      units=scube.coord('year').units)

    x_bounds = get_bounds_list(x_edges)
    temperature_coord = iris.coords.DimCoord(x_values,
                                             standard_name=tcube.standard_name,
                                             long_name=tcube.long_name,
                                             var_name=tcube.var_name,
                                             units=tunits,
                                             bounds=x_bounds)

    basin_coord = iris.coords.DimCoord(y_values,
                                       standard_name=bcube.standard_name,
                                       long_name=bcube.long_name,
                                       var_name=bcube.var_name,
                                       units=bcube.units,
                                       attributes={'flag_values': bcube.attributes['flag_values'],
                                                   'flag_meanings': bcube.attributes['flag_meanings']})
    
    dim_coords_list = [(year_coord, 0), (temperature_coord, 1), (basin_coord, 2)]

    vcube = iris.cube.Cube(vdata,
                           standard_name=vcube.standard_name,
                           long_name=vcube.long_name,
                           var_name=vcube.var_name,
                           units=vcube.units,
                           attributes=vcube.attributes,
                           dim_coords_and_dims=dim_coords_list)

    vs_std_name = scube.standard_name + '_times_' + vcube.standard_name
    vs_units = str(sunits) + ' ' + str(vcube.units)
    iris.std_names.STD_NAMES[vs_std_name] = {'canonical_units': vs_units}
    vscube = iris.cube.Cube(vsdata,
                            standard_name=vs_std_name,
                            long_name=scube.long_name + ' times ' + vcube.long_name,
                            var_name=scube.var_name + '_' + vcube.var_name,
                            units=vs_units,
                            attributes=scube.attributes,
                            dim_coords_and_dims=dim_coords_list) 

    vt_std_name = tcube.standard_name + '_times_' + vcube.standard_name
    vt_units = str(tunits) + ' ' + str(vcube.units)
    iris.std_names.STD_NAMES[vt_std_name] = {'canonical_units': vt_units}
    vtcube = iris.cube.Cube(vtdata,
                            standard_name=vt_std_name,
                            long_name=tcube.long_name + ' times ' + vcube.long_name,
                            var_name=tcube.var_name + '_' + vcube.var_name,
                            units=vt_units,
                            attributes=tcube.attributes,
                            dim_coords_and_dims=dim_coords_list)

    vcube.attributes['history'] = log
    vscube.attributes['history'] = log
    vtcube.attributes['history'] = log

    outcube_list = iris.cube.CubeList([vcube, vscube, vtcube])

    return outcube_list


def main(inargs):
    """Run the program."""

    vcube = iris.load_cube(inargs.volume_file, 'ocean_volume')
    bcube = iris.load_cube(inargs.basin_file, 'region')

    tmin, tmax = inargs.temperature_bounds
    tstep = inargs.bin_size
    x_edges = numpy.arange(tmin, tmax, tstep)
    x_values = (x_edges[1:] + x_edges[:-1]) / 2
    y_edges = numpy.array([10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5])
    y_values = numpy.array([11, 12, 13, 14, 15, 16, 17])
   
    tcube, thistory = gio.combine_files(inargs.temperature_files, 'sea_water_potential_temperature')
    scube, shistory = gio.combine_files(inargs.salinity_files, 'sea_water_salinity')

    metadata_dict = {inargs.basin_file: bcube.attributes['history'],
                     inargs.volume_file: vcube.attributes['history'],
                     inargs.temperature_files[0]: thistory[0],
                     inargs.salinity_files[0]: shistory[0]}
    log = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)

    iris.coord_categorisation.add_year(tcube, 'time')
    iris.coord_categorisation.add_year(scube, 'time')

    syears = set(scube.coord('year').points)
    tyears = set(tcube.coord('year').points)
    assert syears == tyears
    years = numpy.array(list(syears))
    years.sort()

    v_outdata = numpy.ma.zeros([len(years), len(x_values), len(y_values)])
    vs_outdata = numpy.ma.zeros([len(years), len(x_values), len(y_values)])
    vt_outdata = numpy.ma.zeros([len(years), len(x_values), len(y_values)])
    for index, year in enumerate(years):
        print(year)
        year_constraint = iris.Constraint(year=year)
        salinity_year_cube = scube.extract(year_constraint)
        temperature_year_cube = tcube.extract(year_constraint)

        df, sunits, tunits = create_df(temperature_year_cube, salinity_year_cube, vcube, bcube)

        vdist, xbin_edges, ybin_edges = numpy.histogram2d(df['temperature'].values, df['basin'].values,
                                                          weights=df['volume'].values, bins=[x_edges, y_edges])
        vsdist, xbin_edges, ybin_edges = numpy.histogram2d(df['temperature'].values, df['basin'].values,
                                                           weights=df['volume'].values * df['salinity'].values,
                                                           bins=[x_edges, y_edges])
        vtdist, xbin_edges, ybin_edges = numpy.histogram2d(df['temperature'].values, df['basin'].values,
                                                           weights=df['volume'].values * df['temperature'].values,
                                                           bins=[x_edges, y_edges])
        v_outdata[index, :, :] = vdist
        vs_outdata[index, :, :] = vsdist
        vt_outdata[index, :, :] = vtdist

    v_outdata = numpy.ma.masked_invalid(v_outdata)
    vs_outdata = numpy.ma.masked_invalid(vs_outdata)
    vt_outdata = numpy.ma.masked_invalid(vt_outdata)
    outcube_list = construct_cube(v_outdata, vs_outdata, vt_outdata, vcube,
                                  bcube, scube, tcube, sunits, tunits, years, 
                                  x_values, x_edges, y_values, log)

    equalise_attributes(outcube_list)
    iris.save(outcube_list, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Calculate water mass components binned by temperature'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("volume_file", type=str, help="Volume file")
    parser.add_argument("basin_file", type=str, help="Basin file (from calc_basin.py)")
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--temperature_files", type=str, nargs='*',
                        help="Temperature files") 
    parser.add_argument("--salinity_files", type=str, nargs='*',
                        help="Salinity files")

    parser.add_argument("--temperature_bounds", type=float, nargs=2, default=(-2, 30),
                        help='bounds for the temperature (Y) axis')
    parser.add_argument("--bin_size", type=float, default=0.25,
                        help='bin size (i.e. temperature step)')

    args = parser.parse_args()             

    main(args)
