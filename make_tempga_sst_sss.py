# Parse TEMP and SALT from iCESM cam experiment slice NetCDF files.
# Can run from Bash with:
#
# python make_tempga_sst_sss.py \
#   --temp_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.TEMP.*.nc \
#   --salt_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.SALT.*.nc \
#   --tempga_str tempga \
#   --tos_str tos \
#   --sos_str sos \
#   --tempga_outfl /rsgrps/jesst/icesm/b.e12.B1850C5.f19_g16.i21ka.03.pop.h.tempga.nc
#   --tos_outfl /rsgrps/jesst/icesm/b.e12.B1850C5.f19_g16.i21ka.03.pop.h.tos.nc
#   --sos_outfl /rsgrps/jesst/icesm/b.e12.B1850C5.f19_g16.i21ka.03.pop.h.sos.nc
#
# See help with `python make_tempga_sst_sss.py --help`.

from glob import glob
import logging
import argparse
import numpy as np
import scipy.stats as stats
import xarray as xr
import gsw


log = logging.getLogger(__name__)


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
                                         theta.TEMP.values[~isnan_msk], np.array([
                                                                                 0]),
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
    temp_gamma_avg = (ds[target_var] * gamma_weights_norm).sum(dim='z_t')
    # Boom. `temp_gamma_avg` should be it. You can write to netcdf with
    # `temp_gamma_avg.to_netcdf('filename.nc')`

    # Put nans where the top of the original dataarray had nans.
    isnan_msk = ds[target_var].isel(z_t=0).isnull()
    temp_gamma_avg.values[isnan_msk] = np.nan
    return temp_gamma_avg


def parse_icesm(temp_glob, salt_glob, tempga_str, tos_str, sos_str, tempga_outfl, tos_outfl, sos_outfl):
    """Parse POP TEMP and SALT iCESM NetCDF files
    """
    log.debug('working temp files in glob {}'.format(temp_glob))
    log.debug('working salt files in glob {}'.format(salt_glob))

    cutoff_z = 25000

    theta = xr.open_mfdataset(temp_glob).sel(
        z_t=slice(0, cutoff_z)).sortby('time')
    salt = xr.open_mfdataset(salt_glob).sel(
        z_t=slice(0, cutoff_z)).sortby('time')

    # Because using z_t slice doesn't get z_w which has depth layers' bounds.
    theta = theta.sel(z_w_bot=slice(0, cutoff_z))
    theta = theta.isel(z_w=slice(0, len(theta.z_w_bot)))
    theta = theta.isel(z_w_top=slice(0, len(theta.z_w_bot)))

    # First get in-situ temps from potential temps (TEMP), add to theta
    theta = pot2insitu_temp(theta, salt, insitu_temp_name=tos_str)
    # get gamma average, add to theta
    ga = tex86_gammaavg_depth(theta, target_var=tos_str)
    ga.name = tempga_str
    theta[tempga_str] = ga
    theta[tempga_str].attrs['units'] = 'degC'
    theta[tempga_str].attrs['long_name'] = 'Sea Temperature (Gamma-average)'

    # Write ~SST file
    theta[[tos_str, 'time_bnds']].isel(z_t=0).to_netcdf(tos_outfl)

    # Write gamma-average file
    theta[[tempga_str, 'time_bnds']].to_netcdf(tempga_outfl)

    # Write ~SSS file
    salt[sos_str] = salt['SALT'].isel(z_t=0)
    salt[[sos_str, 'time_bnds']].to_netcdf(sos_outfl)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse POP TEMP, SALT from iCESM output')
    parser.add_argument('--temp_glob', metavar='TEMPGLOB', nargs=1,
                        help='glob pattern to input POP TEMP NetCDF files')
    parser.add_argument('--salt_glob', metavar='SALTGLOB', nargs=1,
                        help='glob pattern to input POP SALT NetCDF files')

    parser.add_argument('--tempga_str', metavar='TEMPGASTR', nargs=1,
                        default=['tempga'],
                        help='variable name in output NetCDF file')
    parser.add_argument('--tos_str', metavar='TOSSTR', nargs=1,
                        default=['tos'],
                        help='variable name in output NetCDF file')
    parser.add_argument('--sos_str', metavar='SOSSTR', nargs=1,
                        default=['sos'],
                        help='variable name in output NetCDF file')

    parser.add_argument('--outfl_tempga', metavar='OUTFLTEMPGA', nargs=1,
                        help='path for output NetCDF file')
    parser.add_argument('--outfl_tos', metavar='OUTFLTOS', nargs=1,
                        help='path for output NetCDF file')
    parser.add_argument('--outfl_sos', metavar='OUTFLSOS', nargs=1,
                        help='path for output NetCDF file')

    parser.add_argument('--log', metavar='LOGPATH', nargs=1, default=[None],
                        help='optional path to write log file to')
    args = parser.parse_args()

    if args.log[0] is not None:
        logging.basicConfig(level=logging.DEBUG,
                            filename=args.log[0],
                            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    parse_icesm(temp_glob=str(args.temp_glob[0]),
                salt_glob=str(args.salt_glob[0]),
                tempga_str=str(args.tempga_str[0]),
                tos_str=str(args.tos_str[0]),
                sos_str=str(args.sos_str[0]),
                tempga_outfl=str(args.tempga_outfl[0]),
                tos_outfl=str(args.tos_outfl[0]),
                sos_outfl=str(args.sos_outfl[0]))
