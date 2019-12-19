#!/bin/bash
#
# Description: The BCC CMIP6 models have auxillary latitude and longitude coordinates
# that need to be removed.
#             

function usage {
    echo "USAGE: bash $0 infiles"
    echo "   infiles:      Input file names"
    exit 1
}

infiles=($@)
for infile in "${infiles[@]}"; do
 
    outfile=`echo ${infile} | sed s:data1b/oi10/replicas:data/r87/dbi599:`

    command1="ncks -C -O -x -v latitude ${infile} ${outfile}"
    echo ${command1}
    ${command1}

    command2="ncks -C -O -x -v longitude ${outfile} ${outfile}"
    echo ${command2}
    ${command2}

done
