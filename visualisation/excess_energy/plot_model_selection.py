"""
Filename:     plot_model_selection.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot the globally accumulated excess energy

"""

# Import general Python modules

import sys, os, pdb, re
import argparse
import numpy
import pandas

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.transforms as transforms
import seaborn as sns
sns.set_context('talk')

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

def add_legends():
    """ """
    
    custom_lines = [Line2D([0], [0], color='black', lw=4),
                    Line2D([0], [0], color='red', lw=4),
                    Line2D([0], [0], color='blue', lw=4)]

    legend_elements = [Line2D([0], [0], marker='s', color='w', label='netTOA',
                       markerfacecolor='w', markeredgecolor='grey'),
                       Line2D([0], [0], marker='o', color='w', label='OHU',
                       markerfacecolor='w', markeredgecolor='grey'),
                       Line2D([0], [0], marker='D', color='w', label='OHC',
                       markerfacecolor='w', markeredgecolor='grey')]

    # Create a legend for the first line
    first_legend = plt.legend(custom_lines, ['historical', 'GHG-only', 'AA-only'], loc=2)

    # Add the legend manually to the current Axes
    ax = plt.gca().add_artist(first_legend)

    # Create another legend for the second line
    plt.legend(handles=legend_elements, loc=3)
    

def main(inargs):
    """Run the program."""

    df = pandas.read_csv(inargs.infile)
    
    colors = {'historical': 'black', 'GHG-only': 'red', 'AA-only': 'blue'}

    fig, ax = plt.subplots(figsize=(16,10))

    offset = lambda p: transforms.ScaledTranslation(p/72.,0, plt.gcf().dpi_scale_trans)
    trans = plt.gca().transData

    for experiment in ['historical', 'GHG-only', 'AA-only']:
        toa_vals = numpy.array(df.loc[(df['variable'] == 'netTOA') & (df['experiment'] == experiment)]['accumulated_heat'])
        ohu_vals = numpy.array(df.loc[(df['variable'] == 'OHU') & (df['experiment'] == experiment)]['accumulated_heat'])
        ohc_vals = numpy.array(df.loc[(df['variable'] == 'OHC') & (df['experiment'] == experiment)]['accumulated_heat'])
        xvals = numpy.arange(toa_vals.shape[0])
    
        plt.scatter(xvals, toa_vals, c=colors[experiment], marker='s', transform=trans+offset(-5))
        plt.scatter(xvals, ohu_vals, c=colors[experiment])
        plt.scatter(xvals, ohc_vals, c=colors[experiment], marker='D', transform=trans+offset(5))
    
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True)
    ax.yaxis.major.formatter._useMathText = True
    
    plt.xticks(xvals, list(df.model.unique()), rotation=40, ha='right')
    ax.axhline(y=0, color='0.5', linestyle='--', linewidth=0.5)
    add_legends()
    plt.ylabel('J')
    
    plt.savefig(inargs.outfile, bbox_inches='tight')

    log_text = cmdprov.new_log(git_repo=repo_dir)
    log_file = re.sub('.png', '.met', inargs.outfile)
    cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot the globally accumulated excess energy'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="input csv file") 
    parser.add_argument("outfile", type=str, help="output file")                               
    
    args = parser.parse_args()             
    main(args)
