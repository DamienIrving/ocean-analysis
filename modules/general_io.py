"""
Collection of commonly used functions for general file input and output.

Functions:
  check_iris_var            -- Check if a variable is in the list of iris standard names
  check_time_units          -- Check time axis units
  check_wfo_sign            -- Check that the wfo variable has correct sign
  check_global_ocean_area   -- Check that the global ocean area is within acceptable bounds
  check_global_ocean_volume -- Check that the global ocean volume is within acceptable bounds
  check_xarrayDataset       -- Check xarray.Dataset for data format compliance
  combine_files             -- Create an iris cube from multiple input files
  create_outdir             -- Create the output directory if it doesn't exist already
  get_cmip5_file_details    -- Extract details from a CMIP5 filename
  get_ocean_weights         -- Read the volcello or areacello weights file and sainity check
  get_subset_kwargs         -- Get keyword arguments for xarray subsetting
  get_time_constraint       -- Get the time constraint used for reading an iris cube 
  get_timescale             -- Get the timescale
  get_timestamp             -- Return a time stamp that includes the command line entry
  iris_vertical_constraint  -- Define vertical constraint for iris cube loading.
  read_dates                -- Read in a list of dates
  set_dim_atts              -- Set dimension attributes
  set_global_atts           -- Update the global attributes of an xarray.DataArray
  set_outfile_date          -- Take an outfile name and replace existing date with new one
  standard_datetime         -- Convert any arbitrary date/time to standard format: YYYY-MM-DD
  two_floats                -- Read floats lile -5e20 from the command line
  update_history_att        -- Update the global history attribute of an xarray.DataArray
  vertical_bounds_text      -- Geneate text describing the vertical bounds of a data selection
  write_dates               -- Write a list of dates
  write_metadata            -- Write a metadata output file

"""

# Import general Python modules

import os, sys, pdb
import argparse
import datetime, numpy
from dateutil import parser
from collections import defaultdict
import re
import iris
from iris.experimental.equalise_cubes import equalise_attributes
import cftime
import cf_units
import xarray as xr
import numpy

# Import my modules

try:
    from git import Repo 
    cwd = os.getcwd()
    repo_dir = '/'
    for directory in cwd.split('/')[1:]:
        repo_dir = os.path.join(repo_dir, directory)
        if directory == 'ocean-analysis':
            break
    try:
        MODULE_HASH = Repo(repo_dir).head.commit.hexsha
    except AttributeError: # Older versions of gitpython work differently
        MODULE_HASH = Repo(repo_dir).commits()[0].id
except ImportError:
    MODULE_HASH = 'unknown'

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)
try:
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

#[south_lat, north_lat, west_lon, east_lon]
regions = {'asl': [-75, -60, 180, 310],
           'aus': [-45, -10, 110, 160],
           'ausnz': [-50, 0, 100, 185],
           'emia': [-10, 10, 165, 220],
           'emib': [-15, 5, 250, 290],
           'emic': [-10, 20, 125, 145],
           'eqpacific': [-30, 30, 120, 280],
           'nino1': [-10, -5, 270, 280],
           'nino2': [-5, 0, 270, 280],
           'nino12': [-10, 0, 270, 280],
           'nino3': [-5, 5, 210, 270],
           'nino34': [-5, 5, 190, 240],
           'nino4': [-5, 5, 160, 210],
           'point': [-59.25, -59.25, 255, 255],
           'sh': [-90, 0, 0, 360],
           'shextropics15': [-90, -15, 0, 360],
           'shextropics20': [-90, -20, 0, 360],
           'shextropics30': [-90, -30, 0, 360],
           'small': [-5, 0, 10, 15],
           'tropics': [-30, 30, 0, 360],
           'glatt': [20, 80, -180, 180],
           'nonpolar70': [-70, 70, 0, 360],
           'nonpolar80': [-80, 80, 0, 360],
           'sh-psa': [-90, 0, 90, 450],
           'sh-psa-extra': [-90, 30, 90, 450],
           'world-dateline': [-90, 90, 0, 360],
           'world-dateline-duplicate360': [-90, 90, 0, 360],
           'world-greenwich': [-90, 90, -180, 180],
           'world-psa': [-90, 90, 90, 450],
           'zw31': [-50, -45, 45, 60],
           'zw32': [-50, -45, 161, 171],
           'zw33': [-50, -45, 279, 289],
           }


var_names = {'precipitation_flux': 'precipitation',
             'water_evaporation_flux': 'evaporation',
             'surface_downward_heat_flux_in_sea_water': 'surface downward heat flux',
             'precipitation_minus_evaporation_flux': 'P-E',
             'northward_ocean_heat_transport': 'northward ocean heat transport',
             'ocean_heat_content': 'ocean heat content',
             'surface_upward_latent_heat_flux': 'latent heat flux',
             'surface_upward_sensible_heat_flux': 'sensible heat flux',
             'surface_downwelling_shortwave_flux_in_air': 'downwelling shortwave flux',
             'surface_upwelling_shortwave_flux_in_air': 'upwelling shortwave flux',
             'surface_downwelling_longwave_flux_in_air': 'downwelling longwave flux',
             'surface_upwelling_longwave_flux_in_air': 'upwelling longwave flux',
             'Downward_Heat_Flux_at_Sea_Water_Surface_nh_sum_minus_sh_sum': 'interhemispheric difference in surface downward heat flux (NH minus SH)',
             'surface_downward_eastward_stress': 'eastward surface wind stress'
             }


history = []

def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    if 'history' in cube.attributes:
        history.append(cube.attributes['history']) 


def check_evap_sign(cube):
    """Check that the evaporation variable has correct sign."""

    wrong_sign_models = ['EC-Earth3', 'EC-Earth3-Veg']

    assert cube.standard_name in ['water_evaporation_flux', 'water_evapotranspiration_flux']
    try:
        model = cube.attributes['source_id']
    except KeyError:
        model = cube.attributes['model_id']
                  
    if model in wrong_sign_models:
        cube.data = cube.data * -1

    return cube


def check_iris_var(var, alternate_names=False):
    """Check if variable is in the list of iris standard variables.

    If not, replace underscores with spaces (my convention is to give
      an appropriate long_name (with spaces) if not an iris standard name.

    """ 

    if not var in list(iris.std_names.STD_NAMES.keys()):
        if var in ['cp*rivermix*rho_dzt*temp', 'vert diffusion of heat due to diff_cbt']:
           pass
        else:
            var = var.replace('_', ' ')

    wrong_names = {'atmosphere_mass_content_of_water_vapor': 'atmosphere_water_vapor_content',
                   'water_evapotranspiration_flux': 'water_evaporation_flux',
                   'atmosphere_mass_content_of_cloud_condensed_water': 'atmosphere_cloud_condensed_water_content'}

    if alternate_names and (var in wrong_names):
        var = wrong_names[var]

    return var


def check_global_surface_area(global_area):
    """Check that the global surface area is within acceptable bounds."""

    assert global_area > 4.9e+14, "Global surface area is %s. Typical value is 5.1e+14 m2" %(str(global_area))
    assert global_area < 5.3e+14, "Global surface area is %s. Typical value is 5.1e+14 m2" %(str(global_area))


def check_global_ocean_area(global_area):
    """Check that the global ocean area is within acceptable bounds.

    The 7.0e+14 allows for no ocean mask.

    """

    assert global_area > 3.4e+14, "Global ocean area is %s. Typical value (ocean masked) is 3.6e+14 m2" %(str(global_area))
    assert global_area < 7.0e+14, "Global ocean area is %s. Typical value (ocean masked) is 3.6e+14 m2" %(str(global_area))


def check_global_ocean_volume(global_volume):
    """Check that the global ocean volume is within acceptable bounds."""

    assert global_volume > 1.2e+18, "Global ocean volume is %s. Typical value is 1.3e+18 m3" %(str(global_volume))
    assert global_volume < 1.45e+18, "Global ocean volume is %s. Typical value is 1.3e+18 m3" %(str(global_volume))


def check_time_units(cube, new_calendar=None):
    """Check time axis units."""

    time_units = str(cube.coord('time').units)
    calendar = new_calendar if new_calendar else cube.coord('time').units.calendar
    
    fixed_time_units = fix_time_descriptor(time_units)
    altered_units_flag = fixed_time_units != time_units
    time_units = fixed_time_units
    
    if altered_units_flag or new_calendar:
        cube.coord('time').units = cf_units.Unit(time_units, calendar=calendar)

    return cube


def check_hfds_sign(cube):
    """Check that the hfds variable has correct sign."""

    wrong_sign_models = ['SAM0-UNICON']

    assert cube.standard_name == 'surface_downward_heat_flux_in_sea_water'
    try:
        model = cube.attributes['source_id']
    except KeyError:
        model = cube.attributes['model_id']
                  
    if model in wrong_sign_models:
        cube.data = cube.data * -1
        print('CHANGING HFDS SIGN')

    return cube


def check_wfo_sign(cube):
    """Check that the wfo variable has correct sign."""

    wrong_sign_models = ['CMCC-CM',
                         'CNRM-CM6-1', 'CNRM-ESM2-1',
                         'EC-Earth3', 'EC-Earth3-Veg',
                         'FGOALS-f3-L',
                         'GISS-E2-1-G', 'GISS-E2-1-G-CC', 
                         'IPSL-CM5A-LR', 'IPSL-CM6A-LR',
                         'IPSL-CM5A-MR', 'IPSL-CM5B-LR',
                         'MIROC-ESM', 'MIROC-ESM-CHEM']

    assert cube.standard_name == 'water_flux_into_sea_water'
    try:
        model = cube.attributes['source_id']
    except KeyError:
        model = cube.attributes['model_id']
                  
    if model in wrong_sign_models:
        cube.data = cube.data * -1
        print('CHANGING WFO SIGN')

    return cube


def check_xarrayDataset(dset, var_list):
    """Check xarray.Dataset for data format compliance.
    
    Args:
      dset (xarray.Dataset)
      vars (list of str): Variables to check
    
    """
    
    var_list = uconv.single2list(var_list)
    for var in var_list:
    
        # Variable attributes
        assert 'units' in list(dset[var].attrs.keys()), \
        "variable must have a units attribute"
    
        assert 'long_name' in list(dset[var].attrs.keys()), \
        "variable must have a long_name attribute"
    
        assert len(dset[var].attrs['long_name'].split(' ')) == 1, \
        "long_name must have no spaces" # Iris plotting library requires this
    
        # Axis names and order
        accepted_dims = ['time', 'latitude', 'longitude', 'level']
        for dim_name in dset[var].dims:
            assert dim_name in accepted_dims, \
            "accepted dimension names are %s" %(" ".join(accepted_dims))

        correct_order = []
        for dim_name in accepted_dims:
            if dim_name in dset[var].dims:
                correct_order.append(dim_name)
    
        if dset[var].dims != tuple(correct_order):
            print('swapping dimension order...')
            dset[var] = dset[var].transpose(*correct_order)
        
    # Axis values 
    if 'latitude' in list(dset.keys()):
        lat_values = dset['latitude'].values
        
        assert lat_values[0] <= lat_values[-1], \
        'Latitude axis must be in ascending order'
        
    if 'longitude' in list(dset.keys()):
        lon_values = dset['longitude'].values
    
        assert lon_values[0] <= lon_values[-1], \
        'Longitude axis must be in ascending order'
    
        assert 0 <= lon_values.max() <= 360, \
        'Longitude axis must be 0 to 360E'

        assert 0 <= lon_values.min() <= 360, \
        'Longitude axis must be 0 to 360E'


def clean_coordinate_attributes(cube):
    """Fix common issues with coordinate attributes."""

    dim_coord_names = [coord.name() for coord in cube.dim_coords]
    aux_coord_names = [coord.name() for coord in cube.aux_coords]
    
    if 'time' in dim_coord_names:
        cube.coord('time').attributes = {}
    
    if 'year' in aux_coord_names:
        cube.coord('year').attributes = {}
    
    for coord_name in aux_coord_names:
         if 'history' in cube.coord(coord_name).attributes:
            del cube.coord(coord_name).attributes['history']
    
    return cube


def check_data(cube):
    """Check (and fix if needed) the data in an iris cube."""

    try:
        model = cube.attributes['source_id']
    except KeyError:
        model = cube.attributes['model_id']

    if model in ['MRI-ESM2-0']:
        cube.data = numpy.ma.masked_invalid(cube.data)

    if cube.standard_name == 'water_flux_into_sea_water':
        cube = check_wfo_sign(cube)
    
    if cube.standard_name == 'surface_downward_heat_flux_in_sea_water':
        cube = check_hfds_sign(cube)

    if cube.standard_name in ['water_evaporation_flux', 'water_evapotranspiration_flux']:
        cube = check_evap_sign(cube)

    if cube.long_name == 'Ocean Grid-Cell Area':
        global_area = cube.data.sum()
        check_global_ocean_area(global_area)
    
    if cube.standard_name == 'ocean_volume':
        global_volume = cube.data.sum()
        check_global_ocean_volume(global_volume)
    
    if cube.standard_name in ['sea_water_salinity', 'sea_surface_salinity']:
        cube = salinity_unit_check(cube)
    
    return cube


def combine_cubes(cube_list, new_calendar=None, data_checks=False):
    """Combine multiple iris cubes."""

    equalise_attributes(cube_list)
    iris.util.unify_time_units(cube_list)
    ref_dtype = cube_list[0].dtype
    for cube in cube_list:
        cube = clean_coordinate_attributes(cube)
        if cube.dtype != ref_dtype:
            cube.data = cube.data.astype(ref_dtype)
        if data_checks:
            cube = check_data(cube)
    cube = cube_list.concatenate_cube()
    cube = iris.util.squeeze(cube)

    coord_names = [coord.name() for coord in cube.dim_coords]
    if 'time' in coord_names:
        cube = check_time_units(cube, new_calendar=new_calendar)

    return cube


def combine_files(files, var, new_calendar=None, checks=False):
    """Create an iris cube from multiple input files."""

    files = uconv.single2list(files)

    try:
        cube_list = iris.load(files, check_iris_var(var), callback=save_history)
    except iris.exceptions.ConstraintMismatchError:
        cube_list = []

    if not cube_list: 
        cube_list = iris.load(files, check_iris_var(var, alternate_names=True), callback=save_history)
    
    if (len(cube_list) < len(files)) and check_iris_var(var, alternate_names=True) == 'water_evaporation_flux':
        cube_list = iris.load(files, callback=save_history)
        assert len(cube_list) == len(files)
        for cube in cube_list:
            cube.standard_name = 'water_evaporation_flux'
            cube.long_name = 'Evaporation'

    cube = combine_cubes(cube_list, new_calendar=new_calendar, data_checks=checks)

    return cube, history


def create_outdir(outfile):
    """Create the output file directory if it doesn't exist already.

    Expected input is the entire ouput file name and path:
       /path/to/file/outfile.nc

    """

    outfile_components = outfile.split('/')
    outfile_components.pop(-1)
    outdir = "/".join(outfile_components)
    mkdir_command = 'mkdir -p ' + outdir

    print(mkdir_command)
    os.system(mkdir_command)


def fix_time_descriptor(time_unit_text):
    """Fix common problems with netCDF time descriptor if necessary.

    Iris requires "days since YYYY-MM-DD".

    Known issues in CMIP data files:
      Not including the day (e.g. days since 0001-01)
      Including hours, minutes and seconds 
        e.g. days since 1850-01-01-00-00-00
        e.g. days since 1850-01-01 00:00:00
        e.g. days since 1850-01-01 0:0:0.0
      No zero padding (e.g. days since 4150-1-1)
    """

    assert 'days since' in time_unit_text

    missing_day_pattern = 'days since ([0-9]{4})-([0-9]{1,2})$'
    if bool(re.search(missing_day_pattern, time_unit_text)):
        time_unit_text = time_unit_text + '-01'

    time_unit_text = time_unit_text[0:21]  # gets rid of hours, minutes, seconds

    year, month, day = re.findall("(\d{1,4})-(\d{1,2})-(\d{1,2})", time_unit_text)[0]
    time_unit_text = f"days since {year:0>4}-{month:0>2}-{day:0>2}"

    valid_pattern = 'days since ([0-9]{4})-([0-9]{2})-([0-9]{2})$'
    assert bool(re.search(valid_pattern, time_unit_text)), 'Time units not in days since YYYY-MM-DD format'

    return time_unit_text


def get_cmip5_file_details(cube):
    """Extract model, experiment and run information from CMIP5 file attributes.

    Args:
      cube (iris.cube.Cube): Data cube containing standard CMIP5 global attributes

    """

    model = cube.attributes['model_id']
    experiment = cube.attributes['experiment_id']

    physics = cube.attributes['physics_version']
    realization = cube.attributes['realization']
    initialization = cube.attributes['initialization_method']

    run = 'r'+str(realization)+'i'+str(initialization)+'p'+str(physics)    

    # To get same information from a file name...
    #name = filename.split('/')[-1]
    #components = name.split('_')
    #model, experiment, run = components[2:5]

    return model, experiment, run


def get_ocean_weights(infile):
    """Read the volcello or areacello weights file and sainity check.

    This function is needed because for some reason iris can't read some volcello files.

    """

    try:
        cube = iris.load_cube(infile)
    except iris.exceptions.ConstraintMismatchError:
        dset = xr.open_dataset(infile)
        try:
            cube = dset['volcello'].to_iris()
        except KeyError:
            cube = dset['areacello'].to_iris()
        cube.attributes = dset.attrs

    assert cube.var_name in ['areacello', 'volcello']
    if cube.var_name == 'volcello':
        check_global_ocean_volume(cube.data.sum())
    else:
        check_global_ocean_area(cube.data.sum())

    return cube 


def get_subset_kwargs(namespace):
    """Get keyword arguments for xarray subsetting.
    
    namespace is usually generated by argparse at the beginning of a script.

    Args:
      namespace (argparse.Namespace) 
    
    """

    kwarg_dict = {}
    try:
        south_lat, north_lat, west_lon, east_lon = regions[namespace.region]
        kwarg_dict['latitude'] = slice(south_lat, north_lat)
        kwarg_dict['longitude'] = slice(west_lon, east_lon)
    except AttributeError:
        pass 

    for dim in ['time', 'latitude', 'longitude']:
        kwarg_dict = _sel_or_slice(namespace, dim, kwarg_dict)

    return kwarg_dict


def get_time_constraint(time_list):
    """Get the time constraint used for reading an iris cube."""

    if time_list:
        if not type(time_list) in (list, tuple):
            time_list = [time_list]
        date_pattern = '([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})'
        start_date = time_list[0]
        start_year, start_month, start_day = start_date.split('-')
        assert re.search(date_pattern, start_date)

        if len(time_list) == 1:
            time_constraint = iris.Constraint(time=lambda t: cftime.DatetimeNoLeap(int(start_year), int(start_month), int(start_day)) <= t.point)
        else:
            end_date = time_list[1]
            assert re.search(date_pattern, end_date)

            if (start_date == end_date):
                time_constraint = iris.Constraint(time=iris.time.PartialDateTime(year=int(start_year), month=int(start_month), day=int(start_day)))
            else:  
                end_year, end_month, end_day = end_date.split('-')
                start_constraint = iris.Constraint(time=lambda t: cftime.DatetimeNoLeap(int(start_year), int(start_month), int(start_day)) <= t.point)
                end_constraint = iris.Constraint(time=lambda t: t.point <= cftime.DatetimeNoLeap(int(end_year), int(end_month), int(end_day)))
                time_constraint = start_constraint & end_constraint

                #time_constraint = iris.Constraint(time=lambda t: cftime.DatetimeNoLeap(int(start_year), int(start_month), int(start_day)) <= t.point <= cftime.DatetimeNoLeap(int(end_year), int(end_month), int(end_day)))
                #time_constraint = iris.Constraint(time=lambda t: iris.time.PartialDateTime(year=int(start_year), month=int(start_month), day=int(start_day)) <= t.point <= iris.time.PartialDateTime(year=int(end_year), month=int(end_month), day=int(end_day)))
                #time_constraint = iris.Constraint(time=lambda t: iris.time.PartialDateTime(year=int(start_year), month=int(start_month), day=int(start_day)) <= t.point and iris.time.PartialDateTime(year=int(end_year), month=int(end_month), day=int(end_day)) >= t.point)
    else:
        time_constraint = iris.Constraint()

    return time_constraint

    
def get_timescale(times):
    """Get the timescale.
    
    Args:
      times (list/tuple): Tuple containing two or more numpy.datetime64 instances. 
        The difference between them is used to determine the timescale. 

    """

    diff = times[1] - times[0]

    thresholds = {'yearly': numpy.timedelta64(365, 'D'),
                  'monthly': numpy.timedelta64(27, 'D'),
                  'daily': numpy.timedelta64(1, 'D'),
                  '12hourly': numpy.timedelta64(12, 'h'),
                  '6hourly': numpy.timedelta64(6, 'h'),
                  'hourly': numpy.timedelta64(1, 'h')}
    
    timescale = None
    scales = ['yearly', 'monthly', 'daily', '12hourly', '6hourly', 'hourly']
    for key in scales:
        if diff >= thresholds[key]:
            timescale = key
            break
    
    if not timescale:
        print('Invalid timescale data.')
        print('Must be between hourly and yearly.')
        sys.exit(1)

    print(timescale)

    return timescale


def get_timestamp():
    """Return a time stamp that includes the command line entry."""
    
    time_stamp = """%s: %s %s (Git hash: %s)""" %(datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), 
                                                  sys.executable, 
                                                  " ".join(sys.argv), 
                                                  MODULE_HASH[0:7])

    return time_stamp


def iris_vertical_constraint(min_depth, max_depth):
    """Define vertical constraint for iris cube loading."""
    
    if min_depth and max_depth:
        level_subset = lambda cell: min_depth <= cell <= max_depth
        level_constraint = iris.Constraint(depth=level_subset)
    elif max_depth:
        level_subset = lambda cell: cell <= max_depth
        level_constraint = iris.Constraint(depth=level_subset)
    elif min_depth:
        level_subset = lambda cell: cell >= min_depth    
        level_constraint = iris.Constraint(depth=level_subset)
    else:
        level_constraint = iris.Constraint()
    
    return level_constraint


def read_dates(infile):
    """Read a file of dates (one per line) and write to a list.

    Assumes there is a metadata file corresponding to infile which 
    has exactly the same name but ends with .met

    """
    
    fin = open(infile, 'r')
    date_list = []
    for line in fin:
        date_list.append(line.rstrip('\n'))
    fin.close()

    file_body = infile.split('.')[0]
    with open (file_body+'.met', 'r') as metfile:
        date_metadata=metfile.read()

    return date_list, date_metadata


def salinity_unit_check(cube, valid_min=-1, valid_max=80, abort=True):
    """Check CMIP5 salinity units.

    Most modeling groups store their salinity data
    in units of g/kg (typically ranging from 5 to 45 g/kg)
    and label that unit "psu" (which iris doesn't 
    recognise and converts to unknown).

    Some random data files in some runs have some stored 
    with units of kg/kg and the unit is labelled 1.

    This function converts to g/kg and unknown.

    Args:
      cube (iris.cube.Cube) 

    """

    if cube.units == '1' and cube[0, ::].data.mean() < 1.0:
        cube.data = cube.data * 1000

    data_max = cube[0, ::].data.max()
    data_min = cube[0, ::].data.min()
    
    if abort:
        assert data_max < valid_max, 'Salinity max is %f' %(data_max)
        assert data_min >= valid_min , 'Salinity min is %f' %(data_min)
    else: 
        npoints = cube.data.size
        if data_max > valid_max:
            masked_points_before = cube.data.mask.sum()
            cube.data = numpy.ma.masked_where(cube.data > valid_max, cube.data)
            masked_points_after = cube.data.mask.sum()
            new_masked_points = masked_points_after - masked_points_before
            print(f'Salinity max is {data_max}. New masked points = {new_masked_points} of {npoints}')
        if data_min < valid_min:
            masked_points_before = cube.data.mask.sum()
            cube.data = numpy.ma.masked_where(cube.data < valid_min, cube.data)
            masked_points_after = cube.data.mask.sum()
            new_masked_points = masked_points_after - masked_points_before
            print(f'Salinity min is {data_min}. New masked points = {new_masked_points} of {npoints}')

    cube.units = 'g/kg'   #cf_units.Unit('unknown')

    return cube


def _sel_or_slice(inargs, dim, kw_dict):
    """Select or slice."""

    try:
        in_dim = eval('inargs.'+dim)
        if type(in_dim) in (float, int):        
            kw_dict[dim] = in_dim
        else:
            start, end = in_dim
            if start == end:
                kw_dict[dim] = start
            else:
                kw_dict[dim] = slice(start, end)
    except AttributeError:
        pass

    return kw_dict


def set_dim_atts(dset_out, time_units):
    """Set dimension attributes.
    
    Used when writing a new file using xarray when the data
    was originally an iris cube.
    
    """
    
    dset_out['time'].attrs = {'calendar': 'standard', 
                              'long_name': 'time',
                              'units': time_units,
                              'axis': 'T'}
    dset_out['latitude'].attrs = {'standard_name': 'latitude',
                                  'long_name': 'latitude',
                                  'units': 'degrees_north',
                                  'axis': 'Y'}
    dset_out['longitude'].attrs = {'standard_name': 'longitude',
                                   'long_name': 'longitude',
                                   'units': 'degrees_east',
                                   'axis': 'X'}
    
    return dset_out


def set_global_atts(dset, dset_template, hist_dict):
    """Update the global attributes of an xarray.DataArray.
    
    Args:
      dset (xarray.DataArray): DataArray that needs updating
      dset_template (dict): Template global attributes
      hist_dict (dict): History atts from each input file
        (keys = filename, values = history attribute)
    
    """
    
    dset.attrs = dset_template
    
    if 'calendar' in list(dset.attrs.keys()):
        del dset.attrs['calendar']  # Iris does not like it

    dset.attrs['history'] = write_metadata(file_info=hist_dict)


def set_outfile_date(outfile, new_date):
    """Take an outfile name and replace the existing date
    (in YYYY-MM-DD format) with new_date."""

    new_dt = parser.parse(str(new_date))
    
    date_pattern = '([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})'
    assert re.search(date_pattern, outfile), \
    """Output file must contain the date of the final timestep in the format YYYY-MM-DD"""
    
    return re.sub(r'([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})', new_dt.strftime("%Y-%m-%d"), outfile)


def standard_datetime(dt):
    """Take any arbitrarty date/time and convert to the standard
    I use for all outputs: YYYY-MM-DD."""

    new_dt = parser.parse(str(dt))

    return new_dt.strftime("%Y-%m-%d")


def temperature_unit_check(cube, output_unit, abort=True):
    """Check CMIP5 ocean temperature units.

    Args:
      cube (iris.cube.Cube) 

    """

    assert output_unit in ['K', 'C']
    valid_bounds = {'K': [263, 333], 'C': [-10, 60]}
    
    data_median = numpy.ma.median(cube.data)
    assert data_median < 400
    in_unit = 'K' if data_median > 200 else 'C'

    valid_min, valid_max = valid_bounds[in_unit]
    data_max = cube.data.max()
    data_min = cube.data.min()
    if (data_max < valid_max) or (data_min >= valid_min):
        cube.data = numpy.ma.masked_where(cube.data == -1 * cube.data.fill_value, cube.data)
        data_max = cube.data.max()
        data_min = cube.data.min()

    if abort:
        assert data_max < valid_max, 'Temperature max is %f' %(data_max)
        assert data_min >= valid_min , 'Temperature min is %f' %(data_min)
    else: 
        if data_max > valid_max:
            masked_points_before = cube.data.mask.sum()
            cube.data = numpy.ma.masked_where(cube.data > valid_max, cube.data)
            masked_points_after = cube.data.mask.sum()
            new_masked_points = masked_points_after - masked_points_before
            print('Temperature max is %f. New masked points = %f' %(data_max, new_masked_points))
        if data_min < valid_min:
            masked_points_before = cube.data.mask.sum()
            cube.data = numpy.ma.masked_where(cube.data < valid_min, cube.data)
            masked_points_after = cube.data.mask.sum()
            new_masked_points = masked_points_after - masked_points_before
            print('Temperature min is %f. New masked points = %f' %(data_min, new_masked_points))

    if in_unit != output_unit:
        if output_unit == 'C':
            cube.data = cube.data - 273.15
            cube.units = 'C'
        else:
            cube.data = cube.data + 273.15
            cube.units = 'K'

    return cube


def two_floats(value):
    """Read floats lile -5e20 from the command line.

    Using argparse, set type=two_floats

    """

    values = value.split()
    if len(values) != 2:
        raise argparse.ArgumentError
    values = map(float, values)

    return values


def vertical_bounds_text(level_axis, user_top, user_bottom):
    """Generate text describing the vertical bounds of a data selection."""
    
    if user_top and user_bottom:
        level_text = '%f down to %f' %(user_top, user_bottom)
    elif user_bottom:
        level_text = 'input data surface (%f) down to %f' %(level_axis[0], user_bottom)
    elif user_top:
        level_text = '%f down to input data bottom (%f)' %(user_top, level_axis[-1])
    else:
        level_text = 'full depth of input data (%f down to %f)' %(level_axis[0], level_axis[-1])
    
    return level_text


def write_dates(outfile, date_list):
    """Write a list of dates to file."""
    
    fout = open(outfile, 'w')
    for date in date_list:
        fout.write(str(date)+'\n')
    fout.close()


def write_metadata(ofile=None, file_info=None, extra_notes=None):
    """Write a metadata output file.
    
    Args:
      ofile (str, optional): Name of output file that we want to create a .met file 
        alongside (i.e. new file with .met extension will be created)
      file_info (dict, optional): A dictionary where keys are filenames and values are 
        the global attribute history
      extra_notes (list, optional): List containing character strings of extra information 
        (output is one list item per line)
      
    """
    
    result = ''
        
    # Write the timestamp
    time_stamp = get_timestamp()
    result += time_stamp + '\n'
    
    # Write the extra info
    if extra_notes:
        result += 'Extra notes: \n'
        for line in extra_notes:
            result += line + '\n'
    
    # Write the file details
    if file_info:
        assert type(file_info) == dict
        nfiles = len(list(file_info.keys()))
        for fname, history in file_info.items():
            if nfiles > 1:
                result += 'History of %s: \n %s \n' %(fname, history)
            else:
                result += '%s \n' %(history)
    
    # Create outfile or return string
    if ofile:
        fname, extension = ofile.split('.')
        fout = open(fname+'.met', 'w')
        fout.write(result) 
        fout.close()
    else:
        return result
