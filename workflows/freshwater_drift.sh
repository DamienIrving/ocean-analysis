model=CSIRO-Mk3-6-0
#experiment=historical
#rip=r1i1p1

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

ua6_dir=/g/data/ua6/DRSv3/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}


## wfo

mkdir -p ${r87_dir}/piControl/yr/ocean/r1i1p1/wfo/latest/

wfo_control_metric="${python} ${script_dir}/calc_interhemispheric_metric.py ${ua6_dir}/piControl/mon/ocean/r1i1p1/wfo/latest/wfo_Omon_${model}_piControl_r1i1p1_??????-??????.nc water_flux_into_sea_water ${r87_dir}/piControl/yr/ocean/r1i1p1/wfo/latest/wfo-sum-hemispheric-metrics_Oyr_${model}_piControl_r1i1p1_cumsum-all.nc --weights_file ${ua6_dir}/historical/fx/ocean/r0i0p0/areacello/latest/areacello_fx_${model}_historical_r0i0p0.nc --aggregation_method sum --annual --cumsum --flux_to_mag"

echo ${wfo_control_metric}
${wfo_control_metric}

wfo_coefficients="${python} ${script_dir}/calc_drift_coefficients.py ${r87_dir}/piControl/yr/ocean/r1i1p1/wfo/latest/wfo-sum-hemispheric-metrics_Oyr_${model}_piControl_r1i1p1_cumsum-all.nc Water_Flux_into_Sea_Water_globe_sum ${r87_dir}/piControl/yr/ocean/r1i1p1/wfo/latest/wfo-globe-sum-coefficients_Oyr_${model}_piControl_r1i1p1_cumsum-all.nc"

echo ${wfo_coefficients}
${wfo_coefficients}

mkdir -p ${r87_dir}/historical/yr/ocean/r1i1p1/wfo/latest/dedrifted

wfo_exp_metric="${python} ${script_dir}/calc_interhemispheric_metric.py ${ua6_dir}/historical/mon/ocean/r1i1p1/wfo/latest/wfo_Omon_${model}_historical_r1i1p1_??????-??????.nc water_flux_into_sea_water ${r87_dir}/historical/yr/ocean/r1i1p1/wfo/latest/wfo-sum-hemispheric-metrics_Oyr_${model}_historical_r1i1p1_cumsum-all.nc --weights_file ${ua6_dir}/historical/fx/ocean/r0i0p0/areacello/latest/areacello_fx_${model}_historical_r0i0p0.nc --aggregation_method sum --annual --cumsum --flux_to_mag"

echo ${wfo_exp_metric}
${wfo_exp_metric}

wfo_dedrift="${python} ${script_dir}/remove_drift.py ${r87_dir}/historical/yr/ocean/r1i1p1/wfo/latest/wfo-sum-hemispheric-metrics_Oyr_${model}_historical_r1i1p1_cumsum-all.nc Water_Flux_into_Sea_Water_globe_sum annual ${r87_dir}/piControl/yr/ocean/r1i1p1/wfo/latest/wfo-globe-sum-coefficients_Oyr_${model}_piControl_r1i1p1_cumsum-all.nc ${r87_dir}/historical/yr/ocean/r1i1p1/wfo/latest/dedrifted/wfo-globe-sum_Oyr_${model}_historical_r1i1p1_cumsum-all.nc --no_data_check"

echo ${wfo_dedrift}
${wfo_dedrift}


# soga

mkdir -p ${r87_dir}/piControl/yr/ocean/r1i1p1/soga/latest/

soga_control_metric="${python} ${script_dir}/calc_temporal_aggregate.py ${ua6_dir}/piControl/mon/ocean/r1i1p1/soga/latest/soga_Omon_${model}_piControl_r1i1p1_??????-??????.nc sea_water_salinity ${r87_dir}/piControl/yr/ocean/r1i1p1/soga/latest/soga_Oyr_${model}_piControl_r1i1p1_all.nc --annual"

echo ${soga_control_metric}
${soga_control_metric}

soga_coefficients="${python} ${script_dir}/calc_drift_coefficients.py ${r87_dir}/piControl/yr/ocean/r1i1p1/soga/latest/soga_Oyr_${model}_piControl_r1i1p1_all.nc sea_water_salinity ${r87_dir}/piControl/yr/ocean/r1i1p1/soga/latest/soga-coefficients_Oyr_${model}_piControl_r1i1p1_all.nc"

echo ${soga_coefficients}
${soga_coefficients}


mkdir -p ${r87_dir}/historical/yr/ocean/r1i1p1/soga/latest/dedrifted

soga_exp_metric="${python} ${script_dir}/calc_temporal_aggregate.py ${ua6_dir}/historical/mon/ocean/r1i1p1/soga/latest/soga_Omon_${model}_historical_r1i1p1_??????-??????.nc sea_water_salinity ${r87_dir}/historical/yr/ocean/r1i1p1/soga/latest/soga_Oyr_${model}_historical_r1i1p1_all.nc --annual"

echo ${soga_exp_metric}
${soga_exp_metric}

soga_dedrift="${python} ${script_dir}/remove_drift.py ${r87_dir}/historical/yr/ocean/r1i1p1/soga/latest/soga_Oyr_${model}_historical_r1i1p1_all.nc sea_water_salinity annual ${r87_dir}/piControl/yr/ocean/r1i1p1/soga/latest/soga-coefficients_Oyr_${model}_piControl_r1i1p1_all.nc ${r87_dir}/historical/yr/ocean/r1i1p1/soga/latest/dedrifted/soga_Oyr_${model}_historical_r1i1p1_all.nc --no_data_check"

echo ${soga_dedrift}
${soga_dedrift}
