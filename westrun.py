"""
WESTPA Run Analyzer
===================

"""

from contextlib import contextmanager
import subprocess
from pathlib import Path
from .westcli import WESTcli
import pandas as pd
import numpy as np
import h5py


class WESTRun(WESTcli):

    def __init__(self, WEST_SIM_ROOT, *args, **kwargs):
        print ('WESTRun __init__ called!!')
        super(WESTRun, self).__init__(WEST_SIM_ROOT)

        self.root = Path(WEST_SIM_ROOT)
        self.run_name = self.root.stem
        # self._datasets = {}
        # self._parse_file_for_datasets() # fills above
        # self._generate_methods_from_datasets()


    @contextmanager
    def h5file(self):

        file_locked = None
        handle = None
        try:
            handle = h5py.File(self.root / 'west.h5', 'r')
            file_locked = False
        except OSError:
            print('File currently locked... making a copy')
            subprocess.run(['cp', self.root / 'west.h5', 'west_COPY.h5'])
            handle = h5py.File(self.root / 'west_COPY.h5', 'r')
            file_locked = True
        try:
            yield handle
        finally:
            handle.close()
            if file_locked:
                # deleting copy because the state of the file is always changing
                subprocess.run(['rm', self.root / 'west_COPY.h5'])

    @property
    def summary(self):

        with self.h5file() as f:
            dset = f['summary'][()]

        df = pd.DataFrame(dset)
        df.index.names = ['iteration']
        df.index += 1

        return df

    def get_iteration_data(self, n_iter=1):

        iter_ = f'iter_{str(n_iter).zfill(8)}'

        with self.h5file() as f:
            iter_group = f[f'iterations/{iter_}']
            seg_index = iter_group['seg_index'][()]
            n_segments = len(seg_index)
            try:
                gmx_performance = iter_group['auxdata/performance'][()]
            except KeyError:
                gmx_performance = [np.NaN for _ in range(n_segments)]
            try:
                Na_index = np.round(iter_group['auxdata/Na_distance'][:, 0])
                Na_distance = iter_group['auxdata/Na_distance'][:, 1]
            except KeyError:
                Na_index = Na_distance = [np.NaN for _ in range(n_segments)]

        # Create a nice dataframe
        df = pd.DataFrame(seg_index)
        df.insert(0, 'segment', df.index)
        iter_col = [n_iter for _ in range(n_segments)]
        df['iteration'] = iter_col
        df['gmx_performance'] = gmx_performance
        df['SOD_index'] = Na_index
        df['SOD_distance'] = Na_distance

        return df.set_index('iteration')
