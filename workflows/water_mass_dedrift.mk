# water_mass_dedrift.mk
#
# Description: De-drift the ocean volume binned by temperature
#
# To execute:
#   make -n -B -f water_mass_dedrift.mk  (-n is a dry run) (-B is a force make)

all : plot

include water_mass_dedrift_config.mk


# File definitions

VOLCELLO_FILE=${VOLCELLO_DIR}/${INSTITUTION}/${MODEL}/${FX_EXP}/${RUN}/Ofx/volcello/${GRID}/${VOLCELLO_VERSION}/volcello_Ofx_${MODEL}_${FX_EXP}_${RUN}_${GRID}.nc
BASIN_FILE=${MY_DATA_DIR}/${INSTITUTION}/${MODEL}/${FX_EXP}/${RUN}/Ofx/basin/${GRID}/${BASIN_VERSION}/basin_Ofx_${MODEL}_${FX_EXP}_${RUN}_${GRID}.nc
SALINITY_FILES_HIST := $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Omon/so/${GRID}/${HIST_VERSION}/so*.nc) 
TEMPERATURE_FILES_HIST := $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Omon/thetao/${GRID}/${HIST_VERSION}/thetao*.nc)
SALINITY_FILES_CNTRL := $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/piControl/${RUN}/Omon/so/${GRID}/${CNTRL_VERSION}/so*.nc) 
TEMPERATURE_FILES_CNTRL := $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/piControl/${RUN}/Omon/thetao/${GRID}/${CNTRL_VERSION}/thetao*.nc)


# Water mass files

WATER_MASS_DIR_HIST=${MY_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Omon/water-mass/${GRID}/${HIST_VERSION}
WATER_MASS_FILE_HIST=${WATER_MASS_DIR_HIST}/water-mass_Omon_${MODEL}_historical_${RUN}_${GRID}_${HIST_TIME}.nc
${WATER_MASS_FILE_HIST} : ${VOLCELLO_FILE} ${BASIN_FILE}
	mkdir -p ${WATER_MASS_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_water_mass_components.py $< $(word 2,$^) $@ --salinity_files ${SALINITY_FILES_HIST} --temperature_files ${TEMPERATURE_FILES_HIST}

WATER_MASS_DIR_CNTRL=${MY_DATA_DIR}/${INSTITUTION}/${MODEL}/piControl/${RUN}/Omon/water-mass/${GRID}/${CNTRL_VERSION}
WATER_MASS_FILE_CNTRL=${WATER_MASS_DIR_CNTRL}/water-mass_Omon_${MODEL}_piControl_${RUN}_${GRID}_${CNTRL_TIME}.nc
${WATER_MASS_FILE_CNTRL} : ${VOLCELLO_FILE} ${BASIN_FILE}
	mkdir -p ${WATER_MASS_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_water_mass_components.py $< $(word 2,$^) $@ --salinity_files ${SALINITY_FILES_CNTRL} --temperature_files ${TEMPERATURE_FILES_CNTRL}


# Drift removal

DRIFT_COEFFICIENT_FILE=${WATER_MASS_DIR_CNTRL}/volcello-tbin-coefficients_Omon_${MODEL}_piControl_${RUN}_${GRID}_${CNTRL_TIME}.nc
${DRIFT_COEFFICIENT_FILE} : ${WATER_MASS_FILE_CNTRL}
	${PYTHON}  ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< Ocean_Grid-Cell_Volume_binned_by_temperature $@

DEDRIFTED_FILE=${WATER_MASS_DIR_HIST}/volcello-tbin-dedrifted_Omon_${MODEL}_historical_${RUN}_${GRID}_${HIST_TIME}.nc
${DEDRIFTED_FILE} : ${WATER_MASS_FILE_HIST} ${DRIFT_COEFFICIENT_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift_year_axis.py $< Ocean_Grid-Cell_Volume_binned_by_temperature $(word 2,$^) $@ ${BRANCH_YEAR}

# Plot

PLOT_FILE=/g/data/r87/dbi599/temp/volcello-tbin-dedrifted_Omon_${MODEL}_piControl_${RUN}_${GRID}_${CNTRL_TIME}_bin6.png
plot : ${DRIFT_COEFFICIENT_FILE} ${WATER_MASS_FILE_CNTRL} ${WATER_MASS_FILE_HIST} ${DEDRIFTED_FILE}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py Ocean_Grid-Cell_Volume_binned_by_temperature $< ${PLOT_FILE} --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 6 -1 ${BRANCH_YEAR}




