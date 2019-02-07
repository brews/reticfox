# Parse Deuterium (δD; precip) and d18O (precip) from iCESM cam experiment 
# slice output. Assumes raw NetCDF files (below) are in the pwd.

import os
import xarray as xr


# Use globus to load needed files from NCAR. Assumes you ran `globus login` from shell before:
NCAR_DOWNLOAD = True  
CASENAME = 'b.e12.B1850C5.f19_g16.i21ka.03'
OUT_DIR = '.'
D18OSW_STR = 'd18osw'
D18OSW_OUT = '{}.pop.h.{}.nc'.format(CASENAME, D18OSW_STR)
R18O_BLOB = '{}.pop.h.R18O.*.nc'.format(CASENAME)


if NCAR_DOWNLOAD:
    import globus_icesm
    
    from_template = '/gpfs/csfs1/univ/uazn0013/jiangzhu/archive/{}/ocn/proc/tseries/monthly/R18O/'
    from_d = from_template.format(CASENAME)
    to_d = '.'
    globus_icesm.transfer(from_dir=from_d, to_dir=to_d)


# First, deal with d18op
r18o = xr.open_mfdataset(R18O_BLOB).isel(z_t=0).sortby('time')
r18o[D18OSW_STR] = (r18o['R18O'] - 1.0) * 1000.0
# Metadata
r18o[D18OSW_STR].attrs['long_name'] = 'seawater d18O'
r18o[D18OSW_STR].attrs['units'] = 'permil'
# Dump to file
r18o[[D18OSW_STR]].to_netcdf(os.path.join(OUT_DIR, D18OSW_OUT))
r18o.close()

