PYTHON=/g/data/r87/dbi599/miniconda3/envs/ocean3/bin/python
SCRIPT_DIR=/home/599/dbi599/ocean-analysis/data_processing/
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
SFCHP_FILE_HIST=${INDIR}/historical/${RUN}/Omon/sfc-hflux-pme/gn/${VERSION_HIST}/sfc-hflux-pme_Omon_ACCESS-CM2_historical_${RUN}_gn_185001-201412.nc
SWHEAT_FILES_HIST := $(sort $(wildcard ${MYDIR}/historical/${RUN}/Omon/sw-heat/gn/${VERSION_HIST}/sw-heat_Omon_ACCESS-CM2_historical_${RUN}_gn_*.nc))
ETA_FILE_HIST=${INDIR}/historical/${RUN}/Omon/temp-eta-smooth/gn/${VERSION_HIST}/temp-eta-smooth_Omon_ACCESS-CM2_historical_${RUN}_gn_185001-201412.nc
KPP_FILES_HIST := $(sort $(wildcard ${MYDIR}/historical/${RUN}/Omon/temp-nonlocal-KPP/gn/${VERSION_HIST}/temp-nonlocal-KPP_Omon_ACCESS-CM2_historical_${RUN}_gn_*.nc))

FRAZIL_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/frazil-3d/gn/${VERSION_CNTRL}/frazil-3d_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
MIXDOWNSLOPE_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/mixdownslope-temp/gn/${VERSION_CNTRL}/mixdownslope-temp_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
NEUTRAL_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/neutral-diffusion-temp/gn/${VERSION_CNTRL}/neutral-diffusion-temp_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
SFCHP_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/sfc-hflux-pme/gn/${VERSION_CNTRL}/sfc-hflux-pme_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
SWHEAT_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/sw-heat/gn/${VERSION_CNTRL}/sw-heat_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
ETA_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/temp-eta-smooth/gn/${VERSION_CNTRL}/temp-eta-smooth_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))
KPP_FILES_CNTRL := $(sort $(wildcard ${MYDIR}/piControl/${RUN}/Omon/temp-nonlocal-KPP/gn/${VERSION_CNTRL}/temp-nonlocal-KPP_Omon_ACCESS-CM2_piControl_${RUN}_gn_*.nc))

AREACELLO_FILE=${INDIR}/historical/r1i1p1f1/Ofx/areacello/gn/v20191108/areacello_Ofx_ACCESS-CM2_historical_r1i1p1f1_gn.nc
BASIN_FILE=/g/data/r87/dbi599/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/historical/r1i1p1f1/Ofx/basin/gn/v20191118/basin_Ofx_ACCESS-CM2_historical_r1i1p1f1_gn.nc


FRAZIL_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/frazil-3d/gn/${VERSION_HIST}/
FRAZIL_BINNED_HIST_FILE=${FRAZIL_BINNED_HIST_DIR}/frazil-3d-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${FRAZIL_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${FRAZIL_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${FRAZIL_FILES_HIST} ocn_frazil_heat_flux_over_time_step $< $@ --temperature_files ${THETAO_FILES_HIST} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_HIST} --salinity_var sea_water_salinity --area_file $(word 2,$^)
	
FRAZIL_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/frazil-3d/gn/${VERSION_CNTRL}/
FRAZIL_BINNED_CNTRL_FILE=${FRAZIL_BINNED_CNTRL_DIR}/frazil-3d-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${FRAZIL_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${FRAZIL_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${FRAZIL_FILES_CNTRL} ocn_frazil_heat_flux_over_time_step $< $@ --temperature_files ${THETAO_FILES_CNTRL} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_CNTRL} --salinity_var sea_water_salinity --area_file $(word 2,$^)


MIXDOWNSLOPE_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/mixdownslope-temp/gn/${VERSION_HIST}/
MIXDOWNSLOPE_BINNED_HIST_FILE=${MIXDOWNSLOPE_BINNED_HIST_DIR}/mixdownslope-temp-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${MIXDOWNSLOPE_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${MIXDOWNSLOPE_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${MIXDOWNSLOPE_FILES_HIST} "cp*mixdownslope*rho*dzt*temp" $< $@ --temperature_files ${THETAO_FILES_HIST} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_HIST} --salinity_var sea_water_salinity --area_file $(word 2,$^)
	
MIXDOWNSLOPE_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/mixdownslope-temp/gn/${VERSION_CNTRL}/
MIXDOWNSLOPE_BINNED_CNTRL_FILE=${MIXDOWNSLOPE_BINNED_CNTRL_DIR}/mixdownslope-temp-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${MIXDOWNSLOPE_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${MIXDOWNSLOPE_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${MIXDOWNSLOPE_FILES_CNTRL} "cp*mixdownslope*rho*dzt*temp" $< $@ --temperature_files ${THETAO_FILES_CNTRL} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_CNTRL} --salinity_var sea_water_salinity --area_file $(word 2,$^)


NEUTRAL_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/neutral-diffusion-temp/gn/${VERSION_HIST}/
NEUTRAL_BINNED_HIST_FILE=${NEUTRAL_BINNED_HIST_DIR}/neutral-diffusion-temp-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${NEUTRAL_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${NEUTRAL_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${NEUTRAL_FILES_HIST} "rho*dzt*cp*explicit neutral diffusion tendency (heating)" $< $@ --temperature_files ${THETAO_FILES_HIST} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_HIST} --salinity_var sea_water_salinity --area_file $(word 2,$^)
	
NEUTRAL_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/neutral-diffusion-temp/gn/${VERSION_CNTRL}/
NEUTRAL_BINNED_CNTRL_FILE=${NEUTRAL_BINNED_CNTRL_DIR}/neutral-diffusion-temp-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${NEUTRAL_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${NEUTRAL_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${NEUTRAL_FILES_CNTRL} "rho*dzt*cp*explicit neutral diffusion tendency (heating)" $< $@ --temperature_files ${THETAO_FILES_CNTRL} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_CNTRL} --salinity_var sea_water_salinity --area_file $(word 2,$^)


SFCHP_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/sfc-hflux-pme/gn/${VERSION_HIST}/
SFCHP_BINNED_HIST_FILE=${SFCHP_BINNED_HIST_DIR}/sfc-hflux-pme-tos-sos-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${SFCHP_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${SFCHP_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${SFCHP_FILE_HIST} "heat flux (relative to 0C) from pme transfer of water across ocean surface" $< $@ --temperature_files ${TOS_FILES_HIST} --temperature_var sea_surface_temperature --salinity_files ${SOS_FILES_HIST} --salinity_var sea_surface_salinity --area_file $(word 2,$^)
	
SFCHP_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/sfc-hflux-pme/gn/${VERSION_CNTRL}/
SFCHP_BINNED_CNTRL_FILE=${SFCHP_BINNED_CNTRL_DIR}/sfc-hflux-pme-tos-sos-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${SFCHP_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${SFCHP_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${SFCHP_FILES_CNTRL} "heat flux (relative to 0C) from pme transfer of water across ocean surface" $< $@ --temperature_files ${TOS_FILES_CNTRL} --temperature_var sea_surface_temperature --salinity_files ${SOS_FILES_CNTRL} --salinity_var sea_surface_salinity --area_file $(word 2,$^)


SWHEAT_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/sw-heat/gn/${VERSION_HIST}/
SWHEAT_BINNED_HIST_FILE=${SWHEAT_BINNED_HIST_DIR}/sw-heat-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${SWHEAT_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${SWHEAT_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${SWHEAT_FILES_HIST} downwelling_shortwave_flux_in_sea_water $< $@ --temperature_files ${THETAO_FILES_HIST} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_HIST} --salinity_var sea_water_salinity --area_file $(word 2,$^)
	
SWHEAT_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/sw-heat/gn/${VERSION_CNTRL}/
SWHEAT_BINNED_CNTRL_FILE=${SWHEAT_BINNED_CNTRL_DIR}/sw-heat-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${SWHEAT_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${SWHEAT_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${SWHEAT_FILES_CNTRL} downwelling_shortwave_flux_in_sea_water $< $@ --temperature_files ${THETAO_FILES_CNTRL} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_CNTRL} --salinity_var sea_water_salinity --area_file $(word 2,$^)


ETA_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/temp-eta-smooth/gn/${VERSION_HIST}/
ETA_BINNED_HIST_FILE=${ETA_BINNED_HIST_DIR}/temp-eta-smooth-tos-sos-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${ETA_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${ETA_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${ETA_FILE_HIST} "surface smoother for temp" $< $@ --temperature_files ${TOS_FILES_HIST} --temperature_var sea_surface_temperature --salinity_files ${SOS_FILES_HIST} --salinity_var sea_surface_salinity --area_file $(word 2,$^)
	
ETA_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/temp-eta-smooth/gn/${VERSION_CNTRL}/
ETA_BINNED_CNTRL_FILE=${ETA_BINNED_CNTRL_DIR}/temp-eta-smooth-tos-sos-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${ETA_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${ETA_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${ETA_FILES_CNTRL} "surface smoother for temp" $< $@ --temperature_files ${TOS_FILES_CNTRL} --temperature_var sea_surface_temperature --salinity_files ${SOS_FILES_CNTRL} --salinity_var sea_surface_salinity --area_file $(word 2,$^)


KPP_BINNED_HIST_DIR=${OUTDIR}/historical/${RUN}/Omon/temp-nonlocal-KPP/gn/${VERSION_HIST}/
KPP_BINNED_HIST_FILE=${KPP_BINNED_HIST_DIR}/temp-nonlocal-KPP-thetao-so-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_${TIME_HIST}.nc
${KPP_BINNED_HIST_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${KPP_BINNED_HIST_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${KPP_FILES_HIST} "cp*rho*dzt*nonlocal tendency from KPP" $< $@ --temperature_files ${THETAO_FILES_HIST} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_HIST} --salinity_var sea_water_salinity --area_file $(word 2,$^)
	
KPP_BINNED_CNTRL_DIR=${OUTDIR}/piControl/${RUN}/Omon/temp-nonlocal-KPP/gn/${VERSION_CNTRL}/
KPP_BINNED_CNTRL_FILE=${KPP_BINNED_CNTRL_DIR}/temp-nonlocal-KPP-thetao-so-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_${TIME_CNTRL}.nc
${KPP_BINNED_CNTRL_FILE} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${KPP_BINNED_CNTRL_DIR}
	${PYTHON} ${SCRIPT_DIR}/water_mass_binning.py ${KPP_FILES_CNTRL} "cp*rho*dzt*nonlocal tendency from KPP" $< $@ --temperature_files ${THETAO_FILES_CNTRL} --temperature_var sea_water_potential_temperature --salinity_files ${SO_FILES_CNTRL} --salinity_var sea_water_salinity --area_file $(word 2,$^)


frazil-3d : ${FRAZIL_BINNED_HIST_FILE} ${FRAZIL_BINNED_CNTRL_FILE}
mixdownslope-temp : ${MIXDOWNSLOPE_BINNED_HIST_FILE} ${MIXDOWNSLOPE_BINNED_CNTRL_FILE}
neutral-diffusion-temp : ${NEUTRAL_BINNED_HIST_FILE} ${NEUTRAL_BINNED_CNTRL_FILE}
sfc-hflux-pme : ${SFCHP_BINNED_HIST_FILE} ${SFCHP_BINNED_CNTRL_FILE}
sw-heat : ${SWHEAT_BINNED_HIST_FILE} ${SWHEAT_BINNED_CNTRL_FILE}
temp-eta-smooth : ${ETA_BINNED_HIST_FILE} ${ETA_BINNED_CNTRL_FILE}
temp-nonlocal-KPP : ${KPP_BINNED_HIST_FILE} ${KPP_BINNED_CNTRL_FILE}



