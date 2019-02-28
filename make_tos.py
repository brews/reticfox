# Parse TEMP and SALT from iCESM cam experiment slice NetCDF files.
# Can run from Bash with:
#
# python make_tos.py \
#   --temp_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.TEMP.*.nc \
#   --salt_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.SALT.*.nc \
#   --tos_str tos \
#   --outfl /rsgrps/jesst/icesm/b.e12.B1850C5.f19_g16.i21ka.03.pop.h.tos.nc
#
# See help with `python make_tos.py --help`.

from glob import glob
import logging
import argparse
import numpy as np
import xarray as xr
from make_toga import pot2insitu_temp


log = logging.getLogger(__name__)


def parse_icesm(temp_glob, salt_glob, tos_str, outfl=None):
    """Parse POP TEMP iCESM NetCDF files
    """
    log.debug('working temp files in glob {}'.format(temp_glob))
    log.debug('working salt files in glob {}'.format(salt_glob))

    # Note we're grabbing 500 cm depth - should be top-most ocean layer.
    theta = xr.open_mfdataset(temp_glob).sel(z_t=500.0).sortby('time')
    salt = xr.open_mfdataset(salt_glob).sel(z_t=500.0).sortby('time')

    # First get in-situ temps from potential temps (TEMP), add to theta
    theta[tos_str] = pot2insitu_temp(theta, salt, insitu_temp_name=tos_str)

    out = theta[[tos_str, 'time_bound']]
    out[tos_str] = out[tos_str].astype('float32')
    if outfl is not None:
        # Write ~SST file
        out.to_netcdf(outfl, format='NETCDF4', engine='netcdf4')
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse POP TEMP from iCESM output')
    parser.add_argument('--temp_glob', metavar='TEMPGLOB', nargs=1,
                        help='glob pattern to input POP TEMP NetCDF files')
    parser.add_argument('--salt_glob', metavar='SALTGLOB', nargs=1,
                        help='glob pattern to input POP SALT NetCDF files')
    parser.add_argument('--tos_str', metavar='TOSSTR', nargs=1,
                        default=['tos'],
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

    parse_icesm(temp_glob=str(args.temp_glob[0]),
                salt_glob=str(args.salt_glob[0]),
                tos_str=str(args.tos_str[0]),
                outfl=str(args.outfl[0]))
