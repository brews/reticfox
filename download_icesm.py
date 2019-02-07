# Stupid wrapper for `globus-cli` to load cesm files from NCAR server.
# Assumes you've already logged in to globus from shell with `globus login`
#
# Can run from Bash with:
#
# python download_icesm.py \
#     --casename b.e12.B1850C5.f19_g16.i21ka.03 \
#     --downloadpath /xdisk/malevich/transferstuff
#
# See help with `python download_icesm.py --help`.

import os
import pathlib
import subprocess
import argparse
import logging


log = logging.getLogger(__name__)


def globus_find_endpoint(searchname, owner_id):
    """Get globus endpoint ID based on name and owner_id.

    Parameters
    ----------
    searchname : str
        Endpoint name to search for.
    owner_id : str
        Endpoint owner name to filter results by.

    Returns
    -------
    String endpoint ID or `None`.
    """
    log.debug('finding globus endpoint for {} ({})'.format(searchname, owner_id))
    searchname = str(searchname)
    owner_id = str(owner_id)
    # In future might want to change `--format UNIX`, below, to something more
    # machine-readable.
    cmd_template = ["globus", "endpoint", "search", searchname,
                    "--filter-owner-id", owner_id,
                    "--jq", "DATA[0].id", "--format", "UNIX"]
    response = subprocess.run(cmd_template, check=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    endpoint_id = None
    if response.returncode == 0 and response.returncode != b'None\n':
        endpoint_id = response.stdout.rstrip().decode('utf-8')

    log.debug('globus endpoint ID {}'.format(endpoint_id))
    return endpoint_id


def globus_transfer(from_endpoint, from_dir, to_endpoint, to_dir, task_label=None):
    """Globus transfer from 'from' endpoint and dir to 'to endpoint and dir.

    Assumes you've alread run `globus login`.

    Parameters
    ----------
    from_endpoint : str
        Globus ID of endpoint containing data to transfer.
    from_dir : str
        Path to directory on 'from' endpoint containing all the data we will 
        transfer.
    to_endpoint : str
        Globus ID of endpoint we want to transfer data to.
    to_dir : str
        Path to directory on 'to' endpoint we want to transfer data into.
    task_label : str or None
        Optional str label to give globus transfer task.


    Examples
    --------
    > # in shell before, run `globus login`
    > from_d = '/gpfs/csfs1/univ/uazn0013/jiangzhu/archive/b.e12.B1850C5.f19_g16.i21ka.03/atm/proc/tseries/monthly/PS/'
    > to_d = '/xdisk/malevich/'
    > tranfer(from_d, to_d)
    """
    from_endpoint = str(from_endpoint)
    to_endpoint = str(to_endpoint)

    # In future might want to change `--format UNIX`, below, to something more
    # machine-readable.
    cmd_template = ["globus", "transfer", "--recursive", "--sync-level", "mtime",
                    "{}:{}".format(from_endpoint, from_dir),
                    "{}:{}".format(to_endpoint, to_dir),
                    "--jq", "task_id", "--format", "UNIX"]

    if task_label is not None:
        cmd_template.append("--label")
        cmd_template.append(str(task_label))

    subprocess.run(cmd_template, check=True)
    log.debug('created globus transfer task from {}:{} to {}:{}'.format(
        from_endpoint, from_dir, to_endpoint, to_dir))


def download_icesm(casename, download_path, atm_variables, ocn_variables):
    """Start globus transfers of iCESM output from NCAR Campaign to UA HPC.

    You should have run `globus login` from shell terminal before using this command.

    Parameters
    ----------
    casename : str
        iCESM experiment case name. Used to find the model run on NCAR.
    download_path : str
        UA HPC path we're transfering files to. Should be able to handle lots of data.
        Path must already exist.
    atm_variables : list of strs

    """
    log.debug('begin creating globus transfers for {} to {}'.format(
        casename, download_path))
    ncar_endpoint = globus_find_endpoint(
        searchname='NCAR Campaign Storage', owner_id='ncar@globusid.org')
    uahpc_endpoint = globus_find_endpoint(
        searchname='arizona#sdmz-dtn', owner_id='tmerritt@arizona.edu')

    assert ncar_endpoint is not None or uahpc_endpoint is not None, 'could not get globus endpoint IDs'

    lab = 'download_icesm_py'
    # Load files from atmosphere component
    from_atm_template = '/gpfs/csfs1/univ/uazn0013/jiangzhu/archive/{}/atm/proc/tseries/monthly/{}/'
    for variable in atm_variables:
        from_d = from_atm_template.format(casename, variable)
        globus_transfer(from_endpoint=ncar_endpoint, from_dir=from_d,
                        to_endpoint=uahpc_endpoint, to_dir=download_path, task_label=lab)

    # Load files from ocean component
    from_ocn_template = '/gpfs/csfs1/univ/uazn0013/jiangzhu/archive/{}/ocn/proc/tseries/monthly/{}/'
    for variable in ocn_variables:
        from_d = from_ocn_template.format(casename, variable)
        globus_transfer(from_endpoint=ncar_endpoint, from_dir=from_d,
                        to_endpoint=uahpc_endpoint, to_dir=download_path, task_label=lab)
    log.debug('globus transfers created')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Globus transfer iCESM files from NCAR to UA HPC')
    parser.add_argument('--casename', metavar='CASENAME', nargs=1,
                        default=['b.e12.B1850C5.f19_g16.i21ka.03'],
                        help='iCESM experiment case name')
    parser.add_argument('--downloadpath', metavar='DOWNLOADPATH', nargs=1,
                        default=[None],
                        help='directory files will be transferred to to. PWD is default. Will be created if it doesnt exist.')
    parser.add_argument('--log', metavar='LOGPATH', nargs=1, default=[None],
                        help='file path that log will be written to')
    args = parser.parse_args()

    if args.log[0] is not None:
        logging.basicConfig(level=logging.DEBUG,
                            filename=args.log[0],
                            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    dl_path = args.downloadpath[0]
    if dl_path is None:
        dl_path = os.getcwd()

    casename = str(args.casename[0])
    atm_variables = ['PRECC',
                     'PRECL',
                     'PRECSC',
                     'PRECSL',
                     'TS',
                     'TREFHT',
                     'PRECRC_H218Or',
                     'PRECRL_H218OR',
                     'PRECSC_H218Os',
                     'PRECSL_H218OS',
                     'PRECRC_H216Or',
                     'PRECRL_H216OR',
                     'PRECSC_H216Os',
                     'PRECSL_H216OS',
                     'PRECRC_H2Or',
                     'PRECRL_H2OR',
                     'PRECSC_H2Os',
                     'PRECSL_H2OS',
                     'PRECRC_HDOr',
                     'PRECRL_HDOR',
                     'PRECSC_HDOs',
                     'PRECSL_HDOS',
                     'OMEGA',
                     'PS',
                     ]

    ocn_variables = ['R18O',
                     'TEMP',
                     'SALT',
                     ]

    # Create dl path if doesn't exist.
    dl_path = pathlib.Path(dl_path)
    dl_path.mkdir(parents=True, exist_ok=True)

    download_icesm(casename=casename, download_path=dl_path,
                   atm_variables=atm_variables, ocn_variables=ocn_variables)
