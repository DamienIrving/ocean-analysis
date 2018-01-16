

model=IPSL-CM5A-LR

experiment=historical
rip=r1i1p1

fx_rip=r0i0p0
fx_experiment=historical

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}


command="${python} ${script_dir}/calc_ohc.py ${ua6_dir}/${experiment}/mon/ocean/${rip}/thetao/latest/thetao_Omon_${model}_${experiment}_${rip}_*.nc sea_water_potential_temperature --annual --volume_file ${ua6_dir}/historical/fx/ocean/r0i0p0/volcello/latest/volcello_fx_${model}_historical_r0i0p0.nc"

# --area_file ${ua6_dir}/historical/fx/ocean/r0i0p0/areacello/latest/areacello_fx_${model}_historical_r0i0p0.nc
#

echo ${command}
${command}


