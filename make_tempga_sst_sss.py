# Make TEMPGA, SST, SSS netCDF from monthly iCESM TEMP, SALT netCDFs.

import os
from glob import glob
import numpy as np
import scipy.stats as stats
import xarray as xr
import gsw


# Use globus to load needed files from NCAR. Assumes you ran `globus login` from shell before:
NCAR_DOWNLOAD = True  
CASENAME = 'b.e12.B1850C5.f19_g16.i21ka.03'
OUT_DIR = '.'
TEMP_GLOB_PATTERN = '{}.pop.h.TEMP.*.nc'.format(CASENAME)
INSITU_TEMP_STR = 'tos'
GAMMA_TEMP_STR = 'toGA'
SSS_STR = 'sos'
SSS_OUT = '{}.pop.h.{}.nc'.format(CASENAME, SSS_STR)
GAMMA_TEMP_OUT = '{}.pop.h.{}.nc'.format(CASENAME, GAMMA_TEMP_STR)
INSITU_TEMP_OUT = '{}.pop.h.{}.nc'.format(CASENAME, INSITU_TEMP_STR)
CUTOFF_Z = 25000  # Depth in cm. Selecting by z_t also keeps z_w_bot below the CUTOFF_Z too, in this case.


if NCAR_DOWNLOAD:
    import globus_icesm

    variables = ['TEMP',
                 'SALT',
                ]
    from_template = '/gpfs/csfs1/univ/uazn0013/jiangzhu/archive/{}/ocn/proc/tseries/monthly/{}/'
    to_d = '.'

    for variable in variables:
        from_d = from_template.format(CASENAME, variable)
        globus_icesm.transfer(from_dir=from_d, to_dir=to_d)


def pot2insitu_temp(theta, salt, insitu_temp_name='insitu_temp'):
    """Add 'insitu-temp' variable to potential temperature (theta) and salinity (salt) dataset
    """ 
    # Convert depth (cm) to (m) & positive up.
    z_m = -theta.z_t.values * 0.01

    # sea pressure (dbar) from depth (m), note it needs latitude as input,
    # unlike ferret and NCL functions.
    latlon_shape = theta.TEMP.shape[-2:]
    n_depth = len(theta.TEMP.z_t)
    p = gsw.p_from_z(np.tile(z_m, (*latlon_shape[::-1], 1)).T,
                     np.tile(theta.TLAT, (n_depth, 1, 1)))


    # Using nan mask and broadcasting to work around missing values.
    # I think this will be more memory efficient than proper masked arrays.
    isnan_msk = np.isnan(salt.SALT)
    t_insitu = np.empty(theta.TEMP.shape)
    t_insitu[~isnan_msk] = gsw.pt_from_t(salt.SALT.values[~isnan_msk], 
                                         theta.TEMP.values[~isnan_msk], np.array([0]), 
                                         np.broadcast_to(p, salt.SALT.shape)[~isnan_msk])
    t_insitu[isnan_msk] = np.nan

    # Assign back to xarray dataset with some metadata attribs.
    theta[insitu_temp_name] = (theta.TEMP.dims, t_insitu)
    # theta['t_insitu'] = (theta.TEMP.dims, np.empty(theta.TEMP.shape))
    # Add attribute to set long_name and units.
    theta[insitu_temp_name].attrs['units'] = 'degC'
    theta[insitu_temp_name].attrs['long_name'] = 'Sea Temperature (In-situ Temperature)'
    return theta


def tex86_gammaavg_depth(ds, target_var='TEMP'):
    """Return gamma-average DataArray of input temperature Dataset (ds)
    """
    GAMMA_A = 4.5
    # Original spec from Tierney paper was in m, depth in CCSM and CESM is in cm, so * 100:
    GAMMA_B = 15.0 * 100

    # # If you want to see plot of gamma weights over depth.
    # ideal_depths = np.arange(0, 22510, 10)  # in cm
    # gamma_pdf = stats.gamma.pdf(ideal_depths, a=GAMMA_A, scale=GAMMA_B)
    # plt.plot(ideal_depths, gamma_pdf);plt.xlabel('depth (cm)');plt.show()  

    # Diff of CDF between bottom of depth "bin" and top of depth "bin". - i.e. 
    # the gamma distribution mass within the depth "bin". We're using DataArrays 
    # with depth index to ensure this compares apples to apples along depth.
    shallow_cdf = xr.DataArray(stats.gamma.cdf(ds.z_w_top, GAMMA_A, scale=GAMMA_B), 
                               coords=[ds.z_t], dims=['z_t'])
    deep_cdf = xr.DataArray(stats.gamma.cdf(ds.z_w_bot, GAMMA_A, scale=GAMMA_B), 
                            coords=[ds.z_t], dims=['z_t'])
    gamma_weights = deep_cdf - shallow_cdf
    # Can see weights with `gamma_weights.plot()`

    # gamma_weights /= gamma_weights.sum()  # Normalize, no - not like this... <-
    # Normalize, careful to consider grid points with missing depth values:
    gamma_weights_norm = gamma_weights / (ds[target_var].notnull() * gamma_weights).sum('z_t') 
    temp_gamma_avg = (ds[target_var] * gamma_weights_norm).sum(dim='z_t')
    # Boom. `temp_gamma_avg` should be it. You can write to netcdf with 
    # `temp_gamma_avg.to_netcdf('filename.nc')`

    # Put nans where the top of the original dataarray had nans.
    isnan_msk = ds[target_var].isel(z_t=0).isnull() 
    temp_gamma_avg.values[isnan_msk] = np.nan
    return temp_gamma_avg


gamma_temp_files = []
sst_files = []
sss_files = []
tempfiles = glob(TEMP_GLOB_PATTERN)
for tfl in tempfiles:
    out_template = tfl.replace('.TEMP.', '.{}.') 
    sfl = tfl.replace('.TEMP.', '.SALT.')
    theta = xr.open_dataset(tfl).sel(z_t=slice(0, CUTOFF_Z))
    salt = xr.open_dataset(sfl).sel(z_t=slice(0, CUTOFF_Z))
    # Because using z_t slice doesn't get z_w which has depth layers' bounds.
    theta = theta.sel(z_w_bot=slice(0, CUTOFF_Z))
    theta = theta.isel(z_w=slice(0, len(theta.z_w_bot)))
    theta = theta.isel(z_w_top=slice(0, len(theta.z_w_bot)))

    # First get in-situ temps from potential temps (TEMP), add to theta
    theta = pot2insitu_temp(theta, salt, insitu_temp_name=INSITU_TEMP_STR)
    # get gamma average, add to theta
    ga = tex86_gammaavg_depth(theta, target_var=INSITU_TEMP_STR)
    ga.name = GAMMA_TEMP_STR
    theta[GAMMA_TEMP_STR] = ga
    theta[GAMMA_TEMP_STR].attrs['units'] = 'degC'
    theta[GAMMA_TEMP_STR].attrs['long_name'] = 'Sea Temperature (Gamma-average)'

    # Write insitu SST.
    outfl = out_template.format(INSITU_TEMP_STR)
    theta[[INSITU_TEMP_STR]].isel(z_t=0).to_netcdf(outfl)
    sst_files.append(outfl)

    # Write gamma-average insitu sea temperature.
    outfl = out_template.format(GAMMA_TEMP_STR)
    theta[[GAMMA_TEMP_STR]].to_netcdf(outfl)
    gamma_temp_files.append(outfl)

    # Write SSS.
    outfl = out_template.format(SSS_STR)
    salt[SSS_STR] = salt['SALT'].isel(z_t=0)
    salt[[SSS_STR]].to_netcdf(outfl)
    sss_files.append(outfl)

# Now combine the multiple files of same variable, condense to single NetCDF.
# The diff files represent different times.
outfl_ncs = [(GAMMA_TEMP_OUT, gamma_temp_files), (INSITU_TEMP_OUT, sst_files), (SSS_OUT, sss_files)]
for fl_name, var_files in outfl_ncs:
    var_files.sort()
    # Open multiple files and write to `fl_name`.
    ds = xr.open_mfdataset(var_files)
    ds = ds.sortby('time')
    ds.to_netcdf(fl_name)
