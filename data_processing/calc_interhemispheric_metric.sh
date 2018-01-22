
model=CanESM2

experiment=historical
rip=r1i1p1

agg='sum'
# mean sum

fx_rip=r0i0p0
fx_experiment=historical

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}

outfile=${r87_dir}/${experiment}/yr/ocean/${rip}/ohc/latest/ohc-${agg}-hemispheric-metrics_Oyr_${model}_${experiment}_${rip}_all.nc

command="${python} ${script_dir}/calc_interhemispheric_metric.py ${r87_dir}/${experiment}/yr/ocean/${rip}/ohc/latest/ohc_Oyr_${model}_${experiment}_${rip}_*.nc ocean_heat_content ${outfile} --area_file ${ua6_dir}/${fx_experiment}/fx/ocean/${fx_rip}/areacello/latest/areacello_fx_${model}_${fx_experiment}_${fx_rip}.nc --metric global-fraction --aggregation_method ${agg}"
# --annual --nh_lat_bounds -3.5 91 --sh_lat_bounds -91 -3.5

echo ${command}
${command}


