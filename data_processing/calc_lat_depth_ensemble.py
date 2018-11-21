"""
Filename:     calc_lat_depth_ensemble.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  calculate the ensemble aggregate for zonally integrated ocean data (i.e. time, depth, lat)

"""

# Import general Python modules

import sys, os, pdb
import argparse
import iris
from iris.experimental.equalise_cubes import equalise_attributes
import cmdline_provenance as cmdprov

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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def regrid_cube(cube, ref_cube):
    """Regrid to the reference cube grid."""
    
    sample_points = [('depth', ref_cube.coord('depth').points),
                     ('latitude',  ref_cube.coord('latitude').points)]

    cube = cube.interpolate(sample_points, iris.analysis.Linear())
    cube.coord('latitude').bounds = ref_cube.coord('latitude').bounds
    cube.coord('depth').bounds = ref_cube.coord('depth').bounds

    return cube


def calc_ensemble(cube_list, agg_method):
    """Calculate the ensemble"""
    
    agg_functions = {'mean': iris.analysis.MEAN,
                     'median': iris.analysis.MEDIAN}
 
    common_mask = cube_list[0].data.mask
    for cube in cube_list[1:]:
        common_mask = common_mask + cube.data.mask
 
    equalise_attributes(cube_list)
    iris.util.unify_time_units(cube_list)
    ensemble_cube = cube_list.merge_cube()
    ensemble_agg = ensemble_cube.collapsed('ensemble_member', agg_functions[agg_method])
    
    ensemble_agg.data.mask = common_mask
    
    return ensemble_agg


def main(inargs):
    """Run the program."""

    metadata_dict = {}

    if inargs.ref_file:
        ref_cube = iris.load_cube(inargs.ref_file[0], inargs.ref_file[1])
    else:
        ref_cube = None

    cube_list = iris.cube.CubeList([])
    for fnum, filename in enumerate(inargs.infiles):
        cube = iris.load_cube(filename, gio.check_iris_var(inargs.var))
        #coord_names = [coord.name() for coord in cube.dim_coords]
        new_aux_coord = iris.coords.AuxCoord(fnum, long_name='ensemble_member', units='no_unit')
        cube.add_aux_coord(new_aux_coord)
        if ref_cube:
            cube = regrid_cube(cube, ref_cube)
        else:
            ref_cube = cube.copy()        
        cube_list.append(cube)
       
    ensemble_agg = calc_ensemble(cube_list, inargs.aggregation)   
       
    metadata_dict[filename] = cube.attributes['history']
    ensemble_agg.attributes['history'] = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    iris.save(ensemble_agg, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Calculate the ensemble aggregate for zonally integrated ocean data (i.e. time, depth, lat)'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                     
    parser.add_argument("infiles", type=str, nargs='*', help="input file")
    parser.add_argument("var", type=str, help="variable")
    parser.add_argument("aggregation", type=str, choices=('mean', 'median'), help="method for ensemble aggregation")
    parser.add_argument("outfile", type=str, help="output file")

    parser.add_argument("--ref_file", type=str, nargs=2, metavar=('FILE', 'VARIABLE'), default=None,
                        help="reference grid for output")

    args = parser.parse_args()            
    main(args)
