# Parse iCESM to get ts and tas netcdf files.
# Should have TS and TREFHT files in pwd.

import xarray as xr


TS_STR = 'ts'
IN_TS = 'b.e12.B1850C5.f19_g16.i21ka.03.cam.h0.TS.0001-0900.nc'
OUT_TS = 'b.e12.B1850C5.f19_g16.i21ka.03.cam.h0.ts.nc'

TAS_STR = 'tas'
IN_TAS = 'b.e12.B1850C5.f19_g16.i21ka.03.cam.h0.TREFHT.0001-0900.nc'
OUT_TAS = 'b.e12.B1850C5.f19_g16.i21ka.03.cam.h0.tas.nc'


x = xr.open_dataset(IN_TS)
x[TS_STR] = x['TS']
x[[TS_STR]].to_netcdf(OUT_TS)

x = xr.open_dataset(IN_TAS)
x[TAS_STR] = x['TREFHT']
x[[TAS_STR]].to_netcdf(OUT_TAS)
