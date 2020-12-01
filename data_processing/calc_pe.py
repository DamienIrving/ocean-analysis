"""Calculate precipitation minus evaporation."""

import sys
script_dir = sys.path[0]
import pdb
import argparse

import iris
import cmdline_provenance as cmdprov

module_dir = script_dir.replace(script_dir.split('/')[-1], 'modules')
sys.path.append(module_dir)
try:
    import general_io as gio
except ImportError:
    raise ImportError('Script and modules in wrong directories')


def main(inargs):
    """Run the program."""

    pr_cube, pr_history = gio.combine_files(inargs.pr_files, 'precipitation_flux', checks=True)
    evap_cube, evap_history = gio.combine_files(inargs.evap_files, 'water_evapotranspiration_flux', checks=True)

    assert pr_cube.shape == evap_cube.shape
    pe_cube = pr_cube.copy()
    pe_cube.data = pr_cube.data - evap_cube.data

    iris.std_names.STD_NAMES['precipitation_minus_evaporation_flux'] = {'canonical_units': pe_cube.units}
    pe_cube.standard_name = 'precipitation_minus_evaporation_flux'
    pe_cube.long_name = 'precipitation minus evaporation flux'
    pe_cube.var_name = 'pe'
    pe_cube.attributes['history'] = cmdprov.new_log(git_repo=repo_dir)

    iris.save(pe_cube, inargs.outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--pr_files", type=str, nargs='*', required=True,
                        help="precipitation files")
    parser.add_argument("--evap_files", type=str, nargs='*', required=True,
                        help="evaporation files")

    args = parser.parse_args()            
    main(args)
