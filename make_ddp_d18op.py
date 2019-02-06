# Parse Deuterium (δD; precip) and d18O (precip) from iCESM cam experiment 
# slice output. Assumes raw NetCDF files (below) are in the pwd.

import os
import xarray as xr


CASENAME = 'b.e12.B1850C5.f19_g16.i21ka.03'
OUT_DIR = '.'
D18OP_STR = 'd18op'
D18OP_OUT = '{}.cam.h0.{}.nc'.format(CASENAME, D18OP_STR)
DDP_STR = 'ddp'
DDP_OUT = '{}.cam.h0.{}.nc'.format(CASENAME, DDP_STR)
H218O_IN = ['{}.cam.h0.PRECRC_H218Or.0001-0900.nc',
            '{}.cam.h0.PRECRL_H218OR.0001-0900.nc',
            '{}.cam.h0.PRECSC_H218Os.0001-0900.nc',
            '{}.cam.h0.PRECSL_H218OS.0001-0900.nc',
]
H216O_IN = ['{}.cam.h0.PRECRC_H216Or.0001-0900.nc',
            '{}.cam.h0.PRECRL_H216OR.0001-0900.nc',
            '{}.cam.h0.PRECSC_H216Os.0001-0900.nc',
            '{}.cam.h0.PRECSL_H216OS.0001-0900.nc',
]
H2O_IN = ['{}.cam.h0.PRECRC_H2Or.0001-0900.nc',
          '{}.cam.h0.PRECRL_H2OR.0001-0900.nc',
          '{}.cam.h0.PRECSC_H2Os.0001-0900.nc',
          '{}.cam.h0.PRECSL_H2OS.0001-0900.nc',
]
HDO_IN = ['{}.cam.h0.PRECRC_HDOr.0001-0900.nc',
          '{}.cam.h0.PRECRL_HDOR.0001-0900.nc',
          '{}.cam.h0.PRECSC_HDOs.0001-0900.nc',
          '{}.cam.h0.PRECSL_HDOS.0001-0900.nc',
]

# Add casename to input
H218O_IN = [x.format(CASENAME) for x in H218O_IN]
H216O_IN = [x.format(CASENAME) for x in H216O_IN]
H2O_IN = [x.format(CASENAME) for x in H2O_IN]
HDO_IN = [x.format(CASENAME) for x in HDO_IN]

ptiny = 1e-18


# First, deal with d18op
h21xo = xr.open_mfdataset(H218O_IN + H216O_IN)
# Combine parts
h21xo['p18o'] = h21xo.PRECRC_H218Or + h21xo.PRECRL_H218OR + h21xo.PRECSC_H218Os + h21xo.PRECSL_H218OS
h21xo['p16o'] = h21xo.PRECRC_H216Or + h21xo.PRECRL_H216OR + h21xo.PRECSC_H216Os + h21xo.PRECSL_H216OS
h21xo['p16o'] = xr.where(h21xo['p16o'] < ptiny, h21xo['p16o'], ptiny)
h21xo[D18OP_STR] = (h21xo['p18o'] / h21xo['p16o'] - 1.0) * 1000.0
# Metadata
h21xo[D18OP_STR].attrs['long_name'] = 'precipitation d18O'
h21xo[D18OP_STR].attrs['units'] = 'permil'
# Dump to file
h21xo[[D18OP_STR]].to_netcdf(os.path.join(OUT_DIR, D18OP_OUT))
h21xo.close()

# Now for Deuterium (dD)
hxo = xr.open_mfdataset(H2O_IN + HDO_IN)
hxo['ph2o'] = hxo.PRECRC_H2Or + hxo.PRECRL_H2OR + hxo.PRECSC_H2Os + hxo.PRECSL_H2OS
hxo['phdo'] = hxo.PRECRC_HDOr + hxo.PRECRL_HDOR + hxo.PRECSC_HDOs + hxo.PRECSL_HDOS
hxo['ph2o'] = xr.where(hxo['ph2o'] < ptiny, hxo['ph2o'], ptiny)
hxo[DDP_STR] = (hxo['phdo'] / hxo['ph2o'] - 1.0) * 1000.0
# Metadata
hxo[DDP_STR].attrs['long_name'] = 'precipitation dD'
hxo[DDP_STR].attrs['units'] = 'permil'
# Dump to file
hxo[[DDP_STR]].to_netcdf(os.path.join(OUT_DIR, DDP_OUT))
hxo.close()

