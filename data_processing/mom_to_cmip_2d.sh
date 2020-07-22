#!/bin/bash
#
# Description: Run mom_to_cmip.py for a 2D flux variable
#             

function usage {
    echo "USAGE: bash $0 variable experiment"
    echo "   variable:        input variable (with underscores)"
    echo "   experiment:      piControl or historical"
    exit 1
}


data_var=$1
experiment=$2

if [ "${experiment}" == "historical" ] ; then
    data_dir=/g/data/p66/cm2704/archive/bj594/history/ocn
    version=v20191108
    date_range_list=(185001-185912 186001-186912 187001-187912 188001-188912 189001-189912 190001-190912 190001-190912 191001-191912 192001-192912 193001-193912 194001-194912 195001-195912 196001-196912 197001-197912 198001-198912 199001-199912 200001-200912 201001-201412)
else
    data_dir=/g/data/p66/cm2704/archive/bi889/history/ocn
    version=v20191112
    date_range_list=(095001-095912 096001-096912 097001-097912 098001-098912 099001-099912 100001-100912 101001-101912 102001-102912 103001-103912 104001-104912 105001-105912 106001-106912 107001-107912 108001-108912 109001-109912 110001-110912 111001-111912 112001-112912 113001-113912 114001-114912 115001-115912 116001-116912 117001-117912 118001-118912 119001-119912 120001-120912 121001-121912 122001-122912 123001-123912 124001-124912 125001-125912 126001-126912 127001-127912 128001-128912 129001-129912 130001-130912 131001-131912 132001-132912 133001-133912 134001-134912 135001-135912 136001-136912 137001-137912 138001-138912 139001-139912 140001-140912 141001-141912 142001-142912 143001-143912 144001-144912)
fi


file_var=`echo ${data_var} | sed s:_:-:g`
ref_dir=/g/data/fs38/publications/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/${experiment}/r1i1p1f1/Omon/tos/gn/${version}
ref_file=${ref_dir}/tos_Omon_ACCESS-CM2_${experiment}_r1i1p1f1_gn_095001-144912.nc
out_dir=/g/data/r87/dbi599/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/${experiment}/r1i1p1f1/Omon/${file_var}/gn/${version}
python=/g/data/r87/dbi599/miniconda3/envs/ocean3/bin/python

mkdir -p ${out_dir}
for date_range in "${date_range_list[@]}"; do

if [ "$date_range" == "123001-123912" ]; then
    single="--single"
else
    single=" "
fi

command="${python} mom_to_cmip.py ${data_dir}/ocean_month.nc-${date_range:0:3}* ${data_var} ${ref_file} sea_surface_temperature ${out_dir}/${file_var}_Omon_ACCESS-CM2_${experiment}_r1i1p1f1_gn_${date_range}.nc ${single}"

echo ${command}
${command}

done
