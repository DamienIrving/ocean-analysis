"""Remove drift from a data series"""

import sys
script_dir = sys.path[0]
import os
import pdb
import argparse
import re
import numpy
import iris
import iris.util
import cf_units

repo_dir = '/'.join(script_dir.split('/')[:-1])
module_dir = repo_dir + '/modules'
sys.path.append(module_dir)
try:
    import general_io as gio
    import timeseries
except ImportError:
    raise ImportError('Script and modules in wrong directories')


def apply_polynomial(x_data, coefficient_a_data, coefficient_b_data, coefficient_c_data, coefficient_d_data,
                     poly_start=None, chunk=False):
    """Evaluate cubic polynomial.

    Args:
      x_data (numpy.ndarray): One dimensional x-axis data
      coefficient_data (numpy.ndarray): Multi-dimensional coefficient array (e.g. lat, lon, depth)
      chunk (bool): Chunk the polynomial calculation to avoid memory errors

    """
    
    x_data = x_data.astype(numpy.float32)
    coefficient_dict = {}
    coefficient_dict['a'] = coefficient_a_data
    coefficient_dict['b'] = coefficient_b_data
    coefficient_dict['c'] = coefficient_c_data
    coefficient_dict['d'] = coefficient_d_data

    while x_data.ndim < coefficient_a_data.ndim + 1:
        x_data = x_data[..., numpy.newaxis]
    for letter in ['a', 'b', 'c', 'd']:
        coef = coefficient_dict[letter]
        coef = numpy.repeat(coef[numpy.newaxis, ...], x_data.shape[0], axis=0)
        assert x_data.ndim == coef.ndim
        coefficient_dict[letter] = coef

    if chunk:
        polynomial = numpy.zeros(coefficient_dict['b'].shape, dtype='float32')
        result = numpy.zeros(coefficient_dict['b'].shape, dtype='float32')
        for index in range(0, coefficient_dict['b'].shape[-1]):
            # loop to avoid memory error with large arrays 
            poly = coefficient_dict['a'] + coefficient_dict['b'][..., index] * x_data[..., 0] + coefficient_dict['c'][..., index] * x_data[..., 0]**2 + coefficient_dict['d'][..., index] * x_data[..., 0]**3
            if not type(poly_start) == numpy.ma.core.MaskedArray:
                poly_start = poly[0, ::]
            result[..., index] = poly - poly_start
            polynomial[..., index] = poly 
    else:
        polynomial = coefficient_dict['a'] + coefficient_dict['b'] * x_data + coefficient_dict['c'] * x_data**2 + coefficient_dict['d'] * x_data**3
        if not type(poly_start) == numpy.ma.core.MaskedArray:
            try:
                poly_start = polynomial[0, ::]
            except IndexError:
                poly_start = polynomial[0]
        result = polynomial - poly_start

    return result, polynomial 


def check_attributes(data_attrs, control_attrs):
    """Make sure the correct control run has been used."""

    assert data_attrs['parent_experiment_id'] in [control_attrs['experiment_id'], 'N/A']

    control_rip = 'r%si%sp%s' %(control_attrs['realization'],
                                control_attrs['initialization_method'],
                                control_attrs['physics_version'])
    assert data_attrs['parent_experiment_rip'] in [control_rip, 'N/A']


def check_data_units(data_cube, coefficient_cube):
    """Make sure the units of the data and coefficients match."""

    if data_cube.standard_name == 'sea_water_salinity':
         data_cube = gio.salinity_unit_check(data_cube)

    assert data_cube.units == coefficient_cube.units

    return data_cube


def coefficient_sanity_check(coefficient_a_cube, coefficient_b_cube, coefficient_c_cube, coefficient_d_cube, variable):
    """Sanity check the cubic polynomial coefficients.

    Polynomial is a + bx + cx^2 + dx^3. The telling sign of a poor
    fit is an 'a' value that does not represent a realistic value.

    """
    
    assert variable in ['sea_water_potential_temperature', 'sea_water_salinity']

    if variable == 'sea_water_potential_temperature':
        var_max = 330
        var_min = 250
    elif variable == 'sea_water_salinity':
        var_max = 55
        var_min = 2
 
    nmasked_original = numpy.sum(coefficient_a_cube.data.mask)

    a_data = coefficient_a_cube.data

    original_mask = a_data.mask
    
    crazy_mask_min = numpy.ma.where(a_data < var_min, True, False)
    crazy_mask_max = numpy.ma.where(a_data > var_max, True, False)
    new_mask = numpy.ma.mask_or(crazy_mask_min, crazy_mask_max)
    ncrazy_min = numpy.sum(crazy_mask_min)
    ncrazy_max = numpy.sum(crazy_mask_max)
    ncrazy = ncrazy_min + ncrazy_max

    nmasked_new = numpy.sum(new_mask)    
    npoints = numpy.prod(a_data.shape)
    summary = "Masked %i of %i points because cubic fit was poor" %(ncrazy, npoints)  
    #numpy.argwhere(x == np.min(x)) to see what those points are
    
    coefficient_a_cube.data.mask = new_mask
    coefficient_b_cube.data.mask = new_mask
    coefficient_c_cube.data.mask = new_mask
    coefficient_d_cube.data.mask = new_mask
  
    assert nmasked_new == ncrazy + nmasked_original

    return summary


def time_adjustment(first_data_cube, control_cube, timescale, branch_time=None):
    """Determine the adjustment that needs to be made to time axis.

    Args:
        first_data_cube (iris.Cube.cube)
        control_cube (iris.Cube.cube) - can be the control data or coefficient data cube
        timescale (str): annual or monthly
        branch_time (float): Override the branch time in the file metadata

    For CMIP5 monthly data, the branch time represents the start of the month (e.g. 1 Jan),
      while the first data time is mid-month. A factor of 15.5 is used to fix this.
      When iris is used to calculate annual data from these monthly files,
      the first value is shifted from 15.5 to 182.5.
    
    """

    if timescale == 'monthly':
        adjustment = 15.5
    elif timescale == 'annual':
        adjustment = 182.5

    if not branch_time == None:
        branch_time_value = float(branch_time) + adjustment
    else:
        try:
            branch_time_value = float(first_data_cube.attributes['branch_time_in_parent']) + adjustment
        except KeyError:
            branch_time_value = float(first_data_cube.attributes['branch_time']) + adjustment

    try:
        branch_time_unit = control_cube.attributes['time_unit']
        branch_time_calendar = control_cube.attributes['time_calendar']
    except KeyError:
        branch_time_unit = str(control_cube.coord('time').units)
        branch_time_calendar = str(control_cube.coord('time').units.calendar)
    assert 'days' in branch_time_unit

    data_time_coord = first_data_cube.coord('time')
    data_time_calendar = str(data_time_coord.units.calendar)
    if branch_time_calendar != data_time_calendar:
        if ('gregorian' in branch_time_calendar) and ('gregorian' in data_time_calendar):
            branch_time_calendar = data_time_calendar

    new_unit = cf_units.Unit(branch_time_unit, calendar=branch_time_calendar)  
    data_time_coord.convert_units(new_unit)

    first_experiment_time = data_time_coord.points[0]
    time_diff = first_experiment_time - branch_time_value

    return time_diff, branch_time_value, new_unit


def check_time_adjustment(time_values, coefficient_cube, branch_time, fnum):
    """Check that the time adjustment was correct.

    The branch time given in CMIP5 metadata is for monthly timescale data. 

    If the timescale is unchanged, then after the time adjustment the first time point
      of the first data file should be zero.

    If the timescale was changed to annual, then after time adjustment the first point should 
      be about 6 months (182.5 days), because iris sets the time axis values to the mid point of the year.
    
    """

    assert time_values[0] > float(coefficient_cube.attributes['time_start']) - 1.0 
    assert time_values[-1] < float(coefficient_cube.attributes['time_end']) + 1.0
    # 1.0 allows wriggle room for time_adjustment

    if fnum == 0:
        time_diff = time_values[0] - branch_time
        assert time_diff == 0


def check_data(new_cube, orig_cube, infile):
    """Check that the new data is valid."""

    orig_max = orig_cube.data.max()
    orig_min = orig_cube.data.min()

    new_max = new_cube.data.max()
    new_min = new_cube.data.min()

    valid_max = orig_max * 1.4 if orig_max > 0.0 else orig_max * 0.6
    valid_min = orig_min * 1.4 if orig_min < 0.0 else orig_min * 0.6 

    assert new_max < valid_max, f'New data max is {new_max} compared to old value of {orig_max}, {infile}'
    assert new_min >= valid_min, f'New data min is {new_min} compared to old value of {orig_min}, {infile}'


def main(inargs):
    """Run the program."""
    
    # Read drift coefficients
    coefficient_a_cube = iris.load_cube(inargs.coefficient_file, 'coefficient a')
    coefficient_b_cube = iris.load_cube(inargs.coefficient_file, 'coefficient b')
    coefficient_c_cube = iris.load_cube(inargs.coefficient_file, 'coefficient c')
    coefficient_d_cube = iris.load_cube(inargs.coefficient_file, 'coefficient d')
    if inargs.coefficient_check and (inargs.var in ['sea_water_potential_temperature', 'sea_water_salinity']):
        sanity_summary = coefficient_sanity_check(coefficient_a_cube, coefficient_b_cube, coefficient_c_cube, 
                                                  coefficient_d_cube, inargs.var)
    else:
        sanity_summary = None

    # Read first data cube to get some information
    first_data_cube = iris.load_cube(inargs.data_files[0], gio.check_iris_var(inargs.var))
    coord_names = [coord.name() for coord in first_data_cube.coords(dim_coords=True)]
    assert coord_names[0] == 'time'
    
    if inargs.annual:
        assert inargs.timescale == 'annual'
        first_data_cube = timeseries.convert_to_annual(first_data_cube, chunk=12)

    time_diff, branch_time, new_time_unit = time_adjustment(first_data_cube, coefficient_a_cube,
                                                            inargs.timescale, branch_time=inargs.branch_time)
                
    data_history = first_data_cube.attributes['history']
    del first_data_cube

    new_cubelist = []
    for fnum, filename in enumerate(inargs.data_files):
        # Read data
        data_cube = iris.load_cube(filename, gio.check_iris_var(inargs.var))

        # Reinstate time dim_coord if necessary
        aux_coord_names = [coord.name() for coord in data_cube.aux_coords]
        if 'time' in aux_coord_names:
            data_cube = iris.util.new_axis(data_cube, 'time')
        if inargs.annual:
            assert inargs.timescale == 'annual'
            data_cube = timeseries.convert_to_annual(data_cube, chunk=12)
        data_cube = check_data_units(data_cube, coefficient_a_cube)
        data_cube = gio.check_time_units(data_cube)
        data_cube.cell_methods = ()
        if not inargs.no_parent_check:
            check_attributes(data_cube.attributes, coefficient_a_cube.attributes)

        # Sync the data time axis with the coefficient time axis        
        time_coord = data_cube.coord('time')
        time_coord.convert_units(new_time_unit)
        
        time_values = time_coord.points.astype(numpy.float32) - time_diff
        if not inargs.no_time_check:
            check_time_adjustment(time_values, coefficient_a_cube, branch_time, fnum)    

        # Remove the drift
        if fnum == 0:
            drift_signal, start_polynomial = apply_polynomial(time_values, coefficient_a_cube.data,
                                                              coefficient_b_cube.data, coefficient_c_cube.data,
                                                              coefficient_d_cube.data, poly_start=None,
                                                              chunk=inargs.chunk)
        else:
            try:
                start = start_polynomial[0, ::]
            except IndexError:
                start = start_polynomial[0]
            drift_signal, scraps = apply_polynomial(time_values, coefficient_a_cube.data, coefficient_b_cube.data, coefficient_c_cube.data, coefficient_d_cube.data,
                                                    poly_start=start, chunk=inargs.chunk)

        if not inargs.dummy:
            new_cube = data_cube - drift_signal
            #assert new_cube.data.mask.sum() == drift_signal.mask.sum()
            new_cube.data.mask = drift_signal.mask
            if not inargs.no_data_check:
                check_data(new_cube, data_cube, filename)
        else:
            print('fake run - drift signal not subtracted')
            new_cube = data_cube
        new_cube.metadata = data_cube.metadata
        if sanity_summary:
            new_cube.attributes['drift_removal'] = sanity_summary

        assert (inargs.outfile[-3:] == '.nc') or (inargs.outfile[-1] == '/')

        if inargs.outfile[-3:] == '.nc':
            new_cubelist.append(new_cube)
        elif inargs.outfile[-1] == '/':        
            infile = filename.split('/')[-1]
            if inargs.annual:
                infile = re.sub('Omon', 'Oyr', infile)
            outfile = inargs.outfile + infile
            metadata_dict = {infile: data_cube.attributes['history'], 
                             inargs.coefficient_file: coefficient_a_cube.attributes['history']}
            new_cube.attributes['history'] = gio.write_metadata(file_info=metadata_dict)

            #assert new_cube.data.dtype == numpy.float32
            iris.save(new_cube, outfile, netcdf_format='NETCDF3_CLASSIC')
            print('output:', outfile)
            del new_cube
            del drift_signal
            

    if inargs.outfile[-3:] == '.nc':
        new_cubelist = iris.cube.CubeList(new_cubelist)
        iris.util.equalise_attributes(new_cubelist)
        new_cubelist = new_cubelist.concatenate_cube()

        try: 
            metadata_dict = {inargs.data_files[0]: data_history, 
                             inargs.coefficient_file: coefficient_a_cube.attributes['history']}
        except KeyError:
            metadata_dict = {inargs.data_files[0]: data_history}
        new_cubelist.attributes['history'] = gio.write_metadata(file_info=metadata_dict)

        #assert new_cubelist[0].data.dtype == numpy.float32
        iris.save(new_cubelist, inargs.outfile)


if __name__ == '__main__':
    extra_info =""" 
notes:
    Generate the polynomial coefficients first from calc_drift_coefficients.py
"""
    parser = argparse.ArgumentParser(description=__doc__,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("data_files", type=str, nargs='*', help="Input data files, in chronological order (needs to include whole experiment to get time axis correct)")
    parser.add_argument("var", type=str, help="Variable standard_name")
    parser.add_argument("timescale", type=str, choices=('monthly', 'annual'), help="Timescale of input data")
    parser.add_argument("coefficient_file", type=str, help="Input coefficient file")
    parser.add_argument("outfile", type=str, help="Give a path instead of a file name if you want an output file corresponding to each input file")
    
    parser.add_argument("--no_parent_check", action="store_true", default=False,
                        help="Do not perform the parent experiment check [default: False]")
    parser.add_argument("--no_time_check", action="store_true", default=False,
                        help="Do not perform the time axis adjustment check [default: False]")
    parser.add_argument("--no_data_check", action="store_true", default=False,
                        help="Do not perform check of new dta bounds [default: False]")

    parser.add_argument("--chunk", action="store_true", default=False,
                        help="Split the polynomial calculation up to avoid memory errors [default: False]")
    
    parser.add_argument("--coefficient_check", action="store_true", default=False,
                        help="Check for crazy coefficient values [default: False]")

    parser.add_argument("--branch_time", type=float, default=None,
                        help="Override the branch time listed in the file metadata")

    parser.add_argument("--dummy", action="store_true", default=False,
                        help="Do not actually subtract the drift [default: False]")

    parser.add_argument("--annual", action="store_true", default=False,
                        help="Convert data files to annual timescale [default: False]")

    args = parser.parse_args()            
    main(args)
