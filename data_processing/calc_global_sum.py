"""Calculate global sum."""

# Import general Python modules

import sys, os, pdb, re
import argparse
import iris
import cmdline_provenance as cmdprov
import pandas as pd
import iris.coord_categorisation

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
    import spatial_weights
    import timeseries
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def main(inargs):
    """Run the program."""

    assert inargs.var == 'precipitation_flux'

    if inargs.area_file:
        area_cube = gio.get_ocean_weights(inargs.area_file)
    else:
        area_cube = None

    output_cubelist = iris.cube.CubeList([])
    for infile in inargs.infiles:
        cube = iris.load_cube(infile, inargs.var) # kg m-2 s-1 (monthly, gridded)
        coord_names = [coord.name() for coord in cube.dim_coords]
        aux_coord_names = [coord.name() for coord in cube.aux_coords] 
        days_in_year = timeseries.get_days_in_year(cube)

        cube = spatial_weights.multiply_by_area(cube, area_cube=area_cube) # kg s-1 (monthly, gridded)
        cube = cube.collapsed(coord_names[1:], iris.analysis.SUM) # kg s-1 (monthly, globe)
        cube = timeseries.flux_to_total(cube) # kg (monthly, globe)
        cube = timeseries.convert_to_annual(cube, aggregation='sum') # kg (annual, globe)        
        cube.data = cube.data / 5.1e14 # kg m-2 = mm (annual, globe)        
        cube.data = cube.data / days_in_year.values # mm/day (annual, globe)

        cube.units = 'mm/day'
        for coord in coord_names[1:] + aux_coord_names:
            cube.remove_coord(coord)
        output_cubelist.append(cube)
        print(infile)
 
    outcube = gio.combine_cubes(output_cubelist)
    metadata_dict = {}
    metadata_dict[infile] = cube.attributes['history']
    if inargs.area_file:
        metadata_dict[inargs.area_file] = area_cube.attributes['history'] 
    outcube.attributes['history'] = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    iris.save(outcube, inargs.outfile)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                     
    parser.add_argument("infiles", type=str, nargs='*', help="Input files")
    parser.add_argument("var", type=str, help="Input variable")
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--area_file", type=str, default=None,
                        help="Area file (required for curvilinear grids)")

    args = parser.parse_args()
    main(args)
