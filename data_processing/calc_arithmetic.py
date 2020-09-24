"""Perform arithmetic on two files."""

# Import general Python modules

import sys, os, pdb
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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')

# Define functions

def main(args):
    """Run the program."""

    cube1 = iris.load_cube(args.infile1, gio.check_iris_var(args.var1))
    cube2 = iris.load_cube(args.infile2, gio.check_iris_var(args.var2))
    
    if args.operation == 'division':
        outcube = cube1 / cube2

    outcube.attributes = cube1.attributes
    cube1_units = str(cube1.units)
    assert str(cube2.units) == 'm2'
    outcube.units = f'{cube1_units} m-2'
    outcube.var_name = cube1.var_name
    outcube.long_name = cube1.long_name
    if cube1.standard_name:
        outcube.standard_name = cube1.standard_name
    else:
        standard_name = cube1.long_name.replace(' ', '_')
        iris.std_names.STD_NAMES[standard_name] = {'canonical_units': outcube.units}
        outcube.standard_name = standard_name

    metadata_dict = {}
    metadata_dict[args.infile1] = cube1.attributes['history']
    metadata_dict[args.infile2] = cube2.attributes['history']
    outcube.attributes['history'] = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    iris.save(outcube, args.outfile)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("infile1", type=str, help="Input file 1")
    parser.add_argument("var1", type=str, help="Input variable 1")
    parser.add_argument("infile2", type=str, help="Input file 2")
    parser.add_argument("var2", type=str, help="Input variable 2")
    parser.add_argument("operation", type=str, choices=('division'), help="Operation")
    parser.add_argument("outfile", type=str, help="Output file")
    args = parser.parse_args()
    main(args)
