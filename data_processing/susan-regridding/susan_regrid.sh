#!/bin/bash
#
# Description: Run regrid.py over a bunch of files
#             

function usage {
    echo "USAGE: bash $0 infiles"
    echo "   infiles:      Input file names"
    echo "  e.g. bash $0 /g/data/ua6/DRSv3/CMIP5/CCSM4/historical/mon/ocean/r1i1p1/thetao/latest/thetao_Omon_CCSM4_historical_r1i1p1_??????-??????.nc"
    exit 1
}

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

infiles=($@)

for infile in "${infiles[@]}"; do
 
    outfile=`echo ${infile} | sed s:ua6:r87/dbi599:`
    outfile=`echo ${outfile} | sed s:Omon:Oyr:`
    outfile=`echo ${outfile} | sed s:/mon/:/yr/:`
    outfile=`echo ${outfile} | sed s:DRSv3:DRSv2:`
    outfile=`echo ${outfile} | sed s:.nc:_susan-grid.nc:`
    command="${python} ${script_dir}/regrid.py ${infile} sea_water_potential_temperature ${outfile} --annual --lats -80 80 1.0 --lons 2 360 2 --levs 0 5 10 20 30 40 50 60 70 75 80 90 100 110 120 125 130 140 150 160 170 175 180 190 200 210 220 225 230 240 250 260 270 275 280 290 300 325 350 375 400 425 450 475 500 550 600 650 700 750 800 850 900 950 1000 1100 1200 1300 1400 1500 1600 1700 1750 1800 1900 2000" #--chunk

    echo ${command}
    ${command}
    echo ${outfile}

done
