# Parse CAM omega from iCESM cam experiment slice NetCDF files.
# Can run from Bash with:
#
# python make_omega.py \
#   --omega_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.OMEGA.*.nc \
#   --ps_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PS.*.nc \
#   --omega_str omega \
#   --outfl /rsgrps/jesst/icesm/b.e12.B1850C5.f19_g16.i21ka.03.cam.h.omega.nc
#
# See help with `python make_omega.py --help`.

import argparse
import logging
import xarray as xr
import Ngl


log = logging.getLogger(__name__)


def parse_icesm(omega_glob, ps_glob, omega_str, outfl=None, levels=None):
    """Parse CAM omega iCESM netCDF files and write to outfl.
    """
    log.debug('working omega files in glob {}'.format(omega_glob))

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
    if outfl is not None:
        # Dump to file
        log.debug('Writing variable {} to {}'.format(omega_str, outfl))
        out.to_netcdf(outfl, format='NETCDF4', engine='netcdf4')
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse CAM OMEGA from iCESM output')
    parser.add_argument('--omega_glob', metavar='OMEGAGLOB', nargs=1,
                        help='glob pattern to input CAM OMEGA NetCDF files')
    parser.add_argument('--ps_glob', metavar='PSGLOB', nargs=1,
                        help='glob pattern to input CAM PS NetCDF files')
    parser.add_argument('--omega_str', metavar='OMEGASTR', nargs=1,
                        default=['omega'],
                        help='variable name in output NetCDF file')
    parser.add_argument('--outfl', metavar='OUTFL', nargs=1,
                        help='path for output NetCDF file')
    parser.add_argument('--log', metavar='LOGPATH', nargs=1, default=[None],
                        help='optional path to write log file to')
    args = parser.parse_args()

    if args.log[0] is not None:
        logging.basicConfig(level=logging.DEBUG,
                            filename=args.log[0],
                            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    parse_icesm(omega_glob=str(args.omega_glob[0]),
                ps_glob=str(args.ps_glob[0]),
                omega_str=str(args.omega_str[0]),
                outfl=str(args.outfl[0]))
