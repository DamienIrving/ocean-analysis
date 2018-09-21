
model=GISS-E2-R
experiments=(piControl)
rips=(r1i1p1)
vars=(thetao)
# hfds ohc rndt

inferred=false
# true false

agg='mean'
# mean sum


fx_rip=r0i0p0
fx_experiment=historical

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}

for var in "${vars[@]}"; do
for experiment in "${experiments[@]}"; do
for rip in "${rips[@]}"; do

cumsum=' '
tdetails='all'
metric=' '
#'--metric diff global-fraction'

if [[ "${var}" == "ohc" ]] ; then
    infiles=${r87_dir}/${experiment}/yr/ocean/${rip}/ohc/latest/ohc_Oyr_${model}_${experiment}_${rip}_*.nc
    longvar=ocean_heat_content
    weights=' '
    outvar=ohc
    outtscale='Oyr'
    outrealm='ocean'
    smooth=' '
    #tdetails='all'
    #metric='global-fraction'
    #cumsum=' '
elif [ "${var}" == "hfds" ] && [ "${inferred}" == true ] ; then
    infiles=${r87_dir}/${experiment}/mon/ocean/${rip}/hfds/latest/hfds-inferred_Omon_${model}_${experiment}_${rip}_*.nc
    longvar=surface_downward_heat_flux_in_sea_water
    #weights="--weights_file ${ua6_dir}/${fx_experiment}/fx/atmos/${fx_rip}/areacella/latest/areacella_fx_${model}_${fx_experiment}_${fx_rip}.nc"
    weights=' '
    outvar=hfds-inferred
    outtscale='Oyr'
    outrealm='ocean'
    smooth='--annual'
    #tdetails='cumsum-all'
    #metric='diff'
    #cumsum='--cumsum'
elif [[ "${var}" == 'hfds' ]] ; then
    infiles=${ua6_dir}/${experiment}/mon/ocean/${rip}/hfds/latest/hfds_Omon_${model}_${experiment}_${rip}_*.nc
    longvar=surface_downward_heat_flux_in_sea_water
    #weights="--weights_file ${ua6_dir}/${fx_experiment}/fx/ocean/${fx_rip}/areacello/latest/areacello_fx_${model}_${fx_experiment}_${fx_rip}.nc"
    weights=' '
    outvar=hfds
    outtscale='Oyr'
    outrealm='ocean'
    smooth='--annual'
    #tdetails='cumsum-all'
    #metric='diff'
    #cumsum='--cumsum'
elif [[ "${var}" == "rndt" ]] ; then
    infiles=${r87_dir}/${experiment}/mon/atmos/${rip}/rndt/latest/rndt_Amon_${model}_${experiment}_${rip}_*.nc
    longvar='TOA_Incoming_Net_Radiation'
    weights="--weights_file ${ua6_dir}/${fx_experiment}/fx/atmos/${fx_rip}/areacella/latest/areacella_fx_${model}_${fx_experiment}_${fx_rip}.nc"
    outvar=rndt
    outtscale='Ayr'
    outrealm='atmos'
    smooth='--annual'
    #tdetails='cumsum-all'
    #metric='diff'
    #cumsum='--cumsum'
elif [[ "${var}" == "thetao" ]] ; then
    infiles=${ua6_dir}/${experiment}/mon/ocean/${rip}/thetao/latest/thetao_Omon_${model}_${experiment}_${rip}_*.nc
    longvar='sea_water_potential_temperature'
    weights="--weights_file ${r87_dir}/${fx_experiment}/fx/ocean/${fx_rip}/volcello/latest/volcello-inferred_fx_${model}_${fx_experiment}_${fx_rip}.nc"
    outvar=thetao
    outtscale='Oyr'
    outrealm='ocean'
    smooth='--annual'
fi

outdir=${r87_dir}/${experiment}/yr/${outrealm}/${rip}/${var}/latest
mkdir -p ${outdir}
outfile=${outdir}/${outvar}-${agg}-hemispheric-metrics_${outtscale}_${model}_${experiment}_${rip}_${tdetails}.nc

command="${python} -W ignore ${script_dir}/calc_interhemispheric_metric.py ${infiles} ${longvar} ${outfile} ${metric} --aggregation_method ${agg} ${smooth} ${weights} ${cumsum}"
# --nh_lat_bounds -3.5 91 --sh_lat_bounds -91 -3.5 --chunk

echo ${command}
#${command}

done
done
done

