"""Collection of functions for water mass analysis.

Functions:
  create_df  -- Create data frame for water mass analysis 

"""

# Import general modules

import pdb, os, sys
import numpy
import pandas
import logging
logging.basicConfig(level=logging.DEBUG)

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
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')

# Define functions

def multiply_by_days_in_year_frac(data, time_coord):
    """Multiply monthly data by corresponding days in year fraction.

    Useful when needing to account for the slightly different number
      of days in each month.

    """

    assert 'days' in str(time_coord.units)
    time_span_days = time_coord.bounds[:, 1] - time_coord.bounds[:, 0]
    assert len(time_span_days) == 12
    assert time_span_days.max() < 32
    assert time_span_days.min() > 26
    days_in_year = time_span_days.sum()
    assert days_in_year > 359
    assert days_in_year < 367

    for month, time_span in enumerate(time_span_days):
        data[month, ::] = data[month, ::] * (time_span / days_in_year)

    return data


def broadcast_data(cube, target_shape):
    """Broadcast a static cube (e.g. basin, area, volume)."""

    target_ndim = len(target_shape)
    if not cube.ndim == target_ndim:
        diff = target_ndim - cube.ndim
        assert target_shape[diff:] == cube.shape
        data = uconv.broadcast_array(cube.data, [diff, target_ndim - 1], target_shape)
    else:
        data = cube.data

    assert target_shape == data.shape

    return data


def create_df(w_cube, t_cube, s_cube, b_cube,
              s_bounds=None, pct_cube=None,
              multiply_weights_by_days_in_year_frac=False):
    """Create DataFrame for water mass analysis.

    Args:
      w_cube (iris.cube.Cube)  -- weights cube
      t_cube (iris.cube.Cube)  -- temperature cube
      s_cube (iris.cube.Cube)  -- salinity cube
      b_cube (iris.cube.Cube)  -- basin cube
      pct_cube (iris.cube.Cube)  -- percentile weights cube
                                    (i.e. area or volume)
      s_bounds (tuple)         -- salinity bounds
      days_in_month_weights_adjustment (bool) -- multiply
        weights data by (days in month / days in year) 

    """

    t_ndim = t_cube.ndim
    w_data = broadcast_data(w_cube, t_cube.shape)
    b_data = broadcast_data(b_cube, t_cube.shape)
    if pct_cube:
        pct_data = broadcast_data(pct_cube, t_cube.shape)

    if multiply_weights_by_days_in_year_frac:
        w_data = multiply_by_days_in_year_frac(w_data, t_cube.coord('time'))

    t_cube = gio.temperature_unit_check(t_cube, 'C', abort=False)
    if s_bounds:
        s_min, s_max = s_bounds
        s_cube = gio.salinity_unit_check(s_cube, valid_min=s_min, valid_max=s_max, abort=False)
    else:
        s_cube = gio.salinity_unit_check(s_cube, abort=False)

    coord_names = [coord.name() for coord in t_cube.dim_coords]
    if t_cube.coord('latitude').points.ndim == 1:
        lat_pos = coord_names.index('latitude')
        lon_pos = coord_names.index('longitude')
    else:
        lat_pos = lon_pos = [t_ndim - 2, t_ndim -1] 
    lats = uconv.broadcast_array(t_cube.coord('latitude').points, lat_pos, t_cube.shape)
    lons = uconv.broadcast_array(t_cube.coord('longitude').points, lon_pos, t_cube.shape)
   
    t_masked_points = t_cube.data.mask.sum()
    s_masked_points = s_cube.data.mask.sum()
    w_masked_points = w_data.mask.sum()
    if not t_masked_points == s_masked_points: 
        logging.info(f"salinity ({s_masked_points} points) and temperature ({t_masked_points}) masks are different")
    if not w_masked_points == s_masked_points:
         logging.info(f"salinity ({s_masked_points} points) and weights data ({w_masked_points}) masks are different")
    common_mask = w_data.mask + t_cube.data.mask + s_cube.data.mask
    if pct_cube:
        pct_masked_points = pct_data.mask.sum()
        if not pct_masked_points == s_masked_points: 
            logging.info(f"salinity ({s_masked_points} points) and percentile weight ({pct_masked_points}) masks are different")
        common_mask = common_mask + pct_data.mask
        pct_data.mask = common_mask
    t_cube.data.mask = common_mask
    s_cube.data.mask = common_mask
    lats = numpy.ma.masked_array(lats, common_mask)
    lons = numpy.ma.masked_array(lons, common_mask)
    b_data.mask = common_mask
    w_data.mask = common_mask

    t_data = t_cube.data.compressed()
    s_data = s_cube.data.compressed()
    w_data = w_data.compressed()
    b_data = b_data.compressed()
    lat_data = lats.compressed()
    lon_data = lons.compressed()
    if pct_cube:
        pct_data = pct_data.compressed()

    assert s_data.shape == t_data.shape
    assert s_data.shape == w_data.shape
    assert s_data.shape == b_data.shape
    assert s_data.shape == lat_data.shape
    assert s_data.shape == lon_data.shape
    if pct_cube:
        assert s_data.shape == pct_data.shape

    df = pandas.DataFrame(index=range(t_data.shape[0]))
    df['temperature'] = t_data
    df['salinity'] = s_data
    df['weight'] = w_data
    df['basin'] = b_data
    df['latitude'] = lat_data
    df['longitude'] = lon_data
    if pct_cube:
        df['percentile_weights'] = pct_data

    return df, s_cube.units, t_cube.units
    
