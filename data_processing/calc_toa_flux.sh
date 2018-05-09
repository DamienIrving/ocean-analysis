
model=CSIRO-Mk3-6-0
experiments=(historicalGHG)
rips=(r1i1p1)

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}

for experiment in "${experiments[@]}"; do
for rip in "${rips[@]}"; do

rsdt_files=${ua6_dir}/${experiment}/mon/atmos/${rip}/rsdt/latest/rsdt_Amon_${model}_${experiment}_${rip}_*.nc
rsut_files=${ua6_dir}/${experiment}/mon/atmos/${rip}/rsut/latest/rsut_Amon_${model}_${experiment}_${rip}_*.nc
rlut_files=${ua6_dir}/${experiment}/mon/atmos/${rip}/rlut/latest/rlut_Amon_${model}_${experiment}_${rip}_*.nc

command="${python} ${script_dir}/calc_toa_flux.py --rsdt_files ${rsdt_files} --rsut_files ${rsut_files} --rlut_files ${rlut_files}"

echo ${command}
${command}

done
done

