# Stupid wrapper for `globus-cli` to load cesm files from NCAR server.

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

