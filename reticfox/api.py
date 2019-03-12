import logging
import numpy as np
import scipy.stats as stats
import xarray as xr
import gsw


log = logging.getLogger(__name__)


def pot2insitu_temp(theta, salt, insitu_temp_name='insitu_temp'):
    """Get insitu temp DataArray from potential temperature (theta) and salinity (salt) dataset
    """
    # Convert depth (cm) to (m) & positive up.
    # sea pressure (dbar) from depth (m), note it needs latitude as input,
    # unlike ferret and NCL functions.
    p = xr.apply_ufunc(gsw.p_from_z, -theta.z_t * 0.01, theta.TLAT,
                       output_dtypes=['float32'], dask='parallelized')

    insitu_temp = xr.apply_ufunc(gsw.pt_from_t, salt.SALT, theta.TEMP, np.array([0]), p,
                                 output_dtypes=['float32'], dask='parallelized')

    # Add metadata attributes.
    insitu_temp.name = str(insitu_temp_name)
    insitu_temp.attrs['units'] = 'degC'
    insitu_temp.attrs['long_name'] = 'Sea Temperature (In-situ Temperature)'
    return insitu_temp


def tex86_gammaavg_depth(ds, target_var='TEMP'):
    """Return gamma-average DataArray of input temperature Dataset (ds)
    """
    gamma_a = 4.5
    # Original spec from Tierney paper was in m, depth in CCSM and CESM is in cm, so * 100:
    gamma_b = 15.0 * 100

    # # If you want to see plot of gamma weights over depth.
    # ideal_depths = np.arange(0, 22510, 10)  # in cm
    # gamma_pdf = stats.gamma.pdf(ideal_depths, a=GAMMA_A, scale=GAMMA_B)
    # plt.plot(ideal_depths, gamma_pdf);plt.xlabel('depth (cm)');plt.show()

    # Diff of CDF between bottom of depth "bin" and top of depth "bin". - i.e.
    # the gamma distribution mass within the depth "bin". We're using DataArrays
    # with depth index to ensure this compares apples to apples along depth.
    shallow_cdf = xr.DataArray(stats.gamma.cdf(ds.z_w_top, gamma_a, scale=gamma_b),
                               coords=[ds.z_t], dims=['z_t'])
    deep_cdf = xr.DataArray(stats.gamma.cdf(ds.z_w_bot, gamma_a, scale=gamma_b),
                            coords=[ds.z_t], dims=['z_t'])
    gamma_weights = deep_cdf - shallow_cdf
    # Can see weights with `gamma_weights.plot()`

    # gamma_weights /= gamma_weights.sum()  # Normalize, no - not like this... <-
    # Normalize, careful to consider grid points with missing depth values:
    gamma_weights_norm = gamma_weights / \
        (ds[target_var].notnull() * gamma_weights).sum('z_t')
    temp_gamma_avg = (
        ds[target_var] * gamma_weights_norm).sum(dim='z_t').astype('float32')

    # Add metadata attributes.
    temp_gamma_avg.attrs['units'] = 'degC'
    temp_gamma_avg.attrs['long_name'] = 'Sea Temperature (Gamma-average)'

    return temp_gamma_avg
