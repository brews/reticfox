# Combine a glob of NetCDF files into a single NetCDF file
# Can run from Bash with:
#
# python combine_netcdf_glob.py \
#   --nc_glob /xdisk/malevich/b.e12.B1850C5.f19_g16.i21ka.03/*.toGA.*.nc \
#   --sortby time \
#   --outfl /rsgrps/jesst/icesm/b.e12.B1850C5.f19_g16.i21ka.03.pop.h.toga.nc
#
# See help with `python combine_netcdf_glob.py --help`.

import xarray as xr
import logging
import argparse


log = logging.getLogger(__name__)


def combine_netcdf_glob(nc_glob, outfl=None, sortby='time'):
    """Combine a glob of NetCDF file names to a single dataset, write to disk as one file
    """
    ds = xr.open_mfdataset(nc_glob).sortby(sortby)
    if outfl is not None:
        ds.to_netcdf(outfl)
    return ds


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Combine a glob of NetCDF file names to a single dataset, write to disk as one file')
    parser.add_argument('--nc_glob', metavar='NCGLOB', nargs=1,
                        help='glob pattern for NetCDF files')
    parser.add_argument('--outfl', metavar='OUTFL', nargs=1,
                        help='path for output NetCDF file')
    parser.add_argument('--sortby', metavar='OUTFL', nargs=1, default=['time'],
                        help='Variable to sort merged files by')
    parser.add_argument('--log', metavar='LOGPATH', nargs=1, default=[None],
                        help='optional path to write log file to')
    args = parser.parse_args()

    if args.log[0] is not None:
        logging.basicConfig(level=logging.DEBUG,
                            filename=args.log[0],
                            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    combine_netcdf_glob(nc_glob=str(args.nc_glob[0]),
                        outfl=str(args.outfl[0]),
                        sortby=str(args.sortby[0]))
