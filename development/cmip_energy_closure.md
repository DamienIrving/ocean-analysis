## CMIP5 energy closure

For many CMIP5 experiments, one or more external forcings (e.g. greenhouse gases, anthropogenic aerosols)
act to modify the net top of the atmosphere radiation (netTOA).
In other words, there is a sustained non-zero sum of the incoming shortwave radiation (rsdt),
reflected/outgoing shortwave radiation (rsut) and emitted/outgoing longwave radiation (rlut).  

Since the ocean represents Earth's primary energy store, on annual and longer timescales
there should be a close correspondence between global changes in netTOA,
downward heat flux at the ocean surface (HFDS) and ocean heat content (OHC).
A model displaying such correspondence is said to conserve energy.

[Hobbs et al (2016)](https://journals.ametsoc.org/doi/10.1175/JCLI-D-15-0477.1) show that in general terms,
the CMIP5 ensemble is energy conserving so long as the netTOA, HFDS and OHC data have been dedrifted.

A question I'm interested in is whether energy conversation can be demonstrated on an individual model basis.
In many cases, modelling groups haven't archived all the required variables,
or there are issues such as step changes in control experiment timeseries (which are required for drift removal)
or [incorrect ocean volume data](https://github.com/DamienIrving/ocean-analysis/blob/master/development/volume_validation.ipynb).
(The latter is problematic since the volume is required for calculating OHC
and on some model grids it can't be calculated from area and depth interval data.)

This is not purely an academic question. If energy conservation can't be demonstrated for many individual models,
it becomes difficult to conduct simple analyses of heat transport throughout the climate system.

Here's my progress so far:

| Model           | Summary             |                                                               
| ---             | ---                 |                                                      
| CanESM2#        | Closure for historical, historicalGHG and historicalAA. <br/> *Images: [historical](https://www.flickr.com/photos/69921266@N08/41131107735/), [historicalGHG](https://www.flickr.com/photos/69921266@N08/41986802922/), [historicalAA](https://www.flickr.com/photos/69921266@N08/42112837922/), [piControl](https://www.flickr.com/photos/69921266@N08/42159310731/)* |
| CCSM4           | No closure for any experiment due to low OHC values (due to bogus ocean volume data). <br/> *Images: [historical](https://www.flickr.com/photos/69921266@N08/27288104737/), [historicalGHG](https://www.flickr.com/photos/69921266@N08/27288104597/), [piControl](https://www.flickr.com/photos/69921266@N08/27288104447/)* |
| CSIRO-Mk3-6-0   | Closure for historical, historicalGHG and historicalAA. <br/> *Images: [historical](https://www.flickr.com/photos/69921266@N08/40373452040/), [historicalGHG](https://www.flickr.com/photos/69921266@N08/40373451860/), [historicalAA](https://www.flickr.com/photos/69921266@N08/27309155297/), [piControl](https://www.flickr.com/photos/69921266@N08/40373451640/)* <br/> *(The netTOA control timeseries was cut short due to a step change.)* |
| FGOALS-g2       | Closure for historicalGHG and historicalAA, but not for historical due to netTOA shape. <br/> *Images: [historical](https://www.flickr.com/photos/69921266@N08/42113209582/), [historicalGHG](https://www.flickr.com/photos/69921266@N08/42031318811/), [historicalAA](https://www.flickr.com/photos/69921266@N08/42031320271/), [piControl](https://www.flickr.com/photos/69921266@N08/28287866918/)* |
| GFDL-CM3*       | Minor non-closure for all experiments due to HFDS amplitude. <br/> *Images: [historical](https://www.flickr.com/photos/69921266@N08/40223449580/), [historicalGHG](https://www.flickr.com/photos/69921266@N08/40223451350/), [piControl](https://www.flickr.com/photos/69921266@N08/41439145274/)* | 
| GFDL-ESM2M*     | No closure for any experiment due to HFDS amplitude. <br/> *Images: [historical](https://www.flickr.com/photos/69921266@N08/40352935960/), [historicalGHG](https://www.flickr.com/photos/69921266@N08/41258866525/), [piControl](https://www.flickr.com/photos/69921266@N08/41258866415/)* <br/> *(Need to download missing netTOA data for historicalAA.)*  |
| GISS-E2-H (p1)* | Minor non-closure for historical, historicalGHG and historicalAA. <br/> *Images: [historical](https://www.flickr.com/photos/69921266@N08/41367480825/), [historicalGHG](https://www.flickr.com/photos/69921266@N08/41367480555/), [historicalAA](https://www.flickr.com/photos/69921266@N08/28396150098/), [piControl](https://www.flickr.com/photos/69921266@N08/27398767637/)* <br/> *(The OHC control timeseries was cut short due to step changes)* |
| GISS-E2-R (p1)  | Closure for historical and historicalGHG, but not for historicalAA due to OHC amplitude. <br/> *Images: [historical](https://www.flickr.com/photos/69921266@N08/28287701048/), [historicalGHG](https://www.flickr.com/photos/69921266@N08/27288632717/), [historicalAA](https://www.flickr.com/photos/69921266@N08/40353123460/), [piControl](https://www.flickr.com/photos/69921266@N08/28287700818/)* |
| IPSL-CM5A-LR*   | No closure for any experiment due to HFDS amplitude. <br/> *Images: [historical](https://www.flickr.com/photos/69921266@N08/40435966960/), [historicalGHG](https://www.flickr.com/photos/69921266@N08/41521709284/), [historicalAA](https://www.flickr.com/photos/69921266@N08/42196735552/), [piControl](https://www.flickr.com/photos/69921266@N08/40435966680/)* <br/> *(The HFDS control timeseries was cut short due missing HFLS data)* |
| NorESM1-M       | Unable to calculate OHC due to bogus ocean volume data. |

*Models that didn't archive HFDS or hfsithermds data (and hence the inferred HFDS doesn't account for sea ice thermodynamics)  
#Models that didn't archive HFDS but did archive hfsithermds (and hence the inferred HFDS does account for sea ice thermodynamics)


### Notes

Energy non-closure is often just an amplitude issue, with the shape of the OHC, HFDS and netTOA curves matching

For models where the HFDS variable is not archived, it can be inferred from the other surface fluxes: downwelling shortwave flux (rsds), upwelling shortwave flux (rsus), downwelling longwave flux (rlds), upwelling longwave flux (rlus), sensible heat flux (hfss), latent heat flux (hfss) and heat flux into sea water due to sea ice thermodynamics (hfsithermds). Typically, modelling groups archive all of those variables except hfsithermds. This obviously doesn't cause any problems when looking at zonally integrated surface heat fluxes outside of the high latitudes, but it is problematic when calculating the global intergral (for instance). While its climatological values are relatively small, when looking at the change over time in a forced (or drifting) simulation, the hfsithermds component of the surface energy budget is not negligible.  
