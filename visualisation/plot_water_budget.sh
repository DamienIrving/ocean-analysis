# Script for running the plot_water_budget.py script
# May need to run apply_mask.sh first to apply ocean mask to pr, evspsbl and pe data

model=CSIRO-Mk3-6-0
mip=r1i1p1
experiment=historical

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/visualisation

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}/${experiment}/mon
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}/${experiment}/mon

outfile=/g/data/r87/dbi599/figures/water-cycle/water-budget_Oyr_${model}_${experiment}_${mip}_all.png
pr_files="--pr_files ${r87_dir}/ocean/${mip}/pr/latest/pr-atmos_Omon_${model}_${experiment}_${mip}_*.nc"
evspsbl_files="--evspsbl_files ${r87_dir}/ocean/${mip}/evspsbl/latest/evspsbl-atmos_Omon_${model}_${experiment}_${mip}_*.nc"
pe_files="--pe_files ${r87_dir}/ocean/${mip}/pe/latest/pe_Omon_${model}_${experiment}_${mip}_*.nc"

command="${python} ${script_dir}/plot_water_budget.py ${outfile} ${pr_files} ${evspsbl_files} ${pe_files}"
# --area --time 1850-01-01 2005-12-31

echo ${command}
#${command}
#echo ${outfile}
