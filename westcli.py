"""
WESTPA Command Line Interface
=============================

Module to hold classes that wrap the shell commands

"""

import os
import subprocess
from pathlib import Path
from wand.image import Image
#from . import tools


class CommandBase:
    """A class to generate the explicit command that will be fed into a bash shell."""

    _important_variables = ['WEST_PYTHON', 'WEST_ROOT', 'WEST_BIN']

    def __init__(self, WEST_SIM_ROOT, *args, **kwargs):
        self.WEST_SIM_ROOT = Path(WEST_SIM_ROOT)
        self.WEST_PYTHON = None
        self.WEST_ROOT = None
        self.WEST_BIN = None
        # environment should have been built on import
        self._get_vars_from_environment()

    def _get_vars_from_environment(self):
        """Read the environment and set as instance attributes"""

        environ = os.environ
        WEST_vars_found = [var for var in self._important_variables if var in environ]
        vars_not_found = [var for var in self._important_variables if var not in WEST_vars_found]
        if vars_not_found:
            raise ValueError(f"{vars_not_found} was not found in environment")
        for var in WEST_vars_found:
            setattr(self, var, Path(environ[var]))

    def run(self, command_name, *args, **kwargs):
        """run the command with arguments"""

        processed_args = self._process_args(args, kwargs)
        cmd = self._build_command_line(command_name, processed_args)
        results = self._run_command(cmd)

        return results  # :)

    def _process_args(self, unprocessed_args, unprocessed_kwargs):
        """Put args in a dictionary where the keys are flags"""
        processed_args = {}
        if any(unprocessed_args):
            for arg in unprocessed_args:
                processed_args.update({arg: None})
        for flag, value in unprocessed_kwargs.items():
            flag = str(flag)
            if value is not None:
                if len(flag) == 1:
                    processed_args.update({f'-{flag}': str(value)})
                elif value is True:
                    processed_args.update({f'--{flag}': None})
                else:
                    processed_args.update({f'--{flag}': value})

        return processed_args

    def _build_command_line(self, command_name, processed_args):
        # the start of every command..
        cmd = f"cd {self.WEST_SIM_ROOT} ; {self.WEST_BIN}/{command_name} "
        for flag, value in processed_args.items():
            cmd += f"{flag} {value} " if value is not None else f"{flag} "

        return cmd

    def _run_command(self, cmd, *args, **kwargs):
        bash = subprocess.check_output('which bash', shell=True).decode().strip()
        out = subprocess.run(cmd, shell=True, executable=bash)

        if self.command_name == 'plothist':
            pdf = Image(filename=self.WEST_SIM_ROOT / 'hist.pdf', resolution=100)
            return pdf

        return out

    def __call__(self, *args, **kwargs):
        """Run the command!
        This method runs when the class constructor is called?
        """
        return self.run(self.command_name, *args, **kwargs)


class WESTcli:
    """ This class holds all of the WESTPA tools as class objects in its namespace.

    The idea here is to mix this with an instance of WESTRun.
    """

    # give this Class's namespace the registry of tools created in tools.py
    #from . import tools

    def __init__(self, WEST_SIM_ROOT, *args, **kwargs):
        self.WEST_SIM_ROOT = Path(WEST_SIM_ROOT)
        self._available_w_commands = []
        self._missing_w_commands = []
        self._instantiate_tools()

    def _instantiate_tools(self):
        """instantiate each item in the tools.resgistry registry"""
        from . import tools
        for clsname, cls in tools.registry.items():
            name = clsname.lower().split()[0]
            try:
                # now add our available WESTPA commands to this namespace
                # each element of _have_w_commands is an instantiation of a
                # 'W_*' class whose name in this namespace is 'w_*'
                # i.e. a 'W_bins" class becomes 'WESTcli.w_bins'
                # Each class inherits from CommandBase
                setattr(self, name, cls(self.WEST_SIM_ROOT)) # MAGIC CLASS FACTORY ??
                self._available_w_commands.append(name)
            except:
                self._missing_w_commands.append(name)


class Plothist(CommandBase):
    command_name='plothist'

    def __init__(self, dimension='0::pcoord', title=None, *args, **kwargs):
        print('Plothist __init__ called')
        super(Plothist, self).__init__()
        #self.mode = mode
        #self.input_file = input_file
        #self.dimension = dimension
        #if title is None:
        #    self.title = mode
        #else:
        #    self.title = f"'{title}'"  # extra '' for command line

    def _run_command(self, cmd, *args, **kwargs):
        print('_run_command called from Plothist')
        cmd = f'plothist {self.mode} {self.input_file}'
        bash = subprocess.check_output('which bash', shell=True).decode().strip()
        out = subprocess.run(cmd, shell=True, executable=bash)
        pdf = Image(filename='hist.pdf', resolution=100)

        return pdf
