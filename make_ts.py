# Parse TS from iCESM cam experiment slice NetCDF files.
# Can run from Bash with:
#
# python make_ts.py \
#   --ts_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.TS.*.nc \
#   --ts_str ts \
#   --outfl /rsgrps/jesst/icesm/b.e12.B1850C5.f19_g16.i21ka.03.cam.h0.ts.nc
#
# See help with `python make_ts.py --help`.

import argparse
import logging
from glob import glob
import xarray as xr


log = logging.getLogger(__name__)


def parse_icesm(ts_glob, ts_str, outfl=None):
    """Parse CAM TS iCESM NetCDF files and write to outfl.
    """
    log.debug('working ts files in glob {}'.format(ts_glob))
    x = xr.open_mfdataset(ts_glob).sortby('time')
    x[ts_str] = x['TS']

    out = x[[ts_str, 'time_bnds']]
    if outfl is not None:
        log.debug('Writing variable {} to {}'.format(ts_str, outfl))
        out.to_netcdf(outfl)
    return out
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse CAM TS from iCESM output')
    parser.add_argument('--ts_glob', metavar='TSGLOB', nargs=1,
                        help='glob pattern to input CAM TS NetCDF files')
    parser.add_argument('--ts_str', metavar='TSSTR', nargs=1,
                        default=['ts'],
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

    parse_icesm(ts_glob=str(args.ts_glob[0]),
                ts_str=str(args.ts_str[0]),
                outfl=str(args.outfl[0]))
