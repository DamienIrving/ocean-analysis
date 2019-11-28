"""
Filename:     calc_water_mass_components.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate weight (volume or area), weight*salinity and
              weight*temperature binned by temperature
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
    import water_mass
    import general_io as gio
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def get_bounds_list(edges):
    """Create a bounds list from edge list"""

    bounds_list = []
    for i in range(len(edges) - 1):
        interval = [edges[i], edges[i+1]]
        bounds_list.append(interval)

    return numpy.array(bounds_list)


def construct_cube(wdata, wsdata, wtdata, wcube, bcube, scube, tcube, sunits,
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

    wcube = iris.cube.Cube(wdata,
                           standard_name=wcube.standard_name,
                           long_name=wcube.long_name,
                           var_name=wcube.var_name,
                           units=wcube.units,
                           attributes=wcube.attributes,
                           dim_coords_and_dims=dim_coords_list)

    ws_std_name = scube.standard_name + '_times_' + wcube.standard_name
    ws_units = str(sunits) + ' ' + str(wcube.units)
    iris.std_names.STD_NAMES[ws_std_name] = {'canonical_units': ws_units}
    wscube = iris.cube.Cube(wsdata,
                            standard_name=ws_std_name,
                            long_name=scube.long_name + ' times ' + wcube.long_name,
                            var_name=scube.var_name + '_' + wcube.var_name,
                            units=ws_units,
                            attributes=scube.attributes,
                            dim_coords_and_dims=dim_coords_list) 

    wt_std_name = tcube.standard_name + '_times_' + wcube.standard_name
    wt_units = str(tunits) + ' ' + str(wcube.units)
    iris.std_names.STD_NAMES[wt_std_name] = {'canonical_units': wt_units}
    wtcube = iris.cube.Cube(wtdata,
                            standard_name=wt_std_name,
                            long_name=tcube.long_name + ' times ' + wcube.long_name,
                            var_name=tcube.var_name + '_' + wcube.var_name,
                            units=wt_units,
                            attributes=tcube.attributes,
                            dim_coords_and_dims=dim_coords_list)

    wcube.attributes['history'] = log
    wscube.attributes['history'] = log
    wtcube.attributes['history'] = log

    outcube_list = iris.cube.CubeList([wcube, wscube, wtcube])

    return outcube_list


def main(inargs):
    """Run the program."""

    wcube = iris.load_cube(inargs.weights_file)
    wvar = wcube.var_name
    assert wvar in ['areacello', 'volcello']
    bcube = iris.load_cube(inargs.basin_file, 'region')

    tmin, tmax = inargs.temperature_bounds
    tstep = inargs.bin_size
    x_edges = numpy.arange(tmin, tmax + tstep, tstep)
    x_values = (x_edges[1:] + x_edges[:-1]) / 2
    y_edges = numpy.array([10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5])
    y_values = numpy.array([11, 12, 13, 14, 15, 16, 17])
   
    tcube, thistory = gio.combine_files(inargs.temperature_files, 'sea_water_potential_temperature')
    scube, shistory = gio.combine_files(inargs.salinity_files, 'sea_water_salinity')

    assert tcube.shape == scube.shape
    coord_names = [coord.name() for coord in tcube.dim_coords]

    metadata_dict = {inargs.basin_file: bcube.attributes['history'],
                     inargs.weights_file: wcube.attributes['history'],
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

    w_outdata = numpy.ma.zeros([len(years), len(x_values), len(y_values)])
    ws_outdata = numpy.ma.zeros([len(years), len(x_values), len(y_values)])
    wt_outdata = numpy.ma.zeros([len(years), len(x_values), len(y_values)])
    for index, year in enumerate(years):
        print(year)
        year_constraint = iris.Constraint(year=year)
        if wvar == 'areacello':
            assert scube.ndim == 4
            salinity_year_cube = scube[:, 0, ::].extract(year_constraint)
            temperature_year_cube = tcube[:, 0, ::].extract(year_constraint)
            assert salinity_year_cube.coord(coord_names[1]).bounds[0][0] == 0
        else:
            salinity_year_cube = scube.extract(year_constraint)
            temperature_year_cube = tcube.extract(year_constraint)

        df, sunits, tunits = water_mass.create_df(temperature_year_cube, salinity_year_cube, wcube, bcube)

        wdist, xbin_edges, ybin_edges = numpy.histogram2d(df['temperature'].values, df['basin'].values,
                                                          weights=df['weight'].values, bins=[x_edges, y_edges])
        wsdist, xbin_edges, ybin_edges = numpy.histogram2d(df['temperature'].values, df['basin'].values,
                                                           weights=df['weight'].values * df['salinity'].values,
                                                           bins=[x_edges, y_edges])
        wtdist, xbin_edges, ybin_edges = numpy.histogram2d(df['temperature'].values, df['basin'].values,
                                                           weights=df['weight'].values * df['temperature'].values,
                                                           bins=[x_edges, y_edges])
        ntimes = salinity_year_cube.shape[0]
        w_outdata[index, :, :] = wdist / ntimes
        numpy.testing.assert_allclose(wcube.data.sum(), w_outdata[index, :, :].sum(), rtol=1e-03)
        ws_outdata[index, :, :] = wsdist / ntimes
        wt_outdata[index, :, :] = wtdist / ntimes

    w_outdata = numpy.ma.masked_invalid(w_outdata)
    ws_outdata = numpy.ma.masked_invalid(ws_outdata)
    wt_outdata = numpy.ma.masked_invalid(wt_outdata)
    outcube_list = construct_cube(w_outdata, ws_outdata, wt_outdata, wcube,
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

    parser.add_argument("weights_file", type=str, help="Can be a volcello or areacello file")
    parser.add_argument("basin_file", type=str, help="Basin file (from calc_basin.py)")
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--temperature_files", type=str, nargs='*',
                        help="Temperature files") 
    parser.add_argument("--salinity_files", type=str, nargs='*',
                        help="Salinity files")

    parser.add_argument("--temperature_bounds", type=float, nargs=2, default=(-4, 40),
                        help='bounds for the temperature (Y) axis')
    parser.add_argument("--bin_size", type=float, default=1.0,
                        help='bin size (i.e. temperature step)')

    args = parser.parse_args()             

    main(args)
