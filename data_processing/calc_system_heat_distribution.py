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

#region_names = {'nh': ('Northern Hemisphere', 'northern_hemisphere'),
#                'sh': ('Southern Hemisphere', 'southern_hemisphere'),
#                'arctic': ('Arctic', 'arctic'),
#                'nsubpolar': ('Northern Sub Polar', 'northern_sub_polar'),
#                'ntropics': ('Northern Tropics', 'northern_tropics'),
#                'stropics': ('Southern Tropics', 'southern_tropics'),
#                'ssubpolar': ('Southern Sub Polar', 'southern_sub_polar')}
    
region_constraints = {'globe': iris.Constraint(),
                      'nh': iris.Constraint(latitude=lambda cell: cell >= 0.0),
                      'sh': iris.Constraint(latitude=lambda cell: cell < 0.0),
                      'arctic': iris.Constraint(latitude=lambda cell: cell >= 67.0),
                      'nsubpolar': iris.Constraint(latitude=lambda cell: 42.0 <= cell < 67.0),
                      'ntropics': iris.Constraint(latitude=lambda cell: 0.0 <= cell < 42.0),
                      'stropics': iris.Constraint(latitude=lambda cell: -42.0 <= cell < 0.0),
                      'ssubpolar': iris.Constraint(latitude=lambda cell: cell < -42.0)}

region_boundaries = {'sh':(-91, 0),
                     'nh': (0, 91),
                     'arctic': (67, 91),
                     'nsubpolar': (42, 67),
                     'ntropics': (0, 42),
                     'stropics': (-42, 0),
                     'ssubpolar': (-91, -42)}

region_list = ['globe', 'sh', 'nh', 'arctic', 'nsubpolar', 'ntropics', 'stropics', 'ssubpolar']


def calc_sum(cube, var, region, area_cube):
    """Calculate the region sum."""

    cube = cube.copy() 

    coord_names = [coord.name() for coord in cube.dim_coords]
    assert 'time' in coord_names
    assert len(coord_names) == 3
    aux_coord_names = [coord.name() for coord in cube.aux_coords]
    if aux_coord_names == ['latitude', 'longitude']:
        assert area_cube, "Must give areacello file for non lat/lon grid data"
        print("""processing %s on it's non lat/lon grid""" %(var))

        region_mask = create_region_mask(cube.coord('latitude').points, cube.shape, region)
        land_ocean_mask = cube.data.mask
        complete_mask = region_mask + land_ocean_mask

        cube.data = numpy.ma.asarray(cube.data)
        cube.data.mask = complete_mask
    else:
        cube = cube.extract(region_constraints[region])
    
    cube = multiply_by_area(cube, var, area_cube) # convert W m-2 to W
    coord_names.remove('time')
    sum_cube = cube.collapsed(coord_names, iris.analysis.SUM)
    sum_cube.remove_coord(coord_names[0])
    sum_cube.remove_coord(coord_names[1])

    return sum_cube 


def hfbasin_handling(cube, var, model):
    """Select global ocean from hfbasin cube."""

    if var == 'northward_ocean_heat_transport':
        if model == 'CSIRO-Mk3-6-0':
            cube = cube[:, 2, :]
        else:
            cube = cube.extract(iris.Constraint(region='global_ocean'))
    elif var == 'ocean_heat_y_transport':
        cube = cube.collapsed('longitude', iris.analysis.SUM)
        cube.remove_coord('longitude')
        cube.standard_name = 'northward_ocean_heat_transport'
        cube.long_name = 'Northward Ocean Heat Transport'
        cube.var_name = 'hfbasin'

    return cube


def load_data(filenames, standard_name, metadata_dict, input_timescale):
    """Basic data loading and temporal smoothing"""

    with iris.FUTURE.context(cell_datetime_objects=True):
        cube = iris.load(filenames, gio.check_iris_var(standard_name))
            
        metadata_dict[filenames[0]] = cube[0].attributes['history']
        equalise_attributes(cube)
        iris.util.unify_time_units(cube)
        cube = cube.concatenate_cube()
        cube = gio.check_time_units(cube)
        cube = iris.util.squeeze(cube)
            
    attributes = cube.attributes                   

    if not input_timescale == 'annual':
        cube = timeseries.convert_to_annual(cube, full_months=True)

    return cube, metadata_dict, attributes


def get_transport_data(filenames, standard_name, cube_dict, metadata_dict, attributes, input_timescale='monthly'):
    """Read in ocean heat transport data."""
    
    assert standard_name in ['northward_ocean_heat_transport', 'ocean_heat_y_transport']

    if filenames:
        cube, metadata_dict, attributes = load_data(filenames, standard_name, metadata_dict, input_timescale) 
        for region in region_list[1:]:
            zonal_cube = hfbasin_handling(cube.copy(), standard_name, attributes['model_id'])   
            for index, lat in enumerate(region_boundaries[region]):
                if abs(lat) < 90:
                    direction = 'in' if index == 0 else 'out'
                    target_lat, error = uconv.find_nearest(zonal_cube.coord('latitude').points, lat, index=False)
                    region_sum = zonal_cube.extract(iris.Constraint(latitude=target_lat))
                    region_sum, var_name = rename_cube(region_sum, region, 'ocean', direction=direction)

                    cube_dict[var_name] = region_sum

    return cube_dict, metadata_dict, attributes


def get_data(filenames, standard_name, cube_dict, metadata_dict, attributes, 
             input_timescale='monthly', sftlf_cube=None, include_only=None, area_cube=None):
    """Read, merge, temporally aggregate and calculate regional totals.

    Args:
      include_only (str): 'ocean' or 'land'

    """

    if filenames:
        cube, metadata_dict, attributes = load_data(filenames, standard_name, metadata_dict, input_timescale)        

        if include_only and sftlf_cube:
            mask = create_land_ocean_mask(sftlf_cube, cube.shape, include_only)
            cube.data = numpy.ma.asarray(cube.data)
            cube.data.mask = mask
        
        for region in region_list:
            region_sum = calc_sum(cube.copy(), standard_name, region, area_cube)
            if standard_name == 'ocean_heat_content':
                region_sum, var_name = rename_cube(region_sum, region, None, standard_name='ocean_heat_content',
                                                   long_name='ocean heat content', var_name='ohc')
            else:
                region_sum, var_name = rename_cube(region_sum, region, include_only)
            cube_dict[var_name] = region_sum

    return cube_dict, metadata_dict, attributes


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


def create_region_mask(latitude_array, target_shape, region):
    """Create mask from the latitude auxillary coordinate"""

    target_ndim = len(target_shape)

    southern_lat, northern_lat = region_boundaries(region)
    mask_array = numpy.where(southern_lat <= latitude_array < northern_lat, False, True)

    mask = uconv.broadcast_array(mask_array, [target_ndim - 2, target_ndim - 1], target_shape)
    assert mask.shape == target_shape 

    return mask


def derived_toa_radiation_fluxes(cube_dict):
    """Calculate the net TOA flux."""

    for region in region_list:
        rsnt_var = 'rsnt-%s-sum' %(region)
        rsdt_var = 'rsdt-%s-sum' %(region)
        rsut_var = 'rsut-%s-sum' %(region)
        rsaa_var = 'rsaa-%s-sum' %(region)
        rsns_var = 'rsns-%s-sum' %(region)

        cube_dict[rsnt_var] = cube_dict[rsdt_var] - cube_dict[rsut_var] 
        cube_dict[rsnt_var], var_name = rename_cube(cube_dict[rsnt_var], region, None,
                                                    standard_name='toa_net_shortwave_flux',
                                                    long_name='TOA Net Shortwave Flux',
                                                    var_name='rsnt')
    
        cube_dict[rsaa_var] = cube_dict[rsnt_var] - cube_dict[rsns_var] 
        cube_dict[rsaa_var], var_name = rename_cube(cube_dict[rsaa_var], region, None,
                                                    standard_name='atmosphere_absorbed_shortwave_flux',
                                                    long_name='Atmosphere Absorbed Shortwave Flux',
                                                    var_name='rsaa')

    return cube_dict


def derived_surface_radiation_fluxes(cube_dict, sftlf_cube):
    """Calculate the net surface radiation flux."""

    for region in region_list:
        for realm in [None, 'ocean', 'land']: 
            if realm:
                realm_insert = '-'+realm
            else:
                realm_insert = '' 
            rnds_var = 'rnds-%s%s-sum' %(region, realm_insert)
            rsns_var = 'rsns-%s%s-sum' %(region, realm_insert)
            rsds_var = 'rsds-%s%s-sum' %(region, realm_insert)
            rsus_var = 'rsus-%s%s-sum' %(region, realm_insert)
            rlns_var = 'rlns-%s%s-sum' %(region, realm_insert)
            rlds_var = 'rlds-%s%s-sum' %(region, realm_insert)
            rlus_var = 'rlus-%s%s-sum' %(region, realm_insert)
        
            cube_dict[rsns_var] = cube_dict[rsds_var] - cube_dict[rsus_var]
            cube_dict[rsns_var], var_name = rename_cube(cube_dict[rsns_var], region, realm,
                                                        standard_name='surface_net_shortwave_flux_in_air',
                                                        long_name='Surface Downwelling Net Shortwave Radiation',
                                                        var_name='rsns')

            cube_dict[rlns_var] = cube_dict[rlus_var] - cube_dict[rlds_var]
            cube_dict[rlns_var], var_name = rename_cube(cube_dict[rlns_var], region, realm,
                                                        standard_name='surface_net_longwave_flux_in_air',
                                                        long_name='Surface Upwelling Net Longwave Radiation',
                                                        var_name='rlns')
            
            cube_dict[rnds_var] = cube_dict[rsns_var] - cube_dict[rlns_var]
            cube_dict[rnds_var], var_name = rename_cube(cube_dict[rnds_var], region, realm,
                                                        standard_name='surface_net_flux_in_air',
                                                        long_name='Surface Downwelling Net Radiation',
                                                        var_name='rnds')

    return cube_dict


def multiply_by_area(cube, var, area_cube):
    """Multiply by cell area."""

    if 'm-2' in str(cube.units):
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


def rename_cube(cube, region, realm, standard_name=None, long_name=None, var_name=None, direction=None):
    """Rename a cube according to the specifics of the analysis"""

    assert region in ['globe', 'nh', 'sh', 'arctic', 'nsubpolar', 'ntropics', 'stropics', 'ssubpolar']
    assert realm in ['ocean', 'land', None]

    if not standard_name:
        standard_name = cube.standard_name
    if not long_name:
        long_name = cube.long_name
    if not var_name:
        var_name = cube.var_name

    if realm:
        standard_name = '%s_%s_%s_sum' %(standard_name, region, realm)
        long_name = '%s %s %s sum' %(long_name, region, realm)
        var_name = '%s-%s-%s-sum' %(var_name, region, realm)
    else:
        standard_name = '%s_%s_sum' %(standard_name, region)
        long_name = '%s %s sum' %(long_name, region)
        var_name = '%s-%s-sum' %(var_name, region)

    if direction:
        assert direction in ['in', 'out']
        standard_name = standard_name + '_' + direction
        long_name = long_name + ' ' + direction
        var_name = var_name + '-' + direction

    iris.std_names.STD_NAMES[standard_name] = {'canonical_units': cube.units}
    cube.standard_name = standard_name
    cube.long_name = long_name
    cube.var_name = var_name
    
    return cube, var_name


def create_cube_list(cube_dict, metadata_dict, attributes):
    """Create the cube list for output."""

    cube_list = iris.cube.CubeList()
    for var, cube in cube_dict.items():
        if cube:
            cube_list.append(cube)

    equalise_attributes(cube_list)
    iris.util.unify_time_units(cube_list)

    for cube in cube_list:
        cube.attributes = attributes
        cube.attributes['history'] = gio.write_metadata(file_info=metadata_dict)
        cube.data = numpy.array(cube.data)  #removes _FillValue attribute

    return cube_list


def main(inargs):
    """Run the program."""

    sftlf_cube = iris.load_cube(inargs.sftlf_file, 'land_area_fraction')
    if inargs.areacello_file:
        areacello_cube = iris.load_cube(inargs.areacello_file, 'cell_area')
    else:
        areacello_cube = None

    cube_dict = {}
    metadata_dict = {}
    attributes = {}

    # TOA radiation fluxes
    
    cube_dict, metadata_dict, attributes = get_data(inargs.rsdt_files, 'toa_incoming_shortwave_flux',
                                                    cube_dict, metadata_dict, attributes)
    cube_dict, metadata_dict, attributes = get_data(inargs.rsut_files, 'toa_outgoing_shortwave_flux',
                                                    cube_dict, metadata_dict, attributes)
    cube_dict, metadata_dict, attributes = get_data(inargs.rlut_files, 'toa_outgoing_longwave_flux',
                                                    cube_dict, metadata_dict, attributes)

    # Surface radiation fluxes
    
    for realm in [None, 'ocean', 'land']:
        cube_dict, metadata_dict, attributes = get_data(inargs.rsds_files, 'surface_downwelling_shortwave_flux_in_air',
                                                        cube_dict, metadata_dict, attributes,
                                                        sftlf_cube=sftlf_cube, include_only=realm)
        cube_dict, metadata_dict, attributes = get_data(inargs.rsus_files, 'surface_upwelling_shortwave_flux_in_air',
                                                        cube_dict, metadata_dict, attributes,
                                                        sftlf_cube=sftlf_cube, include_only=realm)
        cube_dict, metadata_dict, attributes = get_data(inargs.rlds_files, 'surface_downwelling_longwave_flux_in_air',
                                                        cube_dict, metadata_dict, attributes,
                                                        sftlf_cube=sftlf_cube, include_only=realm)
        cube_dict, metadata_dict, attributes = get_data(inargs.rlus_files, 'surface_upwelling_longwave_flux_in_air',
                                                        cube_dict, metadata_dict, attributes,
                                                        sftlf_cube=sftlf_cube, include_only=realm)

    # Surface heat fluxes
    
    if inargs.hfrealm == 'atmos':
        hfss_name = 'surface_upward_sensible_heat_flux'
        hfls_name = 'surface_upward_latent_heat_flux'
        for realm in [None, 'ocean', 'land']:
            cube_dict, metadata_dict, attributes = get_data(inargs.hfss_files, hfss_name,
                                                            cube_dict, metadata_dict, attributes, 
                                                            sftlf_cube=sftlf_cube, include_only=realm)
            cube_dict, metadata_dict, attributes = get_data(inargs.hfls_files, hfls_name,
                                                            cube_dict, metadata_dict, attributes, 
                                                            sftlf_cube=sftlf_cube, include_only=realm)
    elif inargs.hfrealm == 'ocean':
        hfss_name = 'surface_downward_sensible_heat_flux'
        hfls_name = 'surface_downward_latent_heat_flux'
        cube_dict, metadata_dict, attributes = get_data(inargs.hfss_files, hfss_name,
                                                        cube_dict, metadata_dict, attributes,
                                                        include_only='ocean', area_cube=areacello_cube)
        cube_dict, metadata_dict, attributes = get_data(inargs.hfls_files, hfls_name,
                                                        region_list, cube_dict, metadata_dict, attributes,
                                                        include_only='ocean', area_cube=areacello_cube)

    cube_dict, metadata_dict, attributes = get_data(inargs.hfds_files, 'surface_downward_heat_flux_in_sea_water',
                                                    cube_dict, metadata_dict, attributes,
                                                    include_only='ocean', area_cube=areacello_cube)
    cube_dict, metadata_dict, attributes = get_data(inargs.hfsithermds_files, 'heat_flux_into_sea_water_due_to_sea_ice_thermodynamics',
                                                    cube_dict, metadata_dict, attributes,
                                                    include_only='ocean', area_cube=areacello_cube)

    # Ocean heat transport / storage
    cube_dict, metadata_dict, attributes = get_data(inargs.ohc_files, 'ocean_heat_content',
                                                    cube_dict, metadata_dict, attributes,
                                                    input_timescale='annual', area_cube=areacello_cube)
    if inargs.hfbasin_files:
        cube_dict, metadata_dict, attributes = get_transport_data(inargs.hfbasin_files, 'northward_ocean_heat_transport',
                                                                  cube_dict, metadata_dict, attributes)
    elif inargs.hfy_files:
        cube_dict, metadata_dict, attributes = get_transport_data(inargs.hfy_files, 'ocean_heat_y_transport',
                                                                  cube_dict, metadata_dict, attributes)

    # Derived fluxes

    iris.util.unify_time_units(cube_dict.values())
    cube_dict = derived_surface_radiation_fluxes(cube_dict, sftlf_cube)
    cube_dict = derived_toa_radiation_fluxes(cube_dict)  

    # Outfile

    cube_list = create_cube_list(cube_dict, metadata_dict, attributes)
    gio.create_outdir(inargs.outfile)
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
    parser.add_argument("--hfbasin_files", type=str, nargs='*', default=None,
                        help="northward ocean heat transport files")
    parser.add_argument("--hfy_files", type=str, nargs='*', default=None,
                        help="ocean heat y transport files")

    parser.add_argument("--hfrealm", type=str, choices=('atmos', 'ocean'), required=True,
                        help="specify whether original hfss and hfls data were atmos or ocean")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=('1850-01-01', '2005-12-31'),
                        help="Time period [default = entire]")

    args = parser.parse_args()             
    main(args)
