import os
import globus_icesm

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


from_atm_template = '/gpfs/csfs1/univ/uazn0013/jiangzhu/archive/{}/atm/proc/tseries/monthly/{}/'
for variable in atm_variables:
    from_d = from_atm_template.format(CASENAME, variable)
    globus_icesm.transfer(from_dir=from_d, to_dir=DOWNLOAD_PATH)

from_ocn_template = '/gpfs/csfs1/univ/uazn0013/jiangzhu/archive/{}/ocn/proc/tseries/monthly/{}/'
for variable in ocn_variables:
    from_d = from_ocn_template.format(CASENAME, variable)
    globus_icesm.transfer(from_dir=from_d, to_dir=DOWNLOAD_PATH)
