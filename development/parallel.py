"""
Toy script to figure out how to parallelise the following:

for lat_index in range(0, nlat):
    lat_agg = lat_aggregate(cube, coord_names, new_lat_bounds[lat_index], agg_method)
    new_data[..., lat_index] = lat_agg.data

"""

import multiprocessing
import numpy


cube = 'hello'
coord_names = 'boo'
agg_method = 'mean'
nlat = 70
new_lat_bounds = numpy.arange(nlat)


def lat_aggregate(cube, coord_names, lat_bounds, agg_method):
    """Dummy."""
    
    return lat_bounds

# Start my pool
print('CPUs:', multiprocessing.cpu_count())
pool = multiprocessing.Pool( multiprocessing.cpu_count() )

# Build task list
tasks = []
for lat_index in range(0, nlat):
    tasks.append( (cube, coord_names, new_lat_bounds[lat_index], agg_method) )
    
# Run tasks
results = [pool.apply_async( lat_aggregate, t ) for t in tasks]

# Process results
for lat_index, result in enumerate(results):
    lat_agg = result.get()
    print(lat_agg)
    #new_data[..., lat_index] = lat_agg.data
        
pool.close()
pool.join()



