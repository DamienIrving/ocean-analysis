"""
Filename:     calc_drift_coefficients.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the polynomial coefficents that characterise model drift 

"""

# Import general Python modules

import sys, os, pdb
import argparse, copy
import numpy
import iris
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
    import timeseries
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

history = []

def save_history(cube, field, filename):
    """Save the history attribute when reading the data.

    (This is required because the history attribute differs between input files 
    and is therefore deleted upon equilising attributes)  

    """ 

    try:
        history.append(cube.attributes['history'])
    except KeyError:
        pass


def polyfit(data, time_axis, masked_array, outlier_threshold):
    """Fit polynomial to data."""    

    if not masked_array:
        if outlier_threshold:
            data, outlier_idx = timeseries.outlier_removal(data, outlier_threshold)
        coeffs = numpy.ma.polyfit(time_axis, data, 3)[::-1]
    elif data.mask.sum() > 0:
        coeffs = numpy.array([data.fill_value]*4) 
    else:    
        if outlier_threshold:
            data, outlier_idx = timeseries.outlier_removal(data, outlier_threshold)
        coeffs = numpy.ma.polyfit(time_axis, data, 3)[::-1]

    return coeffs


def is_masked_array(array):
    """Determine whether an array is masked or not."""

    masked = False
    if type(array) == numpy.ma.core.MaskedArray:
        if array.mask.shape:
            masked = True

    return masked


def calc_coefficients(cube, coord_names, masked_array=True, convert_annual=False, 
                      chunk_annual=False, outlier_threshold=None):
    """Calculate the polynomial coefficients.

    Can select to convert data to annual timescale first.

    Choices are made to avoid memory errors on large arrays.

    """
    
    if 'depth' in coord_names:
        assert coord_names[1] == 'depth', 'coordinate order must be time, depth, ...'
        out_shape = list(cube.shape)
        out_shape[0] = 4
        coefficients = numpy.zeros(out_shape)   #, dtype=numpy.float32)
        for d, cube_slice in enumerate(cube.slices_over('depth')):
            print('Depth:', cube_slice.coord('depth').points[0])
            if convert_annual:
                cube_slice = timeseries.convert_to_annual(cube_slice, chunk=chunk_annual)
            time_axis = cube_slice.coord('time').points  #.astype(numpy.float32)
            coefficients[:,d, ::] = numpy.ma.apply_along_axis(polyfit, 0, cube_slice.data, time_axis,
                                                              masked_array, outlier_threshold)
        fill_value = cube_slice.data.fill_value 
        coefficients = numpy.ma.masked_values(coefficients, fill_value)
    else:
        if convert_annual:
            cube = timeseries.convert_to_annual(cube)
        time_axis = cube.coord('time').points  # .astype(numpy.float32)
        if cube.ndim == 1:
            coefficients = polyfit(cube.data, time_axis, masked_array, outlier_threshold)
        else:   
            coefficients = numpy.ma.apply_along_axis(polyfit, 0, cube.data, time_axis,
                                                     masked_array, outlier_threshold)
            if masked_array:
                fill_value = cube.data.fill_value 
                coefficients = numpy.ma.masked_values(coefficients, fill_value)
    
    time_start = time_axis[0]
    time_end = time_axis[-1]

    return coefficients, time_start, time_end


def set_global_atts(inargs, cube):
    """Set global attributes."""

    atts = copy.copy(cube.attributes)
    atts['polynomial'] = 'a + bx + cx^2 + dx^3'
    try:
        #atts['history'] = gio.write_metadata(file_info={inargs.infiles[0]: history[0]})   
        atts['history'] = cmdprov.new_log(infile_history={inargs.infiles[0]: history[0]}, git_repo=repo_dir)
    except IndexError:
        pass

    return atts


def check_units(cube, variable, magnitude_check=True):
    """Check that the units are valid."""

    if variable == 'sea_water_salinity':
        if magnitude_check:
            salinity_mean = cube.data.mean() 
            assert 2.0 < salinity_mean < 55.0
        cube.units = 'g/kg' 

    return cube


def concatenate_cube(cube_list):
    """Concatenate cube_list"""

    equalise_attributes(cube_list)
    cube = cube_list.concatenate_cube()
    cube = gio.check_time_units(cube)

    coord_names = [coord.name() for coord in cube.coords(dim_coords=True)]
    assert coord_names[0] == 'time', "First axis must be time"

    return cube, coord_names


def main(inargs):
    """Run the program."""

    # Read the data
    cubes = iris.load(inargs.infiles, gio.check_iris_var(inargs.var), callback=save_history)
    global_atts = set_global_atts(inargs, cubes[0])
    masked_array = is_masked_array(cubes[0].data)

    iris.util.unify_time_units(cubes)
    cube, coord_names = concatenate_cube(cubes)

    # Coefficients cube
    coefficients, time_start, time_end = calc_coefficients(cube, coord_names, masked_array=masked_array,
                                                           convert_annual=inargs.annual,
                                                           chunk_annual=inargs.chunk,
                                                           outlier_threshold=inargs.outlier_threshold)
    global_atts['time_unit'] = str(cube.coord('time').units)
    global_atts['time_calendar'] = str(cube.coord('time').units.calendar)
    global_atts['time_start'] = time_start
    global_atts['time_end'] = time_end

    dim_coords = []
    for i, coord_name in enumerate(coord_names[1:]):
        dim_coords.append((cube.coord(coord_name), i))

    if cube.aux_coords:
        assert len(cube.aux_coords) == 2, "Script can only deal with two auxillary coordinates"
        dims = range(0, coefficients[0, ::].ndim)
        aux_coords = [(cube.aux_coords[0], [dims[-2], dims[-1]]), (cube.aux_coords[1], [dims[-2], dims[-1]])]
    else:
        aux_coords = None

    out_cubes = []
    for index, letter in enumerate(['a', 'b', 'c', 'd']):
        standard_name = 'coefficient_'+letter
        iris.std_names.STD_NAMES[standard_name] = {'canonical_units': cube.units}
        try:
            coef = coefficients[index, ::]
        except IndexError:
            coef = coefficients[index]
        new_cube = iris.cube.Cube(coef,
                                  standard_name=standard_name,
                                  long_name='coefficient '+letter,
                                  var_name='coef_'+letter,
                                  units=cube.units,
                                  attributes=global_atts,
                                  dim_coords_and_dims=dim_coords,
                                  aux_coords_and_dims=aux_coords) 
        if letter == 'a':
            new_cube = check_units(new_cube, inargs.var, magnitude_check=True)
        else:
            new_cube = check_units(new_cube, inargs.var, magnitude_check=False)
        out_cubes.append(new_cube)

    # First decadal mean cube
    assert coord_names[0] == 'time'
    end = 10 
    time_mean = cube[0:end, ::].collapsed('time', iris.analysis.MEAN)
    time_mean.remove_coord('time')
    time_mean = check_units(time_mean, inargs.var, magnitude_check=True)
    time_mean.attributes = global_atts
    out_cubes.append(time_mean)

    # Write output file  
  
#    for cube in out_cubes:
#        assert cube.data.dtype == numpy.float32
    cube_list = iris.cube.CubeList(out_cubes)

    iris.save(cube_list, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
notes:
    To avoid memory errors, for 4D data (time, depth, y, x) you may need
      to do the annual smoothing beforehand    

"""

    description='Calculate the polynomial coefficents that characterise model drift'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input file names")
    parser.add_argument("var", type=str, help="Input variable")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--annual", action="store_true", default=False,
                        help="Convert data to annual timescale [default: False]")
    parser.add_argument("--chunk", action="store_true", default=False,
                        help="Chunk annual timescale conversion to avoid memory errors [default: False]")
    parser.add_argument("--outlier_threshold", type=float, default=None,
                        help="Remove points that deviate from the rolling median by greater than this threshold [default: None]")

    args = parser.parse_args()
    main(args)

