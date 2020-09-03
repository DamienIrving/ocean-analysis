"""Calculate global sum."""

# Import general Python modules

import sys, os, pdb, re
import argparse
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

    if inargs.area_file:
        area_cube = gio.get_ocean_weights(inargs.area_file)
    else:
        area_cube = None

    output_cubelist = iris.cube.CubeList([])
    for infile in inargs.infiles:
        cube = iris.load_cube(infile, inargs.invar)
        coord_names = [coord.name() for coord in cube.dim_coords]
        aux_coord_names = [coord.name() for coord in cube.aux_coords]
        ndim = cube.ndim

        if area_cube:
            area_array = uconv.broadcast_array(area_cube.data, [ndim - 2, ndim - 1], cube.shape)
            assert 'm-2' in str(cube.units)
            cube.units = str(cube.units).replace('m-2', '')
            cube.data = cube.data * area_array

        gs = cube.collapsed(coord_names[1:], iris.analysis.SUM)
        for coord in coord_names[1:] + aux_coord_names:
            gs.remove_coord(coord)

        output_cubelist.append(gs)
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
    parser.add_argument("invar", type=str, help="Input variable")
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--area_file", type=str, help="Area file (for multiplying data by m2)")

    args = parser.parse_args()
    main(args)
