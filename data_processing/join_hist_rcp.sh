
model=GFDL-CM3
experiment=rcp85
mip=r1i1p1

vars=(rndt hfds ohc)
# rndt hfds ohc

inferred=true

fx_rip=r0i0p0
fx_experiment=historical

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}

for var in "${vars[@]}"; do

if [[ "${var}" == "rndt" ]] ; then
    long_name=TOA_Incoming_Net_Radiation
    file_ext='cumsum-all.nc'
    tscale='Ayr'
    realm='atmos'
    cumsum='--cumsum'
elif [[ "${var}" == "hfds" ]] ; then
    long_name=Downward_Heat_Flux_at_Sea_Water_Surface
    file_ext='cumsum-all.nc'
    tscale='Oyr'
    realm='ocean'
    cumsum='--cumsum'
elif [[ "${var}" == "ohc" ]] ; then
    long_name=ocean_heat_content
    file_ext='all.nc'
    tscale='Oyr'
    realm='ocean'
    cumsum=' '
fi

if [ "${var}" == "hfds" ] && [ "${inferred}" == true ] ; then
    file_label=${var}-inferred-sum-hemispheric-metrics
else
    file_label=${var}-sum-hemispheric-metrics
fi

hist_file=${r87_dir}/historical/yr/${realm}/r1i1p1/${var}/latest/${file_label}_${tscale}_${model}_historical_r1i1p1_${file_ext}
rcp_file=${r87_dir}/rcp85/yr/${realm}/r1i1p1/${var}/latest/${file_label}_${tscale}_${model}_rcp85_r1i1p1_${file_ext}
outfile=${r87_dir}/rcp85/yr/${realm}/r1i1p1/${var}/latest/${file_label}_${tscale}_${model}_historical-rcp85_r1i1p1_${file_ext}

command="${python} ${script_dir}/join_hist_rcp.py ${hist_file} ${rcp_file} ${outfile} ${long_name}_globe_sum ${long_name}_nh_sum ${long_name}_sh_sum ${cumsum}"

echo ${command}
${command}

done

