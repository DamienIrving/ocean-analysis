# Start: /g/data/r87/dbi599/drstree/CMIP5/GCM/CCCMA/CanESM2/historicalGHG/mon/ocean/tos/r1i1p1/tos_Omon_CanESM2_historicalGHG_r1i1p1_185001-201212.nc
# Intermediate: /g/data/r87/dbi599/drstree/CMIP5/CanESM2/historicalGHG/mon/ocean/tos/r1i1p1/tos_Omon_CanESM2_historicalGHG_r1i1p1_185001-201212.nc
# Target: /g/data/r87/dbi599/DRSv2/CMIP5/FGOALS-g2/historicalGHG/mon/ocean/r1i1p1/hfds/latest/hfds_Omon_FGOALS-g2_historicalGHG_r1i1p1_185001-185912.nc

# Wildcard: .../r1i1p1/dedrifted/

import os
import glob
import pdb


regular_file_list = glob.glob('/g/data/r87/dbi599/drstree/CMIP5/*/*/*/*/*/*i*p*/*.nc')
dedrift_file_list = glob.glob('/g/data/r87/dbi599/drstree/CMIP5/*/*/*/*/*/*i*p*/*/*.nc')

pdb.set_trace()


def rename_files(file_list):
    """Rename a bunch of files."""

    bogus_file_list = []
    for infile in file_list:

        dir_components = infile.split('/')
        filename = dir_components.pop()
        if 'dedrfited' in dir_components:
            dedrifted = True
            dir_components.pop() # remove dedrifted
        else:
            dedrifted = False

        if len(dir_components) == 13:

			model = dir_components[7] 
			experiment = dir_components[8]
			timescale = dir_components[9]
			realm = dir_components[10]
			variable = dir_components[11]
			run = dir_components[12]
	
			if dedrifted:
				new_dir = '/g/data/r87/dbi599/DRSv2/CMIP5/%s/%s/%s/%s/%s/%s/latest/dedrifted/'  %(model, experiment, timescale, realm, run, variable)
			else:
				new_dir = '/g/data/r87/dbi599/DRSv2/CMIP5/%s/%s/%s/%s/%s/%s/latest/'  %(model, experiment, timescale, realm, run, variable)

			mkdir_command = 'mkdir -p %s'  %(new_dir)
			mv_command = 'mv %s %s'  %(infile, new_dir)    
			old_dir = "/".join(dir_components)
			rmdir_command = 'rmdir -r %s' %(old_dir)
	  
			print(mkdir_command)
			os.system(mkdir_command)

			print(mv_command)
			os.system(mv_command)
			
			print(rmdir_command)  
			os.system(rmdir_command)

        else:
        
            bogus_file_list.append("/".join(dir_components))
        
    print bogus_file_list
    

#rename_files(dedrift_file_list)
#rename_files(regular_file_list)

