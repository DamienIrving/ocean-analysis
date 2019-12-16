#!/bin/bash
#
# Description: Run regrid.py over a bunch of files
#             

function usage {
    echo "USAGE: bash $0 var infiles"
    echo "   var:          Input variable"
    echo "   infiles:      Input file names"
    exit 1
}

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

var=$1
shift
infiles=($@)

for infile in "${infiles[@]}"; do
 
    outfile=`echo ${infile} | sed s:data1b/oi10/replicas:data/r87/dbi599:`
    outfile=`echo ${outfile} | sed s:gn:gr:g`

    command="${python} ${script_dir}/regrid.py ${infile} ${var} ${outfile} --lats -89.5 89.5 1.0 --lons 0.5 359.5 1"

    echo ${command}
    ${command}
    echo ${outfile}

done
