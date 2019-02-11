# Parse precipitation δ18O from iCESM cam experiment slice NetCDF files.
# Can run from Bash with:
#
# python make_d18op.py \
#   --precrl_h216o_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECRL_H216OR.*.nc \
#   --precrc_h216o_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECRC_H216Or.*.nc \
#   --precsc_h216o_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECSC_H216Os.*.nc \
#   --precsl_h216o_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECSL_H216OS.*.nc \
#   --precrc_h218o_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECRC_H218Or.*.nc \
#   --precrl_h218o_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECRL_H218OR.*.nc \
#   --precsc_h218o_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECSC_H218Os.*.nc \
#   --precsl_h218o_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECSL_H218OS.*.nc \
#   --d18op_str d18op \
#   --outfl /rsgrps/jesst/icesm/b.e12.B1850C5.f19_g16.i21ka.03.cam.h0.d18op.nc
#
# See help with `python make_d18op.py --help`.

import argparse
import logging
from glob import glob
import xarray as xr


log = logging.getLogger(__name__)


def parse_icesm(precrc_h216o_glob, precrl_h216o_glob, precsc_h216o_glob, precsl_h216o_glob,
                precrc_h218o_glob, precrl_h218o_glob, precsc_h218o_glob, precsl_h218o_glob,
                d18op_str, outfl=None):
    """Parse CAM PRE*_H216O* and PRE*_H218O* iCESM netCDF files and write δ18O to outfl.
    """
    ptiny = 1e-18

    globs = [precrc_h216o_glob, precrl_h216o_glob, precsc_h216o_glob, precsl_h216o_glob,
             precrc_h218o_glob, precrl_h218o_glob, precsc_h218o_glob, precsl_h218o_glob]
    log.debug('working precip d18O files in globs {}'.format(globs))

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
        log.debug('Writing variable {} to {}'.format(d18op_str, outfl))
        out.to_netcdf(outfl, format='NETCDF4', engine='netcdf4')
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse d18O (precip) from iCESM output')
    parser.add_argument('--precrc_h216o_glob', metavar='PRECRCH216OGLOB', nargs=1,
                        help='glob pattern to input CAM PRECRC_H216Or NetCDF files')
    parser.add_argument('--precrl_h216o_glob', metavar='PRECRLH216OGLOB', nargs=1,
                        help='glob pattern to input CAM PRECRL_H216OR NetCDF files')
    parser.add_argument('--precsc_h216o_glob', metavar='PRECSCH216OGLOB', nargs=1,
                        help='glob pattern to input CAM PRECSC_H216Os NetCDF files')
    parser.add_argument('--precsl_h216o_glob', metavar='PRECSLH216OGLOB', nargs=1,
                        help='glob pattern to input CAM PRECSL_H216OS NetCDF files')

    parser.add_argument('--precrc_h218o_glob', metavar='PRECRCH218OGLOB', nargs=1,
                        help='glob pattern to input CAM PRECRC_H218Or NetCDF files')
    parser.add_argument('--precrl_h218o_glob', metavar='PRECRLH218OGLOB', nargs=1,
                        help='glob pattern to input CAM PRECRL_H218OR NetCDF files')
    parser.add_argument('--precsc_h218o_glob', metavar='PRECSCH218OGLOB', nargs=1,
                        help='glob pattern to input CAM PRECSC_H218Os NetCDF files')
    parser.add_argument('--precsl_h218o_glob', metavar='PRECSLH218OGLOB', nargs=1,
                        help='glob pattern to input CAM PRECSL_H218OS NetCDF files')

    parser.add_argument('--d18op_str', metavar='D18OPSTR', nargs=1,
                        default=['d18op'],
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

    parse_icesm(precrc_h216o_glob=str(args.precrc_h216o_glob[0]),
                precrl_h216o_glob=str(args.precrl_h216o_glob[0]),
                precsc_h216o_glob=str(args.precsc_h216o_glob[0]),
                precsl_h216o_glob=str(args.precsl_h216o_glob[0]),
                precrc_h218o_glob=str(args.precrc_h218o_glob[0]),
                precrl_h218o_glob=str(args.precrl_h218o_glob[0]),
                precsc_h218o_glob=str(args.precsc_h218o_glob[0]),
                precsl_h218o_glob=str(args.precsl_h218o_glob[0]),
                d18op_str=str(args.d18op_str[0]), outfl=str(args.outfl[0]))
