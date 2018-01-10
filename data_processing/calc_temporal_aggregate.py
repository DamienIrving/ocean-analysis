"""
Filename:     calc_trend.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the linear trend

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy, math
import iris
from iris.experimental.equalise_cubes import equalise_attributes
from decimal import Decimal

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


def lat_tropics(cell):
    return -30 < cell < 30


def subtract_tropics(cube):
    """Subtract the mean tropics trend."""

    lat_constraint = iris.Constraint(latitude=lat_tropics)
    tropics_cube = cube.extract(lat_constraint)
    tropics_mean = tropics_cube.collapsed(['longitude', 'latitude'], iris.analysis.MEAN)

    cube.data = cube.data - tropics_mean.data

    return cube


def main(inargs):
    """Run the program."""

    # Read data
    try:
        time_constraint = gio.get_time_constraint(inargs.time_bounds)
    except AttributeError:
        time_constraint = iris.Constraint()

    with iris.FUTURE.context(cell_datetime_objects=True):
        cube = iris.load(inargs.infiles, gio.check_iris_var(inargs.var))
        history = cube[0].attributes['history']
        atts = cube[0].attributes
        equalise_attributes(cube)
        iris.util.unify_time_units(cube)
        cube = cube.concatenate_cube()

        cube = gio.check_time_units(cube)
        cube = cube.extract(time_constraint)

        cube = iris.util.squeeze(cube)

        if 'salinity' in inargs.var:
            cube = gio.salinity_unit_check(cube)

        infile_metadata = {inargs.infiles[0]: history}

    agg_cube = get_agg_cube(cube, inargs.aggregation)

    if inargs.regrid:
        before_sum = agg_cube.data.sum()
        before_mean = agg_cube.data.mean()
        agg_cube, coord_names, regrid_status = grids.curvilinear_to_rectilinear(agg_cube)
        if regrid_status:
            print('Warning: Data has been regridded')
            print('Before sum:', '%.2E' % Decimal(before_sum) )
            print('After sum:', '%.2E' % Decimal(agg_cube.data.sum()) )
            print('Before mean:', '%.2E' % Decimal(before_mean) )
            print('After mean:', '%.2E' % Decimal(agg_cube.data.mean()) )

    if inargs.subtract_tropics:
        agg_cube = subtract_tropics(agg_cube)             

    atts['history'] = gio.write_metadata(file_info=infile_metadata)
    agg_cube.attributes = atts

    iris.FUTURE.netcdf_no_unlimited = True
    iris.save(agg_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com
    
"""

    description='Calculate the temporal aggregate (linear trend or climatology) at each grid point'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input files")
    parser.add_argument("var", type=str, help="Variable standard_name")
    parser.add_argument("aggregation", type=str, choices=('trend', 'clim'), help="Method for temporal aggregation")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--time_bounds", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")

    parser.add_argument("--subtract_tropics", action="store_true", default=False,
                        help="Subtract the mean tropics trend from all data points")
    parser.add_argument("--regrid", action="store_true", default=False,
                        help="Regrid to a regular lat/lon grid")

    args = parser.parse_args()            
    main(args)
