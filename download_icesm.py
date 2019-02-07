# Stupid wrapper for `globus-cli` to load cesm files from NCAR server.

import os
import pathlib
import subprocess


def transfer(from_dir, to_dir):
    """Download all files in directory from_dir on NCAR Campaign to to_dir on HPC.

    Assumes you've alread run `globus login`.

    Examples
    --------
    > # in shell before, run `globus login`
    > from_d = '/gpfs/csfs1/univ/uazn0013/jiangzhu/archive/b.e12.B1850C5.f19_g16.i21ka.03/atm/proc/tseries/monthly/PS/'
    > to_d = '/xdisk/malevich/'
    > tranfer(from_d, to_d)
    """
    # In future might want to change `--format UNIX`, below, to something more 
    # machine-readable.

    # Endpoint we upload to
    eplocal = subprocess.run(["globus", "endpoint", "search", "arizona#sdmz-dtn", 
                            "--filter-owner-id", "tmerritt@arizona.edu", 
                            "--jq", "DATA[0].id", "--format", "UNIX"], 
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if eplocal.returncode == 0 and eplocal.returncode != b'None\n':
        endpoint_local = eplocal.stdout.rstrip().decode('utf-8')
    else:
        raise KeyError('could not find local endpoint')

    # Endpoint we download from
    epremote = subprocess.run(["globus", "endpoint", "search", "NCAR Campaign Storage", "--filter-owner-id", "ncar@globusid.org", "--jq", "DATA[0].id", "--format", "UNIX"], 
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if epremote.returncode == 0 and epremote.returncode != b'None\n':
        endpoint_remote = epremote.stdout.rstrip().decode('utf-8')
    else:
        raise KeyError('could not find remote endpoint')

    # set REMOTE_DIR = ${ARCH_REM}/${casename}/${model}/proc/tseries/monthly/${var}
    #  set LOCAL_DIR  = ${ARCH_LOC}/${casename}/${model}/proc/tseries/monthly/${var}

    #  globus transfer --recursive --sync-level mtime                 \
    #      ${EPSTORE}:${REMOTE_DIR} ${EPGLADE}:${LOCAL_DIR}           \
    #      --jq task_id --format UNIX
    transfer_proc = subprocess.run(["globus", "transfer", "--recursive", "--sync-level", "mtime", 
                               "{}:{}".format(endpoint_remote, from_dir), 
                               "{}:{}".format(endpoint_local, to_dir), 
                               "--jq", "task_id", "--format", "UNIX"], 
        check=True)


# Use globus to load needed files from NCAR. Assumes you ran `globus login` from shell before:
CASENAME = 'b.e12.B1850C5.f19_g16.i21ka.03'
DOWNLOAD_PATH = os.getcwd()
atm_variables = ['PRECRC',
                'PRECRL',
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


DOWNLOAD_PATH = pathlib.Path(DOWNLOAD_PATH)
DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)

from_atm_template = '/gpfs/csfs1/univ/uazn0013/jiangzhu/archive/{}/atm/proc/tseries/monthly/{}/'
for variable in atm_variables:
    from_d = from_atm_template.format(CASENAME, variable)
    transfer(from_dir=from_d, to_dir=DOWNLOAD_PATH)

from_ocn_template = '/gpfs/csfs1/univ/uazn0013/jiangzhu/archive/{}/ocn/proc/tseries/monthly/{}/'
for variable in ocn_variables:
    from_d = from_ocn_template.format(CASENAME, variable)
    transfer(from_dir=from_d, to_dir=DOWNLOAD_PATH)
