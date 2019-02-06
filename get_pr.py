# Write 'pr' (precipitaiton) variable from iCESM time slice processed output.
# This needs to be in the same directory as NetCDF CAM files for PRECC, PRECL, PRECSC, PRECSL.

import xarray as xr


PR_STR = 'pr'
IN_PRE = ['b.e12.B1850C5.f19_g16.i21ka.03.cam.h0.PRECC.0001-0900.nc',
          'b.e12.B1850C5.f19_g16.i21ka.03.cam.h0.PRECL.0001-0900.nc',
          'b.e12.B1850C5.f19_g16.i21ka.03.cam.h0.PRECSC.0001-0900.nc',
          'b.e12.B1850C5.f19_g16.i21ka.03.cam.h0.PRECSL.0001-0900.nc',
          ]
OUT_FILE = 'b.e12.B1850C5.f19_g16.i21ka.03.cam.h0.{}.nc'.format(PR_STR)


pre = xr.open_mfdataset(IN_PRE)
pre[PR_STR] = pre['PRECC'] + pre['PRECL'] + pre['PRECSC'] + pre['PRECSL'] 
pre[[PR_STR]].to_netcdf(OUT_FILE)
