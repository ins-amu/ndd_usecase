import os
from glob import glob
from scipy.io.matlab import loadmat
import numpy as np
import pandas as pd
import re
from functools import cached_property
from tvb.simulator.lab import connectivity
from .utils import path
from .parcellation import Parcellation_88

class Synthetic:
    def __init__(self, data_root=None, parcellation=None):
        if data_root is None:
            data_root = path('publish/synthetic')
        self.data_root = data_root
        if parcellation is None:
            parcellation = Parcellation_88(data_root=self.data_root)
        self.parcellation = parcellation

    @cached_property
    def subjects(self):
        return self.subjects_metadata.index.tolist()

    @cached_property
    def subjects_metadata(self):
        return pd.read_csv(os.path.join(self.data_root, 'subjects.tsv'), sep='\t', index_col='id')

    def load_SC(self, subject, normalize=True):
        sc = np.load(os.path.join(self.data_root, 'SC', subject, f'{subject}_sc.npz'))['sc']
        if normalize:
            np.fill_diagonal(sc, 0.0)
            sc = sc / np.max(sc)
            sc = np.abs(sc)
        return sc

    def load_connectivity(self, subject, normalize=True):
        sc = self.load_SC(subject, normalize)
        conn = connectivity.Connectivity(weights=sc)
        conn.centres_spherical()
        conn.tract_lengths = np.ones_like(conn.weights)
        conn.region_labels = np.r_[self.parcellation.load_subject_region()]
        return conn

    def load_bold(self, subject, squeeze=True):
        ts = np.load(os.path.join(self.data_root, 'TS', subject, f'{subject}_ts.npz'))['bold_d']
        if squeeze:
            ts = ts.squeeze()
        return ts
