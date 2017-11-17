

# Script for running the calc_wind_stress_metric.py script

model=CCSM4
rip=r4i1p1
experiment=historicalGHG

fx_rip=r0i0p0
fx_experiment=historical

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}/${experiment}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}/${experiment}
fx_ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}/${fx_experiment}
fx_r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}/${fx_experiment}

sftlf_file=${fx_ua6_dir}/fx/atmos/${fx_rip}/sftlf/latest/sftlf_fx_${model}_${fx_experiment}_${fx_rip}.nc
outdir=${r87_dir}/yr/atmos/${rip}/tauu/latest
outfile=${outdir}/tauu-metrics_Ayr_${model}_${experiment}_${rip}_all.nc
tauu_files="${ua6_dir}/mon/atmos/${rip}/tauu/latest/tauu_Amon_${model}_${experiment}_${rip}_*.nc"

command="${python} ${script_dir}/calc_wind_stress_metric.py ${tauu_files} ${sftlf_file} ${outfile}" 
mkdir -p ${outdir}
echo ${command}
${command}
echo ${outfile}


