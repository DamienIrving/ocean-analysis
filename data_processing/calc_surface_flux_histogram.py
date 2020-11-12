"""
Filename:     calc_surface_flux_histogram.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate surface flux histogram  

"""

# Import general Python modules

import sys
import os
import pdb
import argparse
import logging

import numpy
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

def construct_cube(outdata_dict, flux_cube, t_cube, s_cube, basin_cube, years, 
                   t_values, t_edges, t_units, 
                   s_values, s_edges, s_units, log):
    """Create the iris cube for output"""
    
    for key, data in outdata_dict.items():
        outdata_dict[key], basin_values, flag_values, flag_meanings = uconv.add_globe_basin(data, basin_cube)

    year_coord = iris.coords.DimCoord(years,
                                      standard_name=flux_cube.coord('year').standard_name,
                                      long_name=flux_cube.coord('year').long_name,
                                      var_name=flux_cube.coord('year').var_name,
                                      units=flux_cube.coord('year').units)

    t_bounds = uconv.get_bounds_list(t_edges)
    t_coord = iris.coords.DimCoord(t_values,
                                   standard_name=t_cube.standard_name,
                                   long_name=t_cube.long_name,
                                   var_name=t_cube.var_name,
                                   units=t_units,
                                   bounds=t_bounds)

    s_bounds = uconv.get_bounds_list(s_edges)
    s_coord = iris.coords.DimCoord(s_values,
                                   standard_name=s_cube.standard_name,
                                   long_name=s_cube.long_name,
                                   var_name=s_cube.var_name,
                                   units=s_units,
                                   bounds=s_bounds)

    basin_coord = iris.coords.DimCoord(basin_values,
                                       standard_name=basin_cube.standard_name,
                                       long_name=basin_cube.long_name,
                                       var_name=basin_cube.var_name,
                                       units=basin_cube.units,
                                       attributes={'flag_values': flag_values,
                                                   'flag_meanings': flag_meanings})
    
    tbin_dim_coords_list = [(year_coord, 0), (t_coord, 1), (basin_coord, 2)]
    sbin_dim_coords_list = [(year_coord, 0), (s_coord, 1), (basin_coord, 2)]
    tsbin_dim_coords_list = [(year_coord, 0), (s_coord, 1), (t_coord, 2), (basin_coord, 3)]

    tbin_std_name = flux_cube.standard_name + '_binned_by_temperature'
    iris.std_names.STD_NAMES[tbin_std_name] = {'canonical_units': str(flux_cube.units)}
    tbin_cube = iris.cube.Cube(outdata_dict['tbin'],
                               standard_name=tbin_std_name,
                               long_name=flux_cube.long_name + ' binned by temperature',
                               var_name=flux_cube.var_name + '_tbin',
                               units=flux_cube.units,
                               attributes=flux_cube.attributes,
                               dim_coords_and_dims=tbin_dim_coords_list)

    sbin_std_name = flux_cube.standard_name + '_binned_by_salinity'
    iris.std_names.STD_NAMES[sbin_std_name] = {'canonical_units': str(flux_cube.units)}
    sbin_cube = iris.cube.Cube(outdata_dict['sbin'],
                               standard_name=sbin_std_name,
                               long_name=flux_cube.long_name + ' binned by salinity',
                               var_name=flux_cube.var_name + '_sbin',
                               units=flux_cube.units,
                               attributes=flux_cube.attributes,
                               dim_coords_and_dims=sbin_dim_coords_list)

    tsbin_std_name = flux_cube.standard_name + '_binned_by_temperature_and_salinity'
    iris.std_names.STD_NAMES[tsbin_std_name] = {'canonical_units': str(flux_cube.units)}
    tsbin_cube = iris.cube.Cube(outdata_dict['tsbin'],
                                standard_name=tsbin_std_name,
                                long_name=flux_cube.long_name + ' binned by temperature and salinity',
                                var_name=flux_cube.var_name + '_tsbin',
                                units=flux_cube.units,
                                attributes=flux_cube.attributes,
                                dim_coords_and_dims=tsbin_dim_coords_list)

    tbin_cube.attributes['history'] = log
    sbin_cube.attributes['history'] = log
    tsbin_cube.attributes['history'] = log

    outcube_list = iris.cube.CubeList([tbin_cube, sbin_cube, tsbin_cube])

    return outcube_list


def get_log(inargs, basin_cube_atts, area_cube_atts, flux_history, t_history, s_history):
    """Get the log entry for the output file history attribute."""

    metadata_dict = {}
    if 'history' in basin_cube_atts:
        metadata_dict[inargs.basin_file] = basin_cube_atts['history']
    if 'history' in area_cube_atts:
        metadata_dict[inargs.area_file] = area_cube_atts['history']
    if flux_history:    
        metadata_dict[inargs.flux_files[0]] = flux_history[0]
    if t_history:    
        metadata_dict[inargs.temperature_files[0]] = t_history[0]
    if s_history:    
        metadata_dict[inargs.salinity_files[0]] = s_history[0]

    log = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)

    return log


def clipping_details(orig_data, clipped_data, bin_edges):
    """Details of the clipping"""

    npoints_under = numpy.sum(orig_data < bin_edges[0])
    npoints_min = numpy.sum(orig_data <= bin_edges[1]) - numpy.sum(orig_data <= bin_edges[0])
    npoints_clip_min = numpy.sum(clipped_data <= bin_edges[1]) - numpy.sum(clipped_data <= bin_edges[0])
    assert npoints_clip_min == npoints_under + npoints_min

    npoints_over = numpy.sum(orig_data > bin_edges[-1])
    npoints_max = numpy.sum(orig_data <= bin_edges[-1]) - numpy.sum(orig_data <= bin_edges[-2])
    npoints_clip_max = numpy.sum(clipped_data <= bin_edges[-1]) - numpy.sum(clipped_data <= bin_edges[-2])
    assert npoints_clip_max == npoints_over + npoints_max

    logging.info(f"First bin had {npoints_min} values, clipping added {npoints_under}")
    logging.info(f"Last bin had {npoints_max} values, clipping added {npoints_over}")


def bin_data(df, var_list, edge_list):
    """Bin the data

    Args:
      df (pandas.DataFrame) -- Data
      var_list (list)       -- Variables for binning axes
      edge_list (list)      -- Bin edges for each bin axis variable

    """

    bin_data_list = []
    for var, edges in zip(var_list, edge_list):
        assert var in ['temperature', 'salinity', 'basin']
        values = numpy.clip(df[var].values, edges[0], edges[-1])
        clipping_details(df[var].values, values, edges, var)
        bin_data_list.append(values)
    bin_data = numpy.array(bin_data_list).T
    
    flux_data = df['flux'].astype(numpy.float64).values

    hist, edges = numpy.histogramdd(bin_data, weights=flux_data, bins=edge_list)

    binned_total_flux = hist.sum()
    orig_total_flux = flux_data.sum()
    numpy.testing.assert_allclose(orig_total_flux, binned_total_flux, rtol=1.5e-02)

    return hist


def multiply_flux_by_area(flux_per_unit_area_cube, area_cube, var):
    """Multiply the flux by area."""

    flux_ndim = flux_per_unit_area_cube.ndim
    assert area_cube.ndim == 2
    area_data = uconv.broadcast_array(area_cube.data, [flux_ndim - 2, flux_ndim - 1], flux_per_unit_area_cube.shape)
    flux_cube = flux_per_unit_area_cube.copy()
    flux_cube.data = flux_per_unit_area_cube.data * area_data
    flux_cube.units = str(flux_cube.units).replace('m-2', "").replace("  ", " ")

    return flux_cube


def get_bin_data(files, var, flux_cube):
    """Get binning variable data."""

    cube, history = gio.combine_files(files, var, checks=True)
    if (flux_cube.ndim == 3) and (cube.ndim == 4):
        cube_coord_names = [coord.name() for coord in cube.dim_coords]
        cube = cube[:, 0, ::]
        cube.remove_coord(cube_coord_names[1])
    assert flux_cube.shape == cube.shape

    return cube, history


def main(inargs):
    """Run the program."""

    logging.basicConfig(level=logging.DEBUG)

    mom_vars = {"temp_nonlocal_KPP": "cp*rho*dzt*nonlocal tendency from KPP",
                "temp_vdiffuse_diff_cbt": "vert diffusion of heat due to diff_cbt",
                "mixdownslope_temp": "cp*mixdownslope*rho*dzt*temp",
                "temp_sigma_diff" : "thk wghtd sigma-diffusion heating",
                "temp_vdiffuse_k33": "vert diffusion of heat due to K33 from neutral diffusion",
                "neutral_diffusion_temp": "rho*dzt*cp*explicit neutral diffusion tendency (heating)",
                "temp_tendency": "time tendency for tracer Conservative temperature"}

    flux_var = mom_vars[inargs.flux_var] if inargs.flux_var in mom_vars else inargs.flux_var
    flux_per_area_cube, flux_history = gio.combine_files(inargs.flux_files, flux_var, checks=True)

    t_cube, t_history = get_bin_data(inargs.temperature_files, inargs.temperature_var, flux_per_area_cube)
    s_cube, s_history = get_bin_data(inargs.salinity_files, inargs.salinity_var, flux_per_area_cube)

    s_values, s_edges = uconv.salinity_bins()
    
    t_min, t_max = inargs.temperature_bounds
    t_step = inargs.bin_size
    t_edges = numpy.arange(t_min, t_max + t_step, t_step)
    t_values = (t_edges[1:] + t_edges[:-1]) / 2

    area_cube = gio.get_ocean_weights(inargs.area_file)

    basin_cube = iris.load_cube(inargs.basin_file, 'region')
    basin_values, basin_edges = uconv.get_basin_details(basin_cube)
   
    log = get_log(inargs, basin_cube.attributes, area_cube.attributes, flux_history, t_history, s_history)

    iris.coord_categorisation.add_year(flux_per_area_cube, 'time')
    iris.coord_categorisation.add_year(t_cube, 'time')
    iris.coord_categorisation.add_year(s_cube, 'time')
    flux_years = set(flux_per_area_cube.coord('year').points)
    t_years = set(t_cube.coord('year').points)
    s_years = set(s_cube.coord('year').points)
    assert flux_years == s_years
    assert flux_years == t_years
    years = numpy.array(list(flux_years))
    years.sort()
  
    tbin_outdata = numpy.ma.zeros([len(years), len(t_values), len(basin_values)])
    sbin_outdata = numpy.ma.zeros([len(years), len(s_values), len(basin_values)])
    tsbin_outdata = numpy.ma.zeros([len(years), len(s_values), len(t_values), len(basin_values)])
    for year_index, year in enumerate(years):
        print(year)         
        year_constraint = iris.Constraint(year=year)
        flux_per_area_year_cube = flux_per_area_cube.extract(year_constraint)
        flux_year_cube = multiply_flux_by_area(flux_per_area_year_cube, area_cube, flux_var)
        t_year_cube = t_cube.extract(year_constraint)
        s_year_cube = s_cube.extract(year_constraint)
        df, t_units, sunits = water_mass.create_flux_df(flux_year_cube, t_year_cube, s_year_cube, basin_cube,
                                                        sbounds=(s_edges[0], s_edges[-1]),
                                                        multiply_flux_by_days_in_year_frac=True)
        ntimes = flux_year_cube.shape[0] 
        tbin_outdata[year_index, ::] = bin_data(df, ['temperature', 'basin'], [t_edges, basin_edges])
        sbin_outdata[year_index, ::] = bin_data(df, ['salinity', 'basin'], [s_edges, basin_edges])
        tsbin_outdata[year_index, ::] = bin_data(df, ['salinity', 'temperature', 'basin'], [s_edges, t_edges, basin_edges])

    outdata_dict = {}
    outdata_dict['tbin'] = numpy.ma.masked_invalid(tbin_outdata)
    outdata_dict['sbin'] = numpy.ma.masked_invalid(sbin_outdata)
    outdata_dict['tsbin'] = numpy.ma.masked_invalid(tsbin_outdata)

    outcube_list = construct_cube(outdata_dict, flux_year_cube, t_cube, s_cube, basin_cube, years, 
                                  t_values, t_edges, t_units, s_values, s_edges, t_units, log)
    equalise_attributes(outcube_list)
    iris.save(outcube_list, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Calculate surface flux histogram'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("flux_files", type=str, nargs='*', help="Flux files (per m2)")
    parser.add_argument("flux_var", type=str, help="Flux variable")
    parser.add_argument("area_file", type=str, help="Surface area file")
    parser.add_argument("basin_file", type=str, help="Basin file (from calc_basin.py)")
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--temperature_files", type=str, nargs='*', help="Temperature files for the binning") 
    parser.add_argument("--temperature_var", type=str, help="temperature variable")
    parser.add_argument("--salinity_files", type=str, nargs='*', help="Salinity files for the binning") 
    parser.add_argument("--salinity_var", type=str, help="salinity variable")
     
    parser.add_argument("--temperature_bounds", type=float, nargs=2, default=(-6, 50), help='temperature bin bounds')
    parser.add_argument("--bin_size", type=float, default=1.0, help='temperature bin size')

    args = parser.parse_args()             
    main(args)
