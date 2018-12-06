
model=NorESM1-M
experiments=(historical historicalGHG historicalMisc rcp45)
rips=(r1i1p1)

fx_rip=r0i0p0
fx_experiment=historical

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}


for experiment in "${experiments[@]}"; do
for rip in "${rips[@]}"; do

infiles=${ua6_dir}/${experiment}/mon/aerosol/${rip}/od550aer/latest/od550aer_aero_${model}_${experiment}_${rip}_*.nc
outdir=${r87_dir}/${experiment}/yr/aerosol/${rip}/od550aer/latest
outfile=${outdir}/od550aer-global-mean_aero_${model}_${experiment}_${rip}_all.nc
areafile=${ua6_dir}/${fx_experiment}/fx/atmos/${fx_rip}/areacella/latest/areacella_fx_${model}_${fx_experiment}_${fx_rip}.nc

mkdir -p ${outdir}

command="${python} ${script_dir}/calc_global_metric.py ${infiles} atmosphere_optical_thickness_due_to_ambient_aerosol mean ${outfile} --area_file ${areafile} --smoothing annual"

echo ${command}
${command}

done
done

