# ohc_spatial.mk
#
# Description: Workflow for producing ocean heat content spatial fields
#
# To execute:
#   1. copy name of target file from ohc_spatial.mk 
#   2. paste it into ohc_spatial_config.mk as the target THETAO  
#   3. $ make -n -B -f ohc_spatial.mk  (-n is a dry run) (-B is a force make)


# Define marcos

include ohc_spatial_config.mk
all : ${TARGET}

# Filenames

CONTROL_FILES=$(wildcard ${ORIG_CONTROL_DIR}/${MODEL}/piControl/mon/ocean/${CONTROL_RUN}/thetao/latest/thetao_Omon_${MODEL}_piControl_${CONTROL_RUN}_*.nc)
CONTROL_DIR=${MY_CMIP5_DIR}/${MODEL}/piControl/yr/ocean/${CONTROL_RUN}/thetao/latest
DRIFT_COEFFICIENTS=${CONTROL_DIR}/thetao-coefficients_Oyr_${MODEL}_piControl_${CONTROL_RUN}_all.nc

THETAO_FILES=$(wildcard ${ORIG_THETAO_DIR}/${MODEL}/${EXPERIMENT}/mon/ocean/${RUN}/thetao/latest/thetao_Omon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)

DEDRIFTED_THETAO_DIR=${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/ocean/${RUN}/thetao/latest/dedrifted
DEDRIFTED_THETAO_FILES=$(wildcard ${DEDRIFTED_THETAO_DIR}/thetao_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)

OHC_DIR=${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/ocean/${RUN}/ohc/latest
DEDRIFTED_OHC_DIR=${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/ocean/${RUN}/ohc/latest/dedrifted

OHC_FILES=$(wildcard ${OHC_DIR}/ohc_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
DEDRIFTED_OHC_FILES=$(wildcard ${DEDRIFTED_OHC_DIR}/ohc_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)

OCEAN_AREA_FILE=${ORIG_AREAO_DIR}/${MODEL}/${FX_EXPERIMENT}/fx/ocean/${FX_RUN}/areacello/latest/areacello_fx_${MODEL}_${FX_EXPERIMENT}_${FX_RUN}.nc
OCEAN_VOLUME_FILE=${ORIG_VOL_DIR}/${MODEL}/${FX_EXPERIMENT}/fx/ocean/${FX_RUN}/volcello/latest/volcello_fx_${MODEL}_${FX_EXPERIMENT}_${FX_RUN}.nc

OHC_TREND_FILE=${OHC_DIR}/ohc-trend_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_1850-2005.nc
OHC_TREND_WRT_TROPICS_FILE=${OHC_DIR}/ohc-trend-wrt-tropics_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_1850-2005.nc
DEDRIFTED_OHC_TREND_FILE=${DEDRIFTED_OHC_DIR}/ohc-trend_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_1850-2005.nc
DEDRIFTED_OHC_TREND_WRT_TROPICS_FILE=${DEDRIFTED_OHC_DIR}/ohc-trend-wrt-tropics_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_1850-2005.nc

# De-drift

${DRIFT_COEFFICIENTS} :
	mkdir -p ${CONTROL_DIR} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py ${CONTROL_FILES} $@ --var sea_water_potential_temperature --annual

${DEDRIFTED_THETAO_DIR} : ${DRIFT_COEFFICIENTS}
	mkdir -p $@
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py ${THETAO_FILES} sea_water_potential_temperature $< $@/ --annual 
        #--no_parent_check

# OHC

${OHC_DIR} :
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_ohc.py ${THETAO_FILES} sea_water_potential_temperature --volume_file ${OCEAN_VOLUME_FILE} --annual
        #--area_file ${OCEAN_AREA_FILE} --volume_file ${OCEAN_VOLUME_FILE}

${DEDRIFTED_OHC_DIR} :
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_ohc.py ${DEDRIFTED_THETAO_FILES} sea_water_potential_temperature --area_file ${OCEAN_AREA_FILE}
        #--area_file ${OCEAN_AREA_FILE}

# Trends

${OHC_TREND_FILE} : 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_trend.py ${OHC_FILES} ocean_heat_content $@ --time_bounds 1850-01-01 2005-12-31 --regrid

${OHC_TREND_WRT_TROPICS_FILE} : 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_trend.py ${OHC_FILES} ocean_heat_content $@ --time_bounds 1850-01-01 2005-12-31 --subtract_tropics --regrid

${DEDRIFTED_OHC_TREND_FILE} : 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_trend.py ${DEDRIFTED_OHC_FILES} ocean_heat_content $@ --time_bounds 1850-01-01 2005-12-31 --regrid

${DEDRIFTED_OHC_TREND_WRT_TROPICS_FILE} : 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_trend.py ${DEDRIFTED_OHC_FILES} ocean_heat_content $@ --time_bounds 1850-01-01 2005-12-31 --subtract_tropics --regrid

# Plots

## no-dedrifting, regular trend


## dedrifted, regular trend


## no-dedrifting, trend wrt tropics

#python ../visualisation/plot_map.py 3 4 --infile /g/data/r87/dbi599/DRSv2/CMIP5/CanESM2/historicalMisc/yr/ocean/r1i1p4/ohc/latest/ohc-trend-wrt-tropics_Oyr_CanESM2_historicalMisc_r1i1p4_1850-2005.nc ocean_heat_content none none none colour0 1 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/ohc/latest/ohc-trend-wrt-tropics_Oyr_CCSM4_historicalMisc_r1i1p10_1850-2005.nc ocean_heat_content none none none colour0 2 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/ocean/r1i1p4/ohc/latest/ohc-trend-wrt-tropics_Oyr_CSIRO-Mk3-6-0_historicalMisc_r1i1p4_1850-2005.nc ocean_heat_content none none none colour0 3 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/FGOALS-g2/historicalMisc/yr/ocean/r2i1p1/ohc/latest/ohc-trend-wrt-tropics_Oyr_FGOALS-g2_historicalMisc_r2i1p1_1850-2005.nc ocean_heat_content none none none colour0 4 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/GFDL-CM3/historicalMisc/yr/ocean/r1i1p1/ohc/latest/ohc-trend-wrt-tropics_Oyr_GFDL-CM3_historicalMisc_r1i1p1_1850-2005.nc ocean_heat_content none none none colour0 5 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/GFDL-ESM2M/historicalMisc/yr/ocean/r1i1p5/ohc/latest/ohc-trend-wrt-tropics_Oyr_GFDL-ESM2M_historicalMisc_r1i1p5_1850-2005.nc ocean_heat_content none none none colour0 6 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-H/historicalMisc/yr/ocean/r1i1p107/ohc/latest/ohc-trend-wrt-tropics_Oyr_GISS-E2-H_historicalMisc_r1i1p107_1850-2005.nc ocean_heat_content none none none colour0 7 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-H/historicalMisc/yr/ocean/r1i1p310/ohc/latest/ohc-trend-wrt-tropics_Oyr_GISS-E2-H_historicalMisc_r1i1p310_1850-2005.nc ocean_heat_content none none none colour0 8 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalMisc/yr/ocean/r1i1p107/ohc/latest/ohc-trend-wrt-tropics_Oyr_GISS-E2-R_historicalMisc_r1i1p107_1850-2005.nc ocean_heat_content none none none colour0 9 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalMisc/yr/ocean/r1i1p310/ohc/latest/ohc-trend-wrt-tropics_Oyr_GISS-E2-R_historicalMisc_r1i1p310_1850-2005.nc ocean_heat_content none none none colour0 10 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/IPSL-CM5A-LR/historicalMisc/yr/ocean/r1i1p3/ohc/latest/ohc-trend-wrt-tropics_Oyr_IPSL-CM5A-LR_historicalMisc_r1i1p3_1850-2005.nc ocean_heat_content none none none colour0 11 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/ohc/latest/ohc-trend-wrt-tropics_Oyr_NorESM1-M_historicalMisc_r1i1p1_1850-2005.nc ocean_heat_content none none none colour0 12 PlateCarree --palette RdBu_r --colourbar_ticks -12 -10 -8 -6 -4 -2 0 2 4 6 8 10 12 --colourbar_ticks -0.6 -0.5 -0.4 -0.3 -0.2 -0.1 0.0 0.1 0.2 0.3 0.4 0.5 0.6 --colourbar_ticks -3.0 -2.5 -2.0 -1.5 -1.0 -0.5 0.0 0.5 1.0 1.5 2.0 2.5 3.0 --colourbar_ticks -1.2 -1.0 -0.8 -0.6 -0.4 -0.2 0.0 0.2 0.4 0.6 0.8 1.0 1.2 --colourbar_ticks -3.0 -2.5 -2.0 -1.5 -1 -0.5 0.0 0.5 1.0 1.5 2.0 2.5 3.0 --colourbar_ticks  -1.2 -1.0 -0.8 -0.6 -0.4 -0.2 0.0 0.2 0.4 0.6 0.8 1.0 1.2 --colourbar_ticks -4.5 -3.75 -3 -2.25 -1.5 -0.75 0.0 0.75 1.5 2.25 3 3.75 4.5 --colourbar_ticks -4.5 -3.75 -3 -2.25 -1.5 -0.75 0.0 0.75 1.5 2.25 3 3.75 4.5 --colourbar_ticks -1.8 -1.5 -1.2 -0.9 -0.6 -0.3 0.0 0.3 0.6 0.9 1.2 1.5 1.8 --colourbar_ticks -3.0 -2.5 -2.0 -1.5 -1 -0.5 0.0 0.5 1.0 1.5 2.0 2.5 3.0 --colourbar_ticks -24 -20 -16 -12 -8 -4 0 4 8 12 16 20 24 --colourbar_ticks -1.8 -1.5 -1.2 -0.9 -0.6 -0.3 0.0 0.3 0.6 0.9 1.2 1.5 1.8 --extend both --scale_factor 17 colour0 --subplot_headings CanESM2 CCSM4 CSIRO-Mk3-6-0 FGOALS-g2 GFDL-CM3 GFDL-ESM2M GISS-E2-H_p107 GISS-E2-H_p310 GISS-E2-R_p107 GISS-E2-R_p310 IPSL-CM5A-LR NorESM1-M --title "Trend_in_OHC_wrt_tropics_(historicalAA,_1850-2005)" --ofile /g/data/r87/dbi599/figures/ohc-trend-wrt-tropics_Oyr_ensemble_historicalMisc_r1_1850-2005.png --figure_size 32 24 --colourbar_type individual --exclude_blanks

#height = 8 * nrows
#width = 8 * ncols



## dedrifting, trend wrt tropics

#python ../visualisation/plot_map.py 3 4 --infile /g/data/r87/dbi599/DRSv2/CMIP5/CanESM2/historicalMisc/yr/ocean/r1i1p4/ohc/latest/dedrifted/ohc-trend-wrt-tropics_Oyr_CanESM2_historicalMisc_r1i1p4_1850-2005.nc ocean_heat_content none none none colour0 1 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/ohc/latest/dedrifted/ohc-trend-wrt-tropics_Oyr_CCSM4_historicalMisc_r1i1p10_1850-2005.nc ocean_heat_content none none none colour0 2 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/ocean/r1i1p4/ohc/latest/dedrifted/ohc-trend-wrt-tropics_Oyr_CSIRO-Mk3-6-0_historicalMisc_r1i1p4_1850-2005.nc ocean_heat_content none none none colour0 3 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/FGOALS-g2/historicalMisc/yr/ocean/r2i1p1/ohc/latest/dedrifted/ohc-trend-wrt-tropics_Oyr_FGOALS-g2_historicalMisc_r2i1p1_1850-2005.nc ocean_heat_content none none none colour0 4 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/GFDL-CM3/historicalMisc/yr/ocean/r1i1p1/ohc/latest/dedrifted/ohc-trend-wrt-tropics_Oyr_GFDL-CM3_historicalMisc_r1i1p1_1850-2005.nc ocean_heat_content none none none colour0 5 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/GFDL-ESM2M/historicalMisc/yr/ocean/r1i1p5/ohc/latest/dedrifted/ohc-trend-wrt-tropics_Oyr_GFDL-ESM2M_historicalMisc_r1i1p5_1850-2005.nc ocean_heat_content none none none colour0 6 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-H/historicalMisc/yr/ocean/r1i1p107/ohc/latest/dedrifted/ohc-trend-wrt-tropics_Oyr_GISS-E2-H_historicalMisc_r1i1p107_1850-2005.nc ocean_heat_content none none none colour0 7 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-H/historicalMisc/yr/ocean/r1i1p310/ohc/latest/dedrifted/ohc-trend-wrt-tropics_Oyr_GISS-E2-H_historicalMisc_r1i1p310_1850-2005.nc ocean_heat_content none none none colour0 8 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalMisc/yr/ocean/r1i1p107/ohc/latest/dedrifted/ohc-trend-wrt-tropics_Oyr_GISS-E2-R_historicalMisc_r1i1p107_1850-2005.nc ocean_heat_content none none none colour0 9 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/GISS-E2-R/historicalMisc/yr/ocean/r1i1p310/ohc/latest/dedrifted/ohc-trend-wrt-tropics_Oyr_GISS-E2-R_historicalMisc_r1i1p310_1850-2005.nc ocean_heat_content none none none colour0 10 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/IPSL-CM5A-LR/historicalMisc/yr/ocean/r1i1p3/ohc/latest/dedrifted/ohc-trend-wrt-tropics_Oyr_IPSL-CM5A-LR_historicalMisc_r1i1p3_1850-2005.nc ocean_heat_content none none none colour0 11 PlateCarree --infile /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/ohc/latest/dedrifted/ohc-trend-wrt-tropics_Oyr_NorESM1-M_historicalMisc_r1i1p1_1850-2005.nc ocean_heat_content none none none colour0 12 PlateCarree --palette RdBu_r --colourbar_ticks -12 -10 -8 -6 -4 -2 0 2 4 6 8 10 12 --colourbar_ticks -0.6 -0.5 -0.4 -0.3 -0.2 -0.1 0.0 0.1 0.2 0.3 0.4 0.5 0.6 --colourbar_ticks -3.0 -2.5 -2.0 -1.5 -1.0 -0.5 0.0 0.5 1.0 1.5 2.0 2.5 3.0 --colourbar_ticks -1.2 -1.0 -0.8 -0.6 -0.4 -0.2 0.0 0.2 0.4 0.6 0.8 1.0 1.2 --colourbar_ticks -3.0 -2.5 -2.0 -1.5 -1 -0.5 0.0 0.5 1.0 1.5 2.0 2.5 3.0 --colourbar_ticks  -1.2 -1.0 -0.8 -0.6 -0.4 -0.2 0.0 0.2 0.4 0.6 0.8 1.0 1.2 --colourbar_ticks -4.5 -3.75 -3 -2.25 -1.5 -0.75 0.0 0.75 1.5 2.25 3 3.75 4.5 --colourbar_ticks -4.5 -3.75 -3 -2.25 -1.5 -0.75 0.0 0.75 1.5 2.25 3 3.75 4.5 --colourbar_ticks -1.8 -1.5 -1.2 -0.9 -0.6 -0.3 0.0 0.3 0.6 0.9 1.2 1.5 1.8 --colourbar_ticks -3.0 -2.5 -2.0 -1.5 -1 -0.5 0.0 0.5 1.0 1.5 2.0 2.5 3.0 --colourbar_ticks -24 -20 -16 -12 -8 -4 0 4 8 12 16 20 24 --colourbar_ticks -1.8 -1.5 -1.2 -0.9 -0.6 -0.3 0.0 0.3 0.6 0.9 1.2 1.5 1.8 --extend both --scale_factor 17 colour0 --subplot_headings CanESM2 CCSM4 CSIRO-Mk3-6-0 FGOALS-g2 GFDL-CM3 GFDL-ESM2M GISS-E2-H_p107 GISS-E2-H_p310 GISS-E2-R_p107 GISS-E2-R_p310 IPSL-CM5A-LR NorESM1-M --title "Trend_in_OHC_wrt_tropics_(historicalAA,_1850-2005)" --ofile /g/data/r87/dbi599/figures/ohc-dedrifted-trend-wrt-tropics_Oyr_ensemble_historicalMisc_r1_1850-2005.png --figure_size 32 24 --colourbar_type individual --exclude_blanks
