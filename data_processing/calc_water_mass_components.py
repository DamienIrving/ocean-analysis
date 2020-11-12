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
import logging

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

def construct_cube(outdata_dict,
                   wcube, bcube, scube, tcube, sunits, tunits, years,
                   t_values, t_edges, s_values, s_edges, log):
    """Create the iris cube for output"""

    for key, data in outdata_dict.items():
        outdata_dict[key], b_values, flag_values, flag_meanings = uconv.add_globe_basin(data, bcube)
    
    year_coord = iris.coords.DimCoord(years,
                                      standard_name=scube.coord('year').standard_name,
                                      long_name=scube.coord('year').long_name,
                                      var_name=scube.coord('year').var_name,
                                      units=scube.coord('year').units)

    t_bounds = uconv.get_bounds_list(t_edges)
    temperature_coord = iris.coords.DimCoord(t_values,
                                             standard_name=tcube.standard_name,
                                             long_name=tcube.long_name.strip(),
                                             var_name=tcube.var_name,
                                             units=tunits,
                                             bounds=t_bounds)

    s_bounds = uconv.get_bounds_list(s_edges)
    salinity_coord = iris.coords.DimCoord(s_values,
                                          standard_name=scube.standard_name,
                                          long_name=scube.long_name.strip(),
                                          var_name=scube.var_name,
                                          units=sunits,
                                          bounds=s_bounds)

    basin_coord = iris.coords.DimCoord(b_values,
                                       standard_name=bcube.standard_name,
                                       long_name=bcube.long_name,
                                       var_name=bcube.var_name,
                                       units=bcube.units,
                                       attributes={'flag_values': flag_values,
                                                   'flag_meanings': flag_meanings})
    
    tbin_dim_coords_list = [(year_coord, 0), (temperature_coord, 1), (basin_coord, 2)]
    sbin_dim_coords_list = [(year_coord, 0), (salinity_coord, 1), (basin_coord, 2)]
    tsbin_dim_coords_list = [(year_coord, 0), (salinity_coord, 1), (temperature_coord, 2), (basin_coord, 3)]
    wcube.var_name = wcube.var_name if type(wcube) == iris.cube.Cube else wcube.name

    w_tbin_std_name = wcube.standard_name + '_binned_by_temperature'
    iris.std_names.STD_NAMES[w_tbin_std_name] = {'canonical_units': str(wcube.units)}
    w_tbin_cube = iris.cube.Cube(outdata_dict['w_tbin'],
                                 standard_name=w_tbin_std_name,
                                 long_name=wcube.long_name + ' binned by temperature',
                                 var_name=wcube.var_name + '_tbin',
                                 units=wcube.units,
                                 attributes=tcube.attributes,
                                 dim_coords_and_dims=tbin_dim_coords_list)

    ws_tbin_std_name = scube.standard_name + '_times_' + wcube.standard_name + '_binned_by_temperature'
    ws_units = str(sunits) + ' ' + str(wcube.units)
    iris.std_names.STD_NAMES[ws_tbin_std_name] = {'canonical_units': ws_units}
    ws_tbin_cube = iris.cube.Cube(outdata_dict['ws_tbin'],
                                  standard_name=ws_tbin_std_name,
                                  long_name=scube.long_name.strip() + ' times ' + wcube.long_name + ' binned by temperature',
                                  var_name=scube.var_name + '_' + wcube.var_name + '_tbin',
                                  units=ws_units,
                                  attributes=scube.attributes,
                                  dim_coords_and_dims=tbin_dim_coords_list) 

    wt_tbin_std_name = tcube.standard_name + '_times_' + wcube.standard_name + '_binned_by_temperature'
    wt_units = str(tunits) + ' ' + str(wcube.units)
    iris.std_names.STD_NAMES[wt_tbin_std_name] = {'canonical_units': wt_units}
    wt_tbin_cube = iris.cube.Cube(outdata_dict['wt_tbin'],
                                  standard_name=wt_tbin_std_name,
                                  long_name=tcube.long_name.strip() + ' times ' + wcube.long_name + ' binned by temperature',
                                  var_name=tcube.var_name + '_' + wcube.var_name + '_tbin',
                                  units=wt_units,
                                  attributes=tcube.attributes,
                                  dim_coords_and_dims=tbin_dim_coords_list)

    w_sbin_std_name = wcube.standard_name + '_binned_by_salinity'
    iris.std_names.STD_NAMES[w_sbin_std_name] = {'canonical_units': str(wcube.units)}
    w_sbin_cube = iris.cube.Cube(outdata_dict['w_sbin'],
                                 standard_name=w_sbin_std_name,
                                 long_name=wcube.long_name + ' binned by salinity',
                                 var_name=wcube.var_name + '_sbin',
                                 units=wcube.units,
                                 attributes=scube.attributes,
                                 dim_coords_and_dims=sbin_dim_coords_list)

    ws_sbin_std_name = scube.standard_name + '_times_' + wcube.standard_name + '_binned_by_salinity'
    iris.std_names.STD_NAMES[ws_sbin_std_name] = {'canonical_units': ws_units}
    ws_sbin_cube = iris.cube.Cube(outdata_dict['ws_sbin'],
                                  standard_name=ws_sbin_std_name,
                                  long_name=scube.long_name.strip() + ' times ' + wcube.long_name + ' binned by salinity',
                                  var_name=scube.var_name + '_' + wcube.var_name + '_sbin',
                                  units=ws_units,
                                  attributes=scube.attributes,
                                  dim_coords_and_dims=sbin_dim_coords_list) 

    wt_sbin_std_name = tcube.standard_name + '_times_' + wcube.standard_name + '_binned_by_salinity'
    iris.std_names.STD_NAMES[wt_sbin_std_name] = {'canonical_units': wt_units}
    wt_sbin_cube = iris.cube.Cube(outdata_dict['wt_sbin'],
                                  standard_name=wt_sbin_std_name,
                                  long_name=tcube.long_name.strip() + ' times ' + wcube.long_name + ' binned by salinity',
                                  var_name=tcube.var_name + '_' + wcube.var_name + '_sbin',
                                  units=wt_units,
                                  attributes=tcube.attributes,
                                  dim_coords_and_dims=sbin_dim_coords_list)

    w_tsbin_std_name = wcube.standard_name + '_binned_by_temperature_and_salinity'
    iris.std_names.STD_NAMES[w_tsbin_std_name] = {'canonical_units': str(wcube.units)}
    w_tsbin_cube = iris.cube.Cube(outdata_dict['w_tsbin'],
                                  standard_name=w_tsbin_std_name,
                                  long_name=wcube.long_name + ' binned by temperature and salinity',
                                  var_name=wcube.var_name + '_tsbin',
                                  units=wcube.units,
                                  attributes=tcube.attributes,
                                  dim_coords_and_dims=tsbin_dim_coords_list)

    ws_tsbin_std_name = scube.standard_name + '_times_' + wcube.standard_name + '_binned_by_temperature_and_salinity'
    iris.std_names.STD_NAMES[ws_tsbin_std_name] = {'canonical_units': ws_units}
    ws_tsbin_cube = iris.cube.Cube(outdata_dict['ws_tsbin'],
                                   standard_name=ws_tsbin_std_name,
                                   long_name=scube.long_name.strip() + ' times ' + wcube.long_name + ' binned by temperature and salinity',
                                   var_name=scube.var_name + '_' + wcube.var_name + '_tsbin',
                                   units=ws_units,
                                   attributes=scube.attributes,
                                   dim_coords_and_dims=tsbin_dim_coords_list) 

    wt_tsbin_std_name = tcube.standard_name + '_times_' + wcube.standard_name + '_binned_by_temperature_and_salinity'
    iris.std_names.STD_NAMES[wt_tsbin_std_name] = {'canonical_units': wt_units}
    wt_tsbin_cube = iris.cube.Cube(outdata_dict['wt_tsbin'],
                                   standard_name=wt_tsbin_std_name,
                                   long_name=tcube.long_name.strip() + ' times ' + wcube.long_name + ' binned by temperature and salinity',
                                   var_name=tcube.var_name + '_' + wcube.var_name + '_tsbin',
                                   units=wt_units,
                                   attributes=tcube.attributes,
                                   dim_coords_and_dims=tsbin_dim_coords_list)

    w_tbin_cube.attributes['history'] = log
    ws_tbin_cube.attributes['history'] = log
    wt_tbin_cube.attributes['history'] = log
    w_sbin_cube.attributes['history'] = log
    ws_sbin_cube.attributes['history'] = log
    wt_sbin_cube.attributes['history'] = log
    w_tsbin_cube.attributes['history'] = log
    ws_tsbin_cube.attributes['history'] = log
    wt_tsbin_cube.attributes['history'] = log

    outcube_list = iris.cube.CubeList([w_tbin_cube, ws_tbin_cube, wt_tbin_cube,
                                       w_sbin_cube, ws_sbin_cube, wt_sbin_cube,
                                       w_tsbin_cube, ws_tsbin_cube, wt_tsbin_cube,])

    return outcube_list


def get_log(inargs, bcube_atts, wcube_atts, thistory, shistory):
    """Get the log entry for the output file history attribute."""

    metadata_dict = {}
    if 'history' in bcube_atts:
        metadata_dict[inargs.basin_file] = bcube_atts['history']
    if 'history' in wcube_atts:
        metadata_dict[inargs.weights_file] = wcube_atts['history']
    if thistory:    
        metadata_dict[inargs.temperature_files[0]] = thistory[0]
    if shistory:    
        metadata_dict[inargs.salinity_files[0]] = shistory[0]

    log = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)

    return log


def clipping_details(orig_data, clipped_data, bin_edges, var_name):
    """Details of the clipping"""

    bin_min = bin_edges[0]
    bin_second_min = bin_edges[1]
    bin_max = bin_edges[-1]
    bin_second_max = bin_edges[-2]

    npoints_under = numpy.sum(orig_data < bin_min)
    npoints_min = numpy.sum(orig_data <= bin_second_min) - npoints_under
    npoints_clip_min = numpy.sum(clipped_data <= bin_second_min) - numpy.sum(clipped_data < bin_min)
    assert npoints_clip_min == npoints_under + npoints_min

    npoints_over = numpy.sum(orig_data > bin_max)
    npoints_max = numpy.sum(orig_data <= bin_max) - numpy.sum(orig_data <= bin_second_max)
    npoints_clip_max = numpy.sum(clipped_data <= bin_max) - numpy.sum(clipped_data <= bin_second_max)
    assert npoints_clip_max == npoints_over + npoints_max

    logging.info(f"First {var_name} bin had {npoints_min} values, clipping added {npoints_under}")
    logging.info(f"Last {var_name} bin had {npoints_max} values, clipping added {npoints_over}")


def bin_data(df, var_list, edge_list):
    """Bin the data.

    Args:
      df (pandas.DataFrame)  -- Data
      var_list (list)        -- Variables for binning axes
      edge_list (list)       -- Bin edges for each bin axis variable

    """

    data_list = []
    for var, edges in zip(var_list, edge_list):
        assert var in ['temperature', 'salinity', 'basin']
        values = numpy.clip(df[var].values, edges[0], edges[-1])
        clipping_details(df[var].values, values, edges, var)
        data_list.append(values)
    data = numpy.array(data_list).T

    w_dist, edges = numpy.histogramdd(data, weights=df['weight'].values, bins=edge_list)
    ws_dist, edges = numpy.histogramdd(data, weights=df['weight'].values * df['salinity'].values, bins=edge_list)
    wt_dist, edges = numpy.histogramdd(data, weights=df['weight'].values * df['temperature'].values, bins=edge_list)

    binned_total_weight = w_dist.sum()
    orig_total_weight = df['weight'].values.sum()
    numpy.testing.assert_allclose(orig_total_weight, binned_total_weight, rtol=1e-03)

    return w_dist, ws_dist, wt_dist
   

def main(inargs):
    """Run the program."""

    logging.basicConfig(level=logging.DEBUG)

    wcube = gio.get_ocean_weights(inargs.weights_file)  
    bcube = iris.load_cube(inargs.basin_file, 'region')
    b_values, b_edges = uconv.get_basin_details(bcube)

    tmin, tmax = inargs.temperature_bounds
    tstep = inargs.bin_size
    t_edges = numpy.arange(tmin, tmax + tstep, tstep)
    t_values = (t_edges[1:] + t_edges[:-1]) / 2

    s_values, s_edges = uconv.salinity_bins()
   
    tcube, thistory = gio.combine_files(inargs.temperature_files, inargs.temperature_var, checks=True)
    scube, shistory = gio.combine_files(inargs.salinity_files, 'sea_water_salinity', checks=True)

    assert tcube.shape == scube.shape
    coord_names = [coord.name() for coord in tcube.dim_coords]

    log = get_log(inargs, bcube.attributes, wcube.attributes, thistory, shistory)

    iris.coord_categorisation.add_year(tcube, 'time')
    iris.coord_categorisation.add_year(scube, 'time')

    syears = set(scube.coord('year').points)
    tyears = set(tcube.coord('year').points)
    assert syears == tyears
    years = numpy.array(list(syears))
    years.sort()

    w_tbin_outdata = numpy.ma.zeros([len(years), len(t_values), len(b_values)])
    ws_tbin_outdata = numpy.ma.zeros([len(years), len(t_values), len(b_values)])
    wt_tbin_outdata = numpy.ma.zeros([len(years), len(t_values), len(b_values)])
    w_sbin_outdata = numpy.ma.zeros([len(years), len(s_values), len(b_values)])
    ws_sbin_outdata = numpy.ma.zeros([len(years), len(s_values), len(b_values)])
    wt_sbin_outdata = numpy.ma.zeros([len(years), len(s_values), len(b_values)])
    w_tsbin_outdata = numpy.ma.zeros([len(years), len(s_values), len(t_values), len(b_values)])
    ws_tsbin_outdata = numpy.ma.zeros([len(years), len(s_values), len(t_values), len(b_values)])
    wt_tsbin_outdata = numpy.ma.zeros([len(years), len(s_values), len(t_values), len(b_values)])
    for index, year in enumerate(years):
        print(year)
        year_constraint = iris.Constraint(year=year)
        if wcube.var_name == 'areacello':
            assert scube.ndim == 4
            salinity_year_cube = scube[:, 0, ::].extract(year_constraint)
            temperature_year_cube = tcube[:, 0, ::].extract(year_constraint)
        else:
            salinity_year_cube = scube.extract(year_constraint)
            temperature_year_cube = tcube.extract(year_constraint)
          
        df, sunits, tunits = water_mass.create_df(temperature_year_cube, salinity_year_cube, wcube, bcube,
                                                  sbounds=(s_edges[0], s_edges[-1]), multiply_weights_by_days_in_year_frac=True)

        w_tbin_outdata[index, ::], ws_tbin_outdata[index, ::], wt_tbin_outdata[index, ::] = bin_data(df, ['temperature', 'basin'], [t_edges, b_edges])
        w_sbin_outdata[index, ::], ws_sbin_outdata[index, ::], wt_sbin_outdata[index, ::] = bin_data(df, ['salinity', 'basin'], [s_edges, b_edges])
        w_tsbin_outdata[index, ::], ws_tsbin_outdata[index, ::], wt_tsbin_outdata[index, ::] = bin_data(df, ['salinity', 'temperature', 'basin'],
                                                                                                        [s_edges, t_edges, b_edges])

    outdata_dict = {}
    outdata_dict['w_tbin'] = numpy.ma.masked_invalid(w_tbin_outdata)
    outdata_dict['ws_tbin'] = numpy.ma.masked_invalid(ws_tbin_outdata)
    outdata_dict['wt_tbin'] = numpy.ma.masked_invalid(wt_tbin_outdata)
    outdata_dict['w_sbin'] = numpy.ma.masked_invalid(w_sbin_outdata)
    outdata_dict['ws_sbin'] = numpy.ma.masked_invalid(ws_sbin_outdata)
    outdata_dict['wt_sbin'] = numpy.ma.masked_invalid(wt_sbin_outdata)
    outdata_dict['w_tsbin'] = numpy.ma.masked_invalid(w_tsbin_outdata)
    outdata_dict['ws_tsbin'] = numpy.ma.masked_invalid(ws_tsbin_outdata)
    outdata_dict['wt_tsbin'] = numpy.ma.masked_invalid(wt_tsbin_outdata)
    outcube_list = construct_cube(outdata_dict,
                                  wcube, bcube, scube, tcube, sunits, tunits, years, 
                                  t_values, t_edges, s_values, s_edges, log)

    equalise_attributes(outcube_list)
    iris.save(outcube_list, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Calculate water mass components binned by temperature and salinity'
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

    parser.add_argument("--temperature_bounds", type=float, nargs=2, default=(-6, 50),
                        help='bounds for the temperature (Y) axis')
    parser.add_argument("--bin_size", type=float, default=1.0,
                        help='bin size (i.e. temperature step)')
    parser.add_argument("--temperature_var", type=str, default='sea_water_potential_temperature',
                        help='temperature variable')

    args = parser.parse_args()             

    main(args)
