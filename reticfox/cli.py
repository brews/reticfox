import click
from glob import glob
import xarray as xr
import Ngl
import reticfox.api as api


# Main entry point
@click.group(context_settings={'help_option_names': ['-h', '--help']})
def reticfox_cli():
    """Parse LGM iCESM processed netCDF files"""


@reticfox_cli.command(help='Parse d18O (precip) from iCESM output')
@click.option('--precrc_h216o_glob', help='Glob pattern to input CAM PRECRC_H216Or NetCDF files.')
@click.option('--precrl_h216o_glob', help='Glob pattern to input CAM PRECRL_H216OR NetCDF files.')
@click.option('--precsc_h216o_glob', help='Glob pattern to input CAM PRECSC_H216Os NetCDF files.')
@click.option('--precsl_h216o_glob', help='Glob pattern to input CAM PRECSL_H216OS NetCDF files.')
@click.option('--precrc_h218o_glob', help='Glob pattern to input CAM PRECRL_H218Or NetCDF files.')
@click.option('--precrl_h218o_glob', help='Glob pattern to input CAM PRECRL_H218OR NetCDF files.')
@click.option('--precsc_h218o_glob', help='Glob pattern to input CAM PRECSC_H218Os NetCDF files.')
@click.option('--precsl_h218o_glob', help='Glob pattern to input CAM PRECSL_H218OS NetCDF files.')
@click.option('--d18op_str', default='d18op', help='Variable name in output NetCDF file.')
@click.option('--outfl', help='Path for output NetCDF file.')
def make_d18op(precrc_h216o_glob, precrl_h216o_glob, precsc_h216o_glob, precsl_h216o_glob,
               precrc_h218o_glob, precrl_h218o_glob, precsc_h218o_glob, precsl_h218o_glob,
               d18op_str, outfl=None):
    """Parse CAM PRE*_H216O* and PRE*_H218O* iCESM netCDF files and write δ18O to outfl.
    """
    ptiny = 1e-18

    globs = [precrc_h216o_glob, precrl_h216o_glob, precsc_h216o_glob, precsl_h216o_glob,
             precrc_h218o_glob, precrl_h218o_glob, precsc_h218o_glob, precsl_h218o_glob]
    # log.debug('working precip d18O files in globs {}'.format(globs))

    matched_files = []
    for g in globs:
        for match in glob(g):
            matched_files.append(match)

    h21xo = xr.open_mfdataset(matched_files).sortby('time')

    # Combine parts
    h21xo['p18o'] = h21xo.PRECRC_H218Or + h21xo.PRECRL_H218OR + \
        h21xo.PRECSC_H218Os + h21xo.PRECSL_H218OS
    h21xo['p16o'] = h21xo.PRECRC_H216Or + h21xo.PRECRL_H216OR + \
        h21xo.PRECSC_H216Os + h21xo.PRECSL_H216OS
    h21xo['p16o'] = xr.where(h21xo['p16o'] > ptiny, h21xo['p16o'], ptiny)
    h21xo[d18op_str] = (h21xo['p18o'] / h21xo['p16o'] - 1.0) * 1000.0

    # Metadata
    h21xo[d18op_str].attrs['long_name'] = 'precipitation d18O'
    h21xo[d18op_str].attrs['units'] = 'permil'

    out = h21xo[[d18op_str, 'time_bnds']]
    if outfl is not None:
        # Dump to file
        # log.debug('Writing variable {} to {}'.format(d18op_str, outfl))
        out.to_netcdf(outfl, format='NETCDF4', engine='netcdf4')
    return out


@reticfox_cli.command(help='Parse delta D (precip) from iCESM output')
@click.option('--precrc_h2o_glob', help='Glob pattern to input CAM PRECRC_H2Or NetCDF files.')
@click.option('--precrl_h2o_glob', help='Glob pattern to input CAM PRECRL_H2OR NetCDF files.')
@click.option('--precsc_h2o_glob', help='Glob pattern to input CAM PRECSC_H2Os NetCDF files.')
@click.option('--precsl_h2o_glob', help='Glob pattern to input CAM PRECSL_H2OS NetCDF files.')
@click.option('--precrc_hdo_glob', help='Glob pattern to input CAM PRECRC_HDOr NetCDF files.')
@click.option('--precrl_hdo_glob', help='Glob pattern to input CAM PRECRL_HDOR NetCDF files.')
@click.option('--precsc_hdo_glob', help='Glob pattern to input CAM PRECSC_HDOs NetCDF files.')
@click.option('--precsl_hdo_glob', help='Glob pattern to input CAM PRECSL_HDOS NetCDF files.')
@click.option('--ddp_str', default='ddp', help='Variable name in output NetCDF file.')
@click.option('--outfl', help='Path for output NetCDF file.')
def make_ddp(precrc_h2o_glob, precrl_h2o_glob, precsc_h2o_glob, precsl_h2o_glob,
             precrc_hdo_glob, precrl_hdo_glob, precsc_hdo_glob, precsl_hdo_glob,
             ddp_str, outfl=None):
    """Parse CAM PRE*_HDO* and PRE*_H2O* iCESM netCDF files and write δD to outfl.
    """
    ptiny = 1e-18

    globs = [precrc_h2o_glob, precrl_h2o_glob, precsc_h2o_glob, precsl_h2o_glob,
             precrc_hdo_glob, precrl_hdo_glob, precsc_hdo_glob, precsl_hdo_glob]
    # log.debug('working precip deuterium files in globs {}'.format(globs))

    matched_files = []
    for g in globs:
        for match in glob(g):
            matched_files.append(match)

    hxo = xr.open_mfdataset(matched_files).sortby('time')

    # Combine parts
    hxo['ph2o'] = hxo.PRECRC_H2Or + hxo.PRECRL_H2OR + \
        hxo.PRECSC_H2Os + hxo.PRECSL_H2OS
    hxo['phdo'] = hxo.PRECRC_HDOr + hxo.PRECRL_HDOR + \
        hxo.PRECSC_HDOs + hxo.PRECSL_HDOS
    hxo['ph2o'] = xr.where(hxo['ph2o'] > ptiny, hxo['ph2o'], ptiny)
    hxo[ddp_str] = (hxo['phdo'] / hxo['ph2o'] - 1.0) * 1000.0

    # Metadata
    hxo[ddp_str].attrs['long_name'] = 'precipitation dD'
    hxo[ddp_str].attrs['units'] = 'permil'

    out = hxo[[ddp_str, 'time_bnds']]
    if outfl is not None:
        # Dump to file
        # log.debug('Writing variable {} to {}'.format(ddp_str, outfl))
        out.to_netcdf(outfl, format='NETCDF4', engine='netcdf4')
    return out


@reticfox_cli.command(help='Parse CAM OMEGA from iCESM output')
@click.option('--omega_glob', help='Glob pattern to input CAM OMEGA NetCDF files.')
@click.option('--ps_glob', help='Glob pattern to input CAM PS NetCDF files.')
@click.option('--omega_str', default='omega', help='Variable name in output NetCDF file.')
@click.option('--outfl', help='Path for output NetCDF file.')
@click.option('--levels', default=None, help='Pressure levels to interpolate omega to.')
def make_omega(omega_glob, ps_glob, omega_str, outfl=None, levels=None):
    """Parse CAM omega iCESM netCDF files and write to outfl.
    """
    # log.debug('working omega files in glob {}'.format(omega_glob))
    if levels is None:
        levels = [500.0]

    ps = xr.open_mfdataset(ps_glob).sortby('time')
    omega = xr.open_mfdataset(omega_glob).sortby('time')

    omega500 = Ngl.vinth2p(omega.OMEGA.values, omega.hyam.values, omega.hybm.values,
                           levels, ps.PS.values, 1, 1000.0, 1, True)

    # Setup pressure coordinates
    omega.coords['plev'] = ('plev', levels)
    omega.coords['plev'].attrs['positive'] = 'down'
    omega.coords['plev'].attrs['long_name'] = 'pressure level'
    omega.coords['plev'].attrs['units'] = 'hPa'

    # Add new interpolated omega to dataset and write variable to NetCDF
    omega[omega_str] = (('time', 'plev', 'lat', 'lon'), omega500)
    omega[omega_str].attrs['units'] = 'Pa/s'
    omega[omega_str].attrs['long_name'] = 'Vertical velocity (pressure)'

    out = omega[[omega_str, 'time_bnds']]
    out[omega_str] = out[omega_str].astype('float32')
    if outfl is not None:
        # Dump to file
        # log.debug('Writing variable {} to {}'.format(omega_str, outfl))
        out.to_netcdf(outfl, format='NETCDF4', engine='netcdf4')
    return out


@reticfox_cli.command(help='Parse pr from iCESM output')
@click.option('--precc_glob', help='Glob pattern to input CAM PRECRC NetCDF files.')
@click.option('--precl_glob', help='Glob pattern to input CAM PRECRL NetCDF files.')
@click.option('--pr_str', default='pr', help='Variable name in output NetCDF file.')
@click.option('--outfl', help='Path for output NetCDF file.')
def make_pr(precc_glob, precl_glob, pr_str, outfl=None):
    """Parse CAM PREC* iCESM netCDF files and write to outfl.
    """
    globs = [precc_glob, precl_glob]
    # log.debug('working precip files in glob {}'.format(globs))

    matched_files = []
    for g in globs:
        for match in glob(g):
            matched_files.append(match)

    pre = xr.open_mfdataset(matched_files).sortby('time')

    # Combine parts
    pre[pr_str] = pre['PRECC'] + pre['PRECL']

    # Metadata
    pre[pr_str].attrs['long_name'] = 'total precipitation rate'
    pre[pr_str].attrs['units'] = 'm/s'

    out = pre[[pr_str, 'time_bnds']]
    if outfl is not None:
        # log.debug('Writing variable {} to {}'.format(pr_str, outfl))
        out.to_netcdf(outfl, format='NETCDF4', engine='netcdf4')
    return out


@reticfox_cli.command(help='Parse TREFHT from iCESM output')
@click.option('--trefht_glob', help='Glob pattern to input CAM TREFHT NetCDF files.')
@click.option('--tas_str', default='tas', help='Variable name in output NetCDF file.')
@click.option('--outfl', help='Path for output NetCDF file.')
def make_tas(trefht_glob, tas_str, outfl=None):
    """Parse CAM tas iCESM NetCDF files and write to outfl.
    """
    # log.debug('working trefht files in glob {}'.format(trefht_glob))
    x = xr.open_mfdataset(trefht_glob).sortby('time')
    x[tas_str] = x['TREFHT']

    out = x[[tas_str, 'time_bnds']]
    if outfl is not None:
        # log.debug('Writing variable {} to {}'.format(tas_str, outfl))
        out.to_netcdf(outfl, format='NETCDF4', engine='netcdf4')
    return out


@reticfox_cli.command(help='Parse CAM TS from iCESM output')
@click.option('--ts_glob', help='Glob pattern to input CAM TS NetCDF files.')
@click.option('--ts_str', default='ts', help='Variable name in output NetCDF file.')
@click.option('--outfl', help='Path for output NetCDF file.')
def make_ts(ts_glob, ts_str, outfl=None):
    """Parse CAM TS iCESM NetCDF files and write to outfl.
    """
    # log.debug('working ts files in glob {}'.format(ts_glob))
    x = xr.open_mfdataset(ts_glob).sortby('time')
    x[ts_str] = x['TS']

    out = x[[ts_str, 'time_bnds']]
    if outfl is not None:
        # log.debug('Writing variable {} to {}'.format(ts_str, outfl))
        out.to_netcdf(outfl, format='NETCDF4', engine='netcdf4')
    return out


@reticfox_cli.command(help='Parse POP TEMP from iCESM output')
@click.option('--temp_glob', help='Glob pattern to input POP TEMP NetCDF files.')
@click.option('--salt_glob', help='Glob pattern to input POP SALT NetCDF files.')
@click.option('--tos_str', default='tos', help='Variable name in output NetCDF file.')
@click.option('--outfl', help='Path for output NetCDF file.')
def make_tos(temp_glob, salt_glob, tos_str, outfl=None):
    """Parse POP TEMP iCESM NetCDF files
    """
    # log.debug('working temp files in glob {}'.format(temp_glob))
    # log.debug('working salt files in glob {}'.format(salt_glob))

    # Note we're grabbing 500 cm depth - should be top-most ocean layer.
    theta = xr.open_mfdataset(temp_glob).sel(z_t=500.0).sortby('time')
    salt = xr.open_mfdataset(salt_glob).sel(z_t=500.0).sortby('time')

    # First get in-situ temps from potential temps (TEMP), add to theta
    theta[tos_str] = api.pot2insitu_temp(theta, salt, insitu_temp_name=tos_str)

    out = theta[[tos_str, 'time_bound']]
    out[tos_str] = out[tos_str].astype('float32')
    if outfl is not None:
        # Write ~SST file
        out.to_netcdf(outfl, format='NETCDF4', engine='netcdf4')
    return out


@reticfox_cli.command(help='Parse SALT from iCESM output')
@click.option('--salt_glob', help='Glob pattern to input POP SALT NetCDF files.')
@click.option('--sos_str', default='sos', help='Variable name in output NetCDF file.')
@click.option('--outfl', help='Path for output NetCDF file.')
def make_sos(salt_glob, sos_str, outfl=None):
    """Parse POP SALT iCESM NetCDF files
    """
    # log.debug('working salt files in glob {}'.format(salt_glob))

    # Note we're grabbing 500 cm depth - should be top-most ocean layer.
    salt = xr.open_mfdataset(salt_glob).sel(z_t=500.0).sortby('time')

    salt[sos_str] = salt['SALT']
    out = salt[[sos_str, 'time_bound']]
    if outfl is not None:
        # Write ~SSS file
        out.to_netcdf(outfl, format='NETCDF4', engine='netcdf4')
    return out


@reticfox_cli.command(help='Parse POP TEMP, SALT from iCESM output for gamma-avg temp')
@click.option('--temp_glob', help='Glob pattern to input POP TEMP NetCDF files.')
@click.option('--salt_glob', help='Glob pattern to input POP SALT NetCDF files.')
@click.option('--toga_str', default='toga', help='Variable name in output NetCDF file.')
@click.option('--outfl', help='Path for output NetCDF file.')
def make_toga(temp_glob, salt_glob, toga_str, outfl=None):
    """Parse POP TEMP and SALT iCESM NetCDF files for gamma-average insitu temp
    """
    # log.debug('working temp files in glob {}'.format(temp_glob))
    # log.debug('working salt files in glob {}'.format(salt_glob))
    tos_str = 'insitu_temp'

    cutoff_z = 20000

    theta = xr.open_mfdataset(temp_glob).sel(
        z_t=slice(0, cutoff_z)).sortby('time')
    salt = xr.open_mfdataset(salt_glob).sel(
        z_t=slice(0, cutoff_z)).sortby('time')
    # Because using z_t slice doesn't get z_w which has depth layers' bounds.
    # We trim by z_w_bot length because we don't want the bottom of the layer to
    # be deeper than `cutoff_z`.
    theta = theta.sel(z_w_bot=slice(0, cutoff_z))
    theta = theta.isel(z_t=slice(0, len(theta.z_w_bot)))
    theta = theta.isel(z_w=slice(0, len(theta.z_w_bot)))
    theta = theta.isel(z_w_top=slice(0, len(theta.z_w_bot)))
    salt = salt.isel(z_t=slice(0, len(theta.z_t)))

    # First get in-situ temps from potential temps (TEMP), add to theta
    theta[tos_str] = api.pot2insitu_temp(theta, salt, insitu_temp_name=tos_str)
    # get gamma average, add to theta
    theta[toga_str] = api.tex86_gammaavg_depth(theta, target_var=tos_str)

    out = theta[[toga_str, 'time_bound']]
    out[toga_str] = out[toga_str].astype('float32')
    if outfl is not None:
        # Write gamma-average file
        out.to_netcdf(outfl, format='NETCDF4', engine='netcdf4')
    return out


@reticfox_cli.command(help='Parse d18Osw from iCESM output')
@click.option('--r18o_glob', help='Glob pattern to input POP R18O NetCDF files.')
@click.option('--d18osw_str', default='d18osw', help='Variable name in output NetCDF file.')
@click.option('--outfl', help='Path for output NetCDF file.')
def make_d18osw(r18o_glob, d18osw_str, outfl=None):
    """Parse POP R18O iCESM netCDF files and write to outfl.
    """
    # log.debug('working R18O files in glob {}'.format(r18o_glob))
    r18o = xr.open_mfdataset(r18o_glob).isel(z_t=0).sortby('time')
    r18o[d18osw_str] = (r18o['R18O'] - 1.0) * 1000.0

    # Metadata
    r18o[d18osw_str] = r18o[d18osw_str].astype('float32')
    r18o[d18osw_str].attrs['long_name'] = 'seawater d18O'
    r18o[d18osw_str].attrs['units'] = 'permil'

    out = r18o[[d18osw_str, 'time_bound']]
    if outfl is not None:
        # Dump to file
        # log.debug('Writing variable {} to {}'.format(d18osw_str, outfl))
        out.to_netcdf(outfl, format='NETCDF4', engine='netcdf4')
    return out


@reticfox_cli.command(help='Parse d18Osw from iCESM output')
@click.option('--nc_glob', help='Glob pattern for NetCDF files.')
@click.option('--outfl', help='Path for output NetCDF file.')
@click.option('--sortby', default='time', help='Variable to sort merged files by.')
def combine_netcdf_glob(nc_glob, outfl=None, sortby='time'):
    """Combine a glob of NetCDF file names to a single dataset, write to disk as one file
    """
    ds = xr.open_mfdataset(nc_glob).sortby(sortby)
    if outfl is not None:
        ds.to_netcdf(outfl)
    return ds


if __name__ == '__main__':
    reticfox_cli()