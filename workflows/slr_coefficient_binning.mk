# slr_coefficient_binning.mk
#
# Description: Binning of sea level rise coefficients
#
# To execute:
#   make all -n -B -f slr_coefficient_binning.mk  (-n is a dry run) (-B is a force make)
# 

.PHONY : all exp control

include cmip_config.mk


# FILE DEFINITIONS

BASIN_FILE=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/historical/${BASIN_RUN}/Ofx/basin/${GRID_OCEAN}/${BASIN_VERSION}/basin_Ofx_${MODEL}_historical_${BASIN_RUN}_${GRID_OCEAN}.nc
VOLCELLO_FILE=${VOLCELLO_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/Ofx/volcello/${GRID_OCEAN}/${OFX_VERSION_VOLCELLO}/volcello_Ofx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID_OCEAN}.nc
SALINITY_FILES_EXP := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Omon/so/${GRID_OCEAN}/${EXP_VERSION}/so*.nc)) 
TEMPERATURE_FILES_EXP := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Omon/thetao/${GRID_OCEAN}/${EXP_VERSION}/thetao*.nc))
SALINITY_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Omon/so/${GRID_OCEAN}/${CNTRL_VERSION}/so*${CNTRL_FILE_END})) 
TEMPERATURE_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Omon/thetao/${GRID_OCEAN}/${CNTRL_VERSION}/thetao*${CNTRL_FILE_END}))
ALPHA_FILES_EXP := $(sort $(wildcard ${SHARED_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Omon/alpha/${GRID_OCEAN}/${EXP_VERSION}/alpha*.nc))
BETA_FILES_EXP := $(sort $(wildcard ${SHARED_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Omon/beta/${GRID_OCEAN}/${EXP_VERSION}/beta*.nc))
ALPHA_FILES_CNTRL := $(sort $(wildcard ${SHARED_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Omon/alpha/${GRID_OCEAN}/${CNTRL_VERSION}/alpha*${CNTRL_FILE_END}))
BETA_FILES_CNTRL := $(sort $(wildcard ${SHARED_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Omon/beta/${GRID_OCEAN}/${CNTRL_VERSION}/beta*${CNTRL_FILE_END}))


# COEFFICIENT CALCULATION

# run calc_slr_coefficients.sh


# BINNING - thermal expansion coefficient (alpha)

BINNED_ALPHA_DIR_EXP=${SHARED_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/O${BIN_FREQ}/alpha/${GRID_OCEAN}/${EXP_VERSION}
BINNED_ALPHA_FILE_EXP=${BINNED_ALPHA_DIR_EXP}/alpha-binned_O${BIN_FREQ}_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID_OCEAN}_${EXP_TIME}.nc
${BINNED_ALPHA_FILE_EXP} : ${BASIN_FILE} ${VOLCELLO_FILE}
	mkdir -p ${BINNED_ALPHA_DIR_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/water_mass_binning.py ${ALPHA_FILES_EXP} thermal_expansion_coefficient $< ${BIN_FREQ} $@ --salinity_files ${SALINITY_FILES_EXP} --salinity_var sea_water_salinity --temperature_files ${TEMPERATURE_FILES_EXP} --temperature_var sea_water_conservative_temperature --volume_file $(word 2,$^)

BINNED_ALPHA_DIR_CNTRL=${SHARED_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/O${BIN_FREQ}/alpha/${GRID_OCEAN}/${CNTRL_VERSION}
BINNED_ALPHA_FILE_CNTRL=${BINNED_ALPHA_DIR_CNTRL}/alpha-binned_O${BIN_FREQ}_${MODEL}_piControl_${CNTRL_RUN}_${GRID_OCEAN}_${CNTRL_TIME}.nc
${BINNED_ALPHA_FILE_CNTRL} : ${BASIN_FILE} ${VOLCELLO_FILE}
	mkdir -p ${BINNED_ALPHA_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/water_mass_binning.py ${ALPHA_FILES_CNTRL} thermal_expansion_coefficient $< ${BIN_FREQ} $@ --salinity_files ${SALINITY_FILES_CNTRL} --salinity_var sea_water_salinity --temperature_files ${TEMPERATURE_FILES_CNTRL} --temperature_var sea_water_conservative_temperature --volume_file $(word 2,$^)


# BINNING - saline contraction coefficient (beta)

BINNED_BETA_DIR_EXP=${SHARED_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/O${BIN_FREQ}/beta/${GRID_OCEAN}/${EXP_VERSION}
BINNED_BETA_FILE_EXP=${BINNED_BETA_DIR_EXP}/beta-binned_O${BIN_FREQ}_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID_OCEAN}_${EXP_TIME}.nc
${BINNED_BETA_FILE_EXP} : ${BASIN_FILE} ${VOLCELLO_FILE}
	mkdir -p ${BINNED_BETA_DIR_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/water_mass_binning.py ${BETA_FILES_EXP} thermal_expansion_coefficient $< ${BIN_FREQ} $@ --salinity_files ${SALINITY_FILES_EXP} --salinity_var sea_water_salinity --temperature_files ${TEMPERATURE_FILES_EXP} --temperature_var sea_water_conservative_temperature --volume_file $(word 2,$^)

BINNED_BETA_DIR_CNTRL=${SHARED_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/O${BIN_FREQ}/beta/${GRID_OCEAN}/${CNTRL_VERSION}
BINNED_BETA_FILE_CNTRL=${BINNED_BETA_DIR_CNTRL}/beta-binned_O${BIN_FREQ}_${MODEL}_piControl_${CNTRL_RUN}_${GRID_OCEAN}_${CNTRL_TIME}.nc
${BINNED_BETA_FILE_CNTRL} : ${BASIN_FILE} ${VOLCELLO_FILE}
	mkdir -p ${BINNED_BETA_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/water_mass_binning.py ${BETA_FILES_CNTRL} thermal_expansion_coefficient $< ${BIN_FREQ} $@ --salinity_files ${SALINITY_FILES_CNTRL} --salinity_var sea_water_salinity --temperature_files ${TEMPERATURE_FILES_CNTRL} --temperature_var sea_water_conservative_temperature --volume_file $(word 2,$^)


# targets

exp : ${BINNED_ALPHA_FILE_EXP} ${BINNED_BETA_FILE_EXP}
control : ${BINNED_ALPHA_FILE_CNTRL} ${BINNED_BETA_FILE_CNTRL}
all : exp control


