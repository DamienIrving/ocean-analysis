# System configuration

PYTHON=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
DATA_SCRIPT_DIR=/home/599/dbi599/ocean-analysis/data_processing
VIZ_SCRIPT_DIR=/home/599/dbi599/ocean-analysis/visualisation

#defaults
MY_DATA_DIR=/g/data/r87/dbi599
AUS_CMIP6_DATA_DIR=/g/data/fs38/publications
CMIP6_DATA_DIR=/g/data/oi10/replicas
CMIP6b_DATA_DIR=/g/data1b/oi10/replicas
CMIP5_DATA_DIR=/g/data/al33/replicas
TOS_VAR=tos
TOS_LONG_NAME=sea_surface_temperature
SF_VAR=hfds
# wfo hfds
SF_NAME=surface_downward_heat_flux_in_sea_water
# surface_downward_heat_flux_in_sea_water water_flux_into_sea_water

# CMIP6 #

# ACCESS-CM2
#
#PROJECT=CMIP6
#MIP=CMIP
#INSTITUTION=CSIRO-ARCCSS
#MODEL=ACCESS-CM2
#EXPERIMENT=historical
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20191108
#ATMOS_HIST_VERSION=v20191108
#HIST_VERSION=v20191108
#HIST_TIME=185001-201412
#ATMOS_CNTRL_VERSION=v20191112
#CNTRL_VERSION=v20191112
#CNTRL_TIME=095001-144912
#CMIP6_DATA_DIR=/g/data/fs38/publications
#VOLCELLO_DIR=${AUS_CMIP6_DATA_DIR}
#AREACELLO_DIR=${AUS_CMIP6_DATA_DIR}


# ACCESS-ESM1-5
#
#PROJECT=CMIP6
#MIP=DAMIP
## CMIP DAMIP
#MODEL=ACCESS-ESM1-5
#INSTITUTION=CSIRO
#EXPERIMENT=hist-aer
## historical hist-GHG hist-aer
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20191115
#FX_VERSION=v20191115
#ATMOS_HIST_VERSION=v20200615
##v20191115 (historical r1i1p1), v20191128 (historical r2i1p1f1), v20191203 (historical r3i1p1f1), v20200615 (hist-aer, hist-GHG)
#HIST_VERSION=v20191115
#HIST_TIME=185001-202012
##2014 (historical, 2020 (hist-aer, hist-GHG)
#ATMOS_CNTRL_VERSION=v20191214
#CNTRL_VERSION=v20191214
#CNTRL_TIME=010101-100012
#CMIP6_DATA_DIR=${AUS_CMIP6_DATA_DIR}
#VOLCELLO_DIR=${CMIP6_DATA_DIR}
#AREACELLO_DIR=${CMIP6_DATA_DIR}
#AREACELLA_DIR=${CMIP6_DATA_DIR}


# BCC-CSM2-MR

#PROJECT=CMIP6
#MIP=DAMIP
## CMIP DAMIP
#INSTITUTION=BCC
#MODEL=BCC-CSM2-MR
#EXPERIMENT=hist-GHG
#FX_EXP=historical
## hist-aer historical hist-GHG
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20181126
#FX_VERSION=v20181126
#ATMOS_HIST_VERSION=v20190426
## v20190507 (hist-aer), v20190426 (hist-GHG), v20181126 (historical, r1), v20181115 (historical, r2), v20181119 (historical, r3)
#HIST_VERSION=v20181126
#HIST_TIME=185001-202012
## 185001-201412 (historical), 185001-202012 (DAMIP)
#CNTRL_VERSION=v20181015
#ATMOS_CNTRL_VERSION=v20181016
#CNTRL_TIME=185001-244912
#AREACELLO_DIR=${CMIP6_DATA_DIR}
#AREACELLA_DIR=${MY_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}
## sftlf_file = /g/data/oi10/replicas/CMIP6/GMMIP/BCC/BCC-CSM2-MR/hist-resIPO/r1i1p1f1/fx/sftlf/gn/v20190613/sftlf_fx_BCC-CSM2-MR_hist-resIPO_r1i1p1f1_gn.nc


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


# CanESM5

#PROJECT=CMIP6
#MIP=DAMIP
## CMIP DAMIP
#INSTITUTION=CCCma
#MODEL=CanESM5
#EXPERIMENT=hist-aer
## hist-aer historical hist-GHG
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
## r1i1p1f1 r10i1p1f1 (for hist-GHG)
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#FX_VERSION=v20190429
#OFX_VERSION=v20190429
#HIST_VERSION=v20190429
#ATMOS_HIST_VERSION=v20190429
#HIST_TIME=185001-202012
## 185001-201412 185001-202012
#ATMOS_CNTRL_VERSION=v20190429
#CNTRL_VERSION=v20190429
#CNTRL_TIME=520101-620012
#AREACELLA_DIR=${CMIP6_DATA_DIR}
#AREACELLO_DIR=${CMIP6_DATA_DIR}
#VOLCELLO_DIR=${CMIP6_DATA_DIR}


# CanESM5-CanOE

#PROJECT=CMIP6
#MIP=CMIP
# CMIP DAMIP
#INSTITUTION=CCCma
#MODEL=CanESM5-CanOE
#EXPERIMENT=historical
# hist-aer historical hist-GHG
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

PROJECT=CMIP6
MIP=DAMIP
## CMIP DAMIP
INSTITUTION=NCAR
MODEL=CESM2
EXPERIMENT=hist-aer
# hist-aer historical hist-GHG
FX_EXP=historical
HIST_RUN=r1i1p1f1
CNTRL_RUN=r1i1p1f1
FX_RUN=r1i1p1f1
GRID=gn
# gr for ocean, gn for atmos
FX_VERSION=v20190308
OFX_VERSION=v20190308
HIST_VERSION=v20190308
ATMOS_HIST_VERSION=v20200206
# v20190308 (historical), v20190730 (hist-GHG), v20200206 (hist-aer)
HIST_TIME=185001-201412
## 185001-201412 (historical, hist-aer) 185001-201506 (hist-GHG)
ATMOS_CNTRL_VERSION=v20190320
CNTRL_VERSION=v20190320
CNTRL_TIME=000101-120012
AREACELLA_DIR=${CMIP6_DATA_DIR}
AREACELLO_DIR=${MY_DATA_DIR}
VOLCELLO_DIR=${MY_DATA_DIR}
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


# CNRM-CM6-1
#
#MODEL=CNRM-CM6-1
#INSTITUTION=CNRM-CERFACS
#HIST_RUN=r1i1p1f2
#CNTRL_RUN=r1i1p1f2
#GRID=gr
## gn (ocean), gr (atmos)
#VOLCELLO_VERSION=v20180917
#HIST_VERSION=v20180917
#ATMOS_HIST_VERSION=v20190308
#HIST_TIME=185001-201412
#ATMOS_CNTRL_VERSION=v20180814
#CNTRL_VERSION=v20180814
#CNTRL_TIME=185001-234912
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#CHUNK_ANNUAL=--chunk
#EXPERIMENT=hist-GHG
# hist-aer historical hist-GHG
#MIP=DAMIP
# CMIP DAMIP
#MY_EXP_DATA_DIR=/g/data/r87/dbi599/CMIP6
#MY_CNTRL_DATA_DIR=/g/data/r87/dbi599/CMIP6
#MY_FX_DATA_DIR=/g/data/r87/dbi599/CMIP6
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6


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


# CNRM-ESM2-1
#
#MODEL=CNRM-ESM2-1
#INSTITUTION=CNRM-CERFACS
#RUN=r1i1p1f2
#GRID=gn
#VOLCELLO_VERSION=v20181206
#HIST_VERSION=v20181206
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20181115
#CNTRL_TIME=185001-234912
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


# EC-Earth3
#
#PROJECT=CMIP6
#MIP=CMIP
#INSTITUTION=EC-Earth-Consortium
#MODEL=EC-Earth3
#EXPERIMENT=historical
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20200310
#HIST_VERSION=v20200310
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20200312
#CNTRL_TIME=225901-275912
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${CMIP6_DATA_DIR}
#BRANCH_TIME=--branch_time 149749
#BRANCH_YEAR=--branch_year 2260


# EC-Earth3-Veg
#
#MODEL=EC-Earth3-Veg
#INSTITUTION=EC-Earth-Consortium
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20190605
#HIST_VERSION=v20200225
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20200226
##v20190619
#CNTRL_TIME=185001-234912
#NCI_DATA_DIR=/g/data1b/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical
#BRANCH_YEAR=--branch_year 1930
#BRANCH_TIME=--branch_time 29244
#TOS_VAR=thetao
#TOS_LONG_NAME=sea_water_potential_temperature


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

# FGOALS-f3-L
#
#MODEL=FGOALS-f3-L
#INSTITUTION=CAS
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20190918
#AREACELLA_VERSION=
#ATMOS_HIST_VERSION=v20200411
#HIST_VERSION=v20191007
#HIST_TIME=185001-201412
## 185001-201412 (historical), 185001-202012 (DAMIP)
#CNTRL_VERSION=v20191028
#ATMOS_CNTRL_VERSION=v20191029
#CNTRL_TIME=060001-109912
#EXPERIMENT=historical
# hist-aer historical hist-GHG
#MIP=CMIP
# CMIP DAMIP
#MY_EXP_DATA_DIR=/g/data/r87/dbi599/CMIP6
#MY_CNTRL_DATA_DIR=/g/data/r87/dbi599/CMIP6
#MY_FX_DATA_DIR=/g/data/r87/dbi599/CMIP6
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6
#FX_EXP=historical
#FX_RUN=r1i1p1f1
#AREACELLO_FILE=${MY_FX_DATA_DIR}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/fx/ocean/fx/${FX_RUN}/${VOLCELLO_VERSION}/areacello/areacello_fx_${MODEL}_${FX_EXP}_${FX_RUN}.nc
#AREACELLA_FILE=${NCI_DATA_DIR}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/fx/atmos/fx/${FX_RUN}/${AREACELLA_VERSION}/areacella/areacella_fx_${MODEL}_${FX_EXP}_${FX_RUN}.nc
#VOLCELLO_FILE=${MY_FX_DATA_DIR}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/Ofx/volcello/${GRID}/${VOLCELLO_VERSION}/volcello_Ofx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID}.nc


# FGOALS-g3
#
#MODEL=FGOALS-g3
#INSTITUTION=CAS
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=
#AREACELLA_VERSION=
#ATMOS_HIST_VERSION=v20200411
## v20190818 (historical), v20200411 (hist-aer, hist-GHG)
#HIST_VERSION=v20191007
#HIST_TIME=185001-202012
## 185001-201612 (historical), 185001-202012 (DAMIP)
#CNTRL_VERSION=v20191028
#ATMOS_CNTRL_VERSION=v20190818
#CNTRL_TIME=020001-089912
## 060001-109912 (ocean), 060001-116012 (atmos)
#EXPERIMENT=hist-GHG
# hist-aer historical hist-GHG
#MIP=DAMIP
## CMIP DAMIP
#MY_EXP_DATA_DIR=/g/data/r87/dbi599/CMIP6
#MY_CNTRL_DATA_DIR=/g/data/r87/dbi599/CMIP6
#MY_FX_DATA_DIR=/g/data/r87/dbi599/CMIP6
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6
#FX_EXP=historical
#FX_RUN=r1i1p1f1
#AREACELLO_FILE=${MY_FX_DATA_DIR}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/fx/ocean/fx/${FX_RUN}/${VOLCELLO_VERSION}/areacello/areacello_fx_${MODEL}_${FX_EXP}_${FX_RUN}.nc
#AREACELLA_FILE=${NCI_DATA_DIR}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/fx/atmos/fx/${FX_RUN}/${AREACELLA_VERSION}/areacella/areacella_fx_${MODEL}_${FX_EXP}_${FX_RUN}.nc
#VOLCELLO_FILE=${MY_FX_DATA_DIR}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/Ofx/volcello/${GRID}/${VOLCELLO_VERSION}/volcello_Ofx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID}.nc


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
#INSTITUTION=NOAA-GFDL
#MODEL=GFDL-ESM4
#EXPERIMENT=historical
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#FX_RUN=r1i1p1f1
#GRID=gn
#OFX_VERSION=v20190726
#HIST_VERSION=v20190726
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20180701
#CNTRL_TIME=000101-050012
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${CMIP6_DATA_DIR}
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
#TOS_VAR=thetao
#TOS_LONG_NAME=sea_water_potential_temperature


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
#TOS_VAR=thetao
#TOS_LONG_NAME=sea_water_potential_temperature


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

# IPSL-CM6A-LR

#PROJECT=CMIP6
#MIP=CMIP
#MODEL=IPSL-CM6A-LR
#INSTITUTION=IPSL
#EXPERIMENT=historical
## hist-aer historical hist-GHG
#FX_EXP=historical
#HIST_RUN=r1i1p1f1
#CNTRL_RUN=r1i1p1f1
#GRID=gr
## gn (ocean), gr (atmos)
#OFX_VERSION=v20180803
#HIST_VERSION=v20180803
#ATMOS_HIST_VERSION=v20180803
## v20180803 (historical); v20180914 (hist-aer, hist-ghg)
#HIST_TIME=185001-201412
#ATMOS_CNTRL_VERSION=v20200326
#CNTRL_VERSION=v20190522
##v20181123
#CNTRL_TIME=185001-384912
##185001-304912 (full ocean); 185001-284912 (hfds missing file in middle); 384912 (atmos)
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
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


# MIROC-ES2L
#
#MODEL=MIROC-ES2L
#INSTITUTION=MIROC
#RUN=r1i1p1f2
#GRID=gn
#VOLCELLO_VERSION=v20190823
#HIST_VERSION=v20190823
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190823
#CNTRL_TIME=185001-234912
#NCI_DATA_DIR=/g/data1b/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical
#CHUNK_ANNUAL=--chunk


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
#MODEL=MPI-ESM1-2-HR
#INSTITUTION=MPI-M
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20190710
#HIST_VERSION=v20190710
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190710
#CNTRL_TIME=185001-234912
#NCI_DATA_DIR=/g/data1b/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${NCI_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical


# MPI-ESM1-2-LR

#MODEL=MPI-ESM1-2-LR
#INSTITUTION=MPI-M
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20190710
#HIST_VERSION=v20190710
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190710
#CNTRL_TIME=185001-284912
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${NCI_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical


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
#MODEL=NorESM2-LM
#INSTITUTION=NCC
#RUN=r1i1p1f1
#GRID=gr
#VOLCELLO_VERSION=v20190815
#HIST_VERSION=v20190815
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190920
#CNTRL_TIME=160001-210012
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${NCI_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical


# NorESM2-MM
#
# gn for surface and wfo anomaly, gr for water mass 
# use *912.nc for Omon, piControl
#
#MODEL=NorESM2-MM
#INSTITUTION=NCC
#RUN=r1i1p1f1
#GRID=gr
#VOLCELLO_VERSION=v20191108
#HIST_VERSION=v20191108
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20191108
#CNTRL_TIME=120001-169912
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${NCI_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical


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
#MODEL=UKESM1-0-LL
#INSTITUTION=MOHC
#RUN=r1i1p1f2
#GRID=gn
#VOLCELLO_VERSION=v20190705
#HIST_VERSION=v20190627
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190827
#CNTRL_TIME=196001-305912
#NCI_DATA_DIR=/g/data1b/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=piControl


# CMIP5 #

# CanESM2 #
#
#PROJECT=CMIP5
#MIP=DAMIP
# CMIP DAMIP
#INSTITUTION=CCCma
#MODEL=CanESM2
#EXPERIMENT=historicalMisc
#FX_EXP=historical
#HIST_RUN=r1i1p4
# r1i1p1 r1i1p4
#CNTRL_RUN=r1i1p1
#FX_RUN=r0i0p0
#GRID=gn
#OFX_VERSION=
#FX_VERSION=v20120410
#ATMOS_HIST_VERSION=v20111028
#v20111027 (historicalGHG); v20120718 (historical); v20111028 (historicalMisc)
#HIST_TIME=185001-201212
# 185001-201212  185001-200512
#ATMOS_CNTRL_VERSION=v20120623
#CNTRL_TIME=201501-301012
#AREACELLO_DIR=${CMIP5_DATA_DIR}
#AREACELLA_DIR=${CMIP5_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}


# CCSM4 #
#
#PROJECT=CMIP5
#MIP=DAMIP
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
#OFX_VERSION=
#FX_VERSION=v20130312
#HIST_VERSION=
#ATMOS_HIST_VERSION=v20120604
## v20160829 (historical) v20120604 (historicalGHG) v20120604 (historicalMisc)
#HIST_TIME=185001-200512
#CNTRL_VERSION=
#ATMOS_CNTRL_VERSION=v20160829
#CNTRL_TIME=025001-130012
#AREACELLO_DIR=${CMIP5_DATA_DIR}
#AREACELLA_DIR=${CMIP5_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}
#BRANCH_TIME=--branch_time 342005


# CSIRO-Mk3-6-0
#
# unique wfo DRS: 
# PR_FILES_HIST := $(sort $(wildcard /g/data/rr3/publications/CMIP5/output1/CSIRO-QCCCE/CSIRO-Mk3-6-0/${EXPERIMENT}/mon/atmos/Amon/${HIST_RUN}/${ATMOS_HIST_VERSION}/pr/pr*.nc))
# EVAP_FILES_HIST := $(sort $(wildcard /g/data/rr3/publications/CMIP5/output1/CSIRO-QCCCE/CSIRO-Mk3-6-0/${EXPERIMENT}/mon/atmos/Amon/${HIST_RUN}/${ATMOS_HIST_VERSION}/evspsbl/evspsbl*.nc))
# PR_FILES_CNTRL := $(sort $(wildcard /g/data/rr3/publications/CMIP5/output1/CSIRO-QCCCE/CSIRO-Mk3-6-0/piControl/mon/atmos/Amon/r1i1p1/files/pr_20110518/pr*.nc))
# EVAP_FILES_CNTRL := $(sort $(wildcard /g/data/rr3/publications/CMIP5/output1/CSIRO-QCCCE/CSIRO-Mk3-6-0/piControl/mon/atmos/Amon/r1i1p1/files/evspsbl_20110518/evspsbl*.nc))                
#
#PROJECT=CMIP5
#MIP=CMIP
##DAMIP CMIP
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


# FGOALS-g2 #
#
#PROJECT=CMIP5
#MIP=DAMIP
# CMIP DAMIP
#INSTITUTION=LASG-CESS
#MODEL=FGOALS-g2
#EXPERIMENT=historicalGHG
#historical historicalGHG historicalMisc
#FX_EXP=historical
#HIST_RUN=r1i1p1
#r1i1p1 r2i1p1
#CNTRL_RUN=r1i1p1
#FX_RUN=r0i0p0
#GRID=gn
#VOLCELLO_VERSION=
#AREACELLA_VERSION=v1
#HIST_VERSION=
#ATMOS_HIST_VERSION=v20161204
#v20161204 v1 (historicalGHG); v1 (historical); v20161204 v1 (historicalMisc)
#HIST_TIME=185001-200912
# 2005 or 200912 (historicalMisc); 2005 or 2009 (historicalGHG) 201412 (historical)
#CNTRL_VERSION=
#ATMOS_CNTRL_VERSION=v20161204
## v20161204 v1
#CNTRL_TIME=020101-090012
#AREACELLO_FILE=${NCI_DATA_DIR}
#AREACELLA_FILE=${NCI_DATA_DIR}
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
#VOLCELLO_DIR=${MY_DATA_DIR}

# GFDL-ESM2M #
#
#PROJECT=CMIP5
#MIP=CMIP
#DAMIP CMIP
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
#VOLCELLO_FILE=${MY_DATA_DIR}

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
## 201212 (historicalGHG, historicalMisc)
##CNTRL_VERSION=
#ATMOS_CNTRL_VERSION=v20130506
#CNTRL_TIME=180001-279912
#AREACELLO_DIR=${CMIP5_DATA_DIR}
#AREACELLA_FILE=${CMIP5_DATA_DIR}
#VOLCELLO_FILE=${MY_DATA_DIR}


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
#OFX_VERSION=
#FX_VERSION=v20110901
#HIST_VERSION=
#ATMOS_HIST_VERSION=v20110901
# v20110901 (historical) v20110918 (historicalGHG) v20110918 (historicalMisc)
#HIST_TIME=185001-200512
# 2012 (historicalGHG, Misc)
#CNTRL_VERSION=
#ATMOS_CNTRL_VERSION=v20110901
#CNTRL_TIME=070001-120012
#AREACELLO_DIR=${CMIP5_DATA_DIR}
#AREACELLA_DIR=${CMIP5_DATA_DIR}
#VOLCELLO_DIR=${MY_DATA_DIR}

#/g/data/al33/replicas/CMIP5/combined/NCC/NorESM1-M/historical/mon/ocean/Omon/r1i1p1/v20110901/so/
#/g/data/al33/replicas/CMIP5/combined/NCC/NorESM1-M/historical/mon/ocean/Omon/r1i1p1/v20110901/wfo/
#/g/data/al33/replicas/CMIP5/combined/NCC/NorESM1-M/historicalGHG/mon/ocean/Omon/r1i1p1/v20110918/so/
#/g/data/al33/replicas/CMIP5/combined/NCC/NorESM1-M/historicalGHG/mon/ocean/Omon/r1i1p1/v20110918/wfo/
#/g/data/al33/replicas/CMIP5/combined/NCC/NorESM1-M/historicalMisc/mon/ocean/Omon/r1i1p1/v20110918/wfo/
#/g/data/al33/replicas/CMIP5/combined/NCC/NorESM1-M/piControl/mon/ocean/Omon/r1i1p1/v20110901/so/
#/g/data/al33/replicas/CMIP5/combined/NCC/NorESM1-M/piControl/mon/ocean/Omon/r1i1p1/v20110901/wfo/

