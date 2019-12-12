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

def create_df(tcube, scube, wdata, wvar, bcube):
    """Create DataFrame for water mass analysis.

    Args:
      tcube (iris.cube.Cube)            -- temperature cube
      scube (iris.cube.Cube)            -- salinity cube
      wcube (numpy.ma.core.MaskedArray) -- weights data
      wvar (str)                        -- weights variable (areacello or volcello)
      bcube (iris.cube.Cube)            -- basin cube

    """
 
    assert wvar in ['areacello', 'volcello']
    assert bcube.ndim == 2
    assert bcube.data.min() == 11
    assert bcube.data.max() == 17
    coord_names = [coord.name() for coord in tcube.dim_coords]

    tcube = gio.temperature_unit_check(tcube, 'C')
    scube = gio.salinity_unit_check(scube)

    if tcube.coord('latitude').points.ndim == 1:
        lat_pos = coord_names.index('latitude')
        lon_pos = coord_names.index('longitude')
    else:
        lat_pos = lon_pos = [tcube.ndim - 2, tcube.ndim -1] 
    lats = uconv.broadcast_array(tcube.coord('latitude').points, lat_pos, tcube.shape)
    lons = uconv.broadcast_array(tcube.coord('longitude').points, lon_pos, tcube.shape)

    if tcube.ndim == 3:
        bdata = uconv.broadcast_array(bcube.data, [1, 2], tcube.shape)
        if wvar == 'areacello':
            assert coord_names[0] in ['time', 'month', 'year']
            wdata = uconv.broadcast_array(wdata, [1, 2], tcube.shape)
        else:
            assert coord_names[0] not in ['time', 'month', 'year']
    elif tcube.ndim == 4:
        bdata = uconv.broadcast_array(bcube.data, [2, 3], tcube.shape)
        if wvar == 'areacello':
            wdata = uconv.broadcast_array(wdata, [2, 3], tcube.shape)
        else:
            wdata = uconv.broadcast_array(wdata, [1, 3], tcube.shape)
        
    lats = numpy.ma.masked_array(lats, tcube.data.mask)
    lons = numpy.ma.masked_array(lons, tcube.data.mask)
    bdata.mask = tcube.data.mask
    wdata.mask = tcube.data.mask

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
    

def create_flux_df(flux_cube, bin_cube, basin_cube):
    """Create DataFrame for surface flux analysis.

    Args:
      flux_cube (iris.cube.Cube) -- flux cube
      bin_cube (iris.cube.Cube) -- data cube for defining bins
      basin_cube (iris.cube.Cube) -- basin cube

    """

    assert basin_cube.ndim == 2
    assert basin_cube.data.min() == 11
    assert basin_cube.data.max() == 17

    assert flux_cube.ndim == bin_cube.ndim == 3
    coord_names = [coord.name() for coord in flux_cube.dim_coords]

    if 'temperature' in bin_cube.long_name:
        bin_cube = gio.temperature_unit_check(bin_cube, 'C')

    if flux_cube.coord('latitude').points.ndim == 1:
        lat_pos = coord_names.index('latitude')
        lon_pos = coord_names.index('longitude')
    else:
        lat_pos = lon_pos = [flux_cube.ndim - 2, flux_cube.ndim -1] 
    lats = uconv.broadcast_array(flux_cube.coord('latitude').points, lat_pos, flux_cube.shape)
    lons = uconv.broadcast_array(flux_cube.coord('longitude').points, lon_pos, flux_cube.shape)

    basin_data = uconv.broadcast_array(basin_cube.data, [1, 2], flux_cube.shape)
        
    lats = numpy.ma.masked_array(lats, flux_cube.data.mask)
    lons = numpy.ma.masked_array(lons, flux_cube.data.mask)
    basin_data.mask = flux_cube.data.mask
 
    flux_data = flux_cube.data.compressed()
    bin_data = bin_cube.data.compressed()
    basin_data = basin_data.compressed()
    lat_data = lats.compressed()
    lon_data = lons.compressed()

    assert flux_data.shape == bin_data.shape
    assert flux_data.shape == basin_data.shape
    assert flux_data.shape == lat_data.shape
    assert flux_data.shape == lon_data.shape

    df = pandas.DataFrame(index=range(flux_data.shape[0]))
    df['flux'] = flux_data
    df['bin'] = bin_data
    df['basin'] = basin_data
    df['latitude'] = lat_data
    df['longitude'] = lon_data

    return df, bin_cube.units
