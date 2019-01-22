"""
Filename:     calc_temporal_aggregate.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the temporal aggregate

"""

# Import general Python modules

import sys, os, pdb, re
import argparse
import numpy, math
import iris
from decimal import Decimal
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
    import timeseries
    import grids
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions
    
def calc_linear_trend(data, xaxis):
    """Calculate the linear trend.
    polyfit returns [a, b] corresponding to y = a + bx
    """    

    if data.mask[0]:
        return data.fill_value
    else:    
        return numpy.polynomial.polynomial.polyfit(xaxis, data, 1)[-1]


def get_agg_cube(cube, agg):
    """Get the temporally aggregated data.

    Args:
      cube (iris.cube.Cube)
      agg (str)

    """

    coord_names = [coord.name() for coord in cube.dim_coords]
    assert coord_names[0] == 'time'

    if agg == 'trend':
        trend_data = timeseries.calc_trend(cube, per_yr=True)
        agg_cube = cube[0, ::].copy()
        agg_cube.data = trend_data
        try:
            agg_cube.units = str(cube.units) + ' yr-1'
        except ValueError:
            agg_cube.units = 'yr-1'
    elif agg == 'clim':
        agg_cube = cube.collapsed('time', iris.analysis.MEAN)    
    agg_cube.remove_coord('time')

    return agg_cube


def get_constraints(inargs):
    """Get the time, depth and mask information"""

    time_constraint = gio.get_time_constraint(inargs.time_bounds)
    depth_constraint = gio.iris_vertical_constraint(0.0, inargs.max_depth)

    if inargs.land_mask:
        sftlf_cube = iris.load_cube(inargs.land_mask, 'land_area_fraction')
    else:
        sftlf_cube = None

    return time_constraint, depth_constraint, sftlf_cube


def process_cube(cube, inargs, sftlf_cube):
    """Process a data cube"""

    if 'salinity' in inargs.var:
        cube = gio.salinity_unit_check(cube)

    if inargs.annual:
        cube = timeseries.convert_to_annual(cube, full_months=True)

    if inargs.aggregation:
        cube = get_agg_cube(cube, inargs.aggregation)
        
    if inargs.regrid:
        before_sum = cube.data.sum()
        before_mean = cube.data.mean()
        cube, coord_names, regrid_status = grids.curvilinear_to_rectilinear(cube)
        if regrid_status:
            print('Warning: Data has been regridded')
            print('Before sum:', '%.2E' % Decimal(before_sum) )
            print('After sum:', '%.2E' % Decimal(cube.data.sum()) )
            print('Before mean:', '%.2E' % Decimal(before_mean) )
            print('After mean:', '%.2E' % Decimal(cube.data.mean()) )
            
    if sftlf_cube:
        cube = uconv.apply_land_ocean_mask(cube, sftlf_cube, 'ocean')

    return cube


def new_file_name(filename, inargs):
    """Take the original file name and create new output file name."""

    infile = filename.split('/')[-1]

    if inargs.annual:
        infile = re.sub('Omon', 'Oyr', infile)
        infile = re.sub('Amon', 'Ayr', infile)

    if inargs.max_depth:
        depth_text = '_0-%sm' %(str(int(inargs.max_depth)))
        infile = re.sub('.nc', depth_text + '.nc', infile)

    outfile = inargs.outfile + infile

    print('output:', outfile)

    return outfile


def combine_infiles(inargs, time_constraint, depth_constraint):
    """Combine multiple input files into one cube"""

    cube, history = gio.combine_files(inargs.infiles, inargs.var)
    atts = cube[0].attributes

    cube = cube.extract(time_constraint & depth_constraint)
    cube = iris.util.squeeze(cube)

    log = cmdprov.new_log(infile_history={inargs.infiles[0]: history[0]}, git_repo=repo_dir)
    cube.attributes['history'] = log

    return cube


def main(inargs):
    """Run the program."""

    time_constraint, depth_constraint, sftlf_cube = get_constraints(inargs)
    nfiles = len(inargs.infiles)
    if inargs.aggregation or nfiles == 1:
        assert inargs.outfile[-3:] == '.nc'
        cube = combine_infiles(inargs, time_constraint, depth_constraint)
        cube = process_cube(cube, inargs, sftlf_cube)
        iris.save(cube, inargs.outfile)
    else:
        assert inargs.outfile[-1] == '/'
        for fnum, filename in enumerate(inargs.infiles):
            cube = iris.load_cube(filename, gio.check_iris_var(inargs.var) & depth_constraint)
            cube = gio.check_time_units(cube)
            cube = process_cube(cube, inargs, sftlf_cube)
                   
            outfile = new_file_name(filename, inargs)
            log = cmdprov.new_log(infile_history={filename: cube.attributes['history']}, git_repo=repo_dir) 
            cube.attributes['history'] = log
            iris.save(cube, outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com
    
"""

    description='Calculate the temporal aggregate at each grid point'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input files")
    parser.add_argument("var", type=str, help="Variable standard_name")
    parser.add_argument("outfile", type=str, help="Output file name (or directory if you want each of many input files processed separately")

    parser.add_argument("--aggregation", type=str, choices=('trend', 'clim'), default=None,
                        help="Method for temporal aggregation [default = None]")

    parser.add_argument("--annual", action="store_true", default=False,
                        help="Convert data to annual mean [default=False]")

    parser.add_argument("--time_bounds", type=str, nargs=2, default=None, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")

    parser.add_argument("--max_depth", type=float, default=None,
                        help="Only include data above this vertical level")

    parser.add_argument("--regrid", action="store_true", default=False,
                        help="Regrid to a regular lat/lon grid")

    parser.add_argument("--land_mask", type=str, default=None,
                        help="Name of sftlf file to use for land mask")

    args = parser.parse_args()            
    main(args)
