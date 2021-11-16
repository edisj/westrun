"""
WESTPA Command Line Interface
=============================

Module to hold classes that wrap the shell commands

"""

import os
import subprocess
from pathlib import Path
#from . import tools

class CommandBase:
    """A class to generate the explicit command that will be fed into a bash shell."""

    _important_variables = ['WEST_PYTHON', 'WEST_ROOT', 'WEST_BIN']

    def __init__(self, WEST_SIM_ROOT, *args, **kwargs):
        print(f'CommandBase __init__ called for {self.command_name}')
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

        cmd = self._build_command_line(command_name, args, kwargs)
        results = self._run_command(cmd)

        return results  # :)

    def _build_command_line(self, command_name, unprocessed_args, *args, **kwargs):

        # temporary hack
        if command_name == 'w_bins':
            command_name += ' info'
        # this is always the base command
        cmd = f"cd {self.WEST_SIM_ROOT} ; {self.WEST_BIN}/{command_name}"
        processed_args = self._process_args(args, kwargs)
        for flag, value in processed_args.items():
            cmd += f" {flag} {value}" if value is not None else f" {flag}"

        return cmd

    def _run_command(self, cmd, *args, **kwargs):

        bash = subprocess.check_output('which bash', shell=True).decode().strip()
        out = subprocess.run(cmd, shell=True, executable=bash)

        return out

    def _process_args(self, *args, **kwargs):
        """Put args in a dictionary where the keys are flags"""

        processed_args = {}
        for flag, value in kwargs.items():
            flag = str(flag)
            if value is not None:
                if len(flag) == 1:
                    processed_args.update({f'-{flag}': str(value)})
                elif value is True:
                    processed_args.update({f'--{flag}': None})
                else:
                    processed_args.update({f'--{flag}': value})
        #if any(args):
        #    for arg in args:
        #        processed_args.update({arg[0]: None})

        return processed_args

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
    from . import tools

    def __init__(self, WEST_SIM_ROOT, *args, **kwargs):
        print('WESTcli __init__ called!!')
        self.WEST_SIM_ROOT = Path(WEST_SIM_ROOT)
        self._available_w_commands = []
        self._missing_w_commands = []
        self._instantiate_tools()

    def _instantiate_tools(self):
        """instantiate each item in the tools.resgistry registry"""
        #from . import tools
        for clsname, cls in self.tools.registry.items():
            name = clsname.lower().split()[0]
            try:
                # now add our available WESTPA commands to this namespace
                # each element of _have_w_commands is an instantiation of a
                # 'W_*' class whose name in this namespace is 'w_*'
                # i.e. a 'W_bins" class becomes 'WESTcli.w_bins'
                # Each class inherits from CommandBase
                setattr(self, name, cls(self.WEST_SIM_ROOT)) # MAGIC METACLASS ??
                self._available_w_commands.append(name)
            except:
                self._missing_w_commands.append(name)


    """class W_Pdist:
        prog = 'w_pdist'

        def __init__(self, WEST_SIM_ROOT):
            super().__init__(WEST_SIM_ROOT)

            self.WEST_SIM_ROOT = Path(WEST_SIM_ROOT)

    def w_pdist(self, binexpr=None, **kwargs):
        cmd = self._cmd_base('w_pdist', kwargs)
        p = subprocess.run(cmd, shell=True, executable='/usr/bin/bash')
        print(p.stdout)

    class W_Bins:
        prog = 'w_bins'

        def __init__(self, WEST_SIM_ROOT):
            super().__init__(WEST_SIM_ROOT)
            self.WEST_SIM_ROOT = Path(WEST_SIM_ROOT)

    def w_bins(self, n=None, detail=False, **kwargs):

        if n is not None:
            assert n != 1
            kwargs.update({'n': n})
        if detail is True:
            kwargs.update({'detail': True})

        cmd = self._cmd_base('w_bins info', kwargs)
        p = subprocess.run(cmd, shell=True, executable='/usr/bin/bash')
        print(p.stdout)

    class W_Trace:
        prog = 'w_trace'

        def __init__(self, WEST_SIM_ROOT):
            super().__init__(WEST_SIM_ROOT)

            self.WEST_SIM_ROOT = Path(WEST_SIM_ROOT)

    def w_trace(self, n_iter, n_seg, **kwargs):

        cmd = self._cmd_base(f'w_trace {n_iter}:{n_seg}', kwargs)
        p = subprocess.run(cmd, shell=True, executable='/usr/bin/bash')
        print(p.stdout)

    class Plothist(CLIBase):
        pass



    def plothist(self, mode, input_file=None, dimension='0::pcoord', title=None, **kwargs):
        from wand.image import Image

        if title is None:
            title = mode
        else:
            title = f"'{title}'"  # extra '' for command line
        kwargs.update({'title': title})

        if input_file is None:
            if 'pdist.h5' not in [file.name for file in self.WEST_SIM_ROOT.glob('*')]:
                self.w_pdist()
            cmd = self._cmd_base(f'plothist {mode} pdist.h5 {dimension}', kwargs)
        else:
            cmd = self._cmd_base(f'plothist {mode} {input_file} {dimension}', kwargs)

        print(f'{cmd=}')
        p = subprocess.run(cmd, shell=True, executable='/usr/bin/bash')
        pdf = Image(filename='hist.pdf', resolution=100)

        return pdf"""


