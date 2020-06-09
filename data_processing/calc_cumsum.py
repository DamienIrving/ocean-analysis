"""
Filename:     calc_cumsum.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the cumulative sum

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
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
    import convenient_universal as uconv
    import timeseries
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def main(inargs):
    """Run the program."""

    cube, history = gio.combine_files(inargs.infiles, inargs.var)
    if inargs.annual:
        cube = timeseries.convert_to_annual(cube)
    if inargs.flux_to_mag:
        cube = uconv.flux_to_magnitude(cube)

    dim_coord_names = [coord.name() for coord in cube.dim_coords]
    assert dim_coord_names[0] in ['time', 'year']
    cube.data = numpy.cumsum(cube.data, axis=0)

    cube.attributes['history'] = cmdprov.new_log(git_repo=repo_dir, infile_history={inargs.infiles[0]: history[0]})
    iris.save(cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com
    
"""

    description='Calculate cumulative sum'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input files")
    parser.add_argument("var", type=str, help="Variable standard_name")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--flux_to_mag", action="store_true", default=False,
                        help="Convert units from a flux to a magnitude [default: False]")
    parser.add_argument("--annual", action="store_true", default=False,
                        help="Output annual mean [default=False]")

    args = parser.parse_args()            
    main(args)
