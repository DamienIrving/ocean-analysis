

exp_list=(hist-GHG hist-aer)
run_list=(r1i1p1f1 r2i1p1f1 r3i1p1f1)
var_list=(sfc_hflux_pme temp_eta_smooth)

for exp in "${exp_list[@]}"; do
for run in "${run_list[@]}"; do
for var in "${var_list[@]}"; do

bash mom_to_cmip_2d.sh ${var} ${exp} ${run}

done
done
done
