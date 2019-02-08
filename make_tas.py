# Parse tas from iCESM cam experiment slice NetCDF files.
# Can run from Bash with:
#
# python make_tas.py \
#   --trefht_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.TREFHT.*.nc \
#   --tas_str tas \
#   --outfl /rsgrps/jesst/icesm/b.e12.B1850C5.f19_g16.i21ka.03.cam.h0.tas.nc
#
# See help with `python make_tas.py --help`.

import argparse
import logging
from glob import glob
import xarray as xr


log = logging.getLogger(__name__)


def parse_icesm(trefht_glob, tas_str, outfl=None):
    """Parse CAM tas iCESM NetCDF files and write to outfl.
    """
    log.debug('working trefht files in glob {}'.format(trefht_glob))
    x = xr.open_mfdataset(trefht_glob).sortby('time')
    x[tas_str] = x['TREFHT']

    out = x[[tas_str, 'time_bnds']]
    if outfl is not None:
        log.debug('Writing variable {} to {}'.format(tas_str, outfl))
        out.to_netcdf(outfl)
    return out
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse TREFHT from iCESM output')
    parser.add_argument('--trefht_glob', metavar='TREFHTGLOB', nargs=1,
                        help='glob pattern to input CAM TREFHT NetCDF files')
    parser.add_argument('--tas_str', metavar='TASSTR', nargs=1,
                        default=['tas'],
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

    parse_icesm(trefht_glob=str(args.trefht_glob[0]),
                tas_str=str(args.tas_str[0]),
                outfl=str(args.outfl[0]))
