#!/bin/bash
#
# Description: Run calc_horizontal_aggregate.py over a bunch of files
#             

function usage {
    echo "USAGE: bash $0 var outdir infiles"
    echo "   var:          Variable (so or thetao)"
    echo "   outdir:       Output directory"
    echo "   infiles:      Input file names"
    exit 1
}

python=/g/data/e14/dbi599/miniconda3/envs/cmip/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing
var=$1
outdir=$2
shift
shift
infiles=($@)
basin_file=/g/data/e14/dbi599/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/historical/r1i1p1f1/Ofx/basin/gn/v20191108/basin_Ofx_ACCESS-CM2_historical_r1i1p1f1_gn.nc
volume_file=/g/data/fs38/publications/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/historical/r1i1p1f1/Ofx/volcello/gn/v20191108/volcello_Ofx_ACCESS-CM2_historical_r1i1p1f1_gn.nc

if [[ "${var}" == "so" ]] ; then
    long_var=sea_water_salinity
elif [[ "${var}" == "thetao" ]] ; then
    long_var=sea_water_potential_temperature
fi

for infile in "${infiles[@]}"; do
    filename=`echo ${infile} | rev | cut -d / -f 1 | rev`
    outfile=`echo ${filename} | sed s:${var}_:${var}-globe-zonal-mean_:`
    command="${python} ${script_dir}/calc_horizontal_aggregate.py ${infile} ${long_var} zonal mean ${outdir}/${outfile} --basin ${basin_file} globe --weights ${volume_file}"
    echo ${command}
    ${command}
    echo ${outdir}/${outfile}
done
