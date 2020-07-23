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

def add_globe(outdata, basin_values, basin_cube):
    """Add a global basin.

    Includes all basins (including Arctic) but not marginal seas.

    """

    global_data = outdata[:, :, 0:-1].sum(axis=-1)
    global_data = global_data[..., numpy.newaxis]
    outdata = numpy.ma.concatenate((outdata, global_data), axis=-1)

    basin_values = numpy.append(basin_values, 18)
    flag_values = basin_cube.attributes['flag_values'] + ' 18'
    flag_meanings = basin_cube.attributes['flag_meanings'] + ' globe'

    return outdata, basin_values, flag_values, flag_meanings


def construct_cube(outdata, flux_cube, bin_cube, basin_cube, years, 
                   bin_values, bin_edges, bin_units, basin_values, log):
    """Create the iris cube for output"""
    
    outdata, basin_values, flag_values, flag_meanings = add_globe(outdata, basin_values, basin_cube)

    year_coord = iris.coords.DimCoord(years,
                                      standard_name=flux_cube.coord('year').standard_name,
                                      long_name=flux_cube.coord('year').long_name,
                                      var_name=flux_cube.coord('year').var_name,
                                      units=flux_cube.coord('year').units)

    bin_bounds = uconv.get_bounds_list(bin_edges)
    bin_coord = iris.coords.DimCoord(bin_values,
                                     standard_name=bin_cube.standard_name,
                                     long_name=bin_cube.long_name,
                                     var_name=bin_cube.var_name,
                                     units=bin_units,
                                     bounds=bin_bounds)

    basin_coord = iris.coords.DimCoord(basin_values,
                                       standard_name=basin_cube.standard_name,
                                       long_name=basin_cube.long_name,
                                       var_name=basin_cube.var_name,
                                       units=basin_cube.units,
                                       attributes={'flag_values': flag_values,
                                                   'flag_meanings': flag_meanings})
    
    dim_coords_list = [(year_coord, 0), (bin_coord, 1), (basin_coord, 2)]

    output_cube = iris.cube.Cube(outdata,
                                 standard_name=flux_cube.standard_name,
                                 long_name=flux_cube.long_name,
                                 var_name=flux_cube.var_name,
                                 units=flux_cube.units,
                                 attributes=flux_cube.attributes,
                                 dim_coords_and_dims=dim_coords_list)

    output_cube.attributes['history'] = log

    return output_cube


def get_log(inargs, basin_cube_atts, area_cube_atts, flux_history, bin_history):
    """Get the log entry for the output file history attribute."""

    metadata_dict = {}
    if 'history' in basin_cube_atts:
        metadata_dict[inargs.basin_file] = basin_cube_atts['history']
    if 'history' in area_cube_atts:
        metadata_dict[inargs.area_file] = area_cube_atts['history']
    if flux_history:    
        metadata_dict[inargs.flux_files[0]] = flux_history[0]
    if bin_history:    
        metadata_dict[inargs.bin_files[0]] = bin_history[0]

    log = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)

    return log


def clipping_details(orig_data, clipped_data, bin_min, bin_max, bin_step):
    """Details of the clipping"""

    npoints_under = numpy.sum(orig_data < bin_min)
    npoints_min = numpy.sum(orig_data <= bin_min + bin_step) - numpy.sum(orig_data <= bin_min)
    npoints_clip_min = numpy.sum(clipped_data <= bin_min + bin_step) - numpy.sum(clipped_data <= bin_min)
    assert npoints_clip_min == npoints_under + npoints_min

    npoints_over = numpy.sum(orig_data > bin_max)
    npoints_max = numpy.sum(orig_data <= bin_max) - numpy.sum(orig_data <= bin_max - bin_step)
    npoints_clip_max = numpy.sum(clipped_data <= bin_max) - numpy.sum(clipped_data <= bin_max - bin_step)
    assert npoints_clip_max == npoints_over + npoints_max

    logging.info(f"First bin had {npoints_min} values, clipping added {npoints_under}")
    logging.info(f"Last bin had {npoints_max} values, clipping added {npoints_over}")


def bin_data(df, bin_edges, bin_step, basin_edges, ntimes, nchunks):
    """Bin the data"""

    bin_vals_clipped = numpy.clip(df['bin'].values, bin_edges[0], bin_edges[-1])
    clipping_details(df['bin'].values, bin_vals_clipped, bin_edges[0], bin_edges[-1], bin_step)
    
    flux_data = df['flux'].astype(numpy.float64).values
    bin_vals_split = numpy.array_split(bin_vals_clipped, nchunks)
    basin_vals_split = numpy.array_split(df['basin'].values, nchunks)
    flux_vals_split = numpy.array_split(flux_data, nchunks)

    hist = numpy.zeros([len(bin_edges) - 1, len(basin_edges) - 1])
    for bin_vals, basin_vals, flux_vals in zip(bin_vals_split, basin_vals_split, flux_vals_split):
        hist_chunk, xbin_edges, ybin_edges = numpy.histogram2d(bin_vals, basin_vals, weights=flux_vals, bins=[bin_edges, basin_edges])
        numpy.testing.assert_allclose(hist_chunk.sum(), flux_vals.sum(), rtol=1.5e-02)
        hist = hist + hist_chunk

    hist = hist / ntimes
    binned_total_flux = hist.sum()
    orig_total_flux = flux_data.sum() / ntimes
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


def main(inargs):
    """Run the program."""
    
    logging.basicConfig(level=logging.DEBUG)

    flux_per_area_cube, flux_history = gio.combine_files(inargs.flux_files, inargs.flux_var, checks=True)
    bin_cube, bin_history = gio.combine_files(inargs.bin_files, inargs.bin_var, checks=True)
    if (flux_per_area_cube.ndim == 3) and (bin_cube.ndim == 4):
        bin_coord_names = [coord.name() for coord in bin_cube.dim_coords]
        bin_cube = bin_cube[:, 0, ::]
        bin_cube.remove_coord(bin_coord_names[1])
    assert flux_per_area_cube.shape == bin_cube.shape

    bin_min, bin_max = inargs.bin_bounds
    bin_step = inargs.bin_size
    bin_edges = numpy.arange(bin_min, bin_max + bin_step, bin_step)
    bin_values = (bin_edges[1:] + bin_edges[:-1]) / 2

    area_cube = gio.get_ocean_weights(inargs.area_file)

    basin_cube = iris.load_cube(inargs.basin_file, 'region')
    basin_edges = numpy.array([10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5])
    basin_values = numpy.array([11, 12, 13, 14, 15, 16, 17])
   
    log = get_log(inargs, basin_cube.attributes, area_cube.attributes, flux_history, bin_history)

    iris.coord_categorisation.add_year(flux_per_area_cube, 'time')
    iris.coord_categorisation.add_year(bin_cube, 'time')
    flux_years = set(flux_per_area_cube.coord('year').points)
    bin_years = set(bin_cube.coord('year').points)
    assert flux_years == bin_years
    years = numpy.array(list(flux_years))
    years.sort()
  
    outdata = numpy.ma.zeros([len(years), len(bin_values), len(basin_values)])
    for year_index, year in enumerate(years):
        print(year)         
        year_constraint = iris.Constraint(year=year)
        flux_per_area_year_cube = flux_per_area_cube.extract(year_constraint)
        flux_year_cube = multiply_flux_by_area(flux_per_area_year_cube, area_cube, inargs.flux_var)
        bin_year_cube = bin_cube.extract(year_constraint)
        df, bin_units = water_mass.create_flux_df(flux_year_cube, bin_year_cube, basin_cube)
        ntimes = flux_year_cube.shape[0] 
        outdata[year_index, :, :] = bin_data(df, bin_edges, bin_step, basin_edges, ntimes, inargs.nchunks)
    outdata = numpy.ma.masked_invalid(outdata)
    outcube = construct_cube(outdata, flux_year_cube, bin_cube, basin_cube, years, 
                             bin_values, bin_edges, bin_units, basin_values, log)
    iris.save(outcube, inargs.outfile)


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

    parser.add_argument("--bin_files", type=str, nargs='*', help="Data files for the binning") 
    parser.add_argument("--bin_var", type=str, help="bin variable")
     
    parser.add_argument("--bin_bounds", type=float, nargs=2, default=(-4, 40), help='bin bounds')
    parser.add_argument("--bin_size", type=float, default=1.0, help='bin size')

    parser.add_argument("--nchunks", type=int, default=1,
                        help="Break binning into chunks")

    args = parser.parse_args()             
    main(args)
