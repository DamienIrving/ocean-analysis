
model=ACCESS1-0

experiment=historical
rips=(r1i1p1 r2i1p1 r3i1p1)

outtype=equator
# equator metric

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}

for rip in "${rips[@]}"; do

filedir=${r87_dir}/${experiment}/yr/ocean/${rip}/hfbasin/latest
command="${python} ${script_dir}/calc_hfbasin_metric.py ${filedir}/hfbasin-global_Oyr_${model}_${experiment}_${rip}_all.nc ${outtype} ${filedir}/hfbasin-global-${outtype}_Oyr_${model}_${experiment}_${rip}_all.nc"

echo ${command}
${command}

done
