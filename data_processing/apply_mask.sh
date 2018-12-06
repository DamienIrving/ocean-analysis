

experiment=historicalMisc
fx_experiment=historical
model=GFDL-CM3
rips=(r1i1p1 r3i1p1 r5i1p1)
datadir=r87/dbi599
fxdir=ua6
fxrip=r0i0p0

# rsds rsus rlds rlus hfss hfls
# pr evspsbl pe

for var in pe; do

if [[ "${var}" == "rsds" ]] ; then
    standard_name='surface_downwelling_shortwave_flux_in_air'
elif [[ "${var}" == 'rsus' ]] ; then
    standard_name='surface_upwelling_shortwave_flux_in_air'
elif [[ "${var}" == 'rlds' ]] ; then
    standard_name='surface_downwelling_longwave_flux_in_air'
elif [[ "${var}" == 'rlus' ]] ; then
    standard_name='surface_upwelling_longwave_flux_in_air'
elif [[ "${var}" == 'hfss' ]] ; then
    standard_name='surface_upward_sensible_heat_flux'
elif [[ "${var}" == 'hfls' ]] ; then
    standard_name='surface_upward_latent_heat_flux'
elif [[ "${var}" == 'pr' ]] ; then
    standard_name='precipitation_flux'
elif [[ "${var}" == 'evspsbl' ]] ; then
    standard_name='water_evaporation_flux'
elif [[ "${var}" == 'pe' ]] ; then
    standard_name='precipitation_minus_evaporation_flux'
fi

for rip in "${rips[@]}"; do

command="/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python apply_mask.py /g/data/${datadir}/DRSv2/CMIP5/${model}/${experiment}/mon/atmos/${rip}/${var}/latest/${var}_Amon_${model}_${experiment}_${rip}_*.nc ${standard_name} /g/data/${fxdir}/DRSv2/CMIP5/${model}/${fx_experiment}/fx/atmos/${fxrip}/sftlf/latest/sftlf_fx_${model}_${fx_experiment}_${fxrip}.nc land_area_fraction sftlf --mask_label ocean"

echo ${command}
${command}

done

done
