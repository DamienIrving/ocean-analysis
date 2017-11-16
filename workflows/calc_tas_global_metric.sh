#
# Description: Script for calculating global metrics
#

function usage {
    echo "USAGE: bash $0 model metric datadir experiment runs"
    echo "   e.g. bash $0 CSIRO-Mk3-6-0 tas-global-mean ua6 historical r1i1p1 r1i1p2 r1i1p3"
    echo "   metric choices: tas-global-mean  tas-ita "
    exit 1
}

model=$1
metric=$2
datadir=$3
experiment=$4
shift
shift
shift
shift
runs=( $@ )

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python

for run in "${runs[@]}"; do
    
    data_file=`ls /g/data/${datadir}/DRSv2/CMIP5/${model}/${experiment}/mon/atmos/${run}/tas/latest/tas_Amon_${model}_${experiment}_${run}*.nc`
    standard_name=air_temperature
    outdir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}/${experiment}/yr/atmos/${run}/tas/latest
    mkdir -p ${outdir}

    if [[ "${metric}" == "tas-global-mean" ]] ; then
        agg=mean
        outname=`echo ${data_file} | rev | cut -d / -f 1 | rev | sed s/tas_/tas-global-mean_/`
        outname=`echo ${outname} | sed s/mon/yr/g`
        outname=`echo ${outname} | rev | cut -d _ -f 2- | rev`
        outname=${outname}_all.nc
        out_file=${outdir}/${outname}
        command="${python} /home/599/dbi599/ocean-analysis/data_processing/calc_global_metric.py ${data_file} ${standard_name} ${agg} ${out_file} --smoothing annual"
        echo ${command}
        ${command}

    elif [[ "${metric}" == "tas-ita" ]] ; then
        outname=`echo ${data_file} | rev | cut -d / -f 1 | rev | sed s/tas_/tas-ita_/`
        outname=`echo ${outname} | sed s/mon/yr/g`
        outname=`echo ${outname} | rev | cut -d _ -f 2- | rev`
        outname=${outname}_all.nc
        out_file=${outdir}/${outname}
        command="${python} /home/599/dbi599/ocean-analysis/data_processing/calc_interhemispheric_metric.py ${data_file} ${standard_name} ${out_file}"
        echo ${command}
        ${command}
    fi

done
