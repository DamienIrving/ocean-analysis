
model=CSIRO-Mk3-6-0

experiment=historicalGHG
rips=(r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1 r7i1p1 r8i1p1 r9i1p1 r10i1p1)

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}

for rip in "${rips[@]}"; do

filedir=${r87_dir}/${experiment}/yr/ocean/${rip}/hfbasin/latest
command="${python} ${script_dir}/calc_hfbasin_metric.py ${filedir}/hfbasin-global_Oyr_${model}_${experiment}_${rip}_all.nc ${filedir}/hfbasin-global-metric_Oyr_${model}_${experiment}_${rip}_all.nc"

echo ${command}
${command}

done
