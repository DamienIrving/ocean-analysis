"""Bin data for ocean water mass analysis."""

import sys
script_dir = sys.path[0]
import os
import pdb
import argparse
import logging

import numpy as np
import iris
import iris.coord_categorisation
from iris.experimental.equalise_cubes import equalise_attributes
import cmdline_provenance as cmdprov
from statsmodels.stats.weightstats import DescrStatsW

repo_dir = '/'.join(script_dir.split('/')[:-1])
module_dir = repo_dir + '/modules'
sys.path.append(module_dir)
try:
    import water_mass
    import general_io as gio
    import convenient_universal as uconv
    import spatial_weights
except ImportError:
    raise ImportError('Script and modules in wrong directories')


mom_vars = {"temp_nonlocal_KPP": "cp*rho*dzt*nonlocal tendency from KPP",
            "temp_vdiffuse_diff_cbt": "vert diffusion of heat due to diff_cbt",
            "mixdownslope_temp": "cp*mixdownslope*rho*dzt*temp",
            "temp_sigma_diff" : "thk wghtd sigma-diffusion heating",
            "temp_vdiffuse_k33": "vert diffusion of heat due to K33 from neutral diffusion",
            "neutral_diffusion_temp": "rho*dzt*cp*explicit neutral diffusion tendency (heating)",
            "temp_tendency": "time tendency for tracer Conservative temperature"}


def construct_cube(outdata_dict, w_cube, t_cube, s_cube, b_cube,
                   t_values, t_edges, t_units, s_values, s_edges, s_units,
                   log, years=None, mul_ts=False):
    """Create the iris cube for output"""
    
    for key, data in outdata_dict.items():
        outdata_dict[key], b_values, flag_values, flag_meanings = uconv.add_globe_basin(data, b_cube)

    if years is None:
        time_coord = t_cube.coord('time')
    else:
        assert type(years) == np.ndarray
        time_coord = iris.coords.DimCoord(years,
                                          standard_name=t_cube.coord('year').standard_name,
                                          long_name=t_cube.coord('year').long_name,
                                          var_name=t_cube.coord('year').var_name,
                                          units=t_cube.coord('year').units)

    t_bounds = uconv.get_bounds_list(t_edges)
    t_coord_std_name = t_cube.standard_name
    t_coord_long_name = t_cube.long_name
    t_coord_var_name = t_cube.var_name
    t_coord_units = t_units
    t_coord = iris.coords.DimCoord(t_values,
                                   standard_name=t_coord_std_name,
                                   long_name=t_coord_long_name,
                                   var_name=t_coord_var_name,
                                   units=t_coord_units,
                                   bounds=t_bounds)

    s_bounds = uconv.get_bounds_list(s_edges)
    s_coord_std_name = s_cube.standard_name
    s_coord_long_name = s_cube.long_name
    s_coord_var_name = s_cube.var_name
    s_coord_units = s_units
    s_coord = iris.coords.DimCoord(s_values,
                                   standard_name=s_coord_std_name,
                                   long_name=s_coord_long_name,
                                   var_name=s_coord_var_name,
                                   units=s_coord_units,
                                   bounds=s_bounds)

    b_coord = iris.coords.DimCoord(b_values,
                                   standard_name=b_cube.standard_name,
                                   long_name=b_cube.long_name,
                                   var_name=b_cube.var_name,
                                   units=b_cube.units,
                                   attributes={'flag_values': flag_values,
                                               'flag_meanings': flag_meanings})
    
    tbin_dim_coords_list = [(time_coord, 0), (t_coord, 1), (b_coord, 2)]
    sbin_dim_coords_list = [(time_coord, 0), (s_coord, 1), (b_coord, 2)]
    tsbin_dim_coords_list = [(time_coord, 0), (s_coord, 1), (t_coord, 2), (b_coord, 3)]

    outcube_list = iris.cube.CubeList([])
    wvar_list = ['w', 'wt', 'ws'] if mul_ts else ['w']
    for wvar in wvar_list:
        std_base_name = w_cube.standard_name
        long_base_name = w_cube.long_name
        var_base_name = w_cube.var_name
        if wvar == 'wt':
            if std_base_name:
                std_base_name = t_cube.standard_name + '_times_' + std_base_name
            long_base_name = t_cube.long_name.strip() + ' times ' + long_base_name
            var_base_name = t_cube.var_name + '_' + var_base_name
        if wvar == 'ws':
            if std_base_name:
                std_base_name = s_cube.standard_name + '_times_' + std_base_name  
            long_base_name = s_cube.long_name.strip() + ' times ' + long_base_name
            var_base_name = s_cube.var_name + '_' + var_base_name

        if std_base_name:
            tbin_std_name = std_base_name + '_binned_by_temperature'
            iris.std_names.STD_NAMES[tbin_std_name] = {'canonical_units': str(w_cube.units)}
        else:
            tbin_std_name = None
        tbin_cube = iris.cube.Cube(outdata_dict[wvar + '_tbin'],
                                   standard_name=tbin_std_name,
                                   long_name=long_base_name + ' binned by temperature',
                                   var_name=var_base_name + '_tbin',
                                   units=w_cube.units,
                                   attributes=t_cube.attributes,
                                   dim_coords_and_dims=tbin_dim_coords_list)
        tbin_cube.attributes['history'] = log
        outcube_list.append(tbin_cube)

        if std_base_name:
            sbin_std_name = std_base_name + '_binned_by_salinity'
            iris.std_names.STD_NAMES[sbin_std_name] = {'canonical_units': str(w_cube.units)}
        else:
            sbin_std_name = None
        sbin_cube = iris.cube.Cube(outdata_dict[wvar + '_sbin'],
                                   standard_name=sbin_std_name,
                                   long_name=long_base_name + ' binned by salinity',
                                   var_name=var_base_name + '_sbin',
                                   units=w_cube.units,
                                   attributes=t_cube.attributes,
                                   dim_coords_and_dims=sbin_dim_coords_list)
        sbin_cube.attributes['history'] = log
        outcube_list.append(sbin_cube)

        if std_base_name:
            tsbin_std_name = std_base_name + '_binned_by_temperature_and_salinity'
            iris.std_names.STD_NAMES[tsbin_std_name] = {'canonical_units': str(w_cube.units)}
        else:
            tsbin_std_name = None
        tsbin_cube = iris.cube.Cube(outdata_dict[wvar + '_tsbin'],
                                    standard_name=tsbin_std_name,
                                    long_name=long_base_name + ' binned by temperature and salinity',
                                    var_name=var_base_name + '_tsbin',
                                    units=w_cube.units,
                                    attributes=t_cube.attributes,
                                    dim_coords_and_dims=tsbin_dim_coords_list)
        tsbin_cube.attributes['history'] = log
        outcube_list.append(tsbin_cube)

    return outcube_list


def clipping_details(orig_data, clipped_data, bin_edges, var_name):
    """Details of the clipping"""

    bin_min = bin_edges[0]
    bin_second_min = bin_edges[1]
    bin_max = bin_edges[-1]
    bin_second_max = bin_edges[-2]

    npoints_under = np.sum(orig_data < bin_min)
    npoints_min = np.sum(orig_data <= bin_second_min) - npoints_under
    npoints_clip_min = np.sum(clipped_data <= bin_second_min) - np.sum(clipped_data < bin_min)
    assert npoints_clip_min == npoints_under + npoints_min

    npoints_over = np.sum(orig_data > bin_max)
    npoints_max = np.sum(orig_data <= bin_max) - np.sum(orig_data <= bin_second_max)
    npoints_clip_max = np.sum(clipped_data <= bin_max) - np.sum(clipped_data <= bin_second_max)
    assert npoints_clip_max == npoints_over + npoints_max

    logging.info(f"First {var_name} bin had {npoints_min} values, clipping added {npoints_under}")
    logging.info(f"Last {var_name} bin had {npoints_max} values, clipping added {npoints_over}")
    

def bin_data(df, var_list, edge_list, mul_ts=False):
    """Bin the data.

    Args:
      df (pandas.DataFrame)  -- Data
      var_list (list)        -- Variables for binning axes
      edge_list (list)       -- Bin edges for each bin axis variable
      mul_ts (bool)          -- Bin weights times T and S too

    """

    data_list = []
    for var, edges in zip(var_list, edge_list):
        assert var in ['temperature', 'salinity', 'basin']
        values = np.clip(df[var].values, edges[0], edges[-1])
        clipping_details(df[var].values, values, edges, var)
        data_list.append(values)
    data = np.array(data_list).T

    w_data = df['weight'].astype(np.float64).values
    w_dist, edges = np.histogramdd(data, weights=w_data, bins=edge_list)
    binned_total_weight = w_dist.sum()
    orig_total_weight = w_data.sum()
    logging.info(f"Global total before binning: {orig_total_weight}")
    logging.info(f"Global total after binning: {binned_total_weight}")
    np.testing.assert_allclose(orig_total_weight, binned_total_weight, rtol=0.05)
    if mul_ts:
        ws_dist, edges = np.histogramdd(data, weights=w_data * df['salinity'].values, bins=edge_list)
        wt_dist, edges = np.histogramdd(data, weights=w_data * df['temperature'].values, bins=edge_list)
        return w_dist, ws_dist, wt_dist
    else:
        return w_dist
    

def get_weights_data(file_list, var, area_file):
    """Read the weights data file/s"""
    
    w_var = mom_vars[var] if var in mom_vars else var
    if ('vol' in w_var) or ('area' in w_var):
        assert len(file_list) == 1
        w_cube = gio.get_ocean_weights(file_list[0])
        history = w_cube.attributes['history'] 
    else:
        assert area_file, "Area file needed for flux weights"
        w_cube, history = gio.combine_files(file_list, var, checks=True)

    return w_cube, history


def get_log(inargs, w_history, t_history, s_history, b_cube, a_cube):
    """Get the log entry for the output file history attribute."""

    metadata_dict = {}
    if w_history:    
        metadata_dict[inargs.weights_files[0]] = w_history[0]
    if t_history:    
        metadata_dict[inargs.temperature_files[0]] = t_history[0]
    if s_history:    
        metadata_dict[inargs.salinity_files[0]] = s_history[0]
    if 'history' in b_cube.attributes:
        metadata_dict[inargs.basin_file] = b_cube.attributes['history']
    if a_cube:
        if 'history' in a_cube.attributes:
            metadata_dict[inargs.area_file] = a_cube.attributes['history']

    log = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)

    return log


def get_bin_data(files, var, w_cube):
    """Get binning variable data."""

    cube, history = gio.combine_files(files, var, checks=True)
    w_coord_names = [coord.name() for coord in w_cube.dim_coords]
    coord_names = [coord.name() for coord in cube.dim_coords]
    assert w_cube.shape[-2:] == cube.shape[-2:]
    if not w_cube.shape == cube.shape:
        if (w_cube.ndim == 3) and (cube.ndim == 4) and (w_coord_names[0] == coord_names[0]):
            #e.g. w_cube is surface flux (time, i, j),
            #cube is full depth temperature (time, depth, i, j)
            cube = cube[:, 0, ::]
            cube.remove_coord(coord_names[1])
            assert w_cube.shape == cube.shape 
        elif (w_cube.ndim == 2) and (cube.ndim == 4):
            #e.g. w_cube is area (i, j),
            #cube is full depth temperature (time, depth, i, j)
            cube = cube[:, 0, ::]
            cube.remove_coord(coord_names[1])
            assert w_cube.shape == cube.shape[1:]
        else:
            #e.g. w_cube is area (i, j),
            #cube is surface temperature (time, i, j)
            #e.g. w_cube is volume (depth, i, j),
            #cube is temperature (time, depth, i, j)
            assert w_cube.shape == cube.shape[1:]

    return cube, history


def weighted_percentiles(data, weights, percentiles):
    """Return the weighted percentiles.

    Args:
      data (np.ndarray) : Bin variable (e.g. temperature, salinity)
      weights (np.ndarray): Weights (e.g. cell volume, area)
      percentiles (np.ndarray): Array of requested percentiles (e.g. 0-1 by 0.01)

    """
    
    assert percentiles.max() <= 1.0
    assert percentiles.min() >= 0.0

    wq = DescrStatsW(data=data, weights=weights)
    bin_edges = wq.quantile(probs=percentiles, return_pandas=False)

    # manual method does not give a clean results...
    #ix = np.argsort(data)
    #data = data[ix] # sort data
    #weights = weights[ix] # sort weights
    #cdf = (np.cumsum(weights) - 0.5 * weights) / np.sum(weights) # 'like' a CDF function
    #perc = np.arange(0, 1.01, 0.01)
    #test2 = np.interp(perc, cdf, data)

    return bin_edges


def process_data_by_year(t_cube, s_cube, w_cube,
                         a_cube, b_cube,
                         t_values, s_values, b_values,
                         nt_values, ns_values,
                         s_edges, t_edges, b_edges,
                         flux_data, spatial_data,
                         log, inargs):
    """Implement annual binning."""

    iris.coord_categorisation.add_year(t_cube, 'time')
    iris.coord_categorisation.add_year(s_cube, 'time')
    t_years = set(t_cube.coord('year').points)
    s_years = set(s_cube.coord('year').points)
    assert t_years == s_years
    if flux_data:
        iris.coord_categorisation.add_year(w_cube, 'time')
        w_years = set(w_cube.coord('year').points)
        assert w_years == t_years
    years = np.array(list(t_years))
    years.sort()
    
    w_tbin_outdata = np.ma.zeros([len(years), nt_values, len(b_values)])
    w_sbin_outdata = np.ma.zeros([len(years), ns_values, len(b_values)])
    w_tsbin_outdata = np.ma.zeros([len(years), ns_values, nt_values, len(b_values)])
    if spatial_data:
        ws_tbin_outdata = np.ma.zeros([len(years), nt_values, len(b_values)])
        wt_tbin_outdata = np.ma.zeros([len(years), nt_values, len(b_values)])
        ws_sbin_outdata = np.ma.zeros([len(years), ns_values, len(b_values)])
        wt_sbin_outdata = np.ma.zeros([len(years), ns_values, len(b_values)])
        ws_tsbin_outdata = np.ma.zeros([len(years), ns_values, nt_values, len(b_values)])
        wt_tsbin_outdata = np.ma.zeros([len(years), ns_values, nt_values, len(b_values)])

    for year_index, year in enumerate(years):
        print(year)         
        year_constraint = iris.Constraint(year=year)
        s_year_cube = s_cube.extract(year_constraint)
        t_year_cube = t_cube.extract(year_constraint)
        if flux_data:
            w_year_cube = w_cube.extract(year_constraint)
            w_year_cube = spatial_weights.multiply_by_area(w_year_cube, area_cube=a_cube)
        else:
            w_year_cube = w_cube
        df, s_units, t_units = water_mass.create_df(w_year_cube, t_year_cube, s_year_cube, b_cube,
                                                    multiply_weights_by_days_in_year_frac=True)
        if flux_data:
            w_tbin_outdata[year_index, ::] = bin_data(df, ['temperature', 'basin'], [t_edges, b_edges])
            w_sbin_outdata[year_index, ::] = bin_data(df, ['salinity', 'basin'], [s_edges, b_edges])
            w_tsbin_outdata[year_index, ::] = bin_data(df, ['salinity', 'temperature', 'basin'], [s_edges, t_edges, b_edges])
        else:
            tbin_list = bin_data(df, ['temperature', 'basin'], [t_edges, b_edges], mul_ts=True)
            sbin_list = bin_data(df, ['salinity', 'basin'], [s_edges, b_edges], mul_ts=True)
            tsbin_list = bin_data(df, ['salinity', 'temperature', 'basin'], [s_edges, t_edges, b_edges], mul_ts=True)
            w_tbin_outdata[year_index, ::], ws_tbin_outdata[year_index, ::], wt_tbin_outdata[year_index, ::] = tbin_list
            w_sbin_outdata[year_index, ::], ws_sbin_outdata[year_index, ::], wt_sbin_outdata[year_index, ::] = sbin_list
            w_tsbin_outdata[year_index, ::], ws_tsbin_outdata[year_index, ::], wt_tsbin_outdata[year_index, ::] = tsbin_list

    outdata_dict = {}
    outdata_dict['w_tbin'] = np.ma.masked_invalid(w_tbin_outdata)
    outdata_dict['w_sbin'] = np.ma.masked_invalid(w_sbin_outdata)
    outdata_dict['w_tsbin'] = np.ma.masked_invalid(w_tsbin_outdata)
    if spatial_data:
        outdata_dict['ws_tbin'] = np.ma.masked_invalid(ws_tbin_outdata)
        outdata_dict['wt_tbin'] = np.ma.masked_invalid(wt_tbin_outdata)
        outdata_dict['ws_sbin'] = np.ma.masked_invalid(ws_sbin_outdata)
        outdata_dict['wt_sbin'] = np.ma.masked_invalid(wt_sbin_outdata)
        outdata_dict['ws_tsbin'] = np.ma.masked_invalid(ws_tsbin_outdata)
        outdata_dict['wt_tsbin'] = np.ma.masked_invalid(wt_tsbin_outdata)

    outcube_list = construct_cube(outdata_dict, w_year_cube, t_cube, s_cube, b_cube,
                                  t_values, t_edges, t_units, s_values, s_edges, s_units,
                                  log, years=years, mul_ts=spatial_data)

    return outcube_list


def process_data(t_cube, s_cube, w_cube,
                 a_cube, b_cube,
                 t_values, s_values, b_values,
                 nt_values, ns_values,
                 s_edges, t_edges, b_edges,
                 flux_data, spatial_data,
                 log, inargs):
    """Implement binning."""

    nmonths = t_cube.coord('time').shape[0]
    
    w_tbin_outdata = np.ma.zeros([nmonths, nt_values, len(b_values)])
    w_sbin_outdata = np.ma.zeros([nmonths, ns_values, len(b_values)])
    w_tsbin_outdata = np.ma.zeros([nmonths, ns_values, nt_values, len(b_values)])
    if spatial_data:
        ws_tbin_outdata = np.ma.zeros([nmonths, nt_values, len(b_values)])
        wt_tbin_outdata = np.ma.zeros([nmonths, nt_values, len(b_values)])
        ws_sbin_outdata = np.ma.zeros([nmonths, ns_values, len(b_values)])
        wt_sbin_outdata = np.ma.zeros([nmonths, ns_values, len(b_values)])
        ws_tsbin_outdata = np.ma.zeros([nmonths, ns_values, nt_values, len(b_values)])
        wt_tsbin_outdata = np.ma.zeros([nmonths, ns_values, nt_values, len(b_values)])

    for month in range(nmonths):
        print(month)         
        s_month_cube = s_cube[month, ::]
        t_month_cube = t_cube[month, ::]

        if flux_data:
            w_month_cube = w_cube[month, ::]
            w_month_cube = spatial_weights.multiply_by_area(w_month_cube, area_cube=a_cube)
        else:
            w_month_cube = w_cube
        df, s_units, t_units = water_mass.create_df(w_month_cube, t_month_cube, s_month_cube, b_cube)
        if flux_data:
            w_tbin_outdata[month, ::] = bin_data(df, ['temperature', 'basin'], [t_edges, b_edges])
            w_sbin_outdata[month, ::] = bin_data(df, ['salinity', 'basin'], [s_edges, b_edges])
            w_tsbin_outdata[month, ::] = bin_data(df, ['salinity', 'temperature', 'basin'], [s_edges, t_edges, b_edges])
        else:
            tbin_list = bin_data(df, ['temperature', 'basin'], [t_edges, b_edges], mul_ts=True)
            sbin_list = bin_data(df, ['salinity', 'basin'], [s_edges, b_edges], mul_ts=True)
            tsbin_list = bin_data(df, ['salinity', 'temperature', 'basin'], [s_edges, t_edges, b_edges], mul_ts=True)
            w_tbin_outdata[month, ::], ws_tbin_outdata[month, ::], wt_tbin_outdata[month, ::] = tbin_list
            w_sbin_outdata[month, ::], ws_sbin_outdata[month, ::], wt_sbin_outdata[month, ::] = sbin_list
            w_tsbin_outdata[month, ::], ws_tsbin_outdata[month, ::], wt_tsbin_outdata[month, ::] = tsbin_list

    outdata_dict = {}
    outdata_dict['w_tbin'] = np.ma.masked_invalid(w_tbin_outdata)
    outdata_dict['w_sbin'] = np.ma.masked_invalid(w_sbin_outdata)
    outdata_dict['w_tsbin'] = np.ma.masked_invalid(w_tsbin_outdata)
    if spatial_data:
        outdata_dict['ws_tbin'] = np.ma.masked_invalid(ws_tbin_outdata)
        outdata_dict['wt_tbin'] = np.ma.masked_invalid(wt_tbin_outdata)
        outdata_dict['ws_sbin'] = np.ma.masked_invalid(ws_sbin_outdata)
        outdata_dict['wt_sbin'] = np.ma.masked_invalid(wt_sbin_outdata)
        outdata_dict['ws_tsbin'] = np.ma.masked_invalid(ws_tsbin_outdata)
        outdata_dict['wt_tsbin'] = np.ma.masked_invalid(wt_tsbin_outdata)

    outcube_list = construct_cube(outdata_dict, w_month_cube, t_cube, s_cube, b_cube,
                                  t_values, t_edges, t_units, s_values, s_edges, s_units,
                                  log, mul_ts=spatial_data)

    return outcube_list


def main(inargs):
    """Run the program."""

    logging.basicConfig(level=logging.DEBUG)

    spatial_data = ('vol' in inargs.weights_var) or ('area' in inargs.weights_var)
    flux_data = not spatial_data

    w_cube, w_history = get_weights_data(inargs.weights_files, inargs.weights_var, inargs.area_file)
    t_cube, t_history = get_bin_data(inargs.temperature_files, inargs.temperature_var, w_cube)
    s_cube, s_history = get_bin_data(inargs.salinity_files, inargs.salinity_var, w_cube)
    b_cube = iris.load_cube(inargs.basin_file, 'region')
    if inargs.area_file:
        assert flux_data
        a_cube = gio.get_ocean_weights(inargs.area_file)
    else:
        assert spatial_data
        a_cube = None

    log = get_log(inargs, w_history, t_history, s_history, b_cube, a_cube)

    b_values, b_edges = uconv.get_basin_details(b_cube)
    t_min, t_max = inargs.temperature_bounds
    t_step = inargs.tbin_size
    t_edges = np.arange(t_min, t_max + t_step, t_step)
    t_values = (t_edges[1:] + t_edges[:-1]) / 2 
    s_values, s_edges = uconv.salinity_bins()
    nt_values = len(t_values)
    ns_values = len(s_values)

    if inargs.annual:
        outcube_list = process_data_by_year(t_cube, s_cube, w_cube,
                                            a_cube, b_cube,
                                            t_values, s_values, b_values,
                                            nt_values, ns_values,
                                            s_edges, t_edges, b_edges,
                                            flux_data, spatial_data,
                                            log, inargs) 
    else:
        outcube_list = process_data(t_cube, s_cube, w_cube,
                                    a_cube, b_cube,
                                    t_values, s_values, b_values,
                                    nt_values, ns_values,
                                    s_edges, t_edges, b_edges,
                                    flux_data, spatial_data,
                                    log, inargs)

    equalise_attributes(outcube_list)
    iris.save(outcube_list, inargs.outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("weights_files", type=str, nargs='*', help="volume, area or a flux")
    parser.add_argument("weights_var", type=str, help="weights variable")
    parser.add_argument("basin_file", type=str, help="basin file (from calc_basin.py)")
    parser.add_argument("outfile", type=str, help="output file")
                        
    parser.add_argument("--temperature_files", type=str, nargs='*', help="temperature files for the binning") 
    parser.add_argument("--temperature_var", type=str, help="temperature variable")
    parser.add_argument("--salinity_files", type=str, nargs='*', help="salinity files for the binning") 
    parser.add_argument("--salinity_var", type=str, help="salinity variable")

    parser.add_argument("--area_file", type=str, default=None, help="For converting m-2 flux to total")

    parser.add_argument("--temperature_bounds", type=float, nargs=2, default=(-6, 50),
                        help='bounds for the temperature (Y) axis')
    bin_default = 1/3.
    parser.add_argument("--tbin_size", type=float, default=bin_default, help='temperature bin size')
    parser.add_argument("--annual", action="store_true", default=False,
                        help="Annual binning [default=False]")

    args = parser.parse_args()             
    main(args)
