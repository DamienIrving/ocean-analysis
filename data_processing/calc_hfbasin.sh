
model=NorESM1-M

experiment=historicalMisc
fxexperiment=historical
rips=(r1i1p1)
regions=(global)
#global atlantic-arctic indian-pacific

var=hfbasin
#hfbasin #hfy
name=northward_ocean_heat_transport
#northward_ocean_heat_transport ocean_heat_y_transport

tdetails=cumsum-all
#all cumsum-all

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}
ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}

for rip in "${rips[@]}"; do
for region in "${regions[@]}"; do

outdir=${r87_dir}/${experiment}/yr/ocean/${rip}/hfbasin/latest
mkdir -p ${outdir}

command="${python} ${script_dir}/calc_hfbasin.py ${ua6_dir}/${experiment}/mon/ocean/${rip}/${var}/latest/${var}_Omon_${model}_${experiment}_${rip}_*.nc ${name} ${outdir}/hfbasin-${region}_Oyr_${model}_${experiment}_${rip}_${tdetails}.nc --region ${region}-ocean --basin_file /g/data/ua6/DRSv2/CMIP5/${model}/${fxexperiment}/fx/ocean/r0i0p0/basin/latest/basin_fx_${model}_${fxexperiment}_r0i0p0.nc --cumsum"
# --basin_file /g/data/ua6/DRSv2/CMIP5/${model}/${fxexperiment}/fx/ocean/r0i0p0/basin/latest/basin_fx_${model}_${fxexperiment}_r0i0p0.nc --cumsum

echo ${command}
${command}

done
done
