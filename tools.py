"""
Tools
=====

Module to make a nice registry of WESTPA commands

"""

import subprocess
from .westcli import CommandBase
west_tools = ('w_bins', 'w_truncate', 'w_fork', 'w_assign', 'w_trace', 'w_fluxanl',
              'w_ipa', 'w_pdist', 'w_succ', 'w_crawl', 'w_direct', 'w_select',
              'w_states', 'w_eddist', 'w_ntop', 'w_multi_west', 'plothist', 'ploterr')


class WESTPAToolLoadingError(Exception):
    """Raised when no WESTPA tool could be found."""


def tool_factory(clsname, command_name, base=CommandBase):
    """ Factory for WESTPA commands."""
    clsdict = {
        'command_name': command_name,
    }
    return type(clsname, (base,), clsdict)


def load_tools():
    """ Load the tools

    Parameters
    ----------

    Returns
    -------
    """

    cmds = west_tools
    tools = {}
    for cmd in cmds:
        try:
            out = subprocess.check_output([cmd, '--help'])
        except (subprocess.CalledProcessError, OSError):
            pass
        clsname = cmd.split()[0].title()
        tools[cmd] = tool_factory(clsname, cmd)
    if not tools:
        raise ValueError("Failed to load tools.")

    return tools


try:
    registry = load_tools()
except WESTPAToolLoadingError:
    errmsg = "Autoloading was unable to load any Gromacs tool"
    raise WESTPAToolLoadingError(errmsg)

# Add registry of classes to this modules scope!
globals().update(registry)
__all__ = list(registry.keys())