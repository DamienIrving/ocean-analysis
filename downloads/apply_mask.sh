

experiment=historicalMisc
model=CSIRO-Mk3-6-0
mip=r1i1p4
datadir=ua6
fxdir=ua6
fxmip=r0i0p4


for var in rsds rsus rlds rlus hfss hfls; do

/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python apply_mask.py /g/data/${datadir}/DRSv2/CMIP5/${model}/${experiment}/mon/atmos/${mip}/${var}/latest/${var}_Amon_${model}_${experiment}_${mip}_*.nc /g/data/${fxdir}/DRSv2/CMIP5/${model}/${experiment}/fx/atmos/${fxmip}/sftlf/latest/sftlf_fx_${model}_${experiment}_${fxmip}.nc sftlf --ocean

done
