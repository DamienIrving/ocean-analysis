#!/bin/bash
#
# Description: Bin a MOM 3D flux variable by temperature
#             

function usage {
    echo "USAGE: bash $0 variable"
    echo "   variable:  input variable (with underscores)"
    exit 1
}

data_var=$1
file_var=`echo ${data_var} | sed s:_:-:g`

#bash mom_to_cmip_3d.sh ${data_var} historical

#bash mom_to_cmip_3d.sh ${data_var} piControl

hist_binning_command="/g/data/r87/dbi599/miniconda3/envs/ocean3/bin/python /home/599/dbi599/ocean-analysis/data_processing/calc_surface_flux_histogram.py /g/data/r87/dbi599/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/historical/r1i1p1f1/Omon/${file_var}/gn/v20191108/${file_var}_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_*.nc ${data_var} /g/data/fs38/publications/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/historical/r1i1p1f1/Ofx/areacello/gn/v20191108/areacello_Ofx_ACCESS-CM2_historical_r1i1p1f1_gn.nc /g/data/r87/dbi599/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/historical/r1i1p1f1/Ofx/basin/gn/v20191118/basin_Ofx_ACCESS-CM2_historical_r1i1p1f1_gn.nc /g/data/r87/dbi599/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/historical/r1i1p1f1/Omon/${file_var}/gn/v20191108/${file_var}-thetao-binned_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_185001-201412.nc --bin_files /g/data/fs38/publications/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/historical/r1i1p1f1/Omon/thetao/gn/v20191108/thetao_Omon_ACCESS-CM2_historical_r1i1p1f1_gn_*.nc --bin_var sea_water_potential_temperature"
echo ${hist_binning_command}
${hist_binning_command}

control_binning_command="/g/data/r87/dbi599/miniconda3/envs/ocean3/bin/python /home/599/dbi599/ocean-analysis/data_processing/calc_surface_flux_histogram.py /g/data/r87/dbi599/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/piControl/r1i1p1f1/Omon/${file_var}/gn/v20191112/${file_var}_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_*.nc ${data_var} /g/data/fs38/publications/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/historical/r1i1p1f1/Ofx/areacello/gn/v20191108/areacello_Ofx_ACCESS-CM2_historical_r1i1p1f1_gn.nc /g/data/r87/dbi599/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/historical/r1i1p1f1/Ofx/basin/gn/v20191118/basin_Ofx_ACCESS-CM2_historical_r1i1p1f1_gn.nc /g/data/r87/dbi599/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/piControl/r1i1p1f1/Omon/${file_var}/gn/v20191112/${file_var}-thetao-binned_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_095001-144912.nc --bin_files /g/data/fs38/publications/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/piControl/r1i1p1f1/Omon/thetao/gn/v20191112/thetao_Omon_ACCESS-CM2_piControl_r1i1p1f1_gn_*.nc --bin_var sea_water_potential_temperature"
echo ${control_binning_command}
${control_binning_command}


