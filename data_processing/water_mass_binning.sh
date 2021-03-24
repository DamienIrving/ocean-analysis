
#
# Description: Monthly water mass binning by file
#             

function usage {
    echo "USAGE: bash $0 n_weights_files weight_files weight_var python basin_file area_file temperature_var salinity_var outfile temperature_files"
    echo "   n_weight_files:      Number of weight files"
    echo "   weight_files:        Weight files"
    echo "   weight_var:          Weight variable (e.g. cell_area ocean_volume water_flux_into_sea_water)"
    echo "   python:              e.g. /g/data/e14/dbi599/miniconda3/envs/cmip/bin/python"
    echo "   basin_file:          Basin file"
    echo "   area_file:           Area file"
    echo "   temperature_var:     Temperature variable (thetao or tos)"
    echo "   salinity_var:        Salinity variable (so or sos)"
    echo "   outfile:             Output file name"
    echo "   temperature_files:   Temperature files"

    exit 1
}

n_weight_files=$1
shift

weight_files=(${@:1:${n_weight_files}})
for i in ${weight_files[@]}; do
    shift
done

weight_var=$1
python=$2
basin_file=$3
area_file=$4
temperature_var=$5
salinity_var=$6
outfile=$7
shift
shift
shift
shift
shift
shift
shift
temperature_files=($@)

script_dir=/home/599/dbi599/ocean-analysis/data_processing
bindir=/g/data/e14/dbi599/binning-temp

if [ "${temperature_var}" == "thetao" ]; then
    temperature_name="sea_water_potential_temperature"
else
    temperature_name="sea_surface_temperature"
fi

if [ "${salinity_var}" == "so" ]; then
    salinity_name="sea_water_salinity"
else
    salinity_name="sea_surface_salinity"
fi

if [ "${weight_var}" == "cell_area" ]; then
    area_option=" "
elif [ "${weight_var}" == "ocean_volume" ]; then
    area_option=" "
else
    area_option="--area_file ${area_file}"
fi


outvar=`basename ${outfile} | cut -d '_' -f 1`

mkdir -p ${bindir}
rm -f ${bindir}/*

for i in ${!temperature_files[@]}; do

    if [ "${n_weight_files}" == "1" ]; then
        weight_file=${weight_files[0]}
    else
        weight_file=${weight_files[$i]}
    fi

    temperature_file=${temperature_files[$i]}
    salinity_file=`echo ${temperature_file} | sed s:${temperature_var}:${salinity_var}:g`  
    binfile=`basename ${temperature_file} | sed s:${temperature_var}:${outvar}:g `

    command1="${python} ${script_dir}/water_mass_binning.py ${weight_file} ${weight_var} ${basin_file} mon ${bindir}/${binfile} --salinity_files ${salinity_file} --salinity_var ${salinity_name} --temperature_files ${temperature_file} --temperature_var ${temperature_name} --global_only ${area_option}"
    echo ${command1}
    ${command1}
done

command2="${python} ${script_dir}/merge_files.py ${bindir}/*.nc ${outfile}"
echo ${command2}
${command2}





