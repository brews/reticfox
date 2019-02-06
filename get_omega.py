# Read iCESM experient slice for CAM omega and output omega at certain geopotenial height level.
# Assumes that OMEGA and PS files are available in cwd. This script interpolates
# CAM hybrid levels to pressure levels.


import xarray as xr
import Ngl

OMEGA_STR = 'omega500'
OUT_NC = 'b.e12.B1850C5.f19_g16.i21ka.03.cam.h0.omega500.nc'
PS_IN = 'b.e12.B1850C5.f19_g16.i21ka.03.cam.h0.PS.0001-0900.nc'
OMEGA_IN = 'b.e12.B1850C5.f19_g16.i21ka.03.cam.h0.OMEGA.0001-0900.nc'
TARGET_HGTS = [500.0]

ps = xr.open_dataset(PS_IN)
omega = xr.open_dataset(OMEGA_IN)

omega500 = Ngl.vinth2p(omega.OMEGA.values, omega.hyam.values, omega.hybm.values, TARGET_HGTS, ps.PS.values, 1, 1000.0, 1, True)

# Setup pressure coordinates
omega.coords['plev'] = ('plev', TARGET_HGTS)
omega.coords['plev'].attrs['positive'] = 'down'
omega.coords['plev'].attrs['long_name'] = 'pressure level'
omega.coords['plev'].attrs['units'] = 'hPa'

# Add new interpolated omega to dataset and write variable to NetCDF
omega[OMEGA_STR] = (('time', 'plev', 'lat', 'lon'), omega500)
omega[OMEGA_STR].attrs['units'] = 'Pa/s'
omega[OMEGA_STR].attrs['long_name'] = 'Vertical velocity (pressure)'
omega[[OMEGA_STR]].to_netcdf(OUT_NC)
