"""Perform arithmetic on two files."""

import sys
script_dir = sys.path[0]
import pdb
import argparse

import iris
import cmdline_provenance as cmdprov

repo_dir = '/'.join(script_dir.split('/')[:-1])
module_dir = repo_dir + '/modules'
sys.path.append(module_dir)
try:
    import general_io as gio
except ImportError:
    raise ImportError('Script and modules in wrong directories')


def main(args):
    """Run the program."""

    metadata_dict = {}
    cubes = []
    for filename, var in args.infile:
        cube = iris.load_cube(filename, gio.check_iris_var(var))
        cubes.append(cube)
        metadata_dict[filename] = cube.attributes['history']

    if args.ref_file:
        ref_cube = iris.load_cube(args.ref_file[0], gio.check_iris_var(args.ref_file[1]))
    else:
        ref_cube = cubes[0]
   
    if args.operation == 'division':
        assert len(cubes) == 2
        outcube = cubes[0] / cubes[1]
        assert str(cubes[1].units) == 'm2'
        cube1_units = str(cubes[0].units)
        new_units = f'{cube1_units} m-2'
    elif args.operation == 'addition':
        outcube = cubes[0]
        for cube in cubes[1:]:
            outcube = outcube + cube
        new_units = None

    outcube.attributes = ref_cube.attributes
    if new_units:
        outcube.units = new_units
    outcube.var_name = ref_cube.var_name
    outcube.long_name = ref_cube.long_name
    if ref_cube.standard_name:
        outcube.standard_name = ref_cube.standard_name
    else:
        standard_name = ref_cube.long_name.replace(' ', '_')
        iris.std_names.STD_NAMES[standard_name] = {'canonical_units': outcube.units}
        outcube.standard_name = standard_name

    outcube.attributes['history'] = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    iris.save(outcube, args.outfile)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("operation", type=str, choices=('division', 'addition'), help="Operation")
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--infile", type=str, action='append', nargs=2, default=[],
                        help="Input file and variable name")
    parser.add_argument("--ref_file", type=str, nargs=2, default=None,
                        help="Reference file and variable name")

    args = parser.parse_args()
    main(args)
