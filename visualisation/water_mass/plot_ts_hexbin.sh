
model=CCSM4
experiment=historicalGHG
rip=r1i1p1
basins=(globe indian south_pacific north_pacific south_atlantic north_atlantic)

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing
vis_dir=/home/599/dbi599/ocean-analysis/visualisation/water_mass
fig_dir=/g/data/r87/dbi599/figures/ts

ua6_dir=/g/data/ua6/DRSv3/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}


# Pre-industrial

## Salinity
so_pre="${python} ${script_dir}/calc_temporal_aggregate.py ${ua6_dir}/historical/mon/ocean/r1i1p1/so/latest/so_Omon_${model}_historical_r1i1p1_185001-185912.nc ${ua6_dir}/historical/mon/ocean/r1i1p1/so/latest/so_Omon_${model}_historical_r1i1p1_186001-186912.nc sea_water_salinity ${r87_dir}/historical/yr/ocean/r1i1p1/so/latest/so_Oyr_${model}_historical_r1i1p1_1850-1869-clim.nc --aggregation clim --time_bounds 1850-01-01 1869-12-31"

#echo ${so_pre}
#${so_pre}

## Temperature
thetao_pre="${python} ${script_dir}/calc_temporal_aggregate.py ${ua6_dir}/historical/mon/ocean/r1i1p1/thetao/latest/thetao_Omon_${model}_historical_r1i1p1_185001-185912.nc ${ua6_dir}/historical/mon/ocean/r1i1p1/thetao/latest/thetao_Omon_${model}_historical_r1i1p1_186001-186912.nc sea_water_potential_temperature ${r87_dir}/historical/yr/ocean/r1i1p1/thetao/latest/thetao_Oyr_${model}_historical_r1i1p1_1850-1869-clim.nc --aggregation clim --time_bounds 1850-01-01 1869-12-31"

#echo ${thetao_pre}
#${thetao_re}

# Experiment

## Salinity
so_dir=${r87_dir}/${experiment}/yr/ocean/${rip}/so/latest
mkdir -p ${so_dir}

so_exp="${python} ${script_dir}/calc_temporal_aggregate.py ${r87_dir}/${experiment}/mon/ocean/${rip}/so/latest/so_Omon_${model}_${experiment}_${rip}_198001-198912.nc ${r87_dir}/${experiment}/mon/ocean/${rip}/so/latest/so_Omon_${model}_${experiment}_${rip}_199001-199912.nc ${r87_dir}/${experiment}/mon/ocean/${rip}/so/latest/so_Omon_${model}_${experiment}_${rip}_200001-200512.nc sea_water_salinity ${so_dir}/so_Oyr_${model}_${experiment}_${rip}_1986-2005-clim.nc --aggregation clim --time_bounds 1986-01-01 2005-12-31"

#echo ${so_exp}
#${so_exp}

## Temperature
thetao_dir=${r87_dir}/${experiment}/yr/ocean/${rip}/thetao/latest
mkdir -p ${thetao_dir}

thetao_exp="${python} ${script_dir}/calc_temporal_aggregate.py ${r87_dir}/${experiment}/mon/ocean/${rip}/thetao/latest/thetao_Omon_${model}_${experiment}_${rip}_198001-198912.nc ${r87_dir}/${experiment}/mon/ocean/${rip}/thetao/latest/thetao_Omon_${model}_${experiment}_${rip}_199001-199912.nc ${r87_dir}/${experiment}/mon/ocean/${rip}/thetao/latest/thetao_Omon_${model}_${experiment}_${rip}_200001-200512.nc sea_water_potential_temperature ${thetao_dir}/thetao_Oyr_${model}_${experiment}_${rip}_1986-2005-clim.nc --aggregation clim --time_bounds 1986-01-01 2005-12-31"

#echo ${thetao_exp}
#${thetao_exp}

# Plot

for basin in "${basins[@]}"; do

outfile=/g/data/r87/dbi599/figures/ts/thetao-so-volcello_Oyr_${model}_${experiment}_${rip}_1850-1869vs1986-2005-clim_${basin}.png

#plot="${python} ${vis_dir}/plot_ts_hexbin.py /g/data/r87/dbi599/DRSv2/CMIP5/${model}/historical/fx/ocean/r0i0p0/volcello/latest/volcello-inferred_fx_${model}_historical_r0i0p0.nc /g/data/r87/dbi599/DRSv2/CMIP5/${model}/historical/fx/ocean/r0i0p0/basin/latest/basin_fx_${model}_historical_r0i0p0.nc ${outfile} --temperature_files ${r87_dir}/historical/yr/ocean/r1i1p1/thetao/latest/thetao_Oyr_${model}_historical_r1i1p1_1850-1869-clim.nc ${r87_dir}/${experiment}/yr/ocean/${rip}/thetao/latest/thetao_Oyr_${model}_${experiment}_${rip}_1986-2005-clim.nc --salinity_files ${r87_dir}/historical/yr/ocean/r1i1p1/so/latest/so_Oyr_${model}_historical_r1i1p1_1850-1869-clim.nc ${r87_dir}/${experiment}/yr/ocean/${rip}/so/latest/so_Oyr_${model}_${experiment}_${rip}_1986-2005-clim.nc --colors Greys Reds --labels pre-industrial ${experiment} --basin ${basin} --salinity_bounds 31.5 37.5 --temperature_bounds -2 30.5 --alphas 1.0 0.1"

plot="/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python /home/599/dbi599/ocean-analysis/visualisation/water_mass/plot_ts_hexbin.py /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historical/fx/ocean/r0i0p0/volcello/latest/volcello-inferred_fx_CCSM4_historical_r0i0p0.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historical/fx/ocean/r0i0p0/basin/latest/basin_fx_CCSM4_historical_r0i0p0.nc /g/data/r87/dbi599/figures/ts/thetao-so-volcello_Oyr_CCSM4_historicalAA-GHG_r1i1p1_1850-1869vs1986-2005-clim_${basin}.png --temperature_files /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historical/yr/ocean/r1i1p1/thetao/latest/thetao_Oyr_CCSM4_historical_r1i1p1_1850-1869-clim.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/thetao/latest/thetao_Oyr_CCSM4_historicalMisc_r1i1p10_1986-2005-clim.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalGHG/yr/ocean/r1i1p1/thetao/latest/thetao_Oyr_CCSM4_historicalGHG_r1i1p1_1986-2005-clim.nc --salinity_files /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historical/yr/ocean/r1i1p1/so/latest/so_Oyr_CCSM4_historical_r1i1p1_1850-1869-clim.nc  /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/so/latest/so_Oyr_CCSM4_historicalMisc_r1i1p10_1986-2005-clim.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalGHG/yr/ocean/r1i1p1/so/latest/so_Oyr_CCSM4_historicalGHG_r1i1p1_1986-2005-clim.nc --colors Greys Blues Reds --labels pre-industrial historicalAA historicalGHG --basin ${basin} --salinity_bounds 31.5 37.5 --temperature_bounds -2 30.5 --alphas 1.0 0.1 0.1"

echo ${plot}
${plot}

done
