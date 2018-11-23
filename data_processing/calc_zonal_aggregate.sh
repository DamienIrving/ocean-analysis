
model=CanESM2

experiments=(historical)
rips=(r1i1p1)

fx_rip=r0i0p0
fx_experiment=historical

spatial_agg='mean'
#sum mean

vars=(thetao)
basins=(globe atlantic pacific indian)
#globe atlantic pacific indian

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}

sftlf_file=${ua6_dir}/${fx_experiment}/fx/atmos/${fx_rip}/sftlf/latest/sftlf_fx_${model}_${fx_experiment}_${fx_rip}.nc
basin_file=${r87_dir}/${fx_experiment}/fx/ocean/${fx_rip}/basin/latest/basin_fx_${model}_${fx_experiment}_${fx_rip}.nc
areacello_file=${ua6_dir}/${fx_experiment}/fx/ocean/${fx_rip}/areacello/latest/areacello_fx_${model}_${fx_experiment}_${fx_rip}.nc
areacella_file=${ua6_dir}/${fx_experiment}/fx/atmos/${fx_rip}/areacella/latest/areacella_fx_${model}_${fx_experiment}_${fx_rip}.nc

ref_file=' '
if [[ "${model}" =~ ^('CCSM4'|'NorESM1-M')$ ]]; then
    ref_file="--ref_file ${ua6_dir}/historical/mon/atmos/r1i1p1/rsdt/latest/rsdt_Amon_${model}_historical_r1i1p1_185001-200512.nc toa_incoming_shortwave_flux"
fi


for var in "${vars[@]}"; do

tdetails=all
cumsum=' '
joules=' '
indir=${ua6_dir}
area=' '
if [[ "${var}" == 'pr' ]] ; then
    standard_name='precipitation_flux'
    file_var='pr-ocean'
    realm='atmos'
    prefix='A'
    input_tscale='mon'
    temporal_agg='--annual'
elif [[ "${var}" == 'evspsbl' ]] ; then
    standard_name='water_evaporation_flux'
    file_var='evspsbl-ocean'
    realm='atmos'
    prefix='A'
    input_tscale='mon'
    temporal_agg='--annual'
elif [[ "${var}" == 'pe' ]] ; then
    standard_name='precipitation_minus_evaporation_flux'
    file_var='pe-ocean'
    realm='atmos'
    prefix='A'
    input_tscale='mon'
    temporal_agg='--annual'
elif [[ "${var}" == 'tos' ]] ; then
    standard_name='sea_surface_temperature'
    file_var='tos'
    realm='ocean'
    prefix='O'
    input_tscale='mon'
    temporal_agg='--annual'
elif [[ "${var}" == 'thetao' ]] ; then
    standard_name='sea_water_potential_temperature'
    file_var='thetao'
    realm='ocean'
    prefix='O'
    input_tscale='mon'
    temporal_agg='--annual'
elif [[ "${var}" == 'ohc' ]] ; then
    standard_name='ocean_heat_content'
    file_var='ohc'
    realm='ocean'
    prefix='O'
    input_tscale='yr'
    temporal_agg=' '
    indir=${r87_dir}
elif [[ "${var}" == 'rsds' ]] ; then
    standard_name='surface_downwelling_shortwave_flux_in_air'
    file_var='rsds'
    realm='atmos'
    prefix='A'
    input_tscale='mon'
    temporal_agg='--annual'
elif [[ "${var}" == 'rsus' ]] ; then
    standard_name='surface_upwelling_shortwave_flux_in_air'
    file_var='rsus'
    realm='atmos'
    prefix='A'
    input_tscale='mon'
    temporal_agg='--annual'
elif [[ "${var}" == 'rlds' ]] ; then
    standard_name='surface_downwelling_longwave_flux_in_air'
    file_var='rlds'
    realm='atmos'
    prefix='A'
    input_tscale='mon'
    temporal_agg='--annual'
elif [[ "${var}" == 'rlus' ]] ; then
    standard_name='surface_upwelling_longwave_flux_in_air'
    file_var='rlus'
    realm='atmos'
    prefix='A'
    input_tscale='mon'
    temporal_agg='--annual'
elif [[ "${var}" == 'hfss' ]] ; then
    standard_name='surface_upward_sensible_heat_flux'
    file_var='hfss'
    realm='atmos'
    prefix='A'
    input_tscale='mon'
    temporal_agg='--annual'
elif [[ "${var}" == 'hfls' ]] ; then
    standard_name='surface_upward_latent_heat_flux'
    file_var='hfls'
    realm='atmos'
    prefix='A'
    input_tscale='mon'
    temporal_agg='--annual'
elif [[ "${var}" == 'rndt' ]] ; then
    standard_name='TOA_Incoming_Net_Radiation'
    file_var='rndt'
    realm='atmos'
    prefix='A'
    input_tscale='mon'
    temporal_agg='--annual'
    cumsum='--cumsum'
    tdetails='cumsum-all'
    joules='--joules'
    indir=${r87_dir}
    area="--area ${areacella_file}"
elif [[ "${var}" == 'rsdt' ]] ; then
    standard_name='toa_incoming_shortwave_flux'
    file_var='rsdt'
    realm='atmos'
    prefix='A'
    input_tscale='mon'
    temporal_agg='--annual'
elif [[ "${var}" == 'rsut' ]] ; then
    standard_name='toa_outgoing_shortwave_flux'
    file_var='rsut'
    realm='atmos'
    prefix='A'
    input_tscale='mon'
    temporal_agg='--annual'
elif [[ "${var}" == 'rlut' ]] ; then
    standard_name='toa_outgoing_longwave_flux'
    file_var='rlut'
    realm='atmos'
    prefix='A'
    input_tscale='mon'
    temporal_agg='--annual'
elif [[ "${var}" == 'hfds' ]] ; then
    standard_name='surface_downward_heat_flux_in_sea_water'
    file_var='hfds'
    realm='ocean'
    prefix='O'
    input_tscale='mon'
    temporal_agg='--annual'
    cumsum='--cumsum'
    tdetails='cumsum-all'
    joules='--joules'
    area="--area ${areacello_file}"
elif [[ "${var}" == 'tauu' ]] ; then
    standard_name='surface_downward_eastward_stress'
    file_var='tauu'
    realm='atmos'
    prefix='A'
    input_tscale='mon'
    temporal_agg='--annual'
elif [[ "${var}" == 'uas' ]] ; then
    standard_name='eastward_wind'
    file_var='uas'
    realm='atmos'
    prefix='A'
    input_tscale='mon'
    temporal_agg='--annual'
fi


for basin in "${basins[@]}"; do

if [[ "${basin}" == 'globe' ]] ; then
    basin_opt=' '
else
    basin_opt="--basin ${basin_file} ${basin}"
fi

for experiment in "${experiments[@]}"; do
for rip in "${rips[@]}"; do

input_file=${indir}/${experiment}/${input_tscale}/${realm}/${rip}/${var}/latest/${file_var}_${prefix}${input_tscale}_${model}_${experiment}_${rip}_??????-??????.nc

output_dir=${r87_dir}/${experiment}/yr/${realm}/${rip}/${var}/latest
mkdir -p ${output_dir}
output_file=${output_dir}/${file_var}-zonal-${spatial_agg}_${prefix}yr_${model}_${experiment}_${rip}_${tdetails}_0-2000m-${basin}.nc

command="${python} -W ignore ${script_dir}/calc_zonal_aggregate.py ${input_file} ${standard_name} ${spatial_agg} ${output_file} ${temporal_agg} ${ref_file} ${joules} ${area} ${cumsum} --max_depth 2000 ${basin_opt}"
# --realm ocean --sftlf_file ${sftlf_file}

echo ${command}
${command}

done
done
done
done
