# Parse seawater δ18O from iCESM cam experiment slice NetCDF files.
# Can run from Bash with:
#
# python make_d18osw.py \
#   --r18o_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.R18O.*.nc \
#   --d18osw_str d18osw \
#   --outfl /rsgrps/jesst/icesm/b.e12.B1850C5.f19_g16.i21ka.03.pop.h.d18osw.nc
#
# See help with `python make_d18osw.py --help`.

import argparse
import xarray as xr
import logging


log = logging.getLogger(__name__)


def parse_icesm(r18o_glob, d18osw_str, outfl=None):
    """Parse POP R18O iCESM netCDF files and write to outfl.
    """
    log.debug('working R18O files in glob {}'.format(r18o_glob))

    r18o = xr.open_mfdataset(r18o_glob).isel(z_t=0).sortby('time')
    r18o[d18osw_str] = (r18o['R18O'] - 1.0) * 1000.0

    # Metadata
    r18o[d18osw_str] = r18o[d18osw_str].astype('float')
    r18o[d18osw_str].attrs['long_name'] = 'seawater d18O'
    r18o[d18osw_str].attrs['units'] = 'permil'

    out = r18o[[d18osw_str, 'time_bound']]
    if outfl is not None:
        # Dump to file
        log.debug('Writing variable {} to {}'.format(d18osw_str, outfl))
        out.to_netcdf(outfl, format='NETCDF4', engine='netcdf4')
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse d18Osw from iCESM output')
    parser.add_argument('--r18o_glob', metavar='R18OGLOB', nargs=1,
                        help='glob pattern to input POP R18O NetCDF files')
    parser.add_argument('--d18osw_str', metavar='D18OSWSTR', nargs=1,
                        default=['d18osw'],
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

    parse_icesm(r18o_glob=str(args.r18o_glob[0]),
                d18osw_str=str(args.d18osw_str[0]),
                outfl=str(args.outfl[0]))
