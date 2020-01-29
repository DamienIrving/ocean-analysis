"""
Filename:     plot_regression_boxplot.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot regression coefficients from drift analysis  

"""

# Import general Python modules

import sys
import os
import re
import pdb
import argparse

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import cmdline_provenance as cmdprov

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'ocean-analysis':
        break


# Define functions 

def set_legend(ax):
    """Set the legend"""
    
    label_dict = {"netTOA vs hfds": "$Q_r$ vs. $Q_h$",
                  "hfds vs thermal OHC": "$Q_h$ vs. $H_T$",
                  "netTOA vs thermal OHC": "$Q_r$ vs. $H_T$",
                  "wfo vs masso": "$Q_m$ vs. $M$",
                  "wfo vs soga": "$Q_m$ vs. $S$",
                  "masso vs soga": "$M$ vs. $S$"}
    
    handles, old_labels = ax.get_legend_handles_labels()
    new_labels = []
    for label in old_labels:
        new_labels.append(label_dict[label])
    loc = 1 if "wfo vs masso" in old_labels else 4
    ax.legend(handles=handles, labels=new_labels, loc=loc) #fontsize=8
    

def main(inargs):
    """Run the program."""

    df = pd.read_csv(inargs.infile)

    fig, axes =plt.subplots(1,2)
    sns.set(style="whitegrid")
    
    sns.boxplot(x="project", y="regression coefficient", hue="comparison",
                data=df[df['realm'] == 'energy'], ax=axes[0], palette='hot')
    axes[0].set_title('(a) heat budget')
    axes[0].set_ylim(-0.25, 1.75)
    axes[0].axhline(y=1.0, color='0.5', linewidth=0.2)
    set_legend(axes[0])
    
    sns.boxplot(x="project", y="regression coefficient", hue="comparison",
                data=df[df['realm'] == 'mass'], ax=axes[1], palette='GnBu_r')
    axes[1].set_title('(b) mass budget')
    axes[1].set_ylim(-0.25, 1.75)
    axes[1].axhline(y=1.0, color='0.5', linewidth=0.2)
    set_legend(axes[1])
    
    for ax in axes.flat:
        ax.label_outer()
    
    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=200)
    log_file = re.sub('.png', '.met', inargs.outfile)
    log_text = cmdprov.new_log(git_repo=repo_dir)
    cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot regression coefficients from drift analysis'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("outfile", type=str, help="Output file name")

    args = parser.parse_args()  
    main(args)
