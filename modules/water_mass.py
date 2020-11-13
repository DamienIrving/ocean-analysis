"""Collection of functions for water mass analysis.

Functions:
  create_df  -- Create data frame for water mass analysis 

"""

# Import general modules

import pdb, os, sys
import numpy
import pandas

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
    assert days_in_year in [365, 366]

    for month, time_span in enumerate(time_span_days):
        data[month, ::] = data[month, ::] * (time_span / days_in_year)

    return data


def create_df(w_cube, t_cube, s_cube, b_cube, s_bounds=None,
              multiply_weights_by_days_in_year_frac=False):
    """Create DataFrame for water mass analysis.

    Args:
      w_cube (iris.cube.Cube)  -- weights cube
      t_cube (iris.cube.Cube)  -- temperature cube
      s_cube (iris.cube.Cube)  -- salinity cube
      b_cube (iris.cube.Cube)  -- basin cube
      s_bounds (tuple)         -- salinity bounds
      days_in_month_weights_adjustment (bool) -- multiply
        weights data by (days in month / days in year) 

    """

    t_ndim = t_cube.ndim
    
    w_ndim = w_cube.ndim
    if not w_ndim == t_ndim:
        diff = t_ndim - w_ndim
        assert t_cube.shape[diff:] == w_cube.shape
        w_data = uconv.broadcast_array(w_cube.data, [t_ndim - w_ndim, t_ndim - 1], t_cube.shape)
    else:
        w_data = w_cube.data

    b_ndim = b_cube.ndim
    if not b_ndim == t_ndim:
        diff = t_ndim - b_ndim
        assert t_cube.shape[diff:] == b_cube.shape
        b_data = uconv.broadcast_array(b_cube.data, [t_ndim - b_ndim, t_ndim - 1], t_cube.shape)
    else:
        b_data = b_cube.data

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
   
    #common_mask = t_cube.data.mask + s_cube.data.mask
    assert t_cube.data.mask.sum() == s_cube.data.mask.sum(), "Salinity and temperature masks are different"
    if not w_data.mask.sum() == t_cube.data.mask.sum():
        npoints = w_data.size
        diff = w_data.mask.sum() - t_cube.data.mask.sum()
        print(f"Applying common mask... difference of {diff} data points (weights minus bin mask) for {npoints} total data points")
    common_mask = w_data.mask + t_cube.data.mask
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

    assert s_data.shape == t_data.shape
    assert s_data.shape == w_data.shape
    assert s_data.shape == b_data.shape
    assert s_data.shape == lat_data.shape
    assert s_data.shape == lon_data.shape

    df = pandas.DataFrame(index=range(t_data.shape[0]))
    df['temperature'] = t_data
    df['salinity'] = s_data
    df['weight'] = w_data
    df['basin'] = b_data
    df['latitude'] = lat_data
    df['longitude'] = lon_data

    return df, s_cube.units, t_cube.units
    
