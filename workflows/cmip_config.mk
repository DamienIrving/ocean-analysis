# CMIP configuration

## Variables always required at the command line:
## - MODEL (choices: see below)
## - EXPERIMENT (choices: historical, hist-GHG, hist-aer)
##
## Variables required for certain targets:
## - SF_VAR (choices: wfo, hfds)
## - FLUX_VAR (choices: rsds rsus rlds rlus hfss)
##
##  MODELS: ACCESS-CM2, ACCESS-ESM1-5, CNRM-CM6-1
##

GRID=gn
# gn gr

# DIRECTORIES

PYTHON=/g/data/r87/dbi599/miniconda3/envs/ocean3/bin/python
DATA_SCRIPT_DIR=/home/599/dbi599/ocean-analysis/data_processing
VIZ_SCRIPT_DIR=/home/599/dbi599/ocean-analysis/visualisation
MY_DATA_DIR=/g/data/r87/dbi599
SHARED_DATA_DIR=/g/data/e14/dbi599
AUS_CMIP6_DATA_DIR=/g/data/fs38/publications
REPLICA_CMIP6_DATA_DIR=/g/data/oi10/replicas
REPLICA_CMIP6b_DATA_DIR=/g/data1b/oi10/replicas
REPLICA_CMIP5_DATA_DIR=/g/data/al33/replicas

# VARIABLES

LONG_NAME_hfds=Downward_Heat_Flux_at_Sea_Water_Surface
LONG_NAME_wfo=Water_Flux_into_Sea_Water
STD_NAME_hfds=surface_downward_heat_flux_in_sea_water
STD_NAME_hfss=surface_upward_sensible_heat_flux
STD_NAME_rlds=surface_downwelling_longwave_flux_in_air
STD_NAME_rlus=surface_upwelling_longwave_flux_in_air
STD_NAME_rsds=surface_downwelling_shortwave_flux_in_air
STD_NAME_rsus=surface_upwelling_shortwave_flux_in_air
STD_NAME_so=sea_water_salinity
STD_NAME_sos=sea_surface_salinity
STD_NAME_thetao=sea_water_potential_temperature
STD_NAME_tos=sea_surface_temperature
STD_NAME_wfo=water_flux_into_sea_water

# PROJECTS

MIP_historical=CMIP
MIP_hist-GHG=DAMIP
MIP_hist-aer=DAMIP

# MODEL DETAILS

ACCESS-CM2_PROJECT=CMIP6
ACCESS-CM2_INSTITUTION=CSIRO-ARCCSS
ACCESS-CM2_SURFACE_SBIN_VAR=sos
ACCESS-CM2_SURFACE_TBIN_VAR=tos
ACCESS-CM2_FX_EXP=historical
ACCESS-CM2_EXP_RUN=r1i1p1f1
ACCESS-CM2_CNTRL_RUN=r1i1p1f1
ACCESS-CM2_FX_RUN=r1i1p1f1
ACCESS-CM2_HIST_RUN=r1i1p1f1
ACCESS-CM2_EXP_VERSION=v20191108
ACCESS-CM2_CNTRL_VERSION=v20191112
ACCESS-CM2_OFX_VERSION=v20191108
ACCESS-CM2_HIST_VERSION=v20191108
ACCESS-CM2_ATMOS_EXP_VERSION=v20191108
ACCESS-CM2_ATMOS_CNTRL_VERSION=v20191112
ACCESS-CM2_EXP_TIME=185001-201412
ACCESS-CM2_CNTRL_TIME=095001-144912
ACCESS-CM2_CMIP6_DATA_DIR=${AUS_CMIP6_DATA_DIR}
ACCESS-CM2_VOLCELLO_DIR=${AUS_CMIP6_DATA_DIR}
ACCESS-CM2_AREACELLO_DIR=${AUS_CMIP6_DATA_DIR}

ACCESS-ESM1-5_PROJECT=CMIP6
ACCESS-ESM1-5_INSTITUTION=CSIRO
ACCESS-ESM1-5_SURFACE_SBIN_VAR=sos
ACCESS-ESM1-5_SURFACE_TBIN_VAR=tos
ACCESS-ESM1-5_FX_EXP=historical
ACCESS-ESM1-5_EXP_RUN=r1i1p1f1
ACCESS-ESM1-5_CNTRL_RUN=r1i1p1f1
ACCESS-ESM1-5_FX_RUN=r1i1p1f1
ACCESS-ESM1-5_HIST_RUN=r1i1p1f1
ACCESS-ESM1-5_EXP_VERSION_historical_r1i1p1f1=v20191115
ACCESS-ESM1-5_EXP_VERSION_historical_r2i1p1f1=v20191128
ACCESS-ESM1-5_EXP_VERSION_historical_r3i1p1f1=v20191203
ACCESS-ESM1-5_EXP_VERSION_hist-aer_r1i1p1f1=v20200615
ACCESS-ESM1-5_EXP_VERSION_hist-GHG_r1i1p1f1=v20200615
ACCESS-ESM1-5_CNTRL_VERSION=v20191214
ACCESS-ESM1-5_FX_VERSION=v20191115
ACCESS-ESM1-5_OFX_VERSION=v20191115
ACCESS-ESM1-5_HIST_VERSION=v20191115
ACCESS-ESM1-5_ATMOS_EXP_VERSION=v20191115
ACCESS-ESM1-5_ATMOS_CNTRL_VERSION=v20191214
ACCESS-ESM1-5_EXP_TIME_hist-aer=185001-202012
ACCESS-ESM1-5_EXP_TIME_hist-GHG=185001-202012
ACCESS-ESM1-5_EXP_TIME_historical=185001-201412
ACCESS-ESM1-5_CNTRL_TIME=010101-100012
ACCESS-ESM1-5_CMIP6_DATA_DIR=${AUS_CMIP6_DATA_DIR}
ACCESS-ESM1-5_VOLCELLO_DIR=${AUS_CMIP6_DATA_DIR}
ACCESS-ESM1-5_AREACELLO_DIR=${AUS_CMIP6_DATA_DIR}
ACCESS-ESM1-5_AREACELLA_DIR=${AUS_CMIP6_DATA_DIR}
ACCESS-ESM1-5_SFTLF_DIR=${AUS_CMIP6_DATA_DIR}

CanESM5_PROJECT=CMIP6
CanESM5_INSTITUTION=CCCma
CanESM5_SURFACE_SBIN_VAR=so
CanESM5_SURFACE_TBIN_VAR=thetao
CanESM5_FX_EXP=historical
CanESM5_EXP_RUN_historical=r1i1p1f1
CanESM5_EXP_RUN_hist-GHG=r1i1p1f1
CanESM5_EXP_RUN_hist-aer=r1i1p1f1
CanESM5_CNTRL_RUN=r1i1p1f1
CanESM5_FX_RUN=r1i1p1f1
CanESM5_HIST_RUN=r1i1p1f1
CanESM5_EXP_VERSION=v20190429
CanESM5_CNTRL_VERSION=v20190429
CanESM5_FX_VERSION=v20190429
CanESM5_OFX_VERSION=v20190429
CanESM5_HIST_VERSION=v20190429
CanESM5_ATMOS_EXP_VERSION=v20190429
CanESM5_ATMOS_CNTRL_VERSION=v20190429
CanESM5_EXP_TIME_historical=185001-201412
CanESM5_EXP_TIME_hist-GHG=185001-202012
CanESM5_EXP_TIME_hist-aer=185001-202012
CanESM5_CNTRL_TIME=520101-620012
CanESM5_CMIP6_DATA_DIR=${REPLICA_CMIP6_DATA_DIR}
CanESM5_VOLCELLO_DIR=${MY_DATA_DIR}
CanESM5_AREACELLA_DIR=${REPLICA_CMIP6_DATA_DIR}
CanESM5_AREACELLO_DIR=${REPLICA_CMIP6_DATA_DIR}
CanESM5_SFTLF_DIR=${REPLICA_CMIP6_DATA_DIR}

CNRM-CM6-1_PROJECT=CMIP6
CNRM-CM6-1_INSTITUTION=CNRM-CERFACS
CNRM-CM6-1_SURFACE_SBIN_VAR=sos
CNRM-CM6-1_SURFACE_TBIN_VAR=tos
CNRM-CM6-1_FX_EXP=historical
CNRM-CM6-1_EXP_RUN=r1i1p1f2
CNRM-CM6-1_CNTRL_RUN=r1i1p1f2
CNRM-CM6-1_FX_RUN=r1i1p1f2
CNRM-CM6-1_HIST_RUN=r1i1p1f2
CNRM-CM6-1_EXP_VERSION=v20180917
CNRM-CM6-1_CNTRL_VERSION=v20180814
CNRM-CM6-1_OFX_VERSION=v20180917
CNRM-CM6-1_HIST_VERSION=v20180917
CNRM-CM6-1_ATMOS_EXP_VERSION=v20190308
CNRM-CM6-1_ATMOS_CNTRL_VERSION=v20180814
CNRM-CM6-1_EXP_TIME=185001-201412
CNRM-CM6-1_CNTRL_TIME=185001-234912
CNRM-CM6-1_CMIP6_DATA_DIR=${REPLICA_CMIP6_DATA_DIR}
CNRM-CM6-1_VOLCELLO_DIR=${MY_DATA_DIR}
CNRM-CM6-1_AREACELLO_DIR=${REPLICA_CMIP6_DATA_DIR}
CNRM-CM6-1_AREACELLA_DIR=${REPLICA_CMIP6_DATA_DIR}
#CHUNK_ANNUAL=--chunk

CNRM-ESM2-1_PROJECT=CMIP6
CNRM-ESM2-1_INSTITUTION=CNRM-CERFACS
CNRM-ESM2-1_SURFACE_SBIN_VAR=sos
CNRM-ESM2-1_SURFACE_TBIN_VAR=tos
CNRM-ESM2-1_FX_EXP=historical
CNRM-ESM2-1_EXP_RUN=r1i1p1f2
CNRM-ESM2-1_CNTRL_RUN=r1i1p1f2
CNRM-ESM2-1_FX_RUN=r1i1p1f2
CNRM-ESM2-1_HIST_RUN=r1i1p1f2
CNRM-ESM2-1_EXP_VERSION=v20181206
CNRM-ESM2-1_CNTRL_VERSION=v20181115
CNRM-ESM2-1_OFX_VERSION=v20181206
CNRM-ESM2-1_HIST_VERSION=v20181206
CNRM-ESM2-1_EXP_TIME=185001-201412
CNRM-ESM2-1_CNTRL_TIME=185001-234912
CNRM-ESM2-1_CMIP6_DATA_DIR=${REPLICA_CMIP6_DATA_DIR}
CNRM-ESM2-1_VOLCELLO_DIR=${MY_DATA_DIR}
CNRM-ESM2-1_AREACELLO_DIR=${REPLICA_CMIP6_DATA_DIR}
CNRM-ESM2-1_AREACELLA_DIR=${REPLICA_CMIP6_DATA_DIR}

EC-Earth3_PROJECT=CMIP6
EC-Earth3_INSTITUTION=EC-Earth-Consortium
EC-Earth3_SURFACE_SBIN_VAR=sos
EC-Earth3_SURFACE_TBIN_VAR=tos
EC-Earth3_FX_EXP=historical
EC-Earth3_EXP_RUN=r1i1p1f1
EC-Earth3_CNTRL_RUN=r1i1p1f1
EC-Earth3_FX_RUN=r1i1p1f1
EC-Earth3_HIST_RUN=r1i1p1f1
EC-Earth3_EXP_VERSION=v20200310
EC-Earth3_CNTRL_VERSION=v20200312
EC-Earth3_OFX_VERSION=v20200310
EC-Earth3_HIST_VERSION=v20200310
EC-Earth3_EXP_TIME=185001-201412
EC-Earth3_CNTRL_TIME=225901-275912
EC-Earth3_CMIP6_DATA_DIR=${REPLICA_CMIP6_DATA_DIR}
EC-Earth3_VOLCELLO_DIR=${MY_DATA_DIR}
EC-Earth3_AREACELLO_DIR=${REPLICA_CMIP6_DATA_DIR}
EC-Earth3_BRANCH_TIME=--branch_time 149749
EC-Earth3_BRANCH_YEAR=--branch_year 2260

EC-Earth3-Veg_PROJECT=CMIP6
EC-Earth3-Veg_INSTITUTION=EC-Earth-Consortium
EC-Earth3-Veg_SURFACE_SBIN_VAR=sos
EC-Earth3-Veg_SURFACE_TBIN_VAR=tos
EC-Earth3-Veg_FX_EXP=historical
EC-Earth3-Veg_EXP_RUN=r1i1p1f1
EC-Earth3-Veg_CNTRL_RUN=r1i1p1f1
EC-Earth3-Veg_FX_RUN=r1i1p1f1
EC-Earth3-Veg_HIST_RUN=r1i1p1f1
EC-Earth3-Veg_EXP_VERSION=v20200225
EC-Earth3-Veg_CNTRL_VERSION=v20200226
#v20190619
EC-Earth3-Veg_OFX_VERSION_VOLCELLO=v20190605
EC-Earth3-Veg_OFX_VERSION_AREACELLO=v20200919
EC-Earth3-Veg_HIST_VERSION=v20200225
EC-Earth3-Veg_EXP_TIME=185001-201412
EC-Earth3-Veg_CNTRL_TIME=185001-234912
EC-Earth3-Veg_CMIP6_DATA_DIR=${REPLICA_CMIP6_DATA_DIR}
EC-Earth3-Veg_VOLCELLO_DIR=${MY_DATA_DIR}
EC-Earth3-Veg_AREACELLO_DIR=${REPLICA_CMIP6_DATA_DIR}
EC-Earth3-Veg_BRANCH_YEAR=--branch_year 1930
EC-Earth3-Veg_BRANCH_TIME=--branch_time 29244

FGOALS-f3-L_PROJECT=CMIP6
FGOALS-f3-L_INSTITUTION=CAS
FGOALS-f3-L_SURFACE_SBIN_VAR=sos
FGOALS-f3-L_SURFACE_TBIN_VAR=tos
FGOALS-f3-L_FX_EXP=historical
FGOALS-f3-L_EXP_RUN=r1i1p1f1
FGOALS-f3-L_CNTRL_RUN=r1i1p1f1
FGOALS-f3-L_FX_RUN=r1i1p1f1
FGOALS-f3-L_HIST_RUN=r1i1p1f1
FGOALS-f3-L_EXP_VERSION=v20191007
FGOALS-f3-L_CNTRL_VERSION=v20191028
FGOALS-f3-L_OFX_VERSION=v20190918
FGOALS-f3-L_HIST_VERSION=v20191007
FGOALS-f3-L_ATMOS_EXP_VERSION=v20200411
FGOALS-f3-L_ATMOS_CNTRL_VERSION=v20191029
FGOALS-f3-L_EXP_TIME_historical=185001-201412
FGOALS-f3-L_EXP_TIME_hist-GHG=185001-202012
FGOALS-f3-L_EXP_TIME_hist-aer=185001-202012
FGOALS-f3-L_CNTRL_TIME=060001-109912
FGOALS-f3-L_CMIP6_DATA_DIR=${REPLICA_CMIP6_DATA_DIR}
FGOALS-f3-L_VOLCELLO_DIR=${MY_DATA_DIR}
FGOALS-f3-L_AREACELLO_DIR=${MY_DATA_DIR}

IPSL-CM6A-LR_PROJECT=CMIP6
IPSL-CM6A-LR_INSTITUTION=IPSL
IPSL-CM6A-LR_SURFACE_SBIN_VAR=sos
IPSL-CM6A-LR_SURFACE_TBIN_VAR=tos
IPSL-CM6A-LR_FX_EXP=historical
IPSL-CM6A-LR_EXP_RUN=r1i1p1f1
IPSL-CM6A-LR_CNTRL_RUN=r1i1p1f1
IPSL-CM6A-LR_FX_RUN=r1i1p1f1
IPSL-CM6A-LR_HIST_RUN=r1i1p1f1
IPSL-CM6A-LR_EXP_VERSION_historical_r1i1p1f1=v20180803
IPSL-CM6A-LR_EXP_VERSION_hist-GHG_r1i1p1f1=v20180914
IPSL-CM6A-LR_EXP_VERSION_hist-aer_r1i1p1f1=v20180914
IPSL-CM6A-LR_CNTRL_VERSION=v20200326
IPSL-CM6A-LR_FX_VERSION=v20180803
IPSL-CM6A-LR_OFX_VERSION=v20180803
IPSL-CM6A-LR_HIST_VERSION=v20180803
#IPSL-CM6A-LR_ATMOS_EXP_VERSION_historical=v20180803
#IPSL-CM6A-LR_ATMOS_EXP_VERSION_hist-GHG=v20180914
#IPSL-CM6A-LR_ATMOS_EXP_VERSION_hist-aer=v20180914
IPSL-CM6A-LR_ATMOS_CNTRL_VERSION=v20200326
IPSL-CM6A-LR_EXP_TIME_historical=185001-201412
IPSL-CM6A-LR_EXP_TIME_hist-GHG=185001-202012
IPSL-CM6A-LR_EXP_TIME_hist-aer=185001-202012
IPSL-CM6A-LR_CNTRL_TIME=185001-384912
IPSL-CM6A-LR_CMIP6_DATA_DIR=${REPLICA_CMIP6_DATA_DIR}
IPSL-CM6A-LR_VOLCELLO_DIR=${MY_DATA_DIR}
IPSL-CM6A-LR_AREACELLA_DIR=${REPLICA_CMIP6_DATA_DIR}
IPSL-CM6A-LR_AREACELLO_DIR=${REPLICA_CMIP6_DATA_DIR}
IPSL-CM6A-LR_SFTLF_DIR=${REPLICA_CMIP6_DATA_DIR}
#CHUNK_ANNUAL=--chunk

MIROC-ES2L_PROJECT=CMIP6
MIROC-ES2L_INSTITUTION=MIROC
MIROC-ES2L_SURFACE_SBIN_VAR=sos
MIROC-ES2L_SURFACE_TBIN_VAR=tos
MIROC-ES2L_FX_EXP=historical
MIROC-ES2L_EXP_RUN=r1i1p1f2
MIROC-ES2L_CNTRL_RUN=r1i1p1f2
MIROC-ES2L_FX_RUN=r1i1p1f2
MIROC-ES2L_HIST_RUN=r1i1p1f2
MIROC-ES2L_EXP_VERSION=v20190823
MIROC-ES2L_CNTRL_VERSION=v20190823
MIROC-ES2L_OFX_VERSION=v20190823
MIROC-ES2L_HIST_VERSION=v20190823
MIROC-ES2L_EXP_TIME=185001-201412
MIROC-ES2L_CNTRL_TIME=185001-234912
MIROC-ES2L_CMIP6_DATA_DIR=${REPLICA_CMIP6_DATA_DIR}
MIROC-ES2L_VOLCELLO_DIR=${MY_DATA_DIR}
MIROC-ES2L_AREACELLO_DIR=${REPLICA_CMIP6_DATA_DIR}
#CHUNK_ANNUAL=--chunk

# TOKEN PASTING
EMPTY=${HELLO}

MIP=${MIP_${EXPERIMENT}}
PROJECT=${${MODEL}_PROJECT}
INSTITUTION=${${MODEL}_INSTITUTION}
SURFACE_SBIN_VAR=${${MODEL}_SURFACE_SBIN_VAR}
SURFACE_TBIN_VAR=${${MODEL}_SURFACE_TBIN_VAR}
FX_EXP=${${MODEL}_FX_EXP}

EXP_RUN=${${MODEL}_EXP_RUN}
ifeq (${EXP_RUN}, ${EMPTY})
  EXP_RUN=${${MODEL}_EXP_RUN_${EXPERIMENT}}
endif
CNTRL_RUN=${${MODEL}_CNTRL_RUN}
FX_RUN=${${MODEL}_FX_RUN}
HIST_RUN=${${MODEL}_HIST_RUN}

EXP_VERSION=${${MODEL}_EXP_VERSION}
ifeq (${EXP_VERSION}, ${EMPTY})
  EXP_VERSION=${${MODEL}_EXP_VERSION_${EXPERIMENT}_${EXP_RUN}}
endif
CNTRL_VERSION=${${MODEL}_CNTRL_VERSION}
FX_VERSION=${${MODEL}_FX_VERSION}
OFX_VERSION_AREACELLO=${${MODEL}_OFX_VERSION}
ifeq (${OFX_VERSION_AREACELLO}, ${EMPTY})
  OFX_VERSION_AREACELLO=${${MODEL}_OFX_VERSION_AREACELLO}
endif
OFX_VERSION_VOLCELLO=${${MODEL}_OFX_VERSION}
ifeq (${OFX_VERSION_VOLCELLO}, ${EMPTY})
  OFX_VERSION_VOLCELLO=${${MODEL}_OFX_VERSION_VOLCELLO}
endif
HIST_VERSION=${${MODEL}_HIST_VERSION}
ATMOS_EXP_VERSION=${${MODEL}_ATMOS_EXP_VERSION}
ATMOS_CNTRL_VERSION=${${MODEL}_ATMOS_CNTRL_VERSION}

EXP_TIME=${${MODEL}_EXP_TIME}
ifeq (${EXP_TIME}, ${EMPTY})
  EXP_TIME=${${MODEL}_EXP_TIME_${EXPERIMENT}}
endif
CNTRL_TIME=${${MODEL}_CNTRL_TIME}

CMIP6_DATA_DIR=${${MODEL}_CMIP6_DATA_DIR}
VOLCELLO_DIR=${${MODEL}_VOLCELLO_DIR}
AREACELLO_DIR=${${MODEL}_AREACELLO_DIR}
AREACELLA_DIR=${${MODEL}_AREACELLA_DIR}
SFTLF_DIR=${${MODEL}_SFTLF_DIR}
BRANCH_TIME=${${MODEL}_BRANCH_TIME}
BRANCH_YEAR=${${MODEL}_BRANCH_YEAR}

SURFACE_SBIN_STD_NAME=${STD_NAME_${SURFACE_SBIN_VAR}}
SURFACE_TBIN_STD_NAME=${STD_NAME_${SURFACE_TBIN_VAR}}
SF_STD_NAME=${STD_NAME_${SF_VAR}}
FLUX_NAME=${STD_NAME_${FLUX_VAR}}
SF_LONG_NAME=${LONG_NAME_${SF_VAR}}

help :
	@grep '^##' ./cmip_config.mk


# CMIP6 #

# ACCESS-CM2
# - Projects: CMIP
# - Grids: gn
#
# ACCESS-ESM1-5
# - Projects: CMIP, DAMIP
# - Grids: gn
#
# CanESM5
# - Projects: CMIP, DAMIP
# - Grids: gn
#
# CNRM-CM6-1
# - Projects: CMIP, DAMIP
# - Grids: gn (ocean), gr (atmos)
#
# CNRM-ESM2-1
# - Projects: CMIP, DAMIP
# - Grids: gn
#
# EC-Earth3
# - Projects: CMIP
# - Grids: gn
#
# EC-Earth3-Veg
# - Projects: CMIP
# - Grids: gn
#
# FGOALS-f3-L
# - Projects: CMIP
# - Grids: gn
#
# IPSL-CM6A-LR
# - Projects: CMIP, DAMIP
# - Grids: gn (ocean), gr (atmos)
# - water_evaporation_flux (not evapotranspiration like other CMIP6 models)
# - control time: 185001-284912 for hfds (missing file in middle)
#
# MIROC-ES2L
# - Projects: CMIP
# - Grids: gn


# BCC-CSM2-MR

#PROJECT=CMIP6
#MIP=CMIP
## CMIP DAMIP
#INSTITUTION=BCC
#MODEL=BCC-CSM2-MR
#EXPERIMENT=historical
## hist-aer historical hist-GHG
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20181126
#FX_VERSION=v20181126
#ATMOS_HIST_VERSION=v20181126
## v20190507 (hist-aer), v20190426 (hist-GHG), v20181126 (historical, r1), v20181115 (historical, r2), v20181119 (historical, r3)
#HIST_VERSION=v20181126
#HIST_TIME=185001-201412
## 185001-201412 (historical), 185001-202012 (DAMIP)
#CNTRL_VERSION=v20181015
#ATMOS_CNTRL_VERSION=v20181016
#CNTRL_TIME=185001-244912
#AREACELLO_DIR=${CMIP6_DATA_DIR}
#AREACELLA_DIR=${MY_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}
#SFTLF_FILE=/g/data/oi10/replicas/CMIP6/GMMIP/BCC/BCC-CSM2-MR/hist-resIPO/r1i1p1f1/fx/sftlf/gn/v20190613/sftlf_fx_BCC-CSM2-MR_hist-resIPO_r1i1p1f1_gn.nc


# CAMS-CSM1-0
#
#PROJECT=CMIP6
#MIP=CMIP
# CMIP DAMIP
#INSTITUTION=CAMS
#MODEL=CAMS-CSM1-0
#EXPERIMENT=historical
# hist-aer historical hist-GHG
#FX_EXP=1pctCO2
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r2i1p1f1
#GRID=gn
#OFX_VERSION=v20190830
#HIST_VERSION=v20190708
##ATMOS_HIST_VERSION=
#HIST_TIME=185001-201412
##ATMOS_CNTRL_VERSION=
#CNTRL_VERSION=v20190729
#CNTRL_TIME=290001-339912
#AREACELLO_DIR=${MY_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}
#BRANCH_YEAR=--branch_year 3025
#BRANCH_TIME=--branch_time 45625




# CanESM5-CanOE

#PROJECT=CMIP6
#MIP=CMIP
## CMIP DAMIP
#INSTITUTION=CCCma
#MODEL=CanESM5-CanOE
#EXPERIMENT=historical
## hist-aer historical hist-GHG
#FX_EXP=historical
#HIST_RUN=r1i1p2f1
#CNTRL_RUN=r1i1p2f1
#FX_RUN=r1i1p2f1
#GRID=gn
#OFX_VERSION=v20190429
#HIST_VERSION=v20190429
#ATMOS_HIST_VERSION=v20190429
#HIST_TIME=185001-201412
#ATMOS_CNTRL_VERSION=v20190429
#CNTRL_VERSION=v20190429
#CNTRL_TIME=555001-605012
#AREACELLA_DIR=${CMIP6_DATA_DIR}
#AREACELLO_DIR=${CMIP6_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}


# CAS-ESM2-0
#
#PROJECT=CMIP6
#MIP=CMIP
#INSTITUTION=CAS
#MODEL=CAS-ESM2-0
#EXPERIMENT=historical
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20200306
#HIST_VERSION=v20200306
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20200307
## v2020030[6,7] for surface ocean variables
#CNTRL_TIME=000101-050912
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${MY_DATA_DIR}
#BRANCH_YEAR=--branch_year 80
#BRANCH_TIME=--branch_time 29200


# CESM2

#PROJECT=CMIP6
#MIP=DAMIP
## CMIP DAMIP
#INSTITUTION=NCAR
#MODEL=CESM2
#EXPERIMENT=hist-GHG
## hist-aer historical hist-GHG
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
## gr for ocean, gn for atmos
#FX_VERSION=v20190308
#OFX_VERSION=v20190308
#HIST_VERSION=v20190308
#ATMOS_HIST_VERSION=v20190730
## v20190308 (historical, evspsbl), v20190401 (historical, pr), v20190730 (hist-GHG), v20200206 (hist-aer)
#HIST_TIME=185001-201506
## 185001-201412 (historical, hist-aer) 185001-201506 (hist-GHG)
#ATMOS_CNTRL_VERSION=v20190320
#CNTRL_VERSION=v20190320
#CNTRL_TIME=000101-120012
#AREACELLA_DIR=${CMIP6_DATA_DIR}
#AREACELLO_DIR=${MY_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}
#SFTLF_DIR=${CMIP6_DATA_DIR}
#CHUNK_ANNUAL=--chunk


# CESM2-FV2

#PROJECT=CMIP6
#MIP=CMIP
#INSTITUTION=NCAR
#MODEL=CESM2-FV2
#EXPERIMENT=historical
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gr
#OFX_VERSION=v20191120
#HIST_VERSION=v20191120
##ATMOS_HIST_VERSION=
#HIST_TIME=185001-201412
##ATMOS_CNTRL_VERSION=
#CNTRL_VERSION=v20191120
#CNTRL_TIME=000101-050012
#AREACELLO_DIR=${MY_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}


# CESM2-WACCM-FV2

#PROJECT=CMIP6
#MIP=CMIP
#INSTITUTION=NCAR
#MODEL=CESM2-WACCM-FV2
#EXPERIMENT=historical
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gr
#OFX_VERSION=v20191120
#HIST_VERSION=v20191120
##ATMOS_HIST_VERSION=
#HIST_TIME=185001-201412
##ATMOS_CNTRL_VERSION=
#CNTRL_VERSION=v20191120
#CNTRL_TIME=000101-050012
#AREACELLO_DIR=${MY_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}


# CESM2-WACCM

#PROJECT=CMIP6
#MIP=CMIP
#INSTITUTION=NCAR
#MODEL=CESM2-WACCM
#EXPERIMENT=historical
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gr
#OFX_VERSION=v20190808
#HIST_VERSION=v20190808
##ATMOS_HIST_VERSION=
#HIST_TIME=185001-201412
##ATMOS_CNTRL_VERSION=
#CNTRL_VERSION=v20190320
#CNTRL_TIME=000101-049912
#AREACELLO_DIR=${MY_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}
#CHUNK_ANNUAL=--chunk


# CIESM

#PROJECT=CMIP6
#MIP=CMIP
#INSTITUTION=THU
#MODEL=CIESM
#EXPERIMENT=historical
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20200220
#HIST_VERSION=v20200220
##ATMOS_HIST_VERSION=
#HIST_TIME=185001-201412
##ATMOS_CNTRL_VERSION=
#CNTRL_VERSION=v20200220
#CNTRL_TIME=000101-050012
#AREACELLO_DIR=${CMIP6_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}
#CHUNK_ANNUAL=--chunk


# CMCC-CM2-SR5

#PROJECT=CMIP6
#MIP=CMIP
#INSTITUTION=CMCC
#MODEL=CMCC-CM2-SR5
#EXPERIMENT=historical
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20200616
#HIST_VERSION=v20200616
#ATMOS_HIST_VERSION=v20200616
#HIST_TIME=185001-201412
#ATMOS_CNTRL_VERSION=v20200616
#CNTRL_VERSION=v20200616
#CNTRL_TIME=185001-234912
#AREACELLO_DIR=${CMIP6_DATA_DIR}
#VOLCELLO_DIR=${CMIP6_DATA_DIR}




# CNRM-CM6-1-HR
#
#MODEL=CNRM-CM6-1-HR
#INSTITUTION=CNRM-CERFACS
#RUN=r1i1p1f2
#GRID=gn
#VOLCELLO_VERSION=v20191021
#HIST_VERSION=v20191021
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20191021
#CNTRL_TIME=185001-214912
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical




# E3SM-1-0
# 
# MY_DATA_DIR for thetao and so because have to correct mask
#
#MODEL=E3SM-1-0
#INSTITUTION=E3SM-Project
#RUN=r1i1p1f1
#GRID=gr
#VOLCELLO_VERSION=v20190826
#HIST_VERSION=v20190826
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20191007
#CNTRL_TIME=000101-050012
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical


# E3SM-1-1
# 
#MODEL=E3SM-1-1
#INSTITUTION=E3SM-Project
#RUN=r1i1p1f1
#GRID=gr
#VOLCELLO_VERSION=v20191212
#HIST_VERSION=v20191204
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20191028
#CNTRL_TIME=185001-201412
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical


# EC-Earth3-Veg-LR
#
#PROJECT=CMIP6
#MIP=CMIP
#INSTITUTION=EC-Earth-Consortium
#MODEL=EC-Earth3-Veg-LR
#EXPERIMENT=historical
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20200217
#HIST_VERSION=v20200217
#ATMOS_HIST_VERSION=v20200217
#HIST_TIME=185001-201412
#ATMOS_CNTRL_VERSION=v20200213
#CNTRL_VERSION=v20200213
#CNTRL_TIME=230001-280012
#AREACELLO_DIR=${CMIP6_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}
#BRANCH_TIME=--branch_time 0




# FGOALS-g3
#
#PROJECT=CMIP6
#MIP=DAMIP
## CMIP DAMIP
#MODEL=FGOALS-g3
#INSTITUTION=CAS
#EXPERIMENT=hist-aer
## hist-aer historical hist-GHG
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#FX_VERSION=v20200305
#OFX_VERSION=
#ATMOS_HIST_VERSION=v20200411
## v20190818 (historical), v20200411 (hist-aer, hist-GHG)
#HIST_VERSION=v20191007
#HIST_TIME=185001-202012
## 185001-201612 (historical), 185001-202012 (DAMIP)
#CNTRL_VERSION=v20191028
#ATMOS_CNTRL_VERSION=v20190818
#CNTRL_TIME=060001-116012
## 060001-109912 (ocean), 060001-116012 (atmos)
#AREACELLA_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${MY_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}
#SFTLF_DIR=${CMIP6_DATA_DIR}
#BRANCH_TIME=--branch_time 134685
## branch time is correct in historical files (134685).
## DAMIP branch times incorrect - should be the same as historical


# GFDL-CM4
#
#PROJECT=CMIP6
#MIP=CMIP
#INSTITUTION=NOAA-GFDL
#MODEL=GFDL-CM4
#EXPERIMENT=historical
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20180701
#HIST_VERSION=v20180701
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20180701
#CNTRL_TIME=015101-065012
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${CMIP6_DATA_DIR}
#BRANCH_YEAR=--branch_year 250
#BRANCH_TIME=--branch_time 91250
#CHUNK_ANNUAL=--chunk


# GFDL-ESM4
#
#PROJECT=CMIP6
#MIP=CMIP
## CMIP DAMIP
#INSTITUTION=NOAA-GFDL
#MODEL=GFDL-ESM4
#EXPERIMENT=historical
## historical hist-GHG hist-aer
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gr1
## gn gr1 (atmos)
#FX_VERSION=v20190726
#OFX_VERSION=v20190726
#ATMOS_HIST_VERSION=v20190726
## v20180701 (hist-GHG, hist-aer), v20190726 (hist)
#HIST_VERSION=v20190726
#HIST_TIME=185001-201412
## 2014 (historical), 2020 (hist-GHG, hist-aer)
#CNTRL_VERSION=v20180701
#ATMOS_CNTRL_VERSION=v20180701
#CNTRL_TIME=000101-050012
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${CMIP6_DATA_DIR}
#AREACELLA_DIR=${CMIP6_DATA_DIR}
#SFTLF_FILE=/g/data/oi10/replicas/CMIP6/ScenarioMIP/NOAA-GFDL/GFDL-ESM4/ssp370/r1i1p1f1/fx/sftlf/gr1/v20180701/sftlf_fx_GFDL-ESM4_ssp370_r1i1p1f1_gr1.nc
#CHUNK_ANNUAL=--chunk

# GISS-E2-1-G

#PROJECT=CMIP6
#MIP=CMIP
#INSTITUTION=NASA-GISS
#MODEL=GISS-E2-1-G
#EXPERIMENT=historical
#FX_EXP=piControl
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20180824
#HIST_VERSION=v20180827
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20180824
#CNTRL_TIME=415001-500012
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${CMIP6_DATA_DIR}
#BRANCH_YEAR=--branch_year 4150
# for wfo (but not hfds)...
# Note: BIN_VAR needs to be thetao or so


# GISS-E2-1-G-CC
#
#PROJECT=CMIP6
#MIP=CMIP
#INSTITUTION=NASA-GISS
#MODEL=GISS-E2-1-G-CC
#EXPERIMENT=historical
#FX_EXP=piControl
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20190325
#HIST_VERSION=v20190815
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190815
#CNTRL_TIME=185001-201412
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${CMIP6_DATA_DIR}
#Note: BIN_VAR needs to be thetao or so


# GISS-E2-1-H

#PROJECT=CMIP6
#MIP=CMIP
#INSTITUTION=NASA-GISS
#MODEL=GISS-E2-1-H
#EXPERIMENT=historical
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gr
# gn for hfds, gr for thetao
#OFX_VERSION=v20190403
#HIST_VERSION=v20190403
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190410
#CNTRL_TIME=318001-398012
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${MY_DATA_DIR}


# HadGEM3-GC31-LL

#PROJECT=CMIP6
#MIP=CMIP
# CMIP DAMIP
#INSTITUTION=MOHC
#MODEL=HadGEM3-GC31-LL
#EXPERIMENT=historical
# hist-aer historical hist-GHG
#FX_EXP=piControl
#HIST_RUN=r1i1p1f3
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20190709
#HIST_VERSION=v20190624
#ATMOS_HIST_VERSION=
#HIST_TIME=185001-201412
#ATMOS_CNTRL_VERSION=
#CNTRL_VERSION=v20190628
#CNTRL_TIME=185001-234912
#AREACELLA_DIR=${CMIP6_DATA_DIR}
#AREACELLO_DIR=${CMIP6_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}
#CHUNK_ANNUAL=--chunk



# MCM-UA-1-0

#PROJECT=CMIP6
#MIP=CMIP
#INSTITUTION=UA
#MODEL=MCM-UA-1-0
#EXPERIMENT=historical
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20190731
#HIST_VERSION=v20190731
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190731
#CNTRL_TIME=000101-050012
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${MY_DATA_DIR}





# MIROC6
#
#PROJECT=CMIP6
#MIP=CMIP
## CMIP DAMIP
#MODEL=MIROC6
#INSTITUTION=MIROC
#EXPERIMENT=historical
## historical hist-GHG hist-aer
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#FX_VERSION=v20190311
#OFX_VERSION=
#ATMOS_HIST_VERSION=v20181212
## v20181212 (historical, pr), v20190311 (historical, evspsbl), v20190705 (DAMIP)
##HIST_VERSION=
#HIST_TIME=185001-201412
## 2014 (hist), 2020 (GHG, aer)
#ATMOS_CNTRL_VERSION=v20181212
## v20181212 (pr), v20190311 (evspsbl)
##CNTRL_VERSION=
#CNTRL_TIME=320001-399912
#AREACELLO_DIR=${CMIP6_DATA_DIR}
#AREACELLA_DIR=${CMIP6_DATA_DIR}
#SFTLF_DIR=${CMIP6_DATA_DIR}

# MPI-ESM-1-2-HAM
#
#PROJECT=CMIP6
#MIP=CMIP
#INSTITUTION=HAMMOZ-Consortium
#MODEL=MPI-ESM-1-2-HAM
#EXPERIMENT=historical
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20190627
#HIST_VERSION=v20190627
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190627
#CNTRL_TIME=185001-262912
#VOLCELLO_DIR=${CMIP6_DATA_DIR}
#AREACELLO_DIR=${CMIP6_DATA_DIR}


# MPI-ESM1-2-HR
#
#PROJECT=CMIP6
#MIP=CMIP
#MODEL=MPI-ESM1-2-HR
#INSTITUTION=MPI-M
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#EXPERIMENT=historical
#FX_EXP=historical
#OFX_VERSION=v20190710
#HIST_VERSION=v20190710
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190710
#CNTRL_TIME=185001-234912
#VOLCELLO_DIR=${CMIP6_DATA_DIR}
#AREACELLO_DIR=${CMIP6_DATA_DIR}


# MPI-ESM1-2-LR

#PROJECT=CMIP6
#MIP=CMIP
#MODEL=MPI-ESM1-2-LR
#INSTITUTION=MPI-M
#EXPERIMENT=historical
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20190710
#HIST_VERSION=v20190710
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190710
#CNTRL_TIME=185001-284912
#VOLCELLO_DIR=${CMIP6_DATA_DIR}
#AREACELLO_DIR=${CMIP6_DATA_DIR}


# MRI-ESM2-0
#
#MODEL=MRI-ESM2-0
#INSTITUTION=MRI
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20191205  # problem when calculating global volume
#HIST_VERSION=v20191205
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20191224
#CNTRL_TIME=185001-255012
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical


# NorCPM1
#
#PROJECT=CMIP6
#MIP=CMIP
#INSTITUTION=NCC
#MODEL=NorCPM1
#EXPERIMENT=historical
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#RUN=r1i1p1f1
#GRID=gr
## gn for hfds, gr for thetao 
#OFX_VERSION=v20190914
#HIST_VERSION=v20190914
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190914
#CNTRL_TIME=000101-050012
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${CMIP6b_DATA_DIR}
#BRANCH_YEAR=--branch_year 0
#BRANCH_TIME=--branch_time 0
#CHUNK_ANNUAL=--chunk

# NorESM2-LM
#
# gn for surface and wfo anomaly, gr for water mass 
#
#PROJECT=CMIP6
#MIP=CMIP
#MODEL=NorESM2-LM
#INSTITUTION=NCC
#EXPERIMENT=historical
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20190815
#HIST_VERSION=v20190815
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190920
#CNTRL_TIME=160001-210012
#VOLCELLO_DIR=${CMIP6_DATA_DIR}
#AREACELLO_DIR=${CMIP6_DATA_DIR}


# NorESM2-MM
#
# gn for surface and wfo anomaly, gr for water mass 
# use *912.nc for Omon, piControl
#
#PROJECT=CMIP6
#MIP=CMIP
#MODEL=NorESM2-MM
#INSTITUTION=NCC
#EXPERIMENT=historical
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20191108
#HIST_VERSION=v20191108
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20191108
#CNTRL_TIME=120001-169912
#VOLCELLO_DIR=${CMIP6_DATA_DIR}
#AREACELLO_DIR=${CMIP6_DATA_DIR}


# SAM0-UNICON

#PROJECT=CMIP6
#MIP=CMIP
#INSTITUTION=SNU
#MODEL=SAM0-UNICON
#EXPERIMENT=historical
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20190323
#HIST_VERSION=v20190323
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190910
#CNTRL_TIME=000101-070012
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${CMIP6_DATA_DIR}


# UKESM1-0-LL
#
#PROJECT=CMIP6
#MIP=CMIP
#MODEL=UKESM1-0-LL
#INSTITUTION=MOHC
#EXPERIMENT=historical
#FX_EXP=piControl
#HIST_RUN=r1i1p1f2
#CNTRL_RUN=r1i1p1f2
#FX_RUN=r1i1p1f2
#GRID=gn
#OFX_VERSION=v20190705
#HIST_VERSION=v20190627
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190827
#CNTRL_TIME=196001-305912
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${CMIP6_DATA_DIR}


# CMIP5 #

# CanESM2 #
#
#PROJECT=CMIP5
#MIP=DAMIP
## CMIP DAMIP
#INSTITUTION=CCCma
#MODEL=CanESM2
#EXPERIMENT=historicalMisc
## historical historicalMisc historicalGHG
#FX_EXP=historical
#HIST_RUN=r1i1p4
## r1i1p1 r1i1p4
#CNTRL_RUN=r1i1p1
#FX_RUN=r0i0p0
#GRID=gn
##OFX_VERSION=
#FX_VERSION=v20120410
#ATMOS_HIST_VERSION=v20111028
##v20111027 (historicalGHG); v20120718 (historical); v20111028 (historicalMisc)
#HIST_TIME=185001-201212
## 185001-201212 (GHG, Misc)  185001-200512 (historical)
#ATMOS_CNTRL_VERSION=v20120623
#CNTRL_TIME=201501-301012
#AREACELLO_DIR=${CMIP5_DATA_DIR}
#AREACELLA_DIR=${CMIP5_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}
#SFTLF_DIR=${CMIP5_DATA_DIR}

# CCSM4 #
#
#PROJECT=CMIP5
#MIP=DAMIP
## CMIP DAMIP
#INSTITUTION=NCAR
#MODEL=CCSM4
#EXPERIMENT=historicalMisc
##historical historicalGHG historicalMisc
#FX_EXP=historical
#HIST_RUN=r1i1p10
##r1i1p1 r1i1p10
#CNTRL_RUN=r1i1p1
#FX_RUN=r0i0p0
#GRID=gn
##OFX_VERSION=
#FX_VERSION=v20130312
##HIST_VERSION=
#ATMOS_HIST_VERSION=v20120604
## v20160829 (historical) v20120604 (historicalGHG, historicalMisc)
#HIST_TIME=185001-200512
##CNTRL_VERSION=
#ATMOS_CNTRL_VERSION=v20160829
#CNTRL_TIME=025001-130012
#AREACELLO_DIR=${CMIP5_DATA_DIR}
#AREACELLA_DIR=${CMIP5_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}
#SFTLF_DIR=${CMIP5_DATA_DIR}
#BRANCH_TIME=--branch_time 342005


# CSIRO-Mk3-6-0

#PROJECT=CMIP5
#MIP=CMIP
#DAMIP CMIP
#MODEL=CSIRO-Mk3-6-0
#INSTITUTION=CSIRO-QCCCE
#EXPERIMENT=historical
##historical historicalGHG historicalMisc
#FX_EXP=historical
#HIST_RUN=r1i1p1
##r1i1p1 r1i1p4
#CNTRL_RUN=r1i1p1
#FX_RUN=r0i0p0
#GRID=gn
#OFX_VERSION=v20110518
#FX_VERSION=v20110518
#HIST_VERSION=v20110518
#ATMOS_HIST_VERSION=v20110518
#HIST_TIME=185001-200512
## 201212 (historicalGHG, Misc); 200512 (historical)
#CNTRL_VERSION=v20110518
#ATMOS_CNTRL_VERSION=v20110518
#CNTRL_TIME=000101-050012
#AREACELLO_DIR=${CMIP5_DATA_DIR}
#AREACELLA_DIR=${CMIP5_DATA_DIR}
#VOLCELLO_DIR=${CMIP5_DATA_DIR}

#PR_FILES_HIST := $(sort $(wildcard /g/data/rr3/publications/CMIP5/output1/CSIRO-QCCCE/CSIRO-Mk3-6-0/${EXPERIMENT}/mon/atmos/Amon/${HIST_RUN}/${ATMOS_HIST_VERSION}/pr/pr*.nc))
#EVAP_FILES_HIST := $(sort $(wildcard /g/data/rr3/publications/CMIP5/output1/CSIRO-QCCCE/CSIRO-Mk3-6-0/${EXPERIMENT}/mon/atmos/Amon/${HIST_RUN}/${ATMOS_HIST_VERSION}/evspsbl/evspsbl*.nc))
#PR_FILES_CNTRL := $(sort $(wildcard /g/data/rr3/publications/CMIP5/output1/CSIRO-QCCCE/CSIRO-Mk3-6-0/piControl/mon/atmos/Amon/r1i1p1/files/pr_20110518/pr*.nc))
#EVAP_FILES_CNTRL := $(sort $(wildcard /g/data/rr3/publications/CMIP5/output1/CSIRO-QCCCE/CSIRO-Mk3-6-0/piControl/mon/atmos/Amon/r1i1p1/files/evspsbl_20110518/evspsbl*.nc))  
#AREACELLA_FILE=/g/data/rr3/publications/CMIP5/output1/CSIRO-QCCCE/CSIRO-Mk3-6-0/${FX_EXP}/fx/atmos/fx/${FX_RUN}/${FX_VERSION}/areacella/areacella*.nc
#SFTLF_FILE=/g/data/rr3/publications/CMIP5/output1/CSIRO-QCCCE/CSIRO-Mk3-6-0/${FX_EXP}/fx/atmos/fx/${FX_RUN}/${FX_VERSION}/sftlf/sftlf*.nc


# FGOALS-g2 #
#
#PROJECT=CMIP5
#MIP=DAMIP
## CMIP DAMIP
#INSTITUTION=LASG-CESS
#MODEL=FGOALS-g2
#EXPERIMENT=historicalMisc
##historical historicalGHG historicalMisc
#FX_EXP=historical
#HIST_RUN=r2i1p1
##r1i1p1 r2i1p1
#CNTRL_RUN=r1i1p1
#FX_RUN=r0i0p0
#GRID=gn
##OFX_VERSION=
#FX_VERSION=v1
##HIST_VERSION=
#ATMOS_HIST_VERSION=v20161204
##v20161204 v1 (historicalGHG); v1 (historical); v20161204 v1 (historicalMisc)
#HIST_TIME=185001-200512
## 2009 or 2005 (historicalMisc, historicalGHG) 201412 (historical)
##CNTRL_VERSION=
#ATMOS_CNTRL_VERSION=v20161204
## v20161204 v1
#CNTRL_TIME=020101-090012
#AREACELLO_DIR=${CMIP5_DATA_DIR}
#AREACELLA_DIR=${CMIP5_DATA_DIR}
#SFTLF_DIR=${CMIP5_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}
#BRANCH_TIME=--branch_time 175382.5


# GFDL-CM3
#
#PROJECT=CMIP5
#MIP=CMIP
##DAMIP CMIP
#INSTITUTION=NOAA-GFDL
#MODEL=GFDL-CM3
#EXPERIMENT=historical
##historical historicalGHG historicalMisc
## historicalMisc evspsbl data at r87/dbi599
#FX_EXP=historical
#HIST_RUN=r1i1p1
#CNTRL_RUN=r1i1p1
#FX_RUN=r0i0p0
#GRID=gn
#OFX_VERSION=v20120227
#FX_VERSION=v20110601
#HIST_VERSION=v20110601
#ATMOS_HIST_VERSION=v20120227
#HIST_TIME=186001-200512
#CNTRL_VERSION=v20110601
#ATMOS_CNTRL_VERSION=v20120227
#CNTRL_TIME=000101-050012
##000101-080012; 000101-050012 (atmos)
#AREACELLO_DIR=${CMIP5_DATA_DIR}
#AREACELLA_DIR=${CMIP5_DATA_DIR}
#SFTLF_DIR=${CMIP5_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}
# EVAP_FILES_HIST := $(sort $(wildcard /g/data/r87/dbi599/CMIP5/DAMIP/NOAA-GFDL/GFDL-CM3/historicalMisc/r1i1p1/Amon/evspsbl/gn/v20120227/evspsbl*.nc))

# GFDL-ESM2M #
#
#PROJECT=CMIP5
#MIP=CMIP
##DAMIP CMIP
#INSTITUTION=NOAA-GFDL
#MODEL=GFDL-ESM2M
#EXPERIMENT=historical
##historical historicalGHG historicalMisc
#FX_EXP=historical
#HIST_RUN=r1i1p1
##r1i1p1 r1i1p5
#CNTRL_RUN=r1i1p1
#FX_RUN=r0i0p0
#GRID=gn
#OFX_VERSION=v20130514
#FX_VERSION=v20120123
#HIST_VERSION=v20130226
#ATMOS_HIST_VERSION=v20111228
## v20111228 (historical) v20130214 (historicalGHG, Misc)
#HIST_TIME=185001-200512
#CNTRL_VERSION=v20130226
#ATMOS_CNTRL_VERSION=v20130214
#CNTRL_TIME=000101-050012
#AREACELLO_DIR=${CMIP5_DATA_DIR}
#AREACELLA_DIR=${CMIP5_DATA_DIR}
#SFTLF_DIR=${CMIP5_DATA_DIR}
#VOLCELLO_FILE=${MY_DATA_DIR}

# EVAP_FILES_HIST := $(sort $(wildcard /g/data/r87/dbi599/CMIP5/DAMIP/NOAA-GFDL/GFDL-ESM2M/historicalMisc/r1i1p5/Amon/evspsbl/gn/v20130214/evspsbl*.nc))
#/g/data/al33/replicas/CMIP5/combined/NOAA-GFDL/GFDL-ESM2M/historical/mon/ocean/Omon/r1i1p1/v20130226/so/
#/g/data/al33/replicas/CMIP5/combined/NOAA-GFDL/GFDL-ESM2M/historical/mon/ocean/Omon/r1i1p1/v20130226/wfo/
#/g/data/al33/replicas/CMIP5/combined/NOAA-GFDL/GFDL-ESM2M/historicalGHG/mon/ocean/Omon/r1i1p1/v20130226/so/
#/g/data/al33/replicas/CMIP5/combined/NOAA-GFDL/GFDL-ESM2M/historicalGHG/mon/ocean/Omon/r1i1p1/v20130226/wfo/
#/g/data/al33/replicas/CMIP5/combined/NOAA-GFDL/GFDL-ESM2M/historicalMisc/mon/ocean/Omon/r1i1p5/v20130226/wfo/
#/g/data/al33/replicas/CMIP5/combined/NOAA-GFDL/GFDL-ESM2M/piControl/mon/ocean/Omon/r1i1p1/v20130226/so/
#/g/data/al33/replicas/CMIP5/combined/NOAA-GFDL/GFDL-ESM2M/piControl/mon/ocean/Omon/r1i1p1/v20130226/wfo/

# GISS-E2-H #
#
#PROJECT=CMIP5
#MIP=CMIP
##DAMIP CMIP
#INSTITUTION=NASA-GISS
#MODEL=GISS-E2-H
#EXPERIMENT=historical
##historical historicalGHG historicalMisc
#FX_EXP=historical
#HIST_RUN=r1i1p1
##r1i1p1 r1i1p107
#CNTRL_RUN=r1i1p1
#FX_RUN=r0i0p0
#GRID=gn
##OFX_VERSION=
#FX_VERSION=v20160426
##HIST_VERSION=
#ATMOS_HIST_VERSION=v20160426
## v20160426 (historical) v20160426 (historicalGHG) v20160427 (historicalMisc)
#HIST_TIME=185001-200512
## 201212 (historicalGHG) 200512 (otherwise)
##CNTRL_VERSION=
#ATMOS_CNTRL_VERSION=v20160511
#CNTRL_TIME=241001-294912
## (remove first few control files due to time gap)
#AREACELLO_DIR=${CMIP5_DATA_DIR}
#AREACELLA_DIR=${CMIP5_DATA_DIR}
#SFTLF_DIR=${CMIP5_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}
#BRANCH_TIME=--branch_time 0


# GISS-E2-R
#
#PROJECT=CMIP5
#MIP=CMIP
##DAMIP CMIP
#INSTITUTION=NASA-GISS
#MODEL=GISS-E2-R
#EXPERIMENT=historical
##historical historicalGHG historicalMisc
#FX_EXP=historical
#HIST_RUN=r1i1p1
## r1i1p1 r1i1p310
#CNTRL_RUN=r1i1p1
#FX_RUN=r0i0p0
#GRID=gn
#OFX_VERSION=v20160511
#FX_VERSION=v20160502
#HIST_VERSION=v20160429
#ATMOS_HIST_VERSION=v20160502
# hist=v20160502, ghg=v20160429, aa=v20160503
#HIST_TIME=185001-200512
## 201212 (historicalMisc, GHG) 200512 (historical)
#CNTRL_VERSION=v20160930
#ATMOS_CNTRL_VERSION=v20161004
#CNTRL_TIME=398101-453012
### gaps then 398101-453012
#AREACELLO_DIR=${CMIP5_DATA_DIR}
#AREACELLA_FILE=${CMIP5_DATA_DIR}
#VOLCELLO_FILE=${MY_DATA_DIR}
#BRANCH_TIME=--branch_time 0


# IPSL-CM5A-LR #
#
#PROJECT=CMIP5
#MIP=CMIP
##DAMIP CMIP
#INSTITUTION=IPSL
#MODEL=IPSL-CM5A-LR
#EXPERIMENT=historical
##historical historicalGHG historicalMisc
#FX_EXP=historical
#HIST_RUN=r1i1p1
##r1i1p1 r1i1p3
#CNTRL_RUN=r1i1p1
#FX_RUN=r0i0p0
#GRID=gn
##OFX_VERSION=
#FX_VERSION=v20110406
##HIST_VERSION=
#ATMOS_HIST_VERSION=v20110406
## v20110406 (historical) v20120526 (historicalGHG) v20111119 (historicalMisc)
#HIST_TIME=185001-200512
## 201212 (historicalGHG, historicalMisc), 2005 (historical)
##CNTRL_VERSION=
#ATMOS_CNTRL_VERSION=v20130506
#CNTRL_TIME=180001-279912
#AREACELLO_DIR=${CMIP5_DATA_DIR}
#AREACELLA_DIR=${CMIP5_DATA_DIR}
#SFTLF_DIR=${CMIP5_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}

#EVAP_FILES_HIST := $(sort $(wildcard /g/data/r87/dbi599/CMIP5/DAMIP/IPSL/IPSL-CM5A-LR/historicalMisc/r1i1p3/Amon/evspsbl/gn/v20111119/evspsbl_Amon_IPSL-CM5A-LR_historicalMisc_r1i1p3_*.nc))


# NorESM1-M #
#
#PROJECT=CMIP5
#MIP=CMIP
##DAMIP CMIP
#INSTITUTION=NCC
#MODEL=NorESM1-M
#EXPERIMENT=historical
##historical historicalGHG historicalMisc
#FX_EXP=historical
#HIST_RUN=r1i1p1
#CNTRL_RUN=r1i1p1
#FX_RUN=r0i0p0
#GRID=gn
##OFX_VERSION=
#FX_VERSION=v20110901
##HIST_VERSION=
#ATMOS_HIST_VERSION=v20110901
## v20110901 (historical) v20110918 (historicalGHG, historicalMisc)
#HIST_TIME=185001-200512
## 2012 (historicalGHG, Misc), 2005 (historical)
##CNTRL_VERSION=
#ATMOS_CNTRL_VERSION=v20110901
#CNTRL_TIME=070001-120012
#AREACELLO_DIR=${CMIP5_DATA_DIR}
#AREACELLA_DIR=${CMIP5_DATA_DIR}
#SFTLF_DIR=${CMIP5_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}

#/g/data/al33/replicas/CMIP5/combined/NCC/NorESM1-M/historical/mon/ocean/Omon/r1i1p1/v20110901/so/
#/g/data/al33/replicas/CMIP5/combined/NCC/NorESM1-M/historical/mon/ocean/Omon/r1i1p1/v20110901/wfo/
#/g/data/al33/replicas/CMIP5/combined/NCC/NorESM1-M/historicalGHG/mon/ocean/Omon/r1i1p1/v20110918/so/
#/g/data/al33/replicas/CMIP5/combined/NCC/NorESM1-M/historicalGHG/mon/ocean/Omon/r1i1p1/v20110918/wfo/
#/g/data/al33/replicas/CMIP5/combined/NCC/NorESM1-M/historicalMisc/mon/ocean/Omon/r1i1p1/v20110918/wfo/
#/g/data/al33/replicas/CMIP5/combined/NCC/NorESM1-M/piControl/mon/ocean/Omon/r1i1p1/v20110901/so/
#/g/data/al33/replicas/CMIP5/combined/NCC/NorESM1-M/piControl/mon/ocean/Omon/r1i1p1/v20110901/wfo/

