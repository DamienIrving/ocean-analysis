"""
Filename:     calc_amoc_metric.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the AMOC metric

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
    import convenient_universal as uconv
    import timeseries
    import spatial_weights
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

history = []

basin_index = {'pacific': 1,
               'atlantic': 0,
               'globe': 2}

def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history']) 

    
def main(inargs):
    """Run the program."""

    region_constraint = iris.Constraint(region='atlantic_arctic_ocean')   # "atlantic_arctic_ocean", "indian_pacific_ocean ", "global_ocean         "
    cube = iris.load(inargs.infiles, 'ocean_meridional_overturning_mass_streamfunction' & region_constraint, callback=save_history)
    if not cube:
       cube = iris.load(inargs.infiles, 'ocean_meridional_overturning_mass_streamfunction', callback=save_history)
       equalise_attributes(cube)
       cube = cube.concatenate_cube()
       cube = cube[:, 0, : ,:]   # index for Atlantic
    else:   
        equalise_attributes(cube)
        cube = cube.concatenate_cube()
        cube.remove_coord('region')

    cube = gio.check_time_units(cube)

    cube = timeseries.convert_to_annual(cube)

    target_lat, error = uconv.find_nearest(cube.coord('latitude').points, 30, index=False)
    cube = cube.extract(iris.Constraint(latitude=target_lat))
    cube.remove_coord('latitude')

    assert str(cube.units) == 'kg s-1'
    cube.data = (cube.data / 1023) / 1e+6
    cube.units = 'Sv'

    #dim_coord_names = [coord.name() for coord in cube.dim_coords]
    #vert_extents = spatial_weights.calc_vertical_weights_1D(cube.coord('depth'), dim_coord_names, cube.shape)
    
    metric = cube.collapsed('depth', iris.analysis.MAX)
    metric.remove_coord('depth')
    
    try:
        metric.attributes['history'] = gio.write_metadata(file_info={inargs.infiles[0]: cube.attributes['history']})
    except KeyError:
        pass
    iris.save(metric, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Calculate the AMOC metric (annual-mean maximum volume transport streamfunction at 30N)'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                                            
    parser.add_argument("infiles", type=str, nargs='*', help="Input msftmyz files")  
    parser.add_argument("outfile", type=str, help="Output file")  

    args = parser.parse_args()             
    main(args)
