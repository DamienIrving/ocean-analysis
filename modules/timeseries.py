"""Collection of functions for dealing with timeseries.

Functions:
  calc_seasonal_cycle         -- Calculate the seasonal cycle
  calc_trend                  -- Calculate the linear trend
  convert_to_annual           -- Convert the data to annual mean
  get_control_time_constraint -- Define the time constraint for the control data

"""

import numpy
import iris
import iris.coord_categorisation
import cf_units
import pdb


def convert_to_seconds(time_axis):
    """Convert time axis units to seconds.

    Args:
      time_axis(iris.DimCoord)

    """

    old_units = str(time_axis.units)
    old_timestep = old_units.split(' ')[0]
    new_units = old_units.replace(old_timestep, 'seconds') 

    new_unit = cf_units.Unit(new_units, calendar=time_axis.units.calendar)  
    time_axis.convert_units(new_unit)

    return time_axis


def get_control_time_constraint(control_cube, ref_cube, time_bounds):
    """Define the time constraint for control data.

    Args:
      control_cube (iris.cube.Cube): cube for piControl experiment
      ref_cube (iris.cube.Cube): reference cube (e.g. from historical experiment)
      time_bounds (list): selected time periods from reference cube
        (e.g. ['1861-01-01', '2005-12-31'])

    """

    iris.coord_categorisation.add_year(control_cube, 'time')
    iris.coord_categorisation.add_year(ref_cube, 'time')

    branch_time = ref_cube.attributes['branch_time']
    
    index = 0
    for bounds in control_cube.coord('time').bounds:
        lower, upper = bounds
        if lower <= branch_time < upper:
            break
        else:
            index = index + 1

    branch_year = control_cube.coord('year').points[index]
    ref_start_year = ref_cube.coord('year').points[0]
    start_gap = int(time_bounds[0].split('-')[0]) - ref_start_year
    end_gap = int(time_bounds[1].split('-')[0]) - ref_start_year

    control_start_year = branch_year + start_gap
    control_end_year = branch_year + end_gap

    control_start_date = str(control_start_year).zfill(4)+'-01-01'
    control_end_date = str(control_end_year).zfill(4)+'-01-01'

    time_constraint = gio.get_time_constraint([control_start_date, control_end_date])

    control_cube.remove_coord('year')
    ref_cube.remove_coord('year')

    return time_constraint


def _linear_trend(data, time_axis):
    """Calculate the linear trend.

    polyfit returns [a, b] corresponding to y = a + bx

    """    

    masked_flag = False

    if type(data) == numpy.ma.core.MaskedArray:
        if type(data.mask) == numpy.bool_:
            if data.mask:
                masked_flag = True
        elif data.mask[0]:
            masked_flag = True
            
    if masked_flag:
        return data.fill_value
    else:
        return numpy.polynomial.polynomial.polyfit(time_axis, data, 1)[-1]


def undo_unit_scaling(cube):
    """Remove scale factor from input data.

    e.g. Ocean heat content data will often have units like 10^12 J m-2.

    Args:
      cube (iris.cube.Cube)

    """

    units = str(cube.units)

    if '^' in units:
        scaling = units.split(' ')[0]
        factor = float(scaling.split('^')[-1])
        cube = cube * 10**factor
    else:
        pass

    return cube


def calc_seasonal_cycle(cube):
    """Calculate the seasonal cycle.

    cycle = (max - min) for each 12 month window 

    Args:
      cube (iris.cube.Cube)

    """

    max_cube = cube.rolling_window('time', iris.analysis.MAX, 12)
    min_cube = cube.rolling_window('time', iris.analysis.MIN, 12)

    seasonal_cycle_cube = max_cube - min_cube

    return seasonal_cycle_cube


def calc_trend(cube, running_mean=False, per_yr=False, remove_scaling=False):
    """Calculate linear trend.

    Args:
      cube (iris.cube.Cube)
      running_mean(bool, optional): 
        A 12-month running mean can first be applied to the data
      yr (bool, optional):
        Change units from per second to per year

    """

    coord_names = [coord.name() for coord in cube.dim_coords]
    assert coord_names[0] == 'time'

    if remove_scaling:
        cube = undo_unit_scaling(cube)

    if running_mean:
        cube = cube.rolling_window('time', iris.analysis.MEAN, 12)

    time_axis = cube.coord('time')
    time_axis = convert_to_seconds(time_axis)

    trend = numpy.ma.apply_along_axis(_linear_trend, 0, cube.data, time_axis.points)
    if type(cube.data) == numpy.ma.core.MaskedArray:
        trend = numpy.ma.masked_values(trend, cube.data.fill_value)

    if per_yr:
        trend = trend * 60 * 60 * 24 * 365.25

    return trend


def is_annual(cube):
    """Check whether the data is annual timescale."""

    year_diffs = numpy.diff(cube.coord('year').points)
    if year_diffs.min() < 1:
        annual = False
    else:
        annual = True 

    return annual


def convert_to_annual(cube, full_months=False, aggregation='mean'):
    """Convert data to annual timescale.

    Args:
      cube (iris.cube.Cube)
      full_months(bool): only include years with data for all 12 months

    """

    iris.coord_categorisation.add_year(cube, 'time')
    iris.coord_categorisation.add_month(cube, 'time')

    if not is_annual(cube):

        if aggregation == 'mean':
            aggregator = iris.analysis.MEAN
        elif aggregation == 'sum':
            aggregator = iris.analysis.SUM

        cube = cube.aggregated_by(['year'], aggregator)

        if full_months:
            cube = cube.extract(iris.Constraint(month='Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec'))
  
    cube.remove_coord('year')
    cube.remove_coord('month')

    return cube

