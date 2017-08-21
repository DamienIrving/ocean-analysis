"""
Filename:     calc_system_heat_distribution.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Determine distribution of heat trends throughout climate system  

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
from iris.experimental.equalise_cubes import equalise_attributes


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
    import timeseries
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

nh_lat_subset = lambda cell: cell >= 0.0    
sh_lat_subset = lambda cell: cell <= 0.0    
hemisphere_constraints = {'nh': iris.Constraint(latitude=nh_lat_subset),
                          'sh': iris.Constraint(latitude=sh_lat_subset)}

def calc_sum(cube, var, hemisphere, area_cube):
    """Calculate the hemispheric sum."""

    coord_names = [coord.name() for coord in cube.dim_coords]
    assert 'time' in coord_names
    assert len(coord_names) == 3
    aux_coord_names = [coord.name() for coord in cube.aux_coords]
    if aux_coord_names == ['latitude', 'longitude']:
        assert area_cube, "Must give areacello file for non lat/lon grid data"
        print("""processing %s on it's non lat/lon grid""" %(var))

        hemisphere_mask = create_hemisphere_mask(cube.coord('latitude').points, cube.shape, hemisphere)
        land_ocean_mask = cube.data.mask
        complete_mask = hemisphere_mask + land_ocean_mask

        cube.data = numpy.ma.asarray(cube.data)
        cube.data.mask = complete_mask
    else:
        cube = cube.copy().extract(hemisphere_constraints[hemisphere])
    
    cube = multiply_by_area(cube, var, area_cube) # convert W m-2 to W
    coord_names.remove('time')
    sum_cube = cube.collapsed(coord_names, iris.analysis.SUM)
    sum_cube.remove_coord(coord_names[0])
    sum_cube.remove_coord(coord_names[1])

    return sum_cube 


def get_data(filenames, var, metadata_dict, attributes, input_timescale='monthly', 
             sftlf_cube=None, include_only=None, area_cube=None):
    """Read, merge, temporally aggregate and calculate hemispheric totals.

    Args:
      include_only (str): 'ocean' or 'land'

    """

    if filenames:
        with iris.FUTURE.context(cell_datetime_objects=True):
            cube = iris.load(filenames, gio.check_iris_var(var))

            metadata_dict[filenames[0]] = cube[0].attributes['history']
            equalise_attributes(cube)
            iris.util.unify_time_units(cube)
            cube = cube.concatenate_cube()
            cube = gio.check_time_units(cube)
            cube = iris.util.squeeze(cube)

        attributes = cube.attributes
        
        if not input_timescale == 'annual':
            cube = timeseries.convert_to_annual(cube, full_months=True)
            
        if 'J' in str(cube.units):
            cube = joules_to_watts(cube)

        if include_only and sftlf_cube:
            mask = create_land_ocean_mask(sftlf_cube, cube.shape, include_only)
            cube.data = numpy.ma.asarray(cube.data)
            cube.data.mask = mask
            
        nh_sum = calc_sum(cube, var, 'nh', area_cube)
        sh_sum = calc_sum(cube, var, 'sh', area_cube)

        rename_cube(nh_sum, 'nh', include_only)
        rename_cube(sh_sum, 'sh', include_only)
    else:
        nh_sum = None
        sh_sum = None

    return nh_sum, sh_sum, metadata_dict, attributes


def joules_to_watts(cube):
    """Convert data from Joules to Watts.

    1 W = 1 J/s

    The annual timescale data are divided by the number of seconds in a year.

    """ 

    seconds_in_year = 60 * 60 * 24 * 365.0
    cube.data = cube.data / seconds_in_year

    units = str(cube.units)
    cube.units = units.replace('J', 'W')

    return cube


def create_land_ocean_mask(mask_cube, target_shape, include_only):
    """Create a land or ocean mask from an sftlf (land surface fraction) file.

    There is no land when cell value == 0

    """

    target_ndim = len(target_shape)

    if include_only == 'land':
        mask_array = numpy.where(mask_cube.data > 50, False, True)
    elif include_only == 'ocean':
        mask_array = numpy.where(mask_cube.data < 50, False, True)

    mask = uconv.broadcast_array(mask_array, [target_ndim - 2, target_ndim - 1], target_shape)
    assert mask.shape == target_shape 

    return mask


def create_hemisphere_mask(latitude_array, target_shape, hemisphere):
    """Create mask from the latitude auxillary coordinate"""

    target_ndim = len(target_shape)

    if hemisphere == 'nh':
        mask_array = numpy.where(latitude_array >= 0, False, True)
    elif hemisphere == 'sh':
        mask_array = numpy.where(latitude_array < 0, False, True)

    mask = uconv.broadcast_array(mask_array, [target_ndim - 2, target_ndim - 1], target_shape)
    assert mask.shape == target_shape 

    return mask


def derived_toa_radiation_fluxes(cube_dict, hemisphere):
    """Calculate the net TOA flux."""

    if cube_dict['rsdt'] and cube_dict['rsut']:
        cube_dict['rsnt'] = cube_dict['rsdt'] - cube_dict['rsut'] 
        rename_cube(cube_dict['rsnt'], hemisphere, None, 'toa_net_shortwave_flux', 'TOA Net Shortwave Flux', 'rsnt')
    else:
        cube_dict['rsnt'] = None
    
    if cube_dict['rsnt'] and cube_dict['rsns']:
        cube_dict['rsaa'] = cube_dict['rsnt'] - cube_dict['rsns'] 
        rename_cube(cube_dict['rsaa'], hemisphere, None, 'atmosphere_absorbed_shortwave_flux', 'Atmosphere Absorbed Shortwave Flux', 'rsaa')

    return cube_dict


def derived_surface_radiation_fluxes(cube_dict, inargs, sftlf_cube, hemisphere):
    """Calculate the net surface radiation flux."""

    if inargs.rsds_files and inargs.rsus_files and inargs.rlds_files and inargs.rlus_files:
        for realm in ['', '-ocean', '-land']:
            realm_arg = realm[1:] if realm else None

            cube_dict['rsns'+realm] = cube_dict['rsds'+realm] - cube_dict['rsus'+realm]
            rename_cube(cube_dict['rsns'+realm], hemisphere, realm_arg, 'surface_net_shortwave_flux_in_air', 'Surface Net Shortwave Flux in Air', 'rsns')
           
            cube_dict['rlns'+realm] = cube_dict['rlus'+realm] - cube_dict['rlds'+realm]
            rename_cube(cube_dict['rlns'+realm], hemisphere, realm_arg, 'surface_net_longwave_flux_in_air', 'Surface Net Longwave Flux in Air', 'rlns')
    else:
        for realm in ['', '-ocean', '-land']:
            cube_dict['rsns'+realm] = None
            cube_dict['rlns'+realm] = None

    return cube_dict


def derived_surface_heat_fluxes(cube_dict, hemisphere):
    """Calculate the surface heat flux totals."""

    if cube_dict['hfss-ocean'] and cube_dict['hfls-ocean'] and cube_dict['hfds-ocean']:
        cube_dict['hfts-ocean'] = cube_dict['hfss-ocean'] + cube_dict['hfls-ocean'] + cube_dict['hfds-ocean']
        rename_cube(cube_dict['hfts-ocean'], hemisphere, 'ocean', 'surface_total_heat_flux', 'Surface Total Heat Flux', 'hfts')
    else:
        cube_dict['hfts-ocean'] = None

    if cube_dict['hfss-land'] and cube_dict['hfls-land']:
        cube_dict['hfts-land'] = cube_dict['hfss-land'] + cube_dict['hfls-land']
        rename_cube(cube_dict['hfts-land'], hemisphere, 'land', 'surface_total_heat_flux', 'Surface Total Heat Flux', 'hfts')
    else:
        cube_dict['hfts-land'] = None

    if cube_dict['hfts-ocean'] and cube_dict['hfts-land']:
        cube_dict['hfts'] = cube_dict['hfts-ocean'] + cube_dict['hfts-land']
        rename_cube(cube_dict['hfts'], hemisphere, None, 'surface_total_heat_flux', 'Surface Total Heat Flux', 'hfts')
    else:
        cube_dict['hfts'] = None

    return cube_dict


def multiply_by_area(cube, var, area_cube):
    """Multiply by cell area."""

    if cube.units == 'W m-2':

        if area_cube:
            area_data = uconv.broadcast_array(area_cube.data, [1, 2], cube.shape)
        else:
            if not cube.coord('latitude').has_bounds():
                cube.coord('latitude').guess_bounds()
            if not cube.coord('longitude').has_bounds():
                cube.coord('longitude').guess_bounds()
            area_data = iris.analysis.cartography.area_weights(cube)
            units = str(cube.units)
            cube.units = units.replace('m-2', '')

        cube.data = cube.data * area_data
    else:
        print('Did not multiply %s by area. Units = %s' %(var, str(cube.units)))

    return cube


def rename_cube(cube, hemisphere, realm, standard_name=None, long_name=None, var_name=None):
    """Rename a cube according to the specifics of the analysis"""

    assert hemisphere in ['nh', 'sh']
    assert realm in ['ocean', 'land', None]

    if not standard_name:
        standard_name = cube.standard_name
    if not long_name:
        long_name = cube.long_name
    if not var_name:
        var_name = cube.var_name

    if realm:
        standard_name = '%s_%s_%s_sum' %(standard_name, hemisphere, realm)
        long_name = '%s %s %s sum' %(long_name, hemisphere, realm)
        var_name = '%s-%s-%s-sum' %(var_name, hemisphere, realm)
    else:
        standard_name = '%s_%s_sum' %(standard_name, hemisphere)
        long_name = '%s %s sum' %(long_name, hemisphere)
        var_name = '%s-%s-sum' %(var_name, hemisphere)

    iris.std_names.STD_NAMES[standard_name] = {'canonical_units': cube.units}
    cube.standard_name = standard_name
    cube.long_name = long_name
    cube.var_name = var_name


def create_cube_list(nh_cube_dict, sh_cube_dict, metadata_dict, attributes):
    """Create the cube list for output."""

    cube_list = iris.cube.CubeList()
    for var, cube in nh_cube_dict.items():
        if cube:
            cube_list.append(cube)
    for var, cube in sh_cube_dict.items():
        if cube:
            cube_list.append(cube)

    equalise_attributes(cube_list)
    iris.util.unify_time_units(cube_list)
    for cube in cube_list:
        cube.attributes = attributes
        cube.attributes['history'] = gio.write_metadata() #file_info=metadata_dict

    return cube_list


def main(inargs):
    """Run the program."""

    sftlf_cube = iris.load_cube(inargs.sftlf_file, 'land_area_fraction')
    if inargs.areacello_file:
        areacello_cube = iris.load_cube(inargs.areacello_file, 'cell_area')
    else:
        areacello_cube = None

    nh_cube_dict = {}
    sh_cube_dict = {}
    metadata_dict = {}
    attributes = {}

    # TOA radiation fluxes
    nh_cube_dict['rsdt'], sh_cube_dict['rsdt'], metadata_dict, attributes = get_data(inargs.rsdt_files, 'toa_incoming_shortwave_flux', metadata_dict, attributes)
    nh_cube_dict['rsut'], sh_cube_dict['rsut'], metadata_dict, attributes = get_data(inargs.rsut_files, 'toa_outgoing_shortwave_flux', metadata_dict, attributes)
    nh_cube_dict['rlut'], sh_cube_dict['rlut'], metadata_dict, attributes = get_data(inargs.rlut_files, 'toa_outgoing_longwave_flux', metadata_dict, attributes)

    # Surface radiation fluxes
    for realm in ['', '-ocean', '-land']:
        realm_arg = realm[1:] if realm else None
        nh_cube_dict['rsds'+realm], sh_cube_dict['rsds'+realm], metadata_dict, attributes = get_data(inargs.rsds_files, 'surface_downwelling_shortwave_flux_in_air', metadata_dict,
                                                                                                     attributes, sftlf_cube=sftlf_cube, include_only=realm_arg)
        nh_cube_dict['rsus'+realm], sh_cube_dict['rsus'+realm], metadata_dict, attributes = get_data(inargs.rsus_files, 'surface_upwelling_shortwave_flux_in_air', metadata_dict,
                                                                                                     attributes, sftlf_cube=sftlf_cube, include_only=realm_arg)
        nh_cube_dict['rlds'+realm], sh_cube_dict['rlds'+realm], metadata_dict, attributes = get_data(inargs.rlds_files, 'surface_downwelling_longwave_flux_in_air', metadata_dict,
                                                                                                     attributes, sftlf_cube=sftlf_cube, include_only=realm_arg)
        nh_cube_dict['rlus'+realm], sh_cube_dict['rlus'+realm], metadata_dict, attributes = get_data(inargs.rlus_files, 'surface_upwelling_longwave_flux_in_air', metadata_dict,
                                                                                                     attributes, sftlf_cube=sftlf_cube, include_only=realm_arg)

    nh_cube_dict = derived_surface_radiation_fluxes(nh_cube_dict, inargs, sftlf_cube, 'nh')
    sh_cube_dict = derived_surface_radiation_fluxes(sh_cube_dict, inargs, sftlf_cube, 'sh')

    nh_cube_dict = derived_toa_radiation_fluxes(nh_cube_dict, 'nh')
    sh_cube_dict = derived_toa_radiation_fluxes(sh_cube_dict, 'sh')

    # Surface heat fluxes
    if inargs.hfrealm == 'atmos':
        hfss_name = 'surface_upward_sensible_heat_flux'
        hfls_name = 'surface_upward_latent_heat_flux'
        for realm in ['', '-ocean', '-land']:
            realm_arg = realm[1:] if realm else None
            nh_cube_dict['hfss'+realm], sh_cube_dict['hfss'+realm], metadata_dict, attributes = get_data(inargs.hfss_files, hfss_name, metadata_dict, attributes, sftlf_cube=sftlf_cube, include_only=realm_arg)
            nh_cube_dict['hfls'+realm], sh_cube_dict['hfls'+realm], metadata_dict, attributes = get_data(inargs.hfls_files, hfls_name, metadata_dict, attributes, sftlf_cube=sftlf_cube, include_only=realm_arg)
    elif inargs.hfrealm == 'ocean':
        hfss_name = 'surface_downward_sensible_heat_flux'
        hfls_name = 'surface_downward_latent_heat_flux'
        nh_cube_dict['hfss-ocean'], sh_cube_dict['hfss-ocean'], metadata_dict, attributes = get_data(inargs.hfss_files, hfss_name, metadata_dict, attributes, include_only='ocean', area_cube=areacello_cube)
        nh_cube_dict['hfls-ocean'], sh_cube_dict['hfls-ocean'], metadata_dict, attributes = get_data(inargs.hfls_files, hfls_name, metadata_dict, attributes, include_only='ocean', area_cube=areacello_cube)

    nh_cube_dict['hfds-ocean'], sh_cube_dict['hfds-ocean'], metadata_dict, attributes = get_data(inargs.hfds_files, 'surface_downward_heat_flux_in_sea_water', metadata_dict,
                                                                                                 attributes, include_only='ocean', area_cube=areacello_cube)
    nh_cube_dict['hfsithermds-ocean'], sh_cube_dict['hfsithermds-ocean'], metadata_dict, attributes = get_data(inargs.hfsithermds_files,
                                                                                                              'heat_flux_into_sea_water_due_to_sea_ice_thermodynamics',
                                                                                                               metadata_dict, attributes, include_only='ocean', area_cube=areacello_cube)
    nh_cube_dict = derived_surface_heat_fluxes(nh_cube_dict, 'nh')
    sh_cube_dict = derived_surface_heat_fluxes(sh_cube_dict, 'sh')

    # Ocean heat transport / storage
    nh_cube_dict['ohc-ocean'], sh_cube_dict['ohc-ocean'], metadata_dict, attributes = get_data(inargs.ohc_files, 'ocean_heat_content', metadata_dict, attributes, input_timescale='annual', include_only='ocean', area_cube=areacello_cube)
    ## FIXME: Add hfy analysis

    cube_list = create_cube_list(nh_cube_dict, sh_cube_dict, metadata_dict, attributes)
    iris.save(cube_list, inargs.outfile, netcdf_format='NETCDF3_CLASSIC')


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Determine distribution of heat trends throughout climate system'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("sftlf_file", type=str, help="Land fraction file")
    parser.add_argument("outfile", type=str, help="Output txt file")                                     

    parser.add_argument("--areacello_file", type=str, default=None, 
                        help="Input ocean area file [required for non lat/lon grids]")

    parser.add_argument("--rsdt_files", type=str, nargs='*', default=None,
                        help="toa incoming shortwave flux files")
    parser.add_argument("--rsut_files", type=str, nargs='*', default=None,
                        help="toa outgoing shortwave flux files")
    parser.add_argument("--rlut_files", type=str, nargs='*', default=None,
                        help="toa outgoing longwave flux files")

    parser.add_argument("--rsds_files", type=str, nargs='*', default=None,
                        help="surface downwelling shortwave flux files")
    parser.add_argument("--rsus_files", type=str, nargs='*', default=None,
                        help="surface upwelling shortwave flux files")
    parser.add_argument("--rlds_files", type=str, nargs='*', default=None,
                        help="surface downwelling longwave flux files")
    parser.add_argument("--rlus_files", type=str, nargs='*', default=None,
                        help="surface upwelling longwave flux files")

    parser.add_argument("--hfss_files", type=str, nargs='*', default=None,
                        help="surface sensible heat flux files")
    parser.add_argument("--hfls_files", type=str, nargs='*', default=None,
                        help="surface latent heat flux files")
    parser.add_argument("--hfds_files", type=str, nargs='*', default=None,
                        help="surface downward heat flux files")
    parser.add_argument("--hfsithermds_files", type=str, nargs='*', default=None,
                        help="heat flux due to sea ice files")

    parser.add_argument("--ohc_files", type=str, nargs='*', default=None,
                        help="ocean heat content files")

    parser.add_argument("--hfrealm", type=str, choices=('atmos', 'ocean'), required=True,
                        help="specify whether original hfss and hfls data were atmos or ocean")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=('1850-01-01', '2005-12-31'),
                        help="Time period [default = entire]")

    args = parser.parse_args()             
    main(args)
