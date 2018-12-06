
model=NorESM1-M

experiment=historicalMisc
rips=(r1i1p1)

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}


for rip in "${rips[@]}"; do

command="${python} ${script_dir}/calc_pe_metric.py ${r87_dir}/${experiment}/mon/atmos/${rip}/pe/latest/pe-ocean_Amon_${model}_${experiment}_${rip}_*.nc ${r87_dir}/${experiment}/yr/atmos/${rip}/pe/latest/pe-ocean-metrics_Ayr_${model}_${experiment}_${rip}_all.nc"

echo ${command}
${command}

done
