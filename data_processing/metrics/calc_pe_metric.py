"""
Filename:     calc_pe_metric.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate P-E metric

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
from scipy.interpolate import interp1d
import iris
import iris.coord_categorisation
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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')

# Define functions

history = []

def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def pe_amplitude(xdata, ydata, hemisphere):
    """Calculate the amplitude of the zonal mean P-E"""

    if (hemisphere == 'sh'):
        selection = (xdata < 0)
        y_filtered = numpy.where(selection, ydata, 0)
    elif (hemisphere == 'nh'):
        selection = (xdata > 0)
        y_filtered = numpy.where(selection, ydata, 0)
    else:
        y_filtered = ydata.copy() 
    
    amplitude = numpy.sum(numpy.abs(y_filtered))
    
    return amplitude


def create_outcubes(metric_dict, atts, units, time_coord):
    """Create an iris cube for each metric."""
   
    cube_list = []
    for hemisphere, data in metric_dict.items():
        standard_name = 'pe_amplitude_%s' %(hemisphere)
        long_name = 'pe amplitude %s' %(hemisphere)
        var_name = 'pe_amp_%s' %(hemisphere)
        iris.std_names.STD_NAMES[standard_name] = {'canonical_units': units}
        metric_cube = iris.cube.Cube(data,
                                     standard_name=standard_name,
                                     long_name=long_name,
                                     var_name=var_name,
                                     units=units,
                                     attributes=atts,
                                     dim_coords_and_dims=[(time_coord, 0)],
                                     )
        cube_list.append(metric_cube)        

    cube_list = iris.cube.CubeList(cube_list)
    cube_list = cube_list.concatenate()

    return cube_list


def main(inargs):
    """Run the program."""

    # Read data
    cube = iris.load(inargs.infiles, 'precipitation minus evaporation flux', callback=save_history)
    equalise_attributes(cube)
    iris.util.unify_time_units(cube)
    cube = cube.concatenate_cube()
    cube = gio.check_time_units(cube)

    # Prepare data
    cube = timeseries.convert_to_annual(cube)    
    zonal_mean_cube = cube.collapsed('longitude', iris.analysis.MEAN)

    # Calculate metrics
    xdata = cube.coord('latitude').points
    xnew = numpy.linspace(xdata[0], xdata[-1], num=1000, endpoint=True)

    metric_dict = {'nh': [], 'sh': [], 'globe': []}
    for ycube in zonal_mean_cube.slices(['latitude']):
        func = interp1d(xdata, ycube.data, kind='cubic')
        ynew = func(xnew)
        for hemisphere in ['nh', 'sh', 'globe']:
            amp = pe_amplitude(xnew, ynew, hemisphere)
            metric_dict[hemisphere].append(amp)

    # Write the output file
    atts = cube.attributes
    infile_history = {inargs.infiles[0]: history[0]}
    atts['history'] = gio.write_metadata(file_info=infile_history)
    cube_list = create_outcubes(metric_dict, cube.attributes, cube.units, cube.coord('time'))

    iris.save(cube_list, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com

"""

    description='Calculate P-E metric'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="P-E data files")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    args = parser.parse_args()            

    main(args)
