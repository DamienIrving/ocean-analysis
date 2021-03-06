"""Collection of functions for dealing with timeseries.

Functions:
  calc_seasonal_cycle         -- Calculate the seasonal cycle
  calc_trend                  -- Calculate the linear trend
  convert_to_annual           -- Convert the data to annual mean
  equalise_time_axes          -- Make all the time axes in an iris cube list the same
  flux_to_total               -- Convert a flux (i.e. per second quantity) to total
  get_control_time_constraint -- Define the time constraint for the control data
  outlier_removal             -- Remove outliers from a timeseries
  runmean                     -- Calculae the running mean

"""

import pdb
import math

import numpy as np
import pandas as pd
import iris
import iris.coord_categorisation
import cf_units

import general_io as gio
import convenient_universal as uconv


def adjust_control_time(cube, ref_cube, branch_index=None, branch_time=None):
    """Adjust the control time axis so it matches the reference cube."""

    if branch_index == None:
        if not branch_time:
            branch_time = ref_cube.attributes['branch_time']
            print('branch time =', branch_time)
        branch_index, index_error = uconv.find_nearest(cube.coord('time').points, float(branch_time), index=True)
        print('branch index =', branch_index)
    else:
        print('branch time =', cube.coord('time').points[branch_index])

    iris.util.unify_time_units([ref_cube, cube])
    
    adjustment_factor = cube.coord('time').points[branch_index] - ref_cube.coord('time').points[0]
    cube.coord('time').points = cube.coord('time').points - adjustment_factor

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


def calc_trend(cube, running_mean=False, per_yr=False,
               remove_scaling=False, outlier_threshold=None):
    """Calculate linear trend.

    Args:
      cube (iris.cube.Cube)
      running_mean(bool, optional): 
        A 12-month running mean can first be applied to the data
      per_yr (bool, optional):
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

    trend = np.ma.apply_along_axis(linear_trend, 0, cube.data, time_axis.points, outlier_threshold)
    if type(cube.data) == np.ma.core.MaskedArray:
        trend = np.ma.masked_values(trend, cube.data.fill_value)

    if per_yr:
        trend = trend * 60 * 60 * 24 * 365.25

    return trend


def _check_attributes(data_attrs, control_attrs):
    """Make sure the correct control run has been used."""

    assert data_attrs['parent_experiment_id'] in [control_attrs['experiment_id'], 'N/A']

    control_rip = 'r%si%sp%s' %(control_attrs['realization'],
                                control_attrs['initialization_method'],
                                control_attrs['physics_version'])
    assert data_attrs['parent_experiment_rip'] in [control_rip, 'N/A']


def _chunked_year_aggregation(cube, agg_method, step=12, days_in_month=False):
    """Chunked conversion to annual timescale.

    Args:
      cube (iris.cube.Cube)
      agg_method (iris.analysis.WeightedAggregator): aggregation method
      step (int): Integer number of time steps used in chunking
        (For monthly data this would be a multiple of 12) 

    """

    assert agg_method in [iris.analysis.SUM, iris.analysis.MEAN]
    chunk_list = iris.cube.CubeList([])
    coord_names = [coord.name() for coord in cube.dim_coords]
    start_indexes, step = uconv.get_chunks(cube.shape, coord_names, chunk=True, step=step)
    start_year = end_year = -5
    for index in start_indexes:
        start_year = cube[index:index+step, ...].coord('year').points[0]
        assert start_year != end_year
        print(start_year)
        end_year = cube[index:index+step, ...].coord('year').points[-1]
        if days_in_month:
            chunk = _days_in_month_annual_mean(cube[index:index+step, ...])
        else:
            chunk = cube[index:index+step, ...].aggregated_by(['year'], agg_method)
        chunk_list.append(chunk)

    annual_cube = chunk_list.concatenate()[0]

    return annual_cube


def get_days_in_year(cube, return_df=False):
    """Generate an array of days in each year.

    Returns a pandas data series.

    """

    aux_coord_names = [coord.name() for coord in cube.aux_coords]
    if not 'year' in aux_coord_names:
        iris.coord_categorisation.add_year(cube, 'time')

    assert 'days' in str(cube.coord('time').units)
    time_span_days = cube.coord('time').bounds[:, 1] - cube.coord('time').bounds[:, 0]
    assert time_span_days.max() < 32
    assert time_span_days.min() > 26
  
    df = pd.DataFrame(data={'days_in_month': time_span_days, 'year': cube.coord('year').points})
    days_in_year = df.groupby('year').sum()

    if return_df:
        return df, days_in_year['days_in_month']
    else:
        return days_in_year['days_in_month']


def _days_in_month_annual_mean(cube):
    """Calculate the annual mean timeseries accounting for days in month."""

    df, days_in_year = get_days_in_year(cube, return_df=True)
    
    df['weight'] = df.apply(lambda row: row['days_in_month'] / days_in_year.loc[row['year']], axis=1)
    np.testing.assert_allclose(df.groupby('year').sum()['weight'].min(), 1.0)
    np.testing.assert_allclose(df.groupby('year').sum()['weight'].max(), 1.0)

    weights_array = uconv.broadcast_array(df['weight'].values, 0, cube.shape)
    cube.data = cube.data * weights_array
    cube = cube.aggregated_by(['year'], iris.analysis.SUM)

    return cube
    

def convert_to_annual(cube, aggregation='mean', chunk=False, days_in_month=False):
    """Convert data to annual timescale.

    Args:
      cube (iris.cube.Cube)
      full_months(bool): Only include years with data for all 12 months
      chunk (bool): Chunk along the time axis
        (Set by default to a chunk step of 12 assuming monthly data.)
      days_in_month (bool): Account for the fact that each month has a different
         number of days.

    """

    aux_coord_names = [coord.name() for coord in cube.aux_coords]
    if not 'year' in aux_coord_names:
        iris.coord_categorisation.add_year(cube, 'time')
    iris.coord_categorisation.add_month(cube, 'time')

    if not is_annual(cube):

        if aggregation == 'mean':
            aggregator = iris.analysis.MEAN
        elif aggregation == 'sum':
            aggregator = iris.analysis.SUM
 
        if days_in_month:
            assert aggregation == 'mean'
            if chunk:
                cube = _chunked_year_aggregation(cube, aggregator, step=36, days_in_month=True)
            else:
                cube = _days_in_month_annual_mean(cube)
        else:
            if chunk:
                cube = _chunked_year_aggregation(cube, aggregator, step=12)
            else:
                cube = cube.aggregated_by(['year'], aggregator)

    cube.remove_coord('year')
    cube.remove_coord('month')

    return cube


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


def equalise_time_axes(cube_list):
    """Make all the time axes in an iris cube list the same."""

    iris.util.unify_time_units(cube_list)
    reference_cube = cube_list[0]
    new_cube_list = iris.cube.CubeList([])
    for cube in cube_list:
        assert len(cube.coord('time').points) == len(reference_cube.coord('time').points)
        cube.coord('time').points = reference_cube.coord('time').points
        cube.coord('time').bounds = reference_cube.coord('time').bounds
        cube.coord('time').units = reference_cube.coord('time').units
        cube.coord('time').attributes = reference_cube.coord('time').attributes
        new_cube_list.append(cube)
    
    return new_cube_list


def flux_to_total(cube):
    """Convert a flux (i.e. per second quantity) to total"""

    assert 'days' in str(cube.coord('time').units)
    time_span_days = cube.coord('time').bounds[:, 1] - cube.coord('time').bounds[:, 0]
    time_span_seconds = time_span_days * 60 * 60 * 24
    cube.data = cube.data * time_span_seconds
    units = str(cube.units)
    assert ('s-1' in units) or ('W' in units), 'input units must be a flux per second'
    if 's-1' in units:    
        cube.units = units.replace('s-1', '')
    elif 'W' in units:
        cube.units = units.replace('W', 'J')
        
    return cube


def get_control_time_constraint(control_cube, ref_cube, time_bounds, branch_time=None):
    """Define the time constraint for control data.

    Args:
      control_cube (iris.cube.Cube): cube for piControl experiment
      ref_cube (iris.cube.Cube): reference cube (e.g. from historical experiment)
      time_bounds (list): selected time periods from reference cube
        (e.g. ['1861-01-01', '2005-12-31'])
      branch_time (float): Override the branch time in the ref_cube attributes

    """

    _check_attributes(ref_cube.attributes, control_cube.attributes)

    iris.coord_categorisation.add_year(control_cube, 'time')
    iris.coord_categorisation.add_year(ref_cube, 'time')

    if not branch_time:
        branch_time = ref_cube.attributes['branch_time']
    
    index = 0
    for bounds in control_cube.coord('time').bounds:
        lower, upper = bounds
        if lower <= float(branch_time) < upper:
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
    control_end_date = str(control_end_year).zfill(4)+'-12-31'

    time_constraint = gio.get_time_constraint([control_start_date, control_end_date])

    control_cube.remove_coord('year')
    ref_cube.remove_coord('year')

    return time_constraint


def is_annual(cube):
    """Check whether the data is annual timescale."""

    year_diffs = np.diff(cube.coord('year').points)
    if year_diffs.min() < 1:
        annual = False
    else:
        annual = True 

    return annual


def fit_polynomial(data, time_axis, order, outlier_threshold):
    """Fit a polynomial to data.

    e.g. order 1 polynomial, polyfit returns [b, a] corresponding to y = a + bx
    
    """

    if outlier_threshold:
        data, outlier_idx = outlier_removal(data, outlier_threshold)
    
    coefficients = np.ma.polyfit(time_axis, data, order)

    return coefficients


def linear_trend(data, time_axis, outlier_threshold):
    """Calculate the linear trend.

    polyfit returns [b, a] corresponding to y = a + bx

    """    

    masked_flag = False

    if type(data) == np.ma.core.MaskedArray:
        if type(data.mask) == np.bool_:
            if data.mask:
                masked_flag = True
        elif data.mask[0]:
            masked_flag = True
            
    if masked_flag:
        return data.fill_value
    else:
        coefficients = fit_polynomial(data, time_axis, 1, outlier_threshold)

        return coefficients[0]


def runmean(data, window_width, overlap=True):
    """Calculate the running mean.
    
    If overlap is false, the windows won't overlap.
    
    """
    
    if overlap:
        runmean_data = np.convolve(data, np.ones((window_width,))/window_width, mode='valid')
    else:
        nchunks = math.ceil(len(data) / window_width)
        split_data = [x for x in np.array_split(data, nchunks) if x.size == window_width]
        runmean_data = np.array(list(map(np.mean, split_data)))

    return runmean_data


def outlier_removal(data, outlier_threshold, replacement_method='missing'):
    """Remove outliers from a timeseries.

    Args:
      data (numpy.array)
      outlier_threshold (float): remove points that deviate from
        the rolling median by greater than this threshold
      replacement_method (str): method for replacing outliers

    """

    assert replacement_method in ['missing', 'mean']

    data_series = pd.Series(data)
    median = data_series.rolling(10).median().fillna(method='bfill').fillna(method='ffill')

    difference = np.abs(data_series - median)
    outlier_bools = difference > outlier_threshold

    if replacement_method == 'missing':
        clean_data = np.ma.where(outlier_bools.values, data.mean(), data)
    else:
        clean_data = np.ma.masked_where(outlier_bools.values, data)
    outlier_idx = list(data_series[outlier_bools].index)

    return clean_data, outlier_idx


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


