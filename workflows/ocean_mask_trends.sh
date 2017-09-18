# Script for applying ocean mask then calculating trend

model=CSIRO-Mk3-6-0
mip=r1i1p1
experiment=historical

fx_mip=r0i0p0
fx_experiment=historical

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}/${experiment}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}/${experiment}
fx_ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}/${fx_experiment}
fx_r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}/${fx_experiment}

sftlf_file=${fx_ua6_dir}/fx/atmos/${fx_mip}/sftlf/latest/sftlf_fx_${model}_${fx_experiment}_${fx_mip}.nc

variables=(rsds rlus rlds hfss hfls)   
for var in "${variables[@]}"; do

    if [[ "${var}" == "rsds" ]] ; then
        standard_name=surface_downwelling_shortwave_flux_in_air
    elif [[ "${var}" == "rlus" ]] ; then
        standard_name=surface_upwelling_longwave_flux_in_air
    elif [[ "${var}" == "rlds" ]] ; then
        standard_name=surface_downwelling_longwave_flux_in_air
    elif [[ "${var}" == "hfss" ]] ; then
        standard_name=surface_upward_sensible_heat_flux
    elif [[ "${var}" == "hfls" ]] ; then
        standard_name=surface_upward_latent_heat_flux
    fi

    mask_command="${python} ${script_dir}/downloads/apply_mask.py ${ua6_dir}/mon/atmos/${mip}/${var}/latest/${var}_Amon_${model}_${experiment}_${mip}_*.nc ${standard_name} ${sftlf_file} land_area_fraction sftlf --mask_label ocean"
    echo ${mask_command}
    ${mask_command}

    outfile=${r87_dir}/mon/atmos/${mip}/${var}/latest/${var}-ocean-trend_Amon_${model}_${experiment}_${mip}_1850-2005.nc
    trend_command="${python} ${script_dir}/data_processing/calc_trend.py ${r87_dir}/mon/atmos/${mip}/${var}/latest/${var}-ocean_Amon_${model}_${experiment}_${mip}_*.nc ${standard_name} ${outfile} --time_bounds 1850-01-01 2005-12-31 --regrid"
    echo ${trend_command}
    ${trend_command}  

done

standard_name=surface_downward_heat_flux_in_sea_water
outdir=${r87_dir}/mon/ocean/${mip}/hfds/latest
outfile=${outdir}/hfds-trend_Omon_${model}_${experiment}_${mip}_1850-2005.nc
mkdir -p ${outdir}

trend_command="${python} ${script_dir}/data_processing/calc_trend.py ${ua6_dir}/mon/ocean/${mip}/hfds/latest/hfds_Omon_${model}_${experiment}_${mip}_*.nc ${standard_name} ${outfile} --time_bounds 1850-01-01 2005-12-31 --regrid"
echo ${trend_command}
${trend_command}

 


