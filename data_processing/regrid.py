"""
Filename:     regrid.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Regrid input data
"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
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
    import timeseries
    import grids
    import general_io as gio
    import spatial_weights
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions


def check_inputs(inargs):
    """Check inputs"""

    if inargs.lats:
        assert inargs.lons, 'must provide new lats and lons'

    if inargs.lons:
        assert inargs.lats, 'must provide new lats and lons'


def get_dim_vals(user_input, bounds=False):
    """Get the list of values for a data dimension/axis.

    Args:
      bounds (bool): input represents the bounds, not centre points

    """

    vals = user_input
    if user_input:
        if len(user_input) == 3:
            start, stop, step = user_input
            vals = list(numpy.arange(start, stop + step, step))
        if bounds:
            vals = numpy.array(vals)
            vals = (vals[1:] + vals[:-1]) / 2
        vals = list(vals)    

    return vals


def get_sample_points(cube, dim_vals):
    """Define the sample points for interpolation"""

    sample_points = []
    coord_names = [coord.name() for coord in cube.dim_coords]
    if 'time' in coord_names:
        coord_names.remove('time')

    for coord in coord_names:
        if dim_vals[coord]:
            sample_points.append((coord, dim_vals[coord]))
        else:
            sample_points.append((coord, cube.coord(coord).points))

    return sample_points


def get_depth_bounds(depth_intervals):
    """Create an array of bounds pairs"""

    depth_bounds = []
    for index in range(len(depth_intervals) - 1):
        depth_bounds.append([depth_intervals[index], depth_intervals[index + 1]])

    return numpy.array(depth_bounds)


def remove_nans(cube):
    """Turn NaN masked fill value."""

    nan_locations = numpy.argwhere(numpy.isnan(cube.data))
    for loc in nan_locations:
        cube.data[tuple(loc)] = cube.data.fill_value
        cube.data.mask[tuple(loc)] = True

    print('There was %s NaNs' %(str(len(nan_locations))) )

    return cube


def main(inargs):
    """Run the program."""

    cube = iris.load_cube(inargs.infile, inargs.var)
    cube = gio.check_time_units(cube)
    if inargs.annual:
        cube = timeseries.convert_to_annual(cube, chunk=inargs.chunk)
    log = cmdprov.new_log(infile_history={inargs.infile: cube.attributes['history']}, git_repo=repo_dir) 

    dim_vals = {}
    dim_vals['latitude'] = get_dim_vals(inargs.lats) 
    dim_vals['longitude'] = get_dim_vals(inargs.lons)
    if inargs.levs:
        dim_vals['depth'] = get_dim_vals(inargs.levs)
    else:
        dim_vals['depth'] = get_dim_vals(inargs.depth_bnds, bounds=True)

    # Regrid from curvilinear to rectilinear if necessary
    regrid_status = False
    if inargs.lats:
        horizontal_grid = grids.make_grid(dim_vals['latitude'], dim_vals['longitude'])
        cube, coord_names, regrid_status = grids.curvilinear_to_rectilinear(cube, target_grid_cube=horizontal_grid)

    # Regrid to new grid
    if dim_vals['depth'] or not regrid_status:
        sample_points = get_sample_points(cube, dim_vals)
        cube = cube.interpolate(sample_points, iris.analysis.Linear())
        cube.coord('latitude').guess_bounds()
        cube.coord('longitude').guess_bounds()
        if inargs.levs:
            cube = spatial_weights.guess_depth_bounds(cube)
        else:
            cube.coord('depth').bounds = get_depth_bounds(inargs.depth_bnds)

    if numpy.isnan(numpy.min(cube.data)):
        cube = remove_nans(cube)

    # Reinstate time dim_coord if necessary
    aux_coord_names = [coord.name() for coord in cube.aux_coords]
    if 'time' in aux_coord_names:
        cube = iris.util.new_axis(cube, 'time')

    cube.attributes['history'] = log
    iris.save(cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
    
"""

    description='Apply annual timescale smoothing'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file")
    parser.add_argument("var", type=str, help="Variable name")
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--lats", type=float, nargs='*', default=None, 
                        help="list all latitude points of new grid or three values: start, stop, interval")
    parser.add_argument("--lons", type=float, nargs='*', default=None, 
                        help="list all longitude points of new grid or three values: start, stop, interval")
    parser.add_argument("--levs", type=float, nargs='*', default=None, 
                        help="list all depth points of new grid or three values: start, stop, interval")
    parser.add_argument("--depth_bnds", type=float, nargs='*', default=None, 
                        help="list of the depth bounds of new grid or three values: start, stop, interval")

    parser.add_argument("--annual", action="store_true", default=False,
                        help="Convert data to annual timescale [default: False]")
    parser.add_argument("--chunk", action="store_true", default=False,
                        help="Chunk annual timescale conversion to avoid memory errors [default: False]")


    args = parser.parse_args()            
    check_inputs(args)

main(args)
