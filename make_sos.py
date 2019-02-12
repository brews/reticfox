# Parse TEMP and SALT from iCESM cam experiment slice NetCDF files.
# Can run from Bash with:
#
# python make_sos.py \
#   --salt_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.SALT.*.nc \
#   --sos_str sos \
#   --outfl /rsgrps/jesst/icesm/b.e12.B1850C5.f19_g16.i21ka.03.pop.h.sos.nc
#
# See help with `python make_sos.py --help`.

import logging
import argparse
import numpy as np
import xarray as xr


log = logging.getLogger(__name__)


def parse_icesm(salt_glob, sos_str, outfl=None):
    """Parse POP SALT iCESM NetCDF files
    """
    log.debug('working salt files in glob {}'.format(salt_glob))

    # Note we're grabbing 500 cm depth - should be top-most ocean layer.
    salt = xr.open_mfdataset(salt_glob).sel(z_t=500.0).sortby('time')

    salt[sos_str] = salt['SALT']
    out = salt[[sos_str, 'time_bound']]
    if outfl is not None:
        # Write ~SSS file
        out.to_netcdf(outfl, format='NETCDF4', engine='netcdf4')
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse SALT from iCESM output')
    parser.add_argument('--salt_glob', metavar='SALTGLOB', nargs=1,
                        help='glob pattern to input POP SALT NetCDF files')
    parser.add_argument('--sos_str', metavar='SOSSTR', nargs=1,
                        default=['sos'],
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

    parse_icesm(salt_glob=str(args.salt_glob[0]),
                sos_str=str(args.sos_str[0]),
                outfl=str(args.outfl[0]))
