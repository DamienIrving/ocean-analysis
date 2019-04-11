

model=CCSM4
experiment=historical
rip=r1i1p1

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing
vis_dir=/home/599/dbi599/ocean-analysis/visualisation/water_mass
fig_dir=/g/data/r87/dbi599/figures/ts

ua6_dir=/g/data/ua6/DRSv3/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}


# Pre-industrial

so_pre="${python} ${script_dir}/calc_temporal_aggregate.py ${ua6_dir}/historical/mon/ocean/r1i1p1/so/latest/so_Omon_${model}_historical_r1i1p1_185001-185912.nc ${ua6_dir}/historical/mon/ocean/r1i1p1/so/latest/so_Omon_${model}_historical_r1i1p1_186001-186912.nc sea_water_salinity ${r87_dir}/historical/yr/ocean/r1i1p1/so/latest/so_Oyr_${model}_historical_r1i1p1_1850-1869-clim.nc --aggregation clim --time_bounds 1850-01-01 1869-12-31"

echo ${so_pre}
${so_pre}

thetao_pre="${python} ${script_dir}/calc_temporal_aggregate.py ${ua6_dir}/historical/mon/ocean/r1i1p1/thetao/latest/thetao_Omon_${model}_historical_r1i1p1_185001-185912.nc ${ua6_dir}/historical/mon/ocean/r1i1p1/thetao/latest/thetao_Omon_${model}_historical_r1i1p1_186001-186912.nc sea_water_potential_temperature ${r87_dir}/historical/yr/ocean/r1i1p1/thetao/latest/thetao_Oyr_${model}_historical_r1i1p1_1850-1869-clim.nc --aggregation clim --time_bounds 1850-01-01 1869-12-31"

echo ${thetao_pre}
${thetao_re}

# Experiment

so_dir=${r87_dir}/${experiment}/yr/ocean/${rip}/so/latest
mkdir -p ${so_dir}

so_exp="${python} ${script_dir}/calc_temporal_aggregate.py ${ua6_dir}/${experiment}/mon/ocean/${rip}/so/latest/so_Omon_${model}_${experiment}_${rip}_198001-198912.nc ${ua6_dir}/${experiment}/mon/ocean/${rip}/so/latest/so_Omon_${model}_${experiment}_${rip}_199001-199912.nc ${ua6_dir}/${experiment}/mon/ocean/${rip}/so/latest/so_Omon_${model}_${experiment}_${rip}_200001-200512.nc sea_water_salinity ${so_dir}/so_Oyr_${model}_${experiment}_${rip}_1986-2005-clim.nc --aggregation clim --time_bounds 1986-01-01 2005-12-31"

echo ${so_exp}
${so_exp}


thetao_dir=${r87_dir}/${experiment}/yr/ocean/${rip}/thetao/latest
mkdir -p ${thetao_dir}

thetao_exp="${python} ${script_dir}/calc_temporal_aggregate.py ${ua6_dir}/${experiment}/mon/ocean/${rip}/thetao/latest/thetao_Omon_${model}_${experiment}_${rip}_198001-198912.nc ${ua6_dir}/${experiment}/mon/ocean/${rip}/thetao/latest/thetao_Omon_${model}_${experiment}_${rip}_199001-199912.nc ${ua6_dir}/${experiment}/mon/ocean/${rip}/thetao/latest/thetao_Omon_${model}_${experiment}_${rip}_200001-200512.nc sea_water_salinity ${thetao_dir}/thetao_Oyr_${model}_${experiment}_${rip}_1986-2005-clim.nc --aggregation clim --time_bounds 1986-01-01 2005-12-31"

echo ${thetao_exp}
${thetao_exp}

# Plot

plot="${python} ${vis_dir}/plot_ts_hexbin.py /g/data/r87/dbi599/DRSv2/CMIP5/${model}/historical/fx/ocean/r0i0p0/volcello/latest/volcello-inferred_fx_${model}_historical_r0i0p0.nc /g/data/r87/dbi599/DRSv2/CMIP5/${model}/historical/fx/ocean/r0i0p0/basin/latest/basin_fx_${model}_historical_r0i0p0.nc test.png --temperature_files /g/data/r87/dbi599/DRSv2/CMIP5/${model}/historical/yr/ocean/${rip}/thetao/latest/thetao_Oyr_${model}_historical_${rip}_1850-1869-clim.nc /g/data/r87/dbi599/DRSv2/CMIP5/${model}/${experiment}/yr/ocean/${rip}/thetao/latest/thetao_Oyr_${model}_${experiment}_${rip}_1986-2005-clim.nc --salinity_files /g/data/r87/dbi599/DRSv2/CMIP5/${model}/historical/yr/ocean/${rip}/so/latest/so_Oyr_${model}_historical_${rip}_1850-1869-clim.nc /g/data/r87/dbi599/DRSv2/CMIP5/${model}/${experiment}/yr/ocean/${rip}/so/latest/so_Oyr_${model}_${experiment}_${rip}_1986-2005-clim.nc --colors Greys Reds --labels pre-industrial ${experiment} --basin south_pacific --salinity_bounds 32 36.5 --temperature_bounds -2 30.5 --alphas 1.0 0.1"
