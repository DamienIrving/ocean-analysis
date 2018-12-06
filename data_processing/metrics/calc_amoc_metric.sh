
model=NorESM1-M
experiments=(historicalMisc)
rip=r1i1p1

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}


for experiment in "${experiments[@]}"; do

outdir=${r87_dir}/${experiment}/yr/ocean/${rip}/msftmyz/latest
mkdir -p ${outdir}


command="${python} ${script_dir}/calc_amoc_metric.py ${ua6_dir}/${experiment}/mon/ocean/${rip}/msftmyz/latest/msftmyz_Omon_${model}_${experiment}_${rip}_*.nc ${outdir}/amoc-metric_Oyr_${model}_${experiment}_${rip}_all.nc"
echo ${command}
${command}

done
