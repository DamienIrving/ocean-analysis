# water_mass_dedrift.mk
#
# Description: De-drift the ocean volume binned by temperature
#
# To execute:
#   make all -n -B -f water_mass_dedrift.mk  (-n is a dry run) (-B is a force make)
#
#   (Options besides all: wfo volcello-tbin so-volcello-tbin surface all-but-volcello-tbin)  

include water_mass_dedrift_config.mk


# File definitions

AREACELLO_FILE=${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/${FX_EXP}/${RUN}/Ofx/areacello/${GRID}/${VOLCELLO_VERSION}/areacello_Ofx_${MODEL}_${FX_EXP}_${RUN}_${GRID}.nc
VOLCELLO_FILE=${VOLCELLO_DIR}/${INSTITUTION}/${MODEL}/${FX_EXP}/${RUN}/Ofx/volcello/${GRID}/${VOLCELLO_VERSION}/volcello_Ofx_${MODEL}_${FX_EXP}_${RUN}_${GRID}.nc
BASIN_FILE=${MY_DATA_DIR}/${INSTITUTION}/${MODEL}/${FX_EXP}/${RUN}/Ofx/basin/${GRID}/${BASIN_VERSION}/basin_Ofx_${MODEL}_${FX_EXP}_${RUN}_${GRID}.nc
SALINITY_FILES_HIST := $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Omon/so/${GRID}/${HIST_VERSION}/so*.nc) 
TEMPERATURE_FILES_HIST := $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Omon/thetao/${GRID}/${HIST_VERSION}/thetao*.nc)
TOS_FILES_HIST := $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Omon/tos/${GRID}/${HIST_VERSION}/tos*.nc)
WFO_FILES_HIST := $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Omon/wfo/${GRID}/${HIST_VERSION}/wfo*.nc)
SALINITY_FILES_CNTRL := $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/piControl/${RUN}/Omon/so/${GRID}/${CNTRL_VERSION}/so*.nc) 
TEMPERATURE_FILES_CNTRL := $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/piControl/${RUN}/Omon/thetao/${GRID}/${CNTRL_VERSION}/thetao*.nc)

# wfo(year, tos, basin), "Water Flux Into Sea Water"

WFO_BINNED_DIR_HIST=${MY_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Omon/wfo/${GRID}/${HIST_VERSION}
WFO_BINNED_FILE_HIST=${WFO_BINNED_DIR_HIST}/wfo-tos-binned_Omon_${MODEL}_historical_${RUN}_${GRID}_${HIST_TIME}.nc
${WFO_BINNED_FILE_HIST} : ${AREACELLO_FILE} ${BASIN_FILE}
	mkdir -p ${WFO_BINNED_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_surface_flux_histogram.py ${WFO_FILES_HIST} water_flux_into_sea_water $< $(word 2,$^) $@ --bin_files ${TOS_FILES_HIST} --bin_var sea_surface_temperature


# surface water mass variables

SURFACE_WATER_MASS_DIR_HIST=${MY_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Omon/surface-water-mass/${GRID}/${HIST_VERSION}
SURFACE_WATER_MASS_FILE_HIST=${SURFACE_WATER_MASS_DIR_HIST}/surface-water-mass_Omon_${MODEL}_historical_${RUN}_${GRID}_${HIST_TIME}.nc
${SURFACE_WATER_MASS_FILE_HIST} : ${AREACELLO_FILE} ${BASIN_FILE}
	mkdir -p ${SURFACE_WATER_MASS_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_water_mass_components.py $< $(word 2,$^) $@ --salinity_files ${SALINITY_FILES_HIST} --temperature_files ${TEMPERATURE_FILES_HIST}


# water mass files

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


## drift removal for volcello_tbin(year, thetao, basin)

VOL_DRIFT_COEFFICIENT_FILE=${WATER_MASS_DIR_CNTRL}/volcello-tbin-coefficients_Omon_${MODEL}_piControl_${RUN}_${GRID}_${CNTRL_TIME}.nc
${VOL_DRIFT_COEFFICIENT_FILE} : ${WATER_MASS_FILE_CNTRL}
	${PYTHON}  ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< Ocean_Grid-Cell_Volume_binned_by_temperature $@

VOL_DEDRIFTED_FILE=${WATER_MASS_DIR_HIST}/volcello-tbin-dedrifted_Omon_${MODEL}_historical_${RUN}_${GRID}_${HIST_TIME}.nc
${VOL_DEDRIFTED_FILE} : ${WATER_MASS_FILE_HIST} ${VOL_DRIFT_COEFFICIENT_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift_year_axis.py $< Ocean_Grid-Cell_Volume_binned_by_temperature $(word 2,$^) $@ ${BRANCH_YEAR}

## drift removal for so_volcello_tbin(year, thetao, basin)

SOVOL_DRIFT_COEFFICIENT_FILE=${WATER_MASS_DIR_CNTRL}/so-volcello-tbin-coefficients_Omon_${MODEL}_piControl_${RUN}_${GRID}_${CNTRL_TIME}.nc
${SOVOL_DRIFT_COEFFICIENT_FILE} : ${WATER_MASS_FILE_CNTRL}
	${PYTHON}  ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< Sea_Water_Salinity_times_Ocean_Grid-Cell_Volume_binned_by_temperature $@

SOVOL_DEDRIFTED_FILE=${WATER_MASS_DIR_HIST}/so-volcello-tbin-dedrifted_Omon_${MODEL}_historical_${RUN}_${GRID}_${HIST_TIME}.nc
${SOVOL_DEDRIFTED_FILE} : ${WATER_MASS_FILE_HIST} ${SOVOL_DRIFT_COEFFICIENT_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift_year_axis.py $< Sea_Water_Salinity_times_Ocean_Grid-Cell_Volume_binned_by_temperature $(word 2,$^) $@ ${BRANCH_YEAR}

## plots

VOL_PLOT_FILE=/g/data/r87/dbi599/temp/volcello-tbin-dedrifted_Omon_${MODEL}_piControl_${RUN}_${GRID}_${CNTRL_TIME}_bin6.png
${VOL_PLOT_FILE} : ${VOL_DRIFT_COEFFICIENT_FILE} ${WATER_MASS_FILE_CNTRL} ${WATER_MASS_FILE_HIST} ${VOL_DEDRIFTED_FILE}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py Ocean_Grid-Cell_Volume_binned_by_temperature $< ${VOL_PLOT_FILE} --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 6 -1 ${BRANCH_YEAR}

SOVOL_PLOT_FILE=/g/data/r87/dbi599/temp/so-volcello-tbin-dedrifted_Omon_${MODEL}_piControl_${RUN}_${GRID}_${CNTRL_TIME}_bin6.png
${SOVOL_PLOT_FILE} : ${SOVOL_DRIFT_COEFFICIENT_FILE} ${WATER_MASS_FILE_CNTRL} ${WATER_MASS_FILE_HIST} ${SOVOL_DEDRIFTED_FILE}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py Sea_Water_Salinity_times_Ocean_Grid-Cell_Volume_binned_by_temperature $< ${SOVOL_PLOT_FILE} --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 6 -1 ${BRANCH_YEAR}



# targets

wfo : ${WFO_BINNED_FILE_HIST}
	echo "wfo only"
	
volcello-tbin : ${VOL_PLOT_FILE}
	echo "volcello_tbin"

so-volcello-tbin : ${SOVOL_PLOT_FILE}
	echo "so_volcello_tbin"

surface : ${SURFACE_WATER_MASS_FILE_HIST}
	echo "surface-water-mass"

all-but-volcello-tbin : wfo surface so-volcello-tbin
	echo "all but volcello-tbin"

all : wfo volcello-tbin so-volcello-tbin surface
