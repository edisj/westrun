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
import matplotlib.pyplot as plt

class WESTRun(WESTcli):

    def __init__(self, WEST_SIM_ROOT, *args, **kwargs):
        super(WESTRun, self).__init__(WEST_SIM_ROOT)

        self.root = Path(WEST_SIM_ROOT)
        self.run_name = self.root.stem

    @contextmanager
    def h5file(self):

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

    def assign_h5(self):
         return h5py.File(self.WEST_SIM_ROOT / 'ANALYSIS/BIN_FLUX/assign.h5')

    def direct_h5(self):
        return h5py.File(self.WEST_SIM_ROOT / 'ANALYSIS/BIN_FLUX/direct.h5')

    @property
    def summary(self):

        with self.h5file() as f:
            dset = f['summary'][()]

        df = pd.DataFrame(dset)
        df.index.names = ['iteration']
        df.index += 1

        return df

    @property
    def conditional_fluxes(self):
        with self.direct_h5() as f:
            return f['conditional_fluxes'][()]

    @property
    def conditional_flux_evolution(self):
        with self.direct_h5() as f:
            return f['conditional_flux_evolution'][()]

    @property
    def total_fluxes(self):
        with self.direct_h5() as f:
            return f['total_fluxes'][()]

    @property
    def target_flux_evolution(self):
        with self.direct_h5() as f:
            return f['target_flux_evolution'][()]

    @property
    def rate_evolution(self):
        with self.direct_h5() as f:
            return f['rate_evolution'][()]

    def _make_flux_matrices(self, dataset):

        try:
            return dataset['expected']
        except IndexError:
            return dataset



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

    def plot_conditional_fluxes(self):

        with self.direct_h5():
            conditional_fluxes = self.conditional_fluxes

        flux_matrices = self._make_flux_matrices(conditional_fluxes)
        Pi_bins = {}
        n_iters = len(flux_matrices)
        array = np.empty((n_iters, 14), dtype=np.float64)

        for iteration, matrix in enumerate(flux_matrices):
            sum_J_ji = np.sum(matrix, axis=1)
            sum_J_ij = np.sum(matrix, axis=0)
            Pi = sum_J_ji - sum_J_ij
            array[iteration] = Pi

        for i in range(14):
            Pi_bins[f'bin_{i + 1}'] = array[:, i]

        fig, ax = plt.subplots(1, 1, figsize=(14,8))
        for key, value in Pi_bins.items():
            ax.plot(value, label=key)

    def plot_conditional_flux_evolution(self):

        with self.direct_h5():
            conditional_flux_evolution = self.conditional_flux_evolution

        flux_matrices = self._make_flux_matrices(conditional_flux_evolution)
        Pi_bins = {}
        n_iters = len(flux_matrices)
        array = np.empty((n_iters, 14), dtype=np.float64)

        for iteration, matrix in enumerate(flux_matrices):
            sum_J_ji = np.sum(matrix, axis=1)
            sum_J_ij = np.sum(matrix, axis=0)
            Pi = sum_J_ji - sum_J_ij
            array[iteration] = Pi

        for i in range(14):
            Pi_bins[f'bin_{i+1}'] = array[:,i]

        fig, ax = plt.subplots(1, 1, figsize=(14, 8))

        for key, value in Pi_bins.items():
            ax.plot(value, label=key)


