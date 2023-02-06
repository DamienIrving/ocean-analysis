#!/bin/bash
#
# Description: Run mom_to_cmip.py for a 2D flux variable
#             

function usage {
    echo "USAGE: bash $0 variable experiment run"
    echo "   variable:        input variable (with underscores)"
    echo "   experiment:      piControl, historical, hist-GHG, hist-aer"
    echo "   run:             run (e.g. r1i1p1f1)"
    exit 1
}


data_var=$1
experiment=$2
run=$3

accessdir=/g/data/p73/archive/CMIP6/ACCESS-CM2

if [ "${experiment}" == "historical" ] ; then
    data_dir=${accessdir}/bj594/history/ocn
    version=v20191108
    date_range_list=$(185001-201412)
    project=CMIP

elif [ "${experiment}" == "piControl" ] ; then
    data_dir=${accessdir}/bi889/history/ocn
    version=v20191112
    date_range_list=(095001-095912 096001-096912 097001-097912 098001-098912 099001-099912 100001-100912 101001-101912 102001-102912 103001-103912 104001-104912 105001-105912 106001-106912 107001-107912 108001-108912 109001-109912 110001-110912 111001-111912 112001-112912 113001-113912 114001-114912 115001-115912 116001-116912 117001-117912 118001-118912 119001-119912 120001-120912 121001-121912 122001-122912 123001-123912 124001-124912 125001-125912 126001-126912 127001-127912 128001-128912 129001-129912 130001-130912 131001-131912 132001-132912 133001-133912 134001-134912 135001-135912 136001-136912 137001-137912 138001-138912 139001-139912 140001-140912 141001-141912 142001-142912 143001-143912 144001-144912)
    project=CMIP

elif [ "${experiment}" == "hist-GHG" ] ; then
    date_range_list=(185001-202012)
    version=v20201120
    project=DAMIP
    if [ "${run}" == "r1i1p1f1" ] ; then
        data_dir=${accessdir}/bu010/history/ocn
    elif [ "${run}" == "r2i1p1f1" ] ; then
        data_dir=${accessdir}/bu839/history/ocn
    elif [ "${run}" == "r3i1p1f1" ] ; then
        data_dir=${accessdir}/bu840/history/ocn
    fi

elif [ "${experiment}" == "hist-aer" ] ; then
    date_range_list=(185001-202012)
    version=v20201120
    project=DAMIP
    if [ "${run}" == "r1i1p1f1" ] ; then
        data_dir=${accessdir}/bw966/history/ocn
    elif [ "${run}" == "r2i1p1f1" ] ; then
        data_dir=${accessdir}/bx128/history/ocn
    elif [ "${run}" == "r3i1p1f1" ] ; then
        data_dir=${accessdir}/bx129/history/ocn
    fi

fi


file_var=`echo ${data_var} | sed s:_:-:g`
ref_dir=/g/data/fs38/publications/CMIP6/${project}/CSIRO-ARCCSS/ACCESS-CM2/${experiment}/${run}/Omon/tos/gn/${version}
out_dir=/g/data/e14/dbi599/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/${experiment}/${run}/Omon/${file_var}/gn/${version}
python=/g/data/e14/dbi599/miniconda3/envs/cmip/bin/python

mkdir -p ${out_dir}
for date_range in "${date_range_list[@]}"; do

ref_file=${ref_dir}/tos_Omon_ACCESS-CM2_${experiment}_${run}_gn_${date_range}.nc

if [ "$date_range" == "123001-123912" ]; then
    single="--single"
else
    single=" "
fi

if [ "${experiment}" == "piControl" ] ; then
command="${python} mom_to_cmip.py ${data_dir}/ocean_month.nc-${date_range:0:3}* ${data_var} ${ref_file} sea_surface_temperature ${out_dir}/${file_var}_Omon_ACCESS-CM2_${experiment}_${run}_gn_${date_range}.nc ${single}"
else
command="${python} mom_to_cmip.py ${data_dir}/ocean_month.nc-* ${data_var} ${ref_file} sea_surface_temperature ${out_dir}/${file_var}_Omon_ACCESS-CM2_${experiment}_${run}_gn_${date_range}.nc ${single}"
fi

echo ${command}
${command}

done
