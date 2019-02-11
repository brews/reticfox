# Parse precipitation deuterium (δD) from iCESM cam experiment slice NetCDF files.
# Can run from Bash with:
#
# python make_ddp.py \
#   --precrl_h2o_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECRL_H2OR.*.nc \
#   --precrc_h2o_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECRC_H2Or.*.nc \
#   --precsc_h2o_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECSC_H2Os.*.nc \
#   --precsl_h2o_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECSL_H2OS.*.nc \
#   --precrc_hdo_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECRC_HDOr.*.nc \
#   --precrl_hdo_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECRL_HDOR.*.nc \
#   --precsc_hdo_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECSC_HDOs.*.nc \
#   --precsl_hdo_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.PRECSL_HDOS.*.nc \
#   --ddp_str ddp \
#   --outfl /rsgrps/jesst/icesm/b.e12.B1850C5.f19_g16.i21ka.03.cam.h0.ddp.nc
#
# See help with `python make_ddp.py --help`.

import argparse
import logging
from glob import glob
import xarray as xr


log = logging.getLogger(__name__)


def parse_icesm(precrc_h2o_glob, precrl_h2o_glob, precsc_h2o_glob, precsl_h2o_glob,
                precrc_hdo_glob, precrl_hdo_glob, precsc_hdo_glob, precsl_hdo_glob,
                ddp_str, outfl=None):
    """Parse CAM PRE*_HDO* and PRE*_H2O* iCESM netCDF files and write δD to outfl.
    """
    ptiny = 1e-18

    globs = [precrc_h2o_glob, precrl_h2o_glob, precsc_h2o_glob, precsl_h2o_glob,
             precrc_hdo_glob, precrl_hdo_glob, precsc_hdo_glob, precsl_hdo_glob]
    log.debug('working precip deuterium files in globs {}'.format(globs))

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
        log.debug('Writing variable {} to {}'.format(ddp_str, outfl))
        out.to_netcdf(outfl, format='NETCDF4', engine='netcdf4')
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse delta D (precip) from iCESM output')
    parser.add_argument('--precrc_h2o_glob', metavar='PRECRCH2OGLOB', nargs=1,
                        help='glob pattern to input CAM PRECRC_H2Or NetCDF files')
    parser.add_argument('--precrl_h2o_glob', metavar='PRECRLH2OGLOB', nargs=1,
                        help='glob pattern to input CAM PRECRL_H2OR NetCDF files')
    parser.add_argument('--precsc_h2o_glob', metavar='PRECSCH2OGLOB', nargs=1,
                        help='glob pattern to input CAM PRECSC_H2Os NetCDF files')
    parser.add_argument('--precsl_h2o_glob', metavar='PRECSLH2OGLOB', nargs=1,
                        help='glob pattern to input CAM PRECSL_H2OS NetCDF files')

    parser.add_argument('--precrc_hdo_glob', metavar='PRECRCHDOGLOB', nargs=1,
                        help='glob pattern to input CAM PRECRC_HDOr NetCDF files')
    parser.add_argument('--precrl_hdo_glob', metavar='PRECRLHDOGLOB', nargs=1,
                        help='glob pattern to input CAM PRECRL_HDOR NetCDF files')
    parser.add_argument('--precsc_hdo_glob', metavar='PRECSCHDOGLOB', nargs=1,
                        help='glob pattern to input CAM PRECSC_HDOs NetCDF files')
    parser.add_argument('--precsl_hdo_glob', metavar='PRECSLHDOGLOB', nargs=1,
                        help='glob pattern to input CAM PRECSL_HDOS NetCDF files')

    parser.add_argument('--ddp_str', metavar='DDPSTR', nargs=1,
                        default=['ddp'],
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

    parse_icesm(precrc_h2o_glob=str(args.precrc_h2o_glob[0]),
                precrl_h2o_glob=str(args.precrl_h2o_glob[0]),
                precsc_h2o_glob=str(args.precsc_h2o_glob[0]),
                precsl_h2o_glob=str(args.precsl_h2o_glob[0]),
                precrc_hdo_glob=str(args.precrc_hdo_glob[0]),
                precrl_hdo_glob=str(args.precrl_hdo_glob[0]),
                precsc_hdo_glob=str(args.precsc_hdo_glob[0]),
                precsl_hdo_glob=str(args.precsl_hdo_glob[0]),
                ddp_str=str(args.ddp_str[0]), outfl=str(args.outfl[0]))
