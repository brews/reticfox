# Parse Deuterium (δD; precip) and d18O (precip) from iCESM cam experiment 
# slice output. Assumes raw NetCDF files (below) are in the pwd.


import xarray as xr


D18OSW_STR = 'd18osw'
D18OSW_OUT = 'b.e12.B1850C5.f19_g16.i21ka.03.pop.h.d18osw.nc'
R18O_BLOB = 'b.e12.B1850C5.f19_g16.i21ka.03.pop.h.R18O.*.nc'


# First, deal with d18op
r18o = xr.open_mfdataset(R18O_BLOB).isel(z_t=0).sortby('time')
r18o[D18OSW_STR] = (r18o['R18O'] - 1.0) * 1000.0
# Metadata
r18o[D18OSW_STR].attrs['long_name'] = 'seawater d18O'
r18o[D18OSW_STR].attrs['units'] = 'permil'
# Dump to file
r18o[[D18OSW_STR]].to_netcdf(D18OSW_OUT)
r18o.close()

