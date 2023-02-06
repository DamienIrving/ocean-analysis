

exp_list=(hist-GHG)
#hist-aer
run_list=(r1i1p1f1)
#r2i1p1f1 r3i1p1f1
var_list=(mixdownslope_temp temp_sigma_diff temp_vdiffuse_k33 neutral_diffusion_temp temp_tendency)
#temp_vdiffuse_sbc sw_heat frazil_3d temp_rivermix temp_vdiffuse_diff_cbt temp_nonlocal_KPP 

for exp in "${exp_list[@]}"; do
for run in "${run_list[@]}"; do
for var in "${var_list[@]}"; do

bash mom_to_cmip_3d.sh ${var} ${exp} ${run}

done
done
done
