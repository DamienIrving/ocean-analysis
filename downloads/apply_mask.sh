

experiment=historical
fx_experiment=historical
model=GFDL-CM3
mip=r1i1p1
datadir=ua6
fxdir=ua6
fxmip=r0i0p0

# rsds rsus rlds rlus hfss hfls

for var in rsds rsus rlds rlus hfss hfls; do

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
fi

/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python apply_mask.py /g/data/${datadir}/DRSv2/CMIP5/${model}/${experiment}/mon/atmos/${mip}/${var}/latest/${var}_Amon_${model}_${experiment}_${mip}_*.nc ${standard_name} /g/data/${fxdir}/DRSv2/CMIP5/${model}/${fx_experiment}/fx/atmos/${fxmip}/sftlf/latest/sftlf_fx_${model}_${fx_experiment}_${fxmip}.nc land_area_fraction sftlf --ocean

done
