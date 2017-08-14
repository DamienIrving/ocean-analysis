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
    import grids
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

nh_lat_subset = lambda cell: cell >= 0.0    
nh_lat_constraint = iris.Constraint(latitude=nh_lat_subset)

sh_lat_subset = lambda cell: cell <= 0.0    
sh_lat_constraint = iris.Constraint(latitude=sh_lat_subset)


def get_data(filenames, var, metadata_dict, attributes, sftlf_cube=None, include_only=None):
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

        cube = timeseries.convert_to_annual(cube, full_months=True)

        if include_only:
            mask = create_mask(sftlf_cube, cube.shape, include_only)
            cube.data = numpy.ma.asarray(cube.data)
            cube.data.mask = mask
            
        cube, coord_names, regrid_status = grids.curvilinear_to_rectilinear(cube)
        cube = multiply_by_area(cube) # convert W m-2 to W

        nh_cube = cube.copy().extract(nh_lat_constraint)
        sh_cube = cube.copy().extract(sh_lat_constraint)

        nh_sum = nh_cube.collapsed(['latitude', 'longitude'], iris.analysis.SUM)
        nh_sum.remove_coord('latitude')
        nh_sum.remove_coord('longitude')

        sh_sum = sh_cube.collapsed(['latitude', 'longitude'], iris.analysis.SUM)
        sh_sum.remove_coord('latitude')
        sh_sum.remove_coord('longitude')

        rename_cube(nh_sum, 'nh', include_only)
        rename_cube(sh_sum, 'sh', include_only)

    else:
        nh_sum = None
        sh_sum = None

    return nh_sum, sh_sum, metadata_dict, attributes


def create_mask(mask_cube, target_shape, include_only):
    """Create mask from an sftlf (land surface fraction) file.

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


def derived_toa_radiation_fluxes(cube_dict, inargs, hemisphere):
    """Calculate the net TOA flux."""

    if inargs.rsdt_files and inargs.rsut_files and inargs.rlut_files:
        cube_dict['rnt'] = cube_dict['rsdt'] + cube_dict['rsut'] + cube_dict['rlut']   # net TOA flux
        rename_cube(cube_dict['rnt'], hemisphere, None, 'toa_net_radiative_flux', 'TOA Net Radiative Flux', 'rnt')
    else:
        cube_dict['rnt'] = None
    
    return cube_dict


def derived_surface_radiation_fluxes(cube_dict, inargs, sftlf_cube, hemisphere):
    """Calculate the net surface radiation flux."""

    if inargs.rsds_files and inargs.rsus_files and inargs.rlds_files and inargs.rlus_files:
        cube_dict['rns'] = cube_dict['rsds'] + cube_dict['rsus'] + cube_dict['rlds'] + cube_dict['rlus']
        cube_dict['rns-ocean'] = cube_dict['rsds-ocean'] + cube_dict['rsus-ocean'] + cube_dict['rlds-ocean'] + cube_dict['rlus-ocean']
        cube_dict['rns-land'] = cube_dict['rsds-land'] + cube_dict['rsus-land'] + cube_dict['rlds-land'] + cube_dict['rlus-land']

        rename_cube(cube_dict['rns'], hemisphere, None, 'surface_net_radiative_flux_in_air', 'Surface Net Radiative Flux in Air', 'rns')
        rename_cube(cube_dict['rns-ocean'], hemisphere, 'ocean', 'surface_net_radiative_flux_in_air', 'Surface Net Radiative Flux in Air', 'rns')
        rename_cube(cube_dict['rns-land'], hemisphere, 'land', 'surface_net_radiative_flux_in_air', 'Surface Net Radiative Flux in Air', 'rns')
    else:
        cube_dict['rns'] = None
        cube_dict['rns-ocean'] = None
        cube_dict['rns-land'] = None

    return cube_dict


def multiply_by_area(cube):
    """Multiply by cell area."""

    if not cube.coord('latitude').has_bounds():
        cube.coord('latitude').guess_bounds()
    if not cube.coord('longitude').has_bounds():
        cube.coord('longitude').guess_bounds()
    area_weights = iris.analysis.cartography.area_weights(cube)

    units = str(cube.units)
    cube.data = cube.data * area_weights   
    cube.units = units.replace('m-2', '')

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
    for cube in cube_list:
        cube.attributes = attributes
        cube.attributes['history'] = gio.write_metadata() #file_info=metadata_dict

    return cube_list


def main(inargs):
    """Run the program."""

    sftlf_cube = iris.load_cube(inargs.sftlf_file, 'land_area_fraction')

    nh_cube_dict = {}
    sh_cube_dict = {}
    metadata_dict = {}
    attributes = {}

    # TOA radiation fluxes
    nh_cube_dict['rsdt'], sh_cube_dict['rsdt'], metadata_dict, attributes = get_data(inargs.rsdt_files, 'toa_incoming_shortwave_flux', metadata_dict, attributes)
    nh_cube_dict['rsut'], sh_cube_dict['rsut'], metadata_dict, attributes = get_data(inargs.rsut_files, 'toa_outgoing_shortwave_flux', metadata_dict, attributes)
    nh_cube_dict['rlut'], sh_cube_dict['rlut'], metadata_dict, attributes = get_data(inargs.rlut_files, 'toa_outgoing_longwave_flux', metadata_dict, attributes)

    nh_cube_dict = derived_toa_radiation_fluxes(nh_cube_dict, inargs, 'nh')
    sh_cube_dict = derived_toa_radiation_fluxes(sh_cube_dict, inargs, 'sh')

    # Surface radiation fluxes

    nh_cube_dict['rsds'], sh_cube_dict['rsds'], metadata_dict, attributes = get_data(inargs.rsds_files, 'surface_downwelling_shortwave_flux_in_air', metadata_dict, attributes)
    nh_cube_dict['rsus'], sh_cube_dict['rsus'], metadata_dict, attributes = get_data(inargs.rsus_files, 'surface_upwelling_shortwave_flux_in_air', metadata_dict, attributes)
    nh_cube_dict['rlds'], sh_cube_dict['rlds'], metadata_dict, attributes = get_data(inargs.rlds_files, 'surface_downwelling_longwave_flux_in_air', metadata_dict, attributes)
    nh_cube_dict['rlus'], sh_cube_dict['rlus'], metadata_dict, attributes = get_data(inargs.rlus_files, 'surface_upwelling_longwave_flux_in_air', metadata_dict, attributes)
    for realm in ['ocean', 'land']:
        nh_cube_dict['rsds'+'-'+realm], sh_cube_dict['rsds'+'-'+realm], metadata_dict, attributes = get_data(inargs.rsds_files, 'surface_downwelling_shortwave_flux_in_air', metadata_dict,
                                                                                                             attributes, sftlf_cube=sftlf_cube, include_only=realm)
        nh_cube_dict['rsus'+'-'+realm], sh_cube_dict['rsus'+'-'+realm], metadata_dict, attributes = get_data(inargs.rsus_files, 'surface_upwelling_shortwave_flux_in_air', metadata_dict,
                                                                                                             attributes, sftlf_cube=sftlf_cube, include_only=realm)
        nh_cube_dict['rlds'+'-'+realm], sh_cube_dict['rlds'+'-'+realm], metadata_dict, attributes = get_data(inargs.rlds_files, 'surface_downwelling_longwave_flux_in_air', metadata_dict,
                                                                                                             attributes, sftlf_cube=sftlf_cube, include_only=realm)
        nh_cube_dict['rlus'+'-'+realm], sh_cube_dict['rlus'+'-'+realm], metadata_dict, attributes = get_data(inargs.rlus_files, 'surface_upwelling_longwave_flux_in_air', metadata_dict,
                                                                                                             attributes, sftlf_cube=sftlf_cube, include_only=realm)

    nh_cube_dict = derived_surface_radiation_fluxes(nh_cube_dict, inargs, sftlf_cube, 'nh')
    sh_cube_dict = derived_surface_radiation_fluxes(sh_cube_dict, inargs, sftlf_cube, 'sh')

    # Surface heat fluxes
    if inargs.hfrealm == 'atmos':
        hfss_name = 'surface_upward_sensible_heat_flux'
        hfls_name = 'surface_upward_latent_heat_flux'
    elif inargs.hfrealm == 'ocean':
        hfss_name = 'surface_downward_sensible_heat_flux'
        hfls_name = 'surface_downward_latent_heat_flux'
    nh_cube_dict['hfss'], sh_cube_dict['hfss'], metadata_dict, attributes = get_data(inargs.hfss_files, hfss_name, metadata_dict, attributes)
    nh_cube_dict['hfls'], sh_cube_dict['hfls'], metadata_dict, attributes = get_data(inargs.hfls_files, hfls_name, metadata_dict, attributes)
    nh_cube_dict['hfds'], sh_cube_dict['hfds'], metadata_dict, attributes = get_data(inargs.hfds_files, 'surface_downward_heat_flux_in_sea_water', metadata_dict, attributes)
    nh_cube_dict['hfsithermds'], sh_cube_dict['hfsithermds'], metadata_dict, attributes = get_data(inargs.hfsithermds_files,
                                                                                                   'heat_flux_into_sea_water_due_to_sea_ice_thermodynamics',
                                                                                                    metadata_dict, attributes)                           

    # Ocean heat transport / storage
    nh_cube_dict['ohc'], sh_cube_dict['ohc'], metadata_dict, attributes = get_data(inargs.ohc_files, 'ocean_heat_content', metadata_dict, attributes)
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

    parser.add_argument("--hfrealm", type=str, choices=('atmos', 'ocean'), default='atmos',
                        help="specify whether original hfss and hfls data were atmos or ocean")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=('1850-01-01', '2005-12-31'),
                        help="Time period [default = entire]")

    args = parser.parse_args()             
    main(args)
