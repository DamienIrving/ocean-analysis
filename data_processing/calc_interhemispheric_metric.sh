
model=CanESM2
experiments=(piControl)
rips=(r1i1p1)

agg='sum'
# mean sum

metric='diff'
# diff global-fraction

var='rndt'
# hfds ohc rndt

inferred=false
# true false

fx_rip=r0i0p0
fx_experiment=historical

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}

for experiment in "${experiments[@]}"; do
for rip in "${rips[@]}"; do

if [[ "${var}" == "ohc" ]] ; then
    infiles=${r87_dir}/${experiment}/yr/ocean/${rip}/ohc/latest/ohc_Oyr_${model}_${experiment}_${rip}_*.nc
    longvar=ocean_heat_content
    areafile=${ua6_dir}/${fx_experiment}/fx/ocean/${fx_rip}/areacello/latest/areacello_fx_${model}_${fx_experiment}_${fx_rip}.nc
    outvar=ohc
    outtscale='Oyr'
    outrealm='ocean'
    smooth=' '
elif [ "${var}" == "hfds" ] && [ "${inferred}" == true ] ; then
    infiles=${r87_dir}/${experiment}/mon/ocean/${rip}/hfds/latest/hfds-inferred_Omon_${model}_${experiment}_${rip}_*.nc
    longvar=surface_downward_heat_flux_in_sea_water
    areafile=${ua6_dir}/${fx_experiment}/fx/atmos/${fx_rip}/areacella/latest/areacella_fx_${model}_${fx_experiment}_${fx_rip}.nc
    outvar=hfds-inferred
    outtscale='Oyr'
    outrealm='ocean'
    smooth='--annual'
elif [[ "${var}" == 'hfds' ]] ; then
    infiles=${ua6_dir}/${experiment}/mon/ocean/${rip}/hfds/latest/hfds_Omon_${model}_${experiment}_${rip}_*.nc
    longvar=surface_downward_heat_flux_in_sea_water
    areafile=${ua6_dir}/${fx_experiment}/fx/ocean/${fx_rip}/areacello/latest/areacello_fx_${model}_${fx_experiment}_${fx_rip}.nc
    outvar=hfds
    outtscale='Oyr'
    outrealm='ocean'
    smooth='--annual'
elif [[ "${var}" == "rndt" ]] ; then
    infiles=${r87_dir}/${experiment}/mon/atmos/${rip}/rndt/latest/rndt_Amon_${model}_${experiment}_${rip}_*.nc
    longvar='TOA_Incoming_Net_Radiation'
    areafile=${ua6_dir}/${fx_experiment}/fx/atmos/${fx_rip}/areacella/latest/areacella_fx_${model}_${fx_experiment}_${fx_rip}.nc
    outvar=rndt
    outtscale='Ayr'
    outrealm='atmos'
    smooth='--annual'
fi
outdir=${r87_dir}/${experiment}/yr/${outrealm}/${rip}/${var}/latest
mkdir -p ${outdir}
outfile=${outdir}/${outvar}-${agg}-hemispheric-metrics_${outtscale}_${model}_${experiment}_${rip}_cumsum-all.nc
# cumsum-all

command="${python} ${script_dir}/calc_interhemispheric_metric.py ${infiles} ${longvar} ${outfile} --metric ${metric} --aggregation_method ${agg} ${smooth} --area_file ${areafile} --cumsum"
# --annual --nh_lat_bounds -3.5 91 --sh_lat_bounds -91 -3.5 --chunk --area_file ${areafile} --cumsum

echo ${command}
${command}

done
done

