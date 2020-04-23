"""Collection of convenient functions

Functions:
  adjust_lon_range      -- Express longitude values in desired 360 degree interval
  apply_land_ocean_mask -- Apply a land or ocean mask from an sftlf (land surface fraction) file
  apply_lon_filter      -- Set values outside of specified longitude range to zero
  broadcast_array       -- Broadcast an array to a target shape
  calc_significance     -- Perform significance test
  convert_to_joules     -- Convert units from Watts to Joules
  coordinate_paris      -- Generate lat/lon pairs
  create_basin_array    -- Create an ocean basin array
  dict_filter           -- Filter dictionary according to specified keys
  effective_sample_size -- Calculate the effective sample size (accounting for autocorrelation)
  find_nearest          -- Find the closest array item to value
  find_duplicates       -- Return list of duplicates in a list
  fix_label             -- Fix formatting of an axis label taken from the command line
  get_bounds_list       -- Create a bounds (i.e. pairs) list from an edge list
  get_threshold         -- Turn the user input threshold into a numeric threshold
  hi_lo                 -- Determine the new highest and lowest value.
  list_kwargs           -- List keyword arguments of a function
  mask_marginal_seas    -- Mask the marginal seas
  match_dates           -- Take list of dates and match with the corresponding times 
                           in a detailed time axis
  single2list           -- Check if item is a list, then convert if not
  units_info            -- Make the units taken from a file LaTeX math compliant

"""

import numpy
from scipy import stats
import pdb, re
import inspect
import iris
import statsmodels.api as sm
from statsmodels.tsa.stattools import acf


def adjust_lon_range(lons, radians=True, start=0.0):
    """Express longitude values in a 360 degree (or 2*pi radians) interval.

    Args:
      lons (list/tuple): Longitude axis values (monotonically increasing)
      radians (bool): Specify whether input data are in radians (True) or
        degrees (False). Output will be the same units.
      start (float, optional): Start value for the output interval (add 360 degrees or 2*pi
        radians to get the end point)
    
    """
    
    lons = single2list(lons, numpy_array=True)    
    
    interval360 = 2.0*numpy.pi if radians else 360.0
    end = start + interval360    
    
    less_than_start = numpy.ones([len(lons),])
    while numpy.sum(less_than_start) != 0:
        lons = numpy.where(lons < start, lons + interval360, lons)
        less_than_start = lons < start
    
    more_than_end = numpy.ones([len(lons),])
    while numpy.sum(more_than_end) != 0:
        lons = numpy.where(lons >= end, lons - interval360, lons)
        more_than_end = lons >= end

    return lons


def apply_land_ocean_mask(data_cube, mask_cube, include_only):
    """Apply a land or ocean mask from an sftlf (land surface fraction) file.

    There is no land when cell value == 0

    """

    target_shape = data_cube.shape
    target_ndim = len(target_shape)

    if include_only == 'land':
        mask_array = numpy.where(mask_cube.data > 0.1, False, True)
    elif include_only == 'ocean':
        mask_array = numpy.where(mask_cube.data < 0.1, False, True)

    mask = broadcast_array(mask_array, [target_ndim - 2, target_ndim - 1], target_shape)
    assert mask.shape == target_shape 

    data_cube.data = numpy.ma.asarray(data_cube.data)
    data_cube.data.mask = mask

    return data_cube


def apply_lon_filter(data, lon_bounds):
    """Set values outside of specified longitude range to zero.

    Args:
      data (numpy.ndarray): Array of longitude values.
      lon_bounds (list/tuple): Specified longitude range (min, max)

    """
    
    # Convert to common bounds (0, 360)
    lon_min = adjust_lon_range(lon_bounds[0], radians=False, start=0.0)
    lon_max = adjust_lon_range(lon_bounds[1], radians=False, start=0.0)
    lon_axis = adjust_lon_range(data.getLongitude()[:], radians=False, start=0.0)

    # Make required values zero
    ntimes, nlats, nlons = data.shape
    lon_axis_tiled = numpy.tile(lon_axis, (ntimes, nlats, 1))
    
    new_data = numpy.where(lon_axis_tiled < lon_min, 0.0, data)
    
    return numpy.where(lon_axis_tiled > lon_max, 0.0, new_data)


def broadcast_array(array, axis_index, shape):
    """Broadcast an array to a target shape.
    
    Args:
      array (numpy.ndarray)
      axis_index (int or tuple): Postion in the target shape that the 
        axis/axes of the array corresponds to
          e.g. if array corresponds to (depth, lat, lon) in (time, depth, lat, lon)
          then axis_index = [1, 3]
          e.g. if array corresponds to (lat) in (time, depth, lat, lon)
          then axis_index = 2
      shape (tuple): shape to broadcast to
      
    For a one dimensional array, make start_axis_index = end_axis_index
    
    """

    if type(axis_index) in [float, int]:
        start_axis_index = end_axis_index = axis_index
    else:
        assert len(axis_index) == 2
        start_axis_index, end_axis_index = axis_index
    
    dim = start_axis_index - 1
    while dim >= 0:
        array = array[numpy.newaxis, ...]
        array = numpy.repeat(array, shape[dim], axis=0)
        dim = dim - 1
    
    dim = end_axis_index + 1
    while dim < len(shape):    
        array = array[..., numpy.newaxis]
        array = numpy.repeat(array, shape[dim], axis=-1)
        dim = dim + 1

    return array


def calc_significance(data_subset, data_all, standard_name):
    """Perform significance test.

    One sample t-test, with sample size adjusted for autocorrelation.
    
    Reference:
      Zieba (2010). doi:10.2478/v10178-010-0001-0
    
    """

    from statsmodels.tsa.stattools import acf

    # Data must be three dimensional, with time first
    assert len(data_subset.shape) == 3, "Input data must be 3 dimensional"
    
    # Define autocorrelation function
    n = data_subset.shape[0]
    autocorr_func = numpy.apply_along_axis(acf, 0, data_subset, nlags=n - 2)
    
    # Calculate effective sample size (formula from Zieba2010, eq 12)
    k = numpy.arange(1, n - 1)
    
    r_k_sum = ((n - k[:, None, None]) / float(n)) * autocorr_func[1:] 
    n_eff = float(n) / (1 + 2 * r_k_sum.sum(axis=0))
    
    # Calculate significance
    var_x = data_subset.var(axis=0) / n_eff
    tvals = (data_subset.mean(axis=0) - data_all.mean(axis=0)) / numpy.sqrt(var_x)
    pvals = stats.t.sf(numpy.abs(tvals), n - 1) * 2  # two-sided pvalue = Prob(abs(t)>tt)

    notes = "One sample t-test, with sample size adjusted for autocorrelation (Zieba2010, eq 12)" 
    pval_atts = {'standard_name': standard_name,
                 'long_name': standard_name,
                 'units': ' ',
                 'notes': notes,}

    return pvals, pval_atts


def chunked_collapse_by_time(cube, collapse_dims, agg_method, weights=None):
    """Collapse a spatial dimension by chunking along time axis.

    Args:
      cube (iris.cube.Cube)
      collapse_dim (str): dimension to collapse
      agg_method (iris.analysis.WeightedAggregator): aggregation method
      weights (numpy.ndarray): weights for aggregation

    """

    assert agg_method in [iris.analysis.SUM, iris.analysis.MEAN]

    chunk_list = iris.cube.CubeList([])
    coord_names = [coord.name() for coord in cube.dim_coords]
    start_indexes, step = get_chunks(cube.shape, coord_names, chunk=True)
    for index in start_indexes:
        if type(weights) in [numpy.ndarray, numpy.ma.core.MaskedArray]:
            chunk = cube[index:index+step, ...].collapsed(collapse_dims, agg_method, weights=weights[index:index+step, ...])
        else:
            chunk = cube[index:index+step, ...].collapsed(collapse_dims, agg_method)
        chunk_list.append(chunk)

    collapsed_cube = chunk_list.concatenate()[0]

    return collapsed_cube


def effective_sample_size(data, n_orig):
    """Calculate the effective sample size, accounting for autcorrelation.

     Method from Zieba2010, equation 12
     https://content.sciendo.com/view/journals/mms/17/1/article-p3.xml

     """

    autocorr_func = acf(data, nlags=n_orig-2)
    
    k = numpy.arange(1, n_orig - 1)
    
    r_k_sum = ((n_orig - k[:]) / float(n_orig)) * autocorr_func[1:] 
    n_eff = float(n_orig) / (1 + 2 * r_k_sum.sum())
    
    return n_eff


def flux_to_magnitude(cube):
    """Convert units from a flux to magnitude.

    Caters for s-1 or Watts (i.e. J s-1).

    """
    orig_units = str(cube.units)
    assert ('W' in orig_units) or ('s-1' in orig_units)

    dim_coord_names = [coord.name() for coord in cube.dim_coords]
    if 'year' in dim_coord_names:
        assert 'time' not in dim_coord_names
        time_span_days = [365.25] * cube.coord('year').shape[0]
        time_span_days = numpy.array(time_span_days)
    else:
        assert 'days' in str(cube.coord('time').units)
        time_span_days = cube.coord('time').bounds[:, 1] - cube.coord('time').bounds[:, 0]

    time_span_seconds = time_span_days * 60 * 60 * 24    
    cube.data = cube.data * broadcast_array(time_span_seconds, 0, cube.shape)

    if 'W' in orig_units:
        cube.units = orig_units.replace('W', 'J')
    else:
        cube.units = orig_units.replace('s-1', '')
    
    return cube


def coordinate_pairs(lat_axis, lon_axis):
    """Take the latitude and longitude values from given grid axes
    and produce a flattened lat and lon array, with element-wise pairs 
    corresponding to every grid point."""
    
    lon_mesh, lat_mesh = numpy.meshgrid(lon_axis, lat_axis)  # This is the correct order
    
    return lat_mesh.flatten(), lon_mesh.flatten()


def create_basin_array(cube):
    """Create an ocean basin array.

    For similarity with the CMIP5 basin file, in the output:
      Atlantic Ocean = 2
      Pacific Ocean = 3
      Indian Ocean = 5
      (land = 0)

    FIXME: When applied to CMIP5 data, some of the marginal seas might
      not be masked

    """

    pacific_bounds = [147, 294]
    indian_bounds = [23, 147]

    lat_axis = cube.coord('latitude').points
    lon_axis = adjust_lon_range(cube.coord('longitude').points, radians=False)

    coord_names = [coord.name() for coord in cube.dim_coords]
    lat_index = coord_names.index('latitude')
    lon_index = coord_names.index('longitude')

    lat_array = broadcast_array(lat_axis, lat_index, cube.shape)
    lon_array = broadcast_array(lon_axis, lon_index, cube.shape)

    basin_array = numpy.ones(cube.shape) * 2
    basin_array = numpy.where((lon_array >= pacific_bounds[0]) & (lon_array <= pacific_bounds[1]), 3, basin_array)
    basin_array = numpy.where((lon_array >= indian_bounds[0]) & (lon_array <= indian_bounds[1]), 5, basin_array)

    basin_array = numpy.where((basin_array == 3) & (lon_array >= 279) & (lat_array >= 10), 2, basin_array)
    basin_array = numpy.where((basin_array == 5) & (lon_array >= 121) & (lat_array >= 0), 3, basin_array)

    basin_array = numpy.where((basin_array == 5) & (lat_array >= 25), 0, basin_array)

    return basin_array


def dict_filter(indict, key_list):
    """Filter dictionary according to specified keys."""
    
    return dict((key, value) for key, value in list(indict.items()) if key in key_list)


def find_duplicates(inlist):
    """Return list of duplicates in a list."""
    
    D = defaultdict(list)
    for i,item in enumerate(mylist):
        D[item].append(i)
    D = {k:v for k,v in list(D.items()) if len(v)>1}
    
    return D


def find_nearest(array, value, index=False):
    """Find the closest array item to value.

    index: return index instead of value

    """
    
    idx = (numpy.abs(numpy.array(array) - value)).argmin()
    error = array[idx] - value
    if index:
        return idx, error
    else:
        return array[idx], error


def fix_label(label):
    """Fix axis label taken from the command line."""

    replace_dict = {'_': ' ',
                    'degE': '$^{\circ}$E',
                    'ms-1': '$m s^{-1}$',
                    'm.s-1': '$m s^{-1}$',
                    'Wm-2': '$W m^{-2}$',
                    '1000000 m2.s-1': '$10^6$m$^2$s$^{-1}$'
                   } 

    for value, replacement in list(replace_dict.items()):
        label = label.replace(value, replacement)

    return label 


def get_bounds_list(edges):
    """Create a bounds (i.e. pairs) list from an edge list"""

    bounds_list = []
    for i in range(len(edges) - 1):
        interval = [edges[i], edges[i+1]]
        bounds_list.append(interval)

    return numpy.array(bounds_list)
    

def get_chunks(cube_shape, coord_names, chunk=True, step=2):
    """Provide details for chunking along the time axis.

    The chunk option can be used to just do one single chunk.

    """

    ntimes = cube_shape[0]

    if chunk:
        assert coord_names[0] == 'time'

        remainder = ntimes % step
        while remainder == 1:
            step = step + 1
            remainder = ntimes % step

        start_indexes = range(0, ntimes, step)
    else:
        start_indexes = [0]
        step = ntimes

    return start_indexes, step


def get_threshold(data, threshold_str, axis=None):
    """Turn the user input threshold into a numeric threshold."""
    
    if 'pct' in threshold_str:
        value = float(re.sub('pct', '', threshold_str))
        threshold_float = numpy.percentile(data, value, axis=axis)
    else:
        threshold_float = float(threshold_str)
    
    return threshold_float


def hi_lo(data_series, current_max, current_min):
    """Determine the new highest and lowest value."""
    
    try:
        highest = numpy.max(data_series)
    except:
        highest = max(data_series)
    
    if highest > current_max:
        new_max = highest
    else:
        new_max = current_max
    
    try:    
        lowest = numpy.min(data_series)
    except:
        lowest = min(data_series)
    
    if lowest < current_min:
        new_min = lowest
    else:
        new_min = current_min
    
    return new_max, new_min


def list_kwargs(func):
    """List keyword arguments of a function."""
    
    details = inspect.getargspec(func)
    nopt = len(details.defaults)
    
    return details.args[-nopt:]


def mask_marginal_seas(data_cube, basin_cube):
    """Mask marginal seas.

    The marginal seas all have a basin value > 5.

    """

    data_cube.data = numpy.ma.asarray(data_cube.data)

    ndim = data_cube.ndim
    basin_array = broadcast_array(basin_cube.data, [ndim - 2, ndim - 1], data_cube.shape)

    data_cube.data.mask = numpy.where((data_cube.data.mask == False) & (basin_array <= 5), False, True)

    return data_cube


def mask_unwanted_seas(data_cube, basin_cube, basins_to_keep):
    """Mask unwanted seas.

    Args:
      data_cube (iris.cube.Cube)
      basin_cube (iris.cube.Cube): CMIP5 basin file
      basins_to_keep (list): list of numbers corresponding to basins to keep

    Basin names and corresponding number in basin files
      0 global_land
      1 southern_ocean
      2 atlantic_ocean
      3 pacific_ocean
      4 arctic_ocean
      5 indian_ocean
      6 mediterranean_sea
      7 black_sea
      8 hudson_bay

    """

    ndim = data_cube.ndim
    basin_array = broadcast_array(basin_cube.data, [ndim - 2, ndim - 1], data_cube.shape)

    data_cube.data.mask = numpy.where((data_cube.data.mask == False) & numpy.isin(basin_array, basins_to_keep), False, True)

    return data_cube


def match_dates(datetimes, datetime_axis):
    """Take list of datetimes and match with the corresponding datetimes in a time axis.
 
    Args:   
      datetimes (list/tuple)
      datetime_axis (list/tuple)
        
    """

    dates = list(map(split_dt, datetimes))
    date_axis = list(map(split_dt, datetime_axis[:])) 
    
    match_datetimes = []
    miss_datetimes = [] 

    for i in range(0, len(datetime_axis)):
        if date_axis[i] in dates:
            match_datetimes.append(datetime_axis[i])
        else:
            miss_datetimes.append(datetime_axis[i])    

    return match_datetimes, miss_datetimes


def split_dt(dt):
    """Split a numpy.datetime64 value so as to just keep the date part."""

    return str(dt).split('T')[0]


def single2list(item, numpy_array=False):
    """Check if item is a list, then convert if not."""
    
    if type(item) == list or type(item) == tuple or type(item) == numpy.ndarray:
        output = item 
    elif type(item) == str:
        output = [item,]
    else:
        try:
            test = len(item)
        except TypeError:
            output = [item,]

    if numpy_array and not isinstance(output, numpy.ndarray):
        return numpy.array(output)
    else:
        return output


def units_info(units):
    """Make the units taken from a file LaTeX math compliant.
    
    This function particularly deals with powers:
      e.g. 10^22 J
    """

    components = units.split()

    exponent = None
    pieces = []
    for component in components:
        index = component.find('^')
        if not index == -1:
            exponent = component[index + 1:]
            component = component[:index + 1] + '{' + component[index + 1:]
            component = component + '}'

        index = component.find('-')
        if not index == -1:
            component = component[:index] + '^{' + component[index:]
            component = component + '}'
        
        pieces.append(component)

    tex_units = ''
    for piece in pieces[:-1]:
        tex_units = tex_units + piece + ' \;'
    tex_units = tex_units + ' ' + pieces[-1]            
    tex_units = '$' + tex_units + '$'

    return tex_units, exponent

