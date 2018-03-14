"""
Filename:     calc_hfbasin_metric.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate a northward heat transport metric

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris

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

def sum_sign(data, sign_to_keep):
    """Sum all positive or negative values and return absolute value.
    
    Args:
      data (numpy.ndarray)
      sign_to_keep (str)
      
    """

    data = data.copy()
    data = numpy.ma.asarray(data)
    
    assert sign_to_keep in ['positive', 'negative']
    if sign_to_keep == 'positive':
        mask = data < 0
    else:
        mask = data > 0
    
    data.mask = data.mask + mask
    
    return numpy.abs(data.sum(axis=1))


def calc_shape_metric(cube):
    """Calculate the shape metric.

    This metric takes into account the full shape of the
      zonally integrated northward ocean heat transport.

    """
    
    coord_names = [coord.name() for coord in cube.dim_coords]
    assert coord_names == ['time', 'latitude']
    
    lat_spacing = cube.coord('latitude').bounds[:, 1] - cube.coord('latitude').bounds[:, 0]    
    area_data = cube.data * uconv.broadcast_array(lat_spacing, 1, cube.shape)

    metric_data = sum_sign(area_data, 'positive') - sum_sign(area_data, 'negative')
    
    metric_cube = cube.extract(iris.Constraint(latitude=0))
    metric_cube.remove_coord('latitude')
    metric_cube.data = metric_data

    return metric_cube


def extract_equator(cube):
    """Extract the equator value.

    The output is technically W / lat to account for 
      models of differing resolution.

    """

    cube = cube.extract(iris.Constraint(latitude=0))
    bounds = cube.coord('latitude').bounds.flatten()
    lat_span = bounds[1] - bounds[0]
    cube.data = cube.data / lat_span

    cube.remove_coord('latitude')

    return cube


def main(inargs):
    """Run the program."""

    cube = iris.load_cube(inargs.infile, 'northward_ocean_heat_transport')

    if inargs.outtype == 'metric':
        metric_cube = calc_shape_metric(cube)
    else:
        metric_cube = extract_equator(cube)

    metric_cube.attributes['history'] = gio.write_metadata(file_info={inargs.infile: cube.attributes['history']})
    iris.save(metric_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Calculate a hfbasin metric'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument("infile", type=str, help="Input hfbasin file from calc_hfbasin.py")
    parser.add_argument("outtype", type=str, choices=('equator', 'metric'), help="Output type")            
    parser.add_argument("outfile", type=str, help="Output file")  

    args = parser.parse_args()             
    main(args)
