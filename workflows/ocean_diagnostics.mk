PYTHON=/g/data/r87/dbi599/miniconda3/envs/ocean3/bin/python
SCRIPT_DIR=/home/599/dbi599/ocean-analysis/data_processing
INDIR=/g/data/fs38/publications/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2
MYDIR=/g/data/r87/dbi599/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2
OUTDIR=/g/data/e14/dbi599/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2
RUN=r1i1p1f1
VERSION_HIST=v20191108
VERSION_CNTRL=v20191112
TIME_HIST=185001-201412
TIME_CNTRL=095001-144912

THETAO_FILES_HIST := $(sort $(wildcard ${INDIR}/historical/${RUN}/Omon/thetao/gn/${VERSION_HIST}/thetao_Omon_ACCESS-CM2_historical_${RUN}_gn_*.nc))
SO_FILES_HIST := $(sort $(wildcard ${INDIR}/historical/${RUN}/Omon/so/gn/${VERSION_HIST}/so_Omon_ACCESS-CM2_historical_${RUN}_gn_*.nc))
TOS_FILES_HIST := $(sort $(wildcard ${INDIR}/historical/${RUN}/Omon/tos/gn/${VERSION_HIST}/tos_Omon_ACCESS-CM2_historical_${RUN}_gn_*.nc))
SOS_FILES_HIST := $(sort $(wildcard ${INDIR}/historical/${RUN}/Omon/sos/gn/${VERSION_HIST}/sos_Omon_ACCESS-CM2_historical_${RUN}_gn_*.nc))

THETAO_FILES_CNTRL := $(sort $(wildcard ${INDIR}/piControl/${RUN}/Omon/thetao/gn/${VERSION_CNTRL}/thetao_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
SO_FILES_CNTRL := $(sort $(wildcard ${INDIR}/piControl/${RUN}/Omon/so/gn/${VERSION_CNTRL}/so_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
TOS_FILES_CNTRL := $(sort $(wildcard ${INDIR}/piControl/${RUN}/Omon/tos/gn/${VERSION_CNTRL}/tos_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
SOS_FILES_CNTRL := $(sort $(wildcard ${INDIR}/piControl/${RUN}/Omon/sos/gn/${VERSION_CNTRL}/sos_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))

FRAZIL_FILES_HIST := $(sort $(wildcard ${MYDIR}/historical/${RUN}/Omon/frazil-3d/gn/${VERSION_HIST}/frazil-3d_Omon_ACCESS-CM2_historical_${RUN}_gn_*.nc))
MIXDOWNSLOPE_FILES_HIST := $(sort $(wildcard ${MYDIR}/historical/${RUN}/Omon/mixdownslope-temp/gn/${VERSION_HIST}/mixdownslope-temp_Omon_ACCESS-CM2_historical_${RUN}_gn_*.nc))
NEUTRAL_FILES_HIST := $(sort $(wildcard ${MYDIR}/historical/${RUN}/Omon/neutral-diffusion-temp/gn/${VERSION_HIST}/neutral-diffusion-temp_Omon_ACCESS-CM2_historical_${RUN}_gn_*.nc))
SFCHP_FILE_HIST=${MYDIR}/historical/${RUN}/Omon/sfc-hflux-pme/gn/${VERSION_HIST}/sfc-hflux-pme_Omon_ACCESS-CM2_historical_${RUN}_gn_185001-201412.nc
SWHEAT_FILES_HIST := $(sort $(wildcard ${MYDIR}/historical/${RUN}/Omon/sw-heat/gn/${VERSION_HIST}/sw-heat_Omon_ACCESS-CM2_historical_${RUN}_gn_*.nc))
ETA_FILE_HIST=${MYDIR}/historical/${RUN}/Omon/temp-eta-smooth/gn/${VERSION_HIST}/temp-eta-smooth_Omon_ACCESS-CM2_historical_${RUN}_gn_185001-201412.nc
KPP_FILES_HIST := $(sort $(wildcard ${MYDIR}/historical/${RUN}/Omon/temp-nonlocal-KPP/gn/${VERSION_HIST}/temp-nonlocal-KPP_Omon_ACCESS-CM2_historical_${RUN}_gn_*.nc))
RIVER_FILES_HIST := $(sort $(wildcard ${MYDIR}/historical/${RUN}/Omon/temp-rivermix/gn/${VERSION_HIST}/temp-rivermix_Omon_ACCESS-CM2_historical_${RUN}_gn_*.nc))
SIGMA_FILES_HIST := $(sort $(wildcard ${MYDIR}/historical/${RUN}/Omon/temp-sigma-diff/gn/${VERSION_HIST}/temp-sigma-diff_Omon_ACCESS-CM2_historical_${RUN}_gn_*.nc))
TENDENCY_FILES_HIST := $(sort $(wildcard ${MYDIR}/historical/${RUN}/Omon/temp-tendency/gn/${VERSION_HIST}/temp-tendency_Omon_ACCESS-CM2_historical_${RUN}_gn_*.nc))
CBT_FILES_HIST := $(sort $(wildcard ${MYDIR}/historical/${RUN}/Omon/temp-vdiffuse-diff-cbt/gn/${VERSION_HIST}/temp-vdiffuse-diff-cbt_Omon_ACCESS-CM2_historical_${RUN}_gn_*.nc))
K33_FILES_HIST := $(sort $(wildcard ${MYDIR}/historical/${RUN}/Omon/temp-vdiffuse-k33/gn/${VERSION_HIST}/temp-vdiffuse-k33_Omon_ACCESS-CM2_historical_${RUN}_gn_*.nc))
SBC_FILES_HIST := $(sort $(wildcard ${MYDIR}/historical/${RUN}/Omon/temp-vdiffuse-sbc/gn/${VERSION_HIST}/temp-vdiffuse-sbc_Omon_ACCESS-CM2_historical_${RUN}_gn_*.nc))

FRAZIL_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/frazil-3d/gn/${VERSION_CNTRL}/frazil-3d_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
MIXDOWNSLOPE_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/mixdownslope-temp/gn/${VERSION_CNTRL}/mixdownslope-temp_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
NEUTRAL_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/neutral-diffusion-temp/gn/${VERSION_CNTRL}/neutral-diffusion-temp_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
SFCHP_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/sfc-hflux-pme/gn/${VERSION_CNTRL}/sfc-hflux-pme_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
SWHEAT_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/sw-heat/gn/${VERSION_CNTRL}/sw-heat_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
ETA_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/temp-eta-smooth/gn/${VERSION_CNTRL}/temp-eta-smooth_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
KPP_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/temp-nonlocal-KPP/gn/${VERSION_CNTRL}/temp-nonlocal-KPP_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
RIVER_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/temp-rivermix/gn/${VERSION_CNTRL}/temp-rivermix_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
SIGMA_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/temp-sigma-diff/gn/${VERSION_CNTRL}/temp-sigma-diff_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
TENDENCY_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/temp-tendency/gn/${VERSION_CNTRL}/temp-tendency_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
CBT_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/temp-vdiffuse-diff-cbt/gn/${VERSION_CNTRL}/temp-vdiffuse-diff-cbt_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
K33_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/temp-vdiffuse-k33/gn/${VERSION_CNTRL}/temp-vdiffuse-k33_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
SBC_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/temp-vdiffuse-sbc/gn/${VERSION_CNTRL}/temp-vdiffuse-sbc_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))

AREACELLO_FILE=${INDIR}/historical/r1i1p1f1/Ofx/areacello/gn/v20191108/areacello_Ofx_ACCESS-CM2_historical_r1i1p1f1_gn.nc
BASIN_FILE=${MYDIR}/historical/r1i1p1f1/Ofx/basin/gn/v20191108/basin_Ofx_ACCESS-CM2_historical_r1i1p1f1_gn.nc

# Primary variables

WFO_BINNED_HIST_FILE=${OUTDIR}/historical/${RUN}/Omon/wfo/gn/${VERSION_HIST}/wfo-tos-sos-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
WFO_BINNED_CNTRL_FILE=${OUTDIR}/piControl/${RUN}/Omon/wfo/gn/${VERSION_CNTRL}/wfo-tos-sos-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc

FRAZIL_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/frazil-3d/gn/${VERSION_HIST}
FRAZIL_BINNED_HIST_FILE=${FRAZIL_BINNED_HIST_DIR}/frazil-3d-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${FRAZIL_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${FRAZIL_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${FRAZIL_FILES_HIST} ocn_frazil_heat_flux_over_time_step $< $@ --temperature_files ${THETAO_FILES_HIST} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_HIST} --salinity_var sea_water_salinity --area_file $(word 2,$^)
	
FRAZIL_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/frazil-3d/gn/${VERSION_CNTRL}
FRAZIL_BINNED_CNTRL_FILE=${FRAZIL_BINNED_CNTRL_DIR}/frazil-3d-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${FRAZIL_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${FRAZIL_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${FRAZIL_FILES_CNTRL} ocn_frazil_heat_flux_over_time_step $< $@ --temperature_files ${THETAO_FILES_CNTRL} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_CNTRL} --salinity_var sea_water_salinity --area_file $(word 2,$^)


MIXDOWNSLOPE_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/mixdownslope-temp/gn/${VERSION_HIST}
MIXDOWNSLOPE_BINNED_HIST_FILE=${MIXDOWNSLOPE_BINNED_HIST_DIR}/mixdownslope-temp-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${MIXDOWNSLOPE_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${MIXDOWNSLOPE_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${MIXDOWNSLOPE_FILES_HIST} "cp*mixdownslope*rho*dzt*temp" $< $@ --temperature_files ${THETAO_FILES_HIST} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_HIST} --salinity_var sea_water_salinity --area_file $(word 2,$^)
	
MIXDOWNSLOPE_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/mixdownslope-temp/gn/${VERSION_CNTRL}
MIXDOWNSLOPE_BINNED_CNTRL_FILE=${MIXDOWNSLOPE_BINNED_CNTRL_DIR}/mixdownslope-temp-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${MIXDOWNSLOPE_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${MIXDOWNSLOPE_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${MIXDOWNSLOPE_FILES_CNTRL} "cp*mixdownslope*rho*dzt*temp" $< $@ --temperature_files ${THETAO_FILES_CNTRL} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_CNTRL} --salinity_var sea_water_salinity --area_file $(word 2,$^)


NEUTRAL_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/neutral-diffusion-temp/gn/${VERSION_HIST}
NEUTRAL_BINNED_HIST_FILE=${NEUTRAL_BINNED_HIST_DIR}/neutral-diffusion-temp-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${NEUTRAL_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${NEUTRAL_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${NEUTRAL_FILES_HIST} "rho*dzt*cp*explicit neutral diffusion tendency (heating)" $< $@ --temperature_files ${THETAO_FILES_HIST} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_HIST} --salinity_var sea_water_salinity --area_file $(word 2,$^)
	
NEUTRAL_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/neutral-diffusion-temp/gn/${VERSION_CNTRL}
NEUTRAL_BINNED_CNTRL_FILE=${NEUTRAL_BINNED_CNTRL_DIR}/neutral-diffusion-temp-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${NEUTRAL_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${NEUTRAL_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${NEUTRAL_FILES_CNTRL} "rho*dzt*cp*explicit neutral diffusion tendency (heating)" $< $@ --temperature_files ${THETAO_FILES_CNTRL} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_CNTRL} --salinity_var sea_water_salinity --area_file $(word 2,$^)


SFCHP_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/sfc-hflux-pme/gn/${VERSION_HIST}
SFCHP_BINNED_HIST_FILE=${SFCHP_BINNED_HIST_DIR}/sfc-hflux-pme-tos-sos-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${SFCHP_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${SFCHP_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${SFCHP_FILE_HIST} "heat flux (relative to 0C) from pme transfer of water across ocean surface" $< $@ --temperature_files ${TOS_FILES_HIST} --temperature_var sea_surface_temperature --salinity_files ${SOS_FILES_HIST} --salinity_var sea_surface_salinity --area_file $(word 2,$^)
	
SFCHP_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/sfc-hflux-pme/gn/${VERSION_CNTRL}
SFCHP_BINNED_CNTRL_FILE=${SFCHP_BINNED_CNTRL_DIR}/sfc-hflux-pme-tos-sos-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${SFCHP_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${SFCHP_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${SFCHP_FILES_CNTRL} "heat flux (relative to 0C) from pme transfer of water across ocean surface" $< $@ --temperature_files ${TOS_FILES_CNTRL} --temperature_var sea_surface_temperature --salinity_files ${SOS_FILES_CNTRL} --salinity_var sea_surface_salinity --area_file $(word 2,$^)


SWHEAT_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/sw-heat/gn/${VERSION_HIST}
SWHEAT_BINNED_HIST_FILE=${SWHEAT_BINNED_HIST_DIR}/sw-heat-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${SWHEAT_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${SWHEAT_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${SWHEAT_FILES_HIST} downwelling_shortwave_flux_in_sea_water $< $@ --temperature_files ${THETAO_FILES_HIST} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_HIST} --salinity_var sea_water_salinity --area_file $(word 2,$^)
	
SWHEAT_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/sw-heat/gn/${VERSION_CNTRL}
SWHEAT_BINNED_CNTRL_FILE=${SWHEAT_BINNED_CNTRL_DIR}/sw-heat-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${SWHEAT_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${SWHEAT_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${SWHEAT_FILES_CNTRL} downwelling_shortwave_flux_in_sea_water $< $@ --temperature_files ${THETAO_FILES_CNTRL} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_CNTRL} --salinity_var sea_water_salinity --area_file $(word 2,$^)


ETA_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/temp-eta-smooth/gn/${VERSION_HIST}
ETA_BINNED_HIST_FILE=${ETA_BINNED_HIST_DIR}/temp-eta-smooth-tos-sos-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${ETA_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${ETA_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${ETA_FILE_HIST} "surface smoother for temp" $< $@ --temperature_files ${TOS_FILES_HIST} --temperature_var sea_surface_temperature --salinity_files ${SOS_FILES_HIST} --salinity_var sea_surface_salinity --area_file $(word 2,$^)
	
ETA_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/temp-eta-smooth/gn/${VERSION_CNTRL}
ETA_BINNED_CNTRL_FILE=${ETA_BINNED_CNTRL_DIR}/temp-eta-smooth-tos-sos-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${ETA_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${ETA_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${ETA_FILES_CNTRL} "surface smoother for temp" $< $@ --temperature_files ${TOS_FILES_CNTRL} --temperature_var sea_surface_temperature --salinity_files ${SOS_FILES_CNTRL} --salinity_var sea_surface_salinity --area_file $(word 2,$^)


KPP_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/temp-nonlocal-KPP/gn/${VERSION_HIST}
KPP_BINNED_HIST_FILE=${KPP_BINNED_HIST_DIR}/temp-nonlocal-KPP-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${KPP_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${KPP_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${KPP_FILES_HIST} "cp*rho*dzt*nonlocal tendency from KPP" $< $@ --temperature_files ${THETAO_FILES_HIST} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_HIST} --salinity_var sea_water_salinity --area_file $(word 2,$^)
	
KPP_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/temp-nonlocal-KPP/gn/${VERSION_CNTRL}
KPP_BINNED_CNTRL_FILE=${KPP_BINNED_CNTRL_DIR}/temp-nonlocal-KPP-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${KPP_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${KPP_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${KPP_FILES_CNTRL} "cp*rho*dzt*nonlocal tendency from KPP" $< $@ --temperature_files ${THETAO_FILES_CNTRL} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_CNTRL} --salinity_var sea_water_salinity --area_file $(word 2,$^)


RIVER_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/temp-rivermix/gn/${VERSION_HIST}
RIVER_BINNED_HIST_FILE=${RIVER_BINNED_HIST_DIR}/temp-rivermix-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${RIVER_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${RIVER_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${RIVER_FILES_HIST} "cp*rivermix*rho_dzt*temp" $< $@ --temperature_files ${THETAO_FILES_HIST} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_HIST} --salinity_var sea_water_salinity --area_file $(word 2,$^)

RIVER_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/temp-rivermix/gn/${VERSION_CNTRL}
RIVER_BINNED_CNTRL_FILE=${RIVER_BINNED_CNTRL_DIR}/temp-rivermix-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${RIVER_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${RIVER_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${RIVER_FILES_CNTRL} "cp*rivermix*rho_dzt*temp" $< $@ --temperature_files ${THETAO_FILES_CNTRL} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_CNTRL} --salinity_var sea_water_salinity --area_file $(word 2,$^)


SIGMA_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/temp-sigma-diff/gn/${VERSION_HIST}
SIGMA_BINNED_HIST_FILE=${SIGMA_BINNED_HIST_DIR}/temp-sigma-diff-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${SIGMA_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${SIGMA_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${SIGMA_FILES_HIST} "thk wghtd sigma-diffusion heating" $< $@ --temperature_files ${THETAO_FILES_HIST} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_HIST} --salinity_var sea_water_salinity --area_file $(word 2,$^)
	
SIGMA_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/temp-sigma-diff/gn/${VERSION_CNTRL}
SIGMA_BINNED_CNTRL_FILE=${SIGMA_BINNED_CNTRL_DIR}/temp-sigma-diff-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${SIGMA_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${SIGMA_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${SIGMA_FILES_CNTRL} "thk wghtd sigma-diffusion heating" $< $@ --temperature_files ${THETAO_FILES_CNTRL} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_CNTRL} --salinity_var sea_water_salinity --area_file $(word 2,$^)


TENDENCY_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/temp-tendency/gn/${VERSION_HIST}
TENDENCY_BINNED_HIST_FILE=${TENDENCY_BINNED_HIST_DIR}/temp-tendency-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${TENDENCY_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${TENDENCY_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${TENDENCY_FILES_HIST} "time tendency for tracer Conservative temperature" $< $@ --temperature_files ${THETAO_FILES_HIST} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_HIST} --salinity_var sea_water_salinity --area_file $(word 2,$^)

TENDENCY_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/temp-tendency/gn/${VERSION_CNTRL}
TENDENCY_BINNED_CNTRL_FILE=${TENDENCY_BINNED_CNTRL_DIR}/temp-tendency-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${TENDENCY_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${TENDENCY_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${TENDENCY_FILES_CNTRL} "time tendency for tracer Conservative temperature" $< $@ --temperature_files ${THETAO_FILES_CNTRL} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_CNTRL} --salinity_var sea_water_salinity --area_file $(word 2,$^)


CBT_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/temp-vdiffuse-diff-cbt/gn/${VERSION_HIST}
CBT_BINNED_HIST_FILE=${CBT_BINNED_HIST_DIR}/temp-vdiffuse-diff-cbt-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${CBT_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${CBT_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${CBT_FILES_HIST} "vert diffusion of heat due to diff_cbt" $< $@ --temperature_files ${THETAO_FILES_HIST} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_HIST} --salinity_var sea_water_salinity --area_file $(word 2,$^)
	
CBT_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/temp-vdiffuse-diff-cbt/gn/${VERSION_CNTRL}
CBT_BINNED_CNTRL_FILE=${CBT_BINNED_CNTRL_DIR}/temp-vdiffuse-diff-cbt-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${CBT_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${CBT_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${CBT_FILES_CNTRL} "vert diffusion of heat due to diff_cbt" $< $@ --temperature_files ${THETAO_FILES_CNTRL} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_CNTRL} --salinity_var sea_water_salinity --area_file $(word 2,$^)
	
	
K33_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/temp-vdiffuse-k33/gn/${VERSION_HIST}
K33_BINNED_HIST_FILE=${K33_BINNED_HIST_DIR}/temp-vdiffuse-k33-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${K33_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${K33_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${K33_FILES_HIST} "vert diffusion of heat due to K33 from neutral diffusion" $< $@ --temperature_files ${THETAO_FILES_HIST} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_HIST} --salinity_var sea_water_salinity --area_file $(word 2,$^)
	
K33_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/temp-vdiffuse-k33/gn/${VERSION_CNTRL}
K33_BINNED_CNTRL_FILE=${K33_BINNED_CNTRL_DIR}/temp-vdiffuse-k33-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${K33_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${K33_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${K33_FILES_CNTRL} "vert diffusion of heat due to K33 from neutral diffusion" $< $@ --temperature_files ${THETAO_FILES_CNTRL} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_CNTRL} --salinity_var sea_water_salinity --area_file $(word 2,$^)


SBC_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/temp-vdiffuse-sbc/gn/${VERSION_HIST}
SBC_BINNED_HIST_FILE=${SBC_BINNED_HIST_DIR}/temp-vdiffuse-sbc-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${SBC_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${SBC_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${SBC_FILES_HIST} "vert diffusion of heat due to surface flux" $< $@ --temperature_files ${THETAO_FILES_HIST} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_HIST} --salinity_var sea_water_salinity --area_file $(word 2,$^)
	
SBC_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/temp-vdiffuse-sbc/gn/${VERSION_CNTRL}
SBC_BINNED_CNTRL_FILE=${SBC_BINNED_CNTRL_DIR}/temp-vdiffuse-sbc-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${SBC_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${SBC_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${SBC_FILES_CNTRL} "vert diffusion of heat due to surface flux" $< $@ --temperature_files ${THETAO_FILES_CNTRL} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_CNTRL} --salinity_var sea_water_salinity --area_file $(word 2,$^)


# Secondary variables

VMIX_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/vmix/gn/${VERSION_HIST}
VMIX_BINNED_HIST_FILE=${VMIX_BINNED_HIST_DIR}/vmix-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${VMIX_BINNED_HIST_FILE} : ${CBT_BINNED_HIST_FILE} ${KPP_BINNED_HIST_FILE}
	mkdir -p ${VMIX_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/calc_binned_flux_sum.py $< $(word 2,$^) vmix $@ --invars "vert diffusion of heat due to diff_cbt" "cp*rho*dzt*nonlocal tendency from KPP" 

VMIX_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/vmix/gn/${VERSION_CNTRL}
VMIX_BINNED_CNTRL_FILE=${VMIX_BINNED_CNTRL_DIR}/vmix-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${VMIX_BINNED_CNTRL_FILE} : ${CBT_BINNED_CNTRL_FILE} ${KPP_BINNED_CNTRL_FILE}
	mkdir -p ${VMIX_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/calc_binned_flux_sum.py $< $(word 2,$^) vmix $@ --invars "vert diffusion of heat due to diff_cbt" "cp*rho*dzt*nonlocal tendency from KPP" 


SMIX_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/smix/gn/${VERSION_HIST}
SMIX_BINNED_HIST_FILE=${SMIX_BINNED_HIST_DIR}/smix-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${SMIX_BINNED_HIST_FILE} : ${MIXDOWNSLOPE_BINNED_HIST_FILE} ${SIGMA_BINNED_HIST_FILE}
	mkdir -p ${SMIX_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/calc_binned_flux_sum.py $< $(word 2,$^) smix $@ --invars "cp*mixdownslope*rho*dzt*temp" "thk wghtd sigma-diffusion heating" 

SMIX_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/smix/gn/${VERSION_CNTRL}
SMIX_BINNED_CNTRL_FILE=${SMIX_BINNED_CNTRL_DIR}/smix-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${SMIX_BINNED_CNTRL_FILE} : ${MIXDOWNSLOPE_BINNED_CNTRL_FILE} ${SIGMA_BINNED_CNTRL_FILE}
	mkdir -p ${SMIX_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/calc_binned_flux_sum.py $< $(word 2,$^) smix $@ --invars "cp*mixdownslope*rho*dzt*temp" "thk wghtd sigma-diffusion heating" 


SFCV_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/sfcv/gn/${VERSION_HIST}
SFCV_BINNED_HIST_FILE=${SFCV_BINNED_HIST_DIR}/sfcv-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${SFCV_BINNED_HIST_FILE} : ${RIVER_BINNED_HIST_FILE} ${SFCHP_BINNED_HIST_FILE}
	mkdir -p ${SFCV_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/calc_binned_flux_sum.py $< $(word 2,$^) sfcv $@ --invars "cp*rivermix*rho_dzt*temp" "heat flux (relative to 0C) from pme transfer of water across ocean surface" 

SFCV_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/sfcv/gn/${VERSION_CNTRL}
SFCV_BINNED_CNTRL_FILE=${SFCV_BINNED_CNTRL_DIR}/sfcv-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${SFCV_BINNED_CNTRL_FILE} : ${RIVER_BINNED_CNTRL_FILE} ${SFCHP_BINNED_CNTRL_FILE}
	mkdir -p ${SFCV_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/calc_binned_flux_sum.py $< $(word 2,$^) sfcv $@ --invars "cp*rivermix*rho_dzt*temp" "heat flux (relative to 0C) from pme transfer of water across ocean surface"
	

SFCH_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/sfch/gn/${VERSION_HIST}
SFCH_BINNED_HIST_FILE=${SFCH_BINNED_HIST_DIR}/sfch-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${SFCH_BINNED_HIST_FILE} : ${SBC_BINNED_HIST_FILE} ${SWHEAT_BINNED_HIST_FILE} ${FRAZIL_BINNED_HIST_FILE} ${ETA_BINNED_HIST_FILE}
	mkdir -p ${SFCH_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/calc_binned_flux_sum.py $< $(word 2,$^) $(word 3,$^) $(word 4,$^) sfch $@ --invars "vert diffusion of heat due to surface flux" "penetrative shortwave heating" "ocn frazil heat flux over time step" "surface smoother for temp"
	
SFCH_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/sfch/gn/${VERSION_CNTRL}
SFCH_BINNED_CNTRL_FILE=${SFCH_BINNED_CNTRL_DIR}/sfch-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${SFCH_BINNED_CNTRL_FILE} : ${SBC_BINNED_CNTRL_FILE} ${SWHEAT_BINNED_CNTRL_FILE} ${FRAZIL_BINNED_CNTRL_FILE} ${ETA_BINNED_CNTRL_FILE}
	mkdir -p ${SFCH_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/calc_binned_flux_sum.py $< $(word 2,$^) $(word 3,$^) $(word 4,$^) sfch $@ --invars "vert diffusion of heat due to surface flux" "penetrative shortwave heating" "ocn frazil heat flux over time step" "surface smoother for temp"


SFC_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/sfc/gn/${VERSION_HIST}
SFC_BINNED_HIST_FILE=${SFC_BINNED_HIST_DIR}/sfc-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${SFC_BINNED_HIST_FILE} : ${SFCH_BINNED_HIST_FILE} ${SFCV_BINNED_HIST_FILE}
	mkdir -p ${SFC_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/calc_binned_flux_sum.py $< $(word 2,$^) sfc $@ --invars "surface heat fluxes" "surface heat fluxes from surface volume fluxes"

SFC_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/sfc/gn/${VERSION_CNTRL}
SFC_BINNED_CNTRL_FILE=${SFC_BINNED_CNTRL_DIR}/sfc-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${SFC_BINNED_CNTRL_FILE} : ${SFCH_BINNED_CNTRL_FILE} ${SFCV_BINNED_CNTRL_FILE}
	mkdir -p ${SFC_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/calc_binned_flux_sum.py $< $(word 2,$^) sfc $@ --invars "surface heat fluxes" "surface heat fluxes from surface volume fluxes"


RMIX_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/rmix/gn/${VERSION_HIST}
RMIX_BINNED_HIST_FILE=${RMIX_BINNED_HIST_DIR}/rmix-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${RMIX_BINNED_HIST_FILE} : ${K33_BINNED_HIST_FILE} ${NEUTRAL_BINNED_HIST_FILE}
	mkdir -p ${RMIX_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/calc_binned_flux_sum.py $< $(word 2,$^) rmix $@ --invars "vert diffusion of heat due to K33 from neutral diffusion" "rho*dzt*cp*explicit neutral diffusion tendency (heating)"

RMIX_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/rmix/gn/${VERSION_CNTRL}
RMIX_BINNED_CNTRL_FILE=${RMIX_BINNED_CNTRL_DIR}/rmix-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${RMIX_BINNED_CNTRL_FILE} : ${K33_BINNED_CNTRL_FILE} ${NEUTRAL_BINNED_CNTRL_FILE}
	mkdir -p ${RMIX_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/calc_binned_flux_sum.py $< $(word 2,$^) rmix $@ --invars "vert diffusion of heat due to K33 from neutral diffusion" "rho*dzt*cp*explicit neutral diffusion tendency (heating)"


MIX_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/mix/gn/${VERSION_HIST}
MIX_BINNED_HIST_FILE=${MIX_BINNED_HIST_DIR}/mix-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${MIX_BINNED_HIST_FILE} : ${VMIX_BINNED_HIST_FILE} ${SMIX_BINNED_HIST_FILE} ${RMIX_BINNED_HIST_FILE}
	mkdir -p ${MIX_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/calc_binned_flux_sum.py $< $(word 2,$^) $(word 3,$^) mix $@ --invars vertical_mixing miscellaneous_mixing neutral_diffusion

MIX_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/mix/gn/${VERSION_CNTRL}
MIX_BINNED_CNTRL_FILE=${MIX_BINNED_CNTRL_DIR}/mix-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${MIX_BINNED_CNTRL_FILE} : ${VMIX_BINNED_CNTRL_FILE} ${SMIX_BINNED_CNTRL_FILE} ${RMIX_BINNED_CNTRL_FILE}
	mkdir -p ${MIX_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/calc_binned_flux_sum.py $< $(word 2,$^) $(word 3,$^) mix $@ --invars vertical_mixing miscellaneous_mixing neutral_diffusion


SFCI_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/sfci/gn/${VERSION_HIST}
SFCI_BINNED_HIST_FILE=${SFCI_BINNED_HIST_DIR}/sfci-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${SFCI_BINNED_HIST_FILE} : ${SFC_BINNED_HIST_FILE} ${WFO_BINNED_HIST_FILE}
	mkdir -p ${SFCI_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/calc_sfci.py $< $(word 2,$^) $@

SFCI_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/sfci/gn/${VERSION_CNTRL}
SFCI_BINNED_CNTRL_FILE=${SFCI_BINNED_CNTRL_DIR}/sfci-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${SFCI_BINNED_CNTRL_FILE} : ${SFC_BINNED_CNTRL_FILE} ${WFO_BINNED_CNTRL_FILE}
	mkdir -p ${SFCI_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/calc_sfci.py $< $(word 2,$^) $@


# Documentation

## frazil-3d : bin heat flux from frazil ice
frazil-3d : ${FRAZIL_BINNED_HIST_FILE} ${FRAZIL_BINNED_CNTRL_FILE}

## mixdownslope-temp : 
mixdownslope-temp : ${MIXDOWNSLOPE_BINNED_HIST_FILE} ${MIXDOWNSLOPE_BINNED_CNTRL_FILE}

## neutral-diffusion-temp : bin neutral diffusion
neutral-diffusion-temp : ${NEUTRAL_BINNED_HIST_FILE} ${NEUTRAL_BINNED_CNTRL_FILE}

## sfc-hflux-pme : heat flux (relative to 0C) from pme transfer of water across ocean surface
sfc-hflux-pme : ${SFCHP_BINNED_HIST_FILE} ${SFCHP_BINNED_CNTRL_FILE}

## sw-heat :
sw-heat : ${SWHEAT_BINNED_HIST_FILE} ${SWHEAT_BINNED_CNTRL_FILE}

## temp-eta-smooth :
temp-eta-smooth : ${ETA_BINNED_HIST_FILE} ${ETA_BINNED_CNTRL_FILE}

## temp-nonlocal-KPP :
temp-nonlocal-KPP : ${KPP_BINNED_HIST_FILE} ${KPP_BINNED_CNTRL_FILE}

## temp-rivermix :
temp-rivermix : ${RIVER_BINNED_HIST_FILE} ${RIVER_BINNED_CNTRL_FILE}

## temp-sigma-diff :
temp-sigma-diff : ${SIGMA_BINNED_HIST_FILE} ${SIGMA_BINNED_CNTRL_FILE}

## temp-tendency :
temp-tendency : ${TENDENCY_BINNED_HIST_FILE} ${TENDENCY_BINNED_CNTRL_FILE}

## temp-vdiffuse-diff-cbt :
temp-vdiffuse-diff-cbt : ${CBT_BINNED_HIST_FILE} ${CBT_BINNED_CNTRL_FILE}

## temp-vdiffuse-k33 :
temp-vdiffuse-k33 : ${K33_BINNED_HIST_FILE} ${K33_BINNED_CNTRL_FILE}

## temp-vdiffuse-sbc :
temp-vdiffuse-sbc : ${SBC_BINNED_HIST_FILE} ${SBC_BINNED_CNTRL_FILE}

## vmix : vertical mixing
vmix : ${VMIX_BINNED_HIST_FILE} ${VMIX_BINNED_CNTRL_FILE}

## smix : miscellaneous mixing
smix : ${SMIX_BINNED_HIST_FILE} ${SMIX_BINNED_CNTRL_FILE}

## sfcv : surface heat fluxes from surface volume fluxes
sfcv : ${SFCV_BINNED_HIST_FILE} ${SFCV_BINNED_CNTRL_FILE}

## sfch : surface heat fluxes
sfch : ${SFCH_BINNED_HIST_FILE} ${SFCH_BINNED_CNTRL_FILE}

## sfc : total surface forcing
sfc : ${SFC_BINNED_HIST_FILE} ${SFC_BINNED_CNTRL_FILE}

## sfci : total interal surface forcing
sfci : ${SFCI_BINNED_HIST_FILE} ${SFCI_BINNED_CNTRL_FILE}

## rmix : neutral diffusion
rmix : ${RMIX_BINNED_HIST_FILE} ${RMIX_BINNED_CNTRL_FILE}

## mix : total explicit mixing
mix : ${MIX_BINNED_HIST_FILE} ${MIX_BINNED_CNTRL_FILE}

## all : bin all variables
all : frazil-3d mixdownslope-temp neutral-diffusion-temp sfc-hflux-pme sw-heat temp-eta-smooth temp-nonlocal-KPP temp-rivermix temp-sigma-diff temp-tendency temp-vdiffuse-diff-cbt temp-vdiffuse-k33 temp-vdiffuse-sbc vmix smix sfcv sfch sfc sfci rmix mix

## help : show this message.
help :
	@echo "Usage: $ make <target> -f ocean_diagnostics.mk"
	@echo "Options: -n  show commands but do not execute"
	@echo "         -B  force update"
	@echo "Targets:" 
	@grep -h -E '^##' ./ocean_diagnostics.mk | sed -e 's/## //g' | column -t -s ':'



