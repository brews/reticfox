# Write 'pr' (precipitaiton) variable from iCESM time slice processed output.
# This needs to be in the same directory as NetCDF CAM files for PRECC, PRECL, PRECSC, PRECSL.

import os
import xarray as xr


# Use globus to load needed files from NCAR. Assumes you ran `globus login` from shell before:
NCAR_DOWNLOAD = True  
CASENAME = 'b.e12.B1850C5.f19_g16.i21ka.03'
OUT_DIR = '.'
PR_STR = 'pr'
IN_PRE = ['{}.cam.h0.PRECC.0001-0900.nc',
          '{}.cam.h0.PRECL.0001-0900.nc',
          '{}.cam.h0.PRECSC.0001-0900.nc',
          '{}.cam.h0.PRECSL.0001-0900.nc',
          ]
OUT_FILE = '{}.cam.h0.{}.nc'.format(CASENAME, PR_STR)

IN_PRE = [x.format(CASENAME) for x in IN_PRE]


if NCAR_DOWNLOAD:
    import globus_icesm

    variables = ['PRECRC',
                 'PRECRL',
                 'PRECSC',
                 'PRECSL',
                ]
    from_template = '/gpfs/csfs1/univ/uazn0013/jiangzhu/archive/{}/cam/proc/tseries/monthly/{}/'
    to_d = '.'

    for variable in variables:
        from_d = from_template.format(CASENAME, variable)
        globus_icesm.transfer(from_dir=from_d, to_dir=to_d)


pre = xr.open_mfdataset(IN_PRE)
pre[PR_STR] = pre['PRECC'] + pre['PRECL'] + pre['PRECSC'] + pre['PRECSL'] 
pre[[PR_STR]].to_netcdf(os.path.join(OUT_DIR, OUT_FILE))
