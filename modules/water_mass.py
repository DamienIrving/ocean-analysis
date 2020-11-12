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

def multiply_by_days_in_year_frac(cube, ref_cube=None):
    """Multiply monthly data by corresponding days in year fraction.

    Useful when needing to account for the slightly different number
      of days in each month.

    Output is broadcast to same shape as ref cube
     (assuming cube has no time axis and ref_cube does) 

    """

    assert 'days' in str(ref_cube.coord('time').units)
    time_span_days = ref_cube.coord('time').bounds[:, 1] - ref_cube.coord('time').bounds[:, 0]
    assert len(time_span_days) == 12
    assert time_span_days.max() < 32
    assert time_span_days.min() > 26
    days_in_year = time_span_days.sum()
    assert days_in_year in [365, 366]

    if ref_cube:
        assert ref_cube.ndim in [3, 4]
        if ref_cube.ndim == 3:
            assert cube.var_name == 'areacello'
            data = uconv.broadcast_array(cube.data, [1, 2], ref_cube.shape)
        else:
            data = uconv.broadcast_array(cube.data, [1, 3], ref_cube.shape)
    else:
        data = cube.data

    for month, time_span in enumerate(time_span_days):
        data[month, ::] = data[month, ::] * (time_span / days_in_year)
    numpy.testing.assert_allclose(data.sum(), cube.data.sum(), rtol=1e-03)

    return data


def create_df(tcube, scube, wcube, bcube, sbounds=None,
              multiply_weights_by_days_in_year_frac=False):
    """Create DataFrame for water mass analysis.

    Args:
      tcube (iris.cube.Cube)  -- temperature cube
      scube (iris.cube.Cube)  -- salinity cube
      wcube (iris.cube.Cube)  -- weights cube
      bcube (iris.cube.Cube)  -- basin cube
      sbounds (tuple)         -- salinity bounds
      days_in_month_weights_adjustment (bool) -- multiply
        weights data by (days in month / days in year) 

    """

    assert wcube.var_name in ['areacello', 'volcello']

    if multiply_weights_by_days_in_year_frac:
        wdata = multiply_by_days_in_year_frac(wcube, ref_cube=tcube)
    else:
        wdata = wcube.data

    assert bcube.ndim == 2
    coord_names = [coord.name() for coord in tcube.dim_coords]

    tcube = gio.temperature_unit_check(tcube, 'C', abort=False)
    if sbounds:
        smin, smax = sbounds
        scube = gio.salinity_unit_check(scube, valid_min=smin, valid_max=smax, abort=False)
    else:
        scube = gio.salinity_unit_check(scube, abort=False)

    if tcube.coord('latitude').points.ndim == 1:
        lat_pos = coord_names.index('latitude')
        lon_pos = coord_names.index('longitude')
    else:
        lat_pos = lon_pos = [tcube.ndim - 2, tcube.ndim -1] 
    lats = uconv.broadcast_array(tcube.coord('latitude').points, lat_pos, tcube.shape)
    lons = uconv.broadcast_array(tcube.coord('longitude').points, lon_pos, tcube.shape)

    if tcube.ndim == 3:
        bdata = uconv.broadcast_array(bcube.data, [1, 2], tcube.shape)
        if not tcube.shape == wcube.data.shape:
            if wcube.var_name == 'areacello':
                assert coord_names[0] in ['time', 'month', 'year']
                wdata = uconv.broadcast_array(wdata, [1, 2], tcube.shape)
            else:
                assert coord_names[0] not in ['time', 'month', 'year']
    elif tcube.ndim == 4:
        bdata = uconv.broadcast_array(bcube.data, [2, 3], tcube.shape)
        if not tcube.shape == wdata.shape:
            if wvar == 'areacello':
                wdata = uconv.broadcast_array(wdata, [2, 3], tcube.shape)
            else:
                wdata = uconv.broadcast_array(wdata, [1, 3], tcube.shape)    

    common_mask = tcube.data.mask + scube.data.mask
    scube.data.mask = common_mask
    tcube.data.mask = common_mask
    lats = numpy.ma.masked_array(lats, common_mask)
    lons = numpy.ma.masked_array(lons, common_mask)
    bdata.mask = common_mask
    wdata.mask = common_mask

    sdata = scube.data.compressed()
    tdata = tcube.data.compressed()
    wdata = wdata.compressed()
    bdata = bdata.compressed()
    lat_data = lats.compressed()
    lon_data = lons.compressed()

    assert sdata.shape == tdata.shape
    assert sdata.shape == wdata.shape
    assert sdata.shape == bdata.shape
    assert sdata.shape == lat_data.shape
    assert sdata.shape == lon_data.shape

    df = pandas.DataFrame(index=range(tdata.shape[0]))
    df['temperature'] = tdata
    df['salinity'] = sdata
    df['weight'] = wdata
    df['basin'] = bdata
    df['latitude'] = lat_data
    df['longitude'] = lon_data

    return df, scube.units, tcube.units
    

def create_flux_df(flux_cube, t_cube, s_cube, basin_cube, sbounds=None,
                   multiply_flux_by_days_in_year_frac=False):
    """Create DataFrame for surface flux analysis.

    Args:
      flux_cube (iris.cube.Cube) -- flux cube
      t_cube (iris.cube.Cube) -- temperature cube for defining bins
      s_cube (iris.cube.Cube) -- salinity cube for defining bins
      basin_cube (iris.cube.Cube) -- basin cube
      sbounds (tuple) -- salinity bounds
      multiply_flux_by_days_in_year_frac (bool) -- multiply
        flucx data by (days in month / days in year)

    """

    assert basin_cube.ndim == 2

    coord_names = [coord.name() for coord in flux_cube.dim_coords]

    t_cube = gio.temperature_unit_check(t_cube, 'C')
    if sbounds:
        smin, smax = sbounds
        s_cube = gio.salinity_unit_check(s_cube, valid_min=smin, valid_max=smax, abort=False)
    else:
        s_cube = gio.salinity_unit_check(s_cube, abort=False)

    if flux_cube.coord('latitude').points.ndim == 1:
        lat_pos = coord_names.index('latitude')
        lon_pos = coord_names.index('longitude')
    else:
        lat_pos = lon_pos = [flux_cube.ndim - 2, flux_cube.ndim -1] 
    lats = uconv.broadcast_array(flux_cube.coord('latitude').points, lat_pos, flux_cube.shape)
    lons = uconv.broadcast_array(flux_cube.coord('longitude').points, lon_pos, flux_cube.shape)

    basin_data = uconv.broadcast_array(basin_cube.data, [flux_cube.ndim - 2, flux_cube.ndim -1], flux_cube.shape)

    assert t_cube.data.mask.sum() == s_cube.data.mask.sum(), "Salinity and temperature masks are different"
    if not flux_cube.data.mask.sum() == t_cube.data.mask.sum():
        npoints = flux_cube.data.size
        diff = flux_cube.data.mask.sum() - t_cube.data.mask.sum()
        print(f"Applying common mask... difference of {diff} data points (flux minus bin mask) for {npoints} total data points")
    common_mask = flux_cube.data.mask + t_cube.data.mask
            
    lats = numpy.ma.masked_array(lats, common_mask)
    lons = numpy.ma.masked_array(lons, common_mask)
    basin_data.mask = common_mask
    flux_cube.data.mask = common_mask
    t_cube.data.mask = common_mask
    s_cube.data.mask = common_mask
    
    if multiply_flux_by_days_in_year_frac:
        flux_data = multiply_by_days_in_year_frac(flux_cube)
    else:
        flux_data = flux_cube.data

    flux_data = flux_data.compressed()
    t_data = t_cube.data.compressed()
    s_data = s_cube.data.compressed()
    basin_data = basin_data.compressed()
    lat_data = lats.compressed()
    lon_data = lons.compressed()

    assert flux_data.shape == t_data.shape
    assert flux_data.shape == s_data.shape
    assert flux_data.shape == basin_data.shape
    assert flux_data.shape == lat_data.shape
    assert flux_data.shape == lon_data.shape

    df = pandas.DataFrame(index=range(flux_data.shape[0]))
    df['flux'] = flux_data
    df['temperature'] = t_data
    df['salinity'] = s_data
    df['basin'] = basin_data
    df['latitude'] = lat_data
    df['longitude'] = lon_data

    return df, t_cube.units, s_cube.units
