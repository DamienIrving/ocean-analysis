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

def create_df(tcube, scube, wcube, bcube):
    """Create DataFrame for water mass analysis.

    Args:
      tcube (iris.cube.Cube) -- temperature cube
      scube (iris.cube.Cube) -- salinity cube
      wcube (iris.cube.Cube) -- weights cube (volcello or areacello)
      bcube (iris.cube.Cube) -- basin cube

    """

    assert bcube.ndim == 2
    assert bcube.data.min() == 11
    assert bcube.data.max() == 17
    coord_names = [coord.name() for coord in tcube.dim_coords]

    tcube = gio.temperature_unit_check(tcube, 'C')
    scube = gio.salinity_unit_check(scube)

    if tcube.ndim == 3:
        lats = uconv.broadcast_array(tcube.coord('latitude').points, [1, 2], tcube.shape)
        lons = uconv.broadcast_array(tcube.coord('longitude').points, [1, 2], tcube.shape)
        bdata = uconv.broadcast_array(bcube.data, [1, 2], tcube.shape)
        if wcube.var_name == 'areacello':
            assert coord_names[0] in ['time', 'month', 'year']
            wdata = uconv.broadcast_array(wcube.data, [1, 2], tcube.shape)
        else:
            assert coord_names[0] not in ['time', 'month', 'year']
            wdata = wcube.data
    elif tcube.ndim == 4:
        lats = uconv.broadcast_array(tcube.coord('latitude').points, [2, 3], tcube.shape)
        lons = uconv.broadcast_array(tcube.coord('longitude').points, [2, 3], tcube.shape)
        bdata = uconv.broadcast_array(bcube.data, [2, 3], tcube.shape)
        if wcube.var_name == 'areacello':
            wdata = uconv.broadcast_array(wcube.data, [2, 3], tcube.shape)
        else:
            wdata = uconv.broadcast_array(wcube.data, [1, 3], tcube.shape)
        
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
