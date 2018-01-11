
model=CSIRO-Mk3-6-0
experiment=historicalMisc
rip=r1i1p4

agg=trend
# trend clim

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}
ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}


for var in tauu tauv; do

outdir=${r87_dir}/${experiment}/yr/atmos/${rip}/${var}/latest/
mkdir -p ${outdir}

if [[ "${var}" == "tauu" ]] ; then
    direction='eastward'
elif [[ "${var}" == 'tauv' ]] ; then
    direction='northward'
fi

command="${python} ${script_dir}/calc_temporal_aggregate.py ${ua6_dir}/${experiment}/mon/atmos/${rip}/${var}/latest/${var}_Amon_${model}_${experiment}_${rip}_*.nc surface_downward_${direction}_stress ${agg} ${outdir}/${var}-ocean_Ayr_${model}_${experiment}_${rip}_1861-2005-${agg}.nc --time_bounds 1861-01-01 2005-12-31 --land_mask ${ua6_dir}/historical/fx/atmos/r0i0p0/sftlf/latest/sftlf_fx_${model}_historical_r0i0p0.nc --annual"

echo ${command}
${command}

done






