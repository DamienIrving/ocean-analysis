"""Plot output from calc_pe_spatial_totals.py for globe basin only"""

# Import general Python modules

import sys, os, pdb
import argparse
import matplotlib.pyplot as plt
import iris
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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def get_data(infile, variable, time_constraint):
    """Get the data for a particular model"""
    
    cube, history = gio.combine_files(infile, variable, new_calendar='365_day')
    #cube = iris.load_cube(infile, 'precipitation minus evaporation flux' & time_constraint)
    cube = cube.extract(time_constraint)
    iris.coord_categorisation.add_year(cube, 'time')
    assert cube.ndim == 3
    start_data = cube[0, 0:-1, -1].data
    anomaly_data = cube[:, 0:-1, -1].data - start_data
    
    return cube, anomaly_data, start_data


def main(inargs):
    """Run the program."""

    time_constraint = gio.get_time_constraint(inargs.time_bounds)
    
    anomaly_data = {}
    start_data = {}
    
    hist_cube, anomaly_data['historical'], start_data['historical'] = get_data(inargs.hist_file, inargs.variable, time_constraint)
    ghg_cube, anomaly_data['GHG-only'], start_data['GHG-only'] = get_data(inargs.ghg_file, inargs.variable, time_constraint)
    if inargs.aa_file:
        aa_cube, anomaly_data['AA-only'], start_data['AA-only'] = get_data(inargs.aa_file, inargs.variable, time_constraint)
    else:
        aa_cube = anomaly_data['AA-only'] = start_data['AA-only'] = None
    units = str(hist_cube.units)   

    fig = plt.figure(figsize=[16,12])
    ax0 = plt.subplot2grid((3,6), (0,2), colspan=2)
    ax1 = plt.subplot2grid(shape=(3,6), loc=(1,0), colspan=2)
    ax2 = plt.subplot2grid((3,6), (1,2), colspan=2)
    ax3 = plt.subplot2grid((3,6), (1,4), colspan=2)
    ax4 = plt.subplot2grid((3,6), (2,1), colspan=2)
    ax5 = plt.subplot2grid((3,6), (2,3), colspan=2)

    xvals = [0, 1, 2, 3, 4]
    ax0.bar(xvals, start_data['historical'], color='0.5')
    ax0.set_ylabel(units)
    ax0.set_xticklabels(['', 'SH precip', 'SH evap', 'trop precip', 'NH evap', 'NH precip'])
    ax0.set_title('Year One')

    hist_years = hist_cube.coord('year').points
    ghg_years = ghg_cube.coord('year').points
    if aa_cube:
        aa_years = aa_cube.coord('year').points
        
    ax1.plot(ghg_years, anomaly_data['GHG-only'][:,0], color='red', label='GHG-only')
    ax1.plot(hist_years, anomaly_data['historical'][:,0], color='black', label='historical')
    if aa_cube:
        ax1.plot(aa_years, anomaly_data['AA-only'][:,0], color='blue', label='AA-only')
    ax1.set_title('SH precip')
    ax1.set_ylabel(f'time-integrated anomaly ({units})')
    ax1.grid(True, color='0.8', linestyle='--')
    ax1.legend()

    ax4.plot(ghg_years, anomaly_data['GHG-only'][:,1], color='red', label='GHG-only')
    ax4.plot(hist_years, anomaly_data['historical'][:,1], color='black', label='historical')
    if aa_cube:
        ax4.plot(aa_years, anomaly_data['AA-only'][:,1], color='blue', label='AA-only')
    ax4.set_title('SH evap')
    ax4.set_ylabel(f'time-integrated anomaly ({units})')
    ax4.grid(True, color='0.8', linestyle='--')

    ax2.plot(ghg_years, anomaly_data['GHG-only'][:,2], color='red', label='GHG-only')
    ax2.plot(hist_years, anomaly_data['historical'][:,2], color='black', label='historical')
    if aa_cube:
        ax2.plot(aa_years, anomaly_data['AA-only'][:,2], color='blue', label='AA-only')
    ax2.set_title('tropical precip')
    ax2.grid(True, color='0.8', linestyle='--')

    ax5.plot(ghg_years, anomaly_data['GHG-only'][:,3], color='red', label='GHG-only')
    ax5.plot(hist_years, anomaly_data['historical'][:,3], color='black', label='historical')
    if aa_cube:
        ax5.plot(aa_years, anomaly_data['AA-only'][:,3], color='blue', label='AA-only')
    ax5.set_title('NH evap')
    ax5.grid(True, color='0.8', linestyle='--')

    ax3.plot(ghg_years, anomaly_data['GHG-only'][:,4], color='red', label='GHG-only')
    ax3.plot(hist_years, anomaly_data['historical'][:,4], color='black', label='historical')
    if aa_cube:
        ax3.plot(aa_years, anomaly_data['AA-only'][:,4], color='blue', label='AA-only')
    ax3.set_title('NH precip')
    ax3.grid(True, color='0.8', linestyle='--')

    if inargs.ymax:
        ax1.set_ylim([-inargs.ymax, inargs.ymax])
        ax2.set_ylim([-inargs.ymax, inargs.ymax])
        ax3.set_ylim([-inargs.ymax, inargs.ymax])
        ax4.set_ylim([-inargs.ymax, inargs.ymax])
        ax5.set_ylim([-inargs.ymax, inargs.ymax])

    plt.suptitle(inargs.variable)
    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info={inargs.hist_file: hist_cube.attributes['history']})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                    
    parser.add_argument("hist_file", type=str, help="historical file")
    parser.add_argument("ghg_file", type=str, help="GHG file")
    parser.add_argument("aa_file", type=str, help="aa file")
    parser.add_argument("variable", type=str, help="variable")
    parser.add_argument("outfile", type=str, help="Output file") 

    parser.add_argument("--time_bounds", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=('1850-01-01', '2014-12-31'), help="Time period [default = entire]")
    parser.add_argument("--ymax", type=float, default=None, help='y axis limit')

    args = parser.parse_args()             
    main(args)
