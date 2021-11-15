"""
Configuration stuff
===================
Right now, I just want it to set up the shell environment

"""

import os
import subprocess

class WESTPAEnvironmentLoadingError(Exception):
    """Raised when WESTPA environment failed to build."""

def set_west_environment(w_env): # w_env must be westpa.sh
    """ Set the environment from *w_env*.

    Currently, I'm just doing this explicitly... maybe from a config file later?
    """

    envvars = ['WEST_ROOT', 'WEST_PYTHON', 'WEST_BIN',
               'PATH', 'LD_LIBRARY_PATH']

    bash = subprocess.check_output('which bash', shell=True).decode().strip()
    cmdargs = [f'. {w_env} && echo ___${{{var}}}___' for var in envvars]

    try:
        for var, cmd in zip(envvars, cmdargs):
            out = subprocess.check_output(cmd, shell=True, executable=bash)
            out = out.strip().decode().replace('___', '')  # remove sentinels WHY?
            os.environ[var] = out
    except (subprocess.CalledProcessError, OSError):
        errmsg = "Failed to load WESTPA environment"
        raise WESTPAEnvironmentLoadingError(errmsg)
