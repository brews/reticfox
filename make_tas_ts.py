# Parse iCESM to get ts and tas netcdf files.
# Should have TS and TREFHT files in pwd.

import os
import xarray as xr

# Use globus to load needed files from NCAR. Assumes you ran `globus login` from shell before:
NCAR_DOWNLOAD = True  
CASENAME = 'b.e12.B1850C5.f19_g16.i21ka.03'
OUT_DIR = '.'
TS_STR = 'ts'
IN_TS = '{}.cam.h0.TS.0001-0900.nc'.format(CASENAME)
OUT_TS = '{}.cam.h0.{}.nc'.format(CASENAME, TS_STR)
TAS_STR = 'tas'
IN_TAS = '{}.cam.h0.TREFHT.0001-0900.nc'.format(CASENAME)
OUT_TAS = '{}.cam.h0.{}.nc'.format(CASENAME, TAS_STR)


if NCAR_DOWNLOAD:
    import globus_icesm

    variables = ['TS',
                 'TREFHT',
                ]
    from_template = '/gpfs/csfs1/univ/uazn0013/jiangzhu/archive/{}/atm/proc/tseries/monthly/{}/'
    to_d = '.'

    for variable in variables:
        from_d = from_template.format(CASENAME, variable)
        globus_icesm.transfer(from_dir=from_d, to_dir=to_d)



x = xr.open_dataset(IN_TS)
x[TS_STR] = x['TS']
x[[TS_STR]].to_netcdf(os.path.join(OUT_DIR, OUT_TS))

x = xr.open_dataset(IN_TAS)
x[TAS_STR] = x['TREFHT']
x[[TAS_STR]].to_netcdf(os.path.join(OUT_DIR, OUT_TAS))
