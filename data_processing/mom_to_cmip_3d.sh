data_var=temp_vdiffuse_sbc
data_dir=/g/data/p66/cm2704/archive/bj594/history/ocn
experiment=historical

file_var=`echo ${data_var} | sed s:_:-:g`
ref_dir=/g/data/fs38/publications/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/${experiment}/r1i1p1f1/Omon/thetao/gn/v20191108
out_dir=/g/data/r87/dbi599/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2-MOM5/${experiment}/r1i1p1f1/Omon/${file_var}/gn/v1
python=/g/data/r87/dbi599/miniconda3/envs/ocean3/bin/python

date_range_list=(185001-185912 186001-186912 187001-187912 188001-188912 189001-189912 190001-190912 190001-190912 191001-191912 192001-192912 193001-193912 194001-194912 195001-195912 196001-196912 197001-197912 198001-198912 199001-199912 200001-200912 201001-201412)

mkdir -p ${out_dir}
for date_range in "${date_range_list[@]}"; do

ref_file=${ref_dir}/thetao_Omon_ACCESS-CM2_${experiment}_r1i1p1f1_gn_${date_range}.nc

command="${python} mom_to_cmip.py ${data_dir}/ocean_month.nc-${date_range:0:3}* ${data_var} ${ref_dir}/thetao_Omon_ACCESS-CM2_${experiment}_r1i1p1f1_gn_${date_range}.nc sea_water_potential_temperature ${out_dir}/${file_var}_Omon_ACCESS-CM2-MOM5_${experiment}_r1i1p1f1_gn_${date_range}.nc"

echo ${command}
${command}

done
