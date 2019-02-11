# Parse precip rate from iCESM cam experiment slice NetCDF files.
# Can run from Bash with:
#
# python make_pr.py \
#   --precc_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECC.*.nc \
#   --precl_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECL.*.nc \
#   --precsc_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECSC.*.nc \
#   --precsl_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECSL.*.nc \
#   --pr_str pr \
#   --outfl /rsgrps/jesst/icesm/b.e12.B1850C5.f19_g16.i21ka.03.pop.h.pr.nc
#
# See help with `python make_pr.py --help`.


import argparse
import logging
from glob import glob
import xarray as xr


log = logging.getLogger(__name__)


def parse_icesm(precc_glob, precl_glob, precsc_glob, precsl_glob, pr_str, outfl=None):
    """Parse CAM PREC* iCESM netCDF files and write to outfl.
    """
    globs = [precc_glob, precl_glob, precsc_glob, precsl_glob]
    log.debug('working precip files in glob {}'.format(globs))

    matched_files = []
    for g in globs:
        for match in glob(g):
            matched_files.append(match)

    pre = xr.open_mfdataset(matched_files).sortby('time')

    # Combine parts
    pre[pr_str] = pre['PRECC'] + pre['PRECL'] + pre['PRECSC'] + pre['PRECSL']

    # Metadata
    pre[pr_str].attrs['long_name'] = 'total precipitation rate'
    pre[pr_str].attrs['units'] = 'm/s'

    out = pre[[pr_str, 'time_bnds']]
    if outfl is not None:
        log.debug('Writing variable {} to {}'.format(pr_str, outfl))
        out.to_netcdf(outfl, format='NETCDF4', engine='netcdf4')
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse pr from iCESM output')
    parser.add_argument('--precc_glob', metavar='PRECCGLOB', nargs=1,
                        help='glob pattern to input CAM PRECRC NetCDF files')
    parser.add_argument('--precl_glob', metavar='PRECLGLOB', nargs=1,
                        help='glob pattern to input CAM PRECRL NetCDF files')
    parser.add_argument('--precsc_glob', metavar='PRECSCGLOB', nargs=1,
                        help='glob pattern to input CAM PRECSC NetCDF files')
    parser.add_argument('--precsl_glob', metavar='PRECSLGLOB', nargs=1,
                        help='glob pattern to input CAM PRECSL NetCDF files')
    parser.add_argument('--pr_str', metavar='PRSTR', nargs=1,
                        default=['pr'],
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

    parse_icesm(precc_glob=str(args.precc_glob[0]),
                precl_glob=str(args.precl_glob[0]),
                precsc_glob=str(args.precsc_glob[0]),
                precsl_glob=str(args.precsl_glob[0]),
                pr_str=str(args.pr_str[0]), outfl=str(args.outfl[0]))
