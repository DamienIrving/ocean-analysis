
model=CanESM2
experiment=rcp85
mip=r1i1p1

var=TOA_Incoming_Net_Radiation
# TOA_Incoming_Net_Radiation ocean_heat_content

fx_rip=r0i0p0
fx_experiment=historical

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}


command="${python} ${script_dir}/join_hist_rcp.py ${ua6_dir}/historical/yr/atmos/r1i1p1/rndt/latest/rndt-sum-hemispheric-metrics_Ayr_CanESM2_historical_r1i1p1_cumsum-all.nc ${ua6_dir}/rcp85/yr/atmos/r1i1p1/rndt/latest/rndt-sum-hemispheric-metrics_Ayr_CanESM2_rcp85_r1i1p1_cumsum-all.nc ${ua6_dir}/rcp85/yr/atmos/r1i1p1/rndt/latest/rndt-sum-hemispheric-metrics_Ayr_CanESM2_historical-rcp85_r1i1p1_cumsum-all.nc TOA_Incoming_Net_Radiation_globe_sum TOA_Incoming_Net_Radiation_nh_sum TOA_Incoming_Net_Radiation_sh_sum --cumsum"

echo ${command}
${command}


