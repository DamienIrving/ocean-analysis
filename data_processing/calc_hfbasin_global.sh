
model=GISS-E2-R

experiment=historicalMisc
rips=(r1i1p107 r2i1p107 r3i1p107 r4i1p107 r5i1p107)

var=hfy
#hfbasin #hfy
name=ocean_heat_y_transport
#northward_ocean_heat_transport ocean_heat_y_transport


python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}
ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}

for rip in "${rips[@]}"; do

outdir=${r87_dir}/${experiment}/yr/ocean/${rip}/hfbasin/latest
mkdir -p ${outdir}

command="${python} ${script_dir}/calc_hfbasin_global.py ${ua6_dir}/${experiment}/mon/ocean/${rip}/${var}/latest/${var}_Omon_${model}_${experiment}_${rip}_*.nc ${name} ${outdir}/hfbasin-global_Oyr_${model}_${experiment}_${rip}_all.nc"

echo ${command}
${command}

done
