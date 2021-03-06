"""
Filename:     plot_delsole.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Recreate plot from DelSole et al (2016)

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import matplotlib.pyplot as plt
import seaborn
seaborn.set_context("talk")   #, font_scale=1.4)
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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

experiment_names = {('CanESM2', 'historicalMisc', 4): 'historicalAA',
                    ('CSIRO-Mk3-6-0', 'historicalMisc', 3): 'noAA',
                    ('CSIRO-Mk3-6-0', 'historicalMisc', 4): 'historicalAA',
                    ('IPSL-CM5A-LR', 'historicalMisc', 3): 'historicalAA',
                    ('IPSL-CM5A-LR', 'historicalMisc', 4): 'noAA',
                    ('GFDL-CM3', 'historicalMisc', 1): 'historicalAA'}

experiment_colors = {'historicalGHG': 'r',
                     'noAA': 'g',
                     'historicalAA': 'b',
                     'historical': 'y',
                     'piControl': '0.5',
                     '1pctCO2': 'k',
                     'rcp85': 'c',
                     'rcp45': 'm',
                     'rcp26': 'g'} 

var_label_dict = {'sea_surface_salinity': ('surface salinity', 'g/kg'),
                  'precipitation_flux': ('precipitation',  'mm/day'),
                  'water_evaporation_flux': ('evaporation', 'mm/day'),
                  'air_temperature': ('surface air temperature', 'K'),
                  'sea_water_salinity': ('ocean salinity', 'g/kg'),
                  'precipitation minus evaporation flux': ('P-E', 'mm/day')}


def get_label(var, metric):
    """Get axis label"""

    name, units = var_label_dict[var]

    if metric == 'mean':
        label = 'Global mean %s (%s)'  %(name, units)
    elif metric == 'grid-deviation':
        label = 'Global mean %s grid deviation (%s)'  %(name, units)
    elif metric == 'bulk-deviation':
        label = 'Global mean %s bulk deviation (%s)'  %(name, units)  

    return label, units


def check_attributes(x_cube, y_cube):
    """Check that attributes match and return experiment."""

    # FIXME: Need to handle obs attributes

    x_model = x_cube.attributes['model_id']
    x_experiment = x_cube.attributes['experiment_id']
    x_physics = x_cube.attributes['physics_version']

    y_model = y_cube.attributes['model_id']
    y_experiment = y_cube.attributes['experiment_id']
    y_physics = y_cube.attributes['physics_version']

    assert x_model == y_model
    assert x_experiment == y_experiment
    assert x_physics == y_physics

    atts = (x_model, x_experiment, float(x_physics))

    if atts in list(experiment_names.keys()):
        experiment = experiment_names[atts]
    else:
        experiment = x_experiment

    return experiment, x_model


def calc_trend(x_data, y_data, experiment):
    """Calculate linear trend.

    polyfit returns [a, b] corresponding to y = a + bx

    """

    a_coefficient, b_coefficient = numpy.polynomial.polynomial.polyfit(x_data, y_data, 1)
    x_trend = numpy.arange(x_data.min(), x_data.max(), 0.01)
    y_trend = a_coefficient + b_coefficient * x_trend
    print(experiment, 'trend:', b_coefficient)

    mean_value = y_data.mean()
    pct_change = (b_coefficient / mean_value) * 100

    return x_trend, y_trend, pct_change


def get_data(data, var):
    """Adjust data units if required"""

    if var in ['precipitation_flux', 'water_evaporation_flux', 'precipitation minus evaporation flux']:
        data = data * 86400

    return data


def fix_var_name(var):
    """Fix variable name.

    Iris won't accept a non-standard standard_name,
      so you have to pass the long_name instead

    """

    if var == 'precipitation_minus_evaporation_flux':
        var = 'precipitation minus evaporation flux'
    
    return var


def main(inargs):
    """Run the program."""
 
    data_dict = {}
    for experiment in list(experiment_colors.keys()):
        data_dict[(experiment, 'x_data')] = numpy.array([]) 
        data_dict[(experiment, 'y_data')] = numpy.array([])

    xvar = fix_var_name(inargs.xvar)
    yvar = fix_var_name(inargs.yvar)
    metadata_dict = {}
    for file_pair in inargs.file_pair:      
        xfile, yfile = file_pair

        x_cube = iris.load_cube(xfile, xvar)
        
        y_cube = iris.load_cube(yfile, yvar)
        experiment, model = check_attributes(x_cube, y_cube)
        metadata_dict[xfile] = x_cube.attributes['history']
        metadata_dict[yfile] = y_cube.attributes['history']

        data_dict[(experiment, 'x_data')] = numpy.append(data_dict[(experiment, 'x_data')], get_data(x_cube.data, xvar))
        data_dict[(experiment, 'y_data')] = numpy.append(data_dict[(experiment, 'y_data')], get_data(y_cube.data, yvar))

    xlabel, xunits = get_label(xvar, inargs.xmetric)
    ylabel, yunits = get_label(yvar, inargs.ymetric)
    fig = plt.figure(figsize=(12,8))
    annotation_vertical_pos = 0.96
    for experiment, color in experiment_colors.items():
        x_data = data_dict[(experiment, 'x_data')]
        y_data = data_dict[(experiment, 'y_data')]

        if numpy.any(x_data):
            plt.scatter(x_data[::inargs.thin], y_data[::inargs.thin], facecolors='none', edgecolors=color, label=experiment)
            x_trend, y_trend, pct_change = calc_trend(x_data, y_data, experiment)
            plt.plot(x_trend, y_trend, color=color)

            if 'temperature' in xvar:
                trend_annotation = str(round(pct_change, 2)) + '% $' + xunits +'^{-1}$' 
                plt.annotate(trend_annotation, xy=(0.02, annotation_vertical_pos), xycoords='axes fraction', color=color)
                annotation_vertical_pos = annotation_vertical_pos - 0.04 

    plt.legend(loc=4)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(model)

    # Write output
    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com
    
"""

    description='Recreate plot from DelSole et al (2016)'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("outfile", type=str, help="Output file name")
    parser.add_argument("xvar", type=str, help="x-axis variable")
    parser.add_argument("yvar", type=str, help="y-axis variable")
    parser.add_argument("xmetric", type=str, choices=('bulk-deviation', 'grid-deviation', 'mean'), help="x-axis metric type")
    parser.add_argument("ymetric", type=str, choices=('bulk-deviation', 'grid-deviation', 'mean'), help="y-axis metric type")

    parser.add_argument("--file_pair", type=str, action='append', default=[], nargs=2, metavar=('XFILE', 'YFILE'),
                        help="File pair")
    parser.add_argument("--thin", type=int, default=1,
                        help="Stride for thinning the data (e.g. 3 will keep one-third of the data) [default: 1]")

    args = parser.parse_args()            
    main(args)
