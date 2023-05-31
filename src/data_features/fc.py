import numpy as np
import pandas as pd
from scipy.stats import moment, mode

def fc_homotopic(FC):
    NHALF = int(FC.shape[0]//2)
    return np.diag(FC, k=NHALF)

def _stats(array, prefix=''):
    if prefix:
        prefix += '_'
    stats = pd.Series(
            data = [ np.sum(array), np.max(array), np.min(array), np.mean(array), np.std(array) ],
            index = [ f'{prefix}'+ l for l in ['sum', 'max', 'min', 'mean', 'std']]
    )
    quantiles = pd.Series(
            data = np.quantile(array, [0.05, 0.25, 0.5, 0.75, 0.95]),
            index = [ f'{prefix}'+ l for l in ['q0.05', 'q0.25', 'q0.5', 'q0.75', 'q0.95']]
    )  
    return pd.concat([stats, quantiles])

def fc_stats(FC):
    fc_stats = _stats(FC, prefix='fc')
    fc_homotopic_stats = _stats(fc_homotopic(FC), prefix='fc_homotopic')
    return pd.concat([fc_stats, fc_homotopic_stats])

def fcd_stats(FCD, fcs, win_len=30, prefix='fcd_triu'):
    fcd_stats = _stats(np.triu(FCD, k=win_len), prefix=prefix)
    return pd.concat([fcd_stats])
    


def compute_fc(ts, positive=True):
    """
    Arguments:
        ts:       time series of shape [time,nodes]
        positive: if True, sets the negative values to zero

    Returns:
        FC: matrix of functional connectivity [nodes, nodes]
    """
    rsFC = np.corrcoef(ts)
    if positive:
        rsFC = rsFC * (rsFC > 0)
    rsFC = rsFC - np.diag(np.diag(rsFC))
    return rsFC


def compute_fcd(ts, win_len=30, win_sp=1):
    """
    Arguments:
        ts:      time series of shape [time,nodes]
        win_len: sliding window length in samples
        win_sp:  sliding window step in samples

    Returns:
        FCD: matrix of functional connectivity dynamics
        fcs: windowed functional connectivity matrices
    """
    n_samples, n_nodes = ts.shape
    fc_triu_ids = np.triu_indices(n_nodes, 1)
    n_fcd = len(fc_triu_ids[0])
    fc_stack = []


    for t0 in range( 0, ts.shape[0]-win_len, win_sp ):
        t1=t0+win_len
        fc = np.corrcoef(ts[t0:t1,:].T)
        fc = fc[fc_triu_ids]
        fc_stack.append(fc)

    fcs = np.array(fc_stack)
    FCD = np.corrcoef(fcs)
    return FCD, fcs

def compute_fcd_roi(ts, roi_idx, win_len=30, win_sp=1):
    """Compute dynamic functional connectivity with FC matrix filtered to selected regions.

    Arguments:
        ts:       time series of shape [time,nodes]
        roi_idx:  binary vector defining the ROI [nodes]
        win_len:  sliding window length in samples
        win_sp:   sliding window step in samples
    Returns:
        FCD: matrix of functional connectivity dynamics
        fcs: windowed functional connectivity matrices
        speed_fcd: rate of changes between FC frames
    """
    nn = ts.shape[1]
    mask = np.zeros((nn, nn))
    mask[np.ix_(roi_idx, roi_idx)] = 1  # making a mask

    return compute_fcd_filt(ts, mask, win_len, win_sp)

def compute_fcd_filt(ts, mat_filt, win_len=30, win_sp=1):
    """Compute dynamic functional connectivity with FC matrix filtering
    Arguments:
        ts:       time series of shape [time,nodes]
        mat_filt: binary matrix to act as the filter [nodes, nodes]
        win_len:  sliding window length in samples
        win_sp:   sliding window step in samples
    Returns:
        FCD: matrix of functional connectivity dynamics
        fcs: windowed functional connectivity matrices
        speed_fcd: rate of changes between FC frames
    """
    n_samples, n_nodes = ts.shape 
    fc_triu_ids = np.triu_indices(n_nodes, 1) #returns the indices for upper triangle
    n_fcd = len(fc_triu_ids[0]) #
    fc_stack    = []
    speed_stack = []
    for t0 in range( 0, ts.shape[0]-win_len, win_sp ):
        t1=t0+win_len
        fc = np.corrcoef(ts[t0:t1,:].T)
        fc = fc*(fc>0)*(mat_filt)
        fc = fc[fc_triu_ids]
        fc_stack.append(fc)
        if t0 > 0 :
            corr_fcd  = np.corrcoef([fc,fc_prev])[0,1]
            speed_fcd = 1-corr_fcd
            speed_stack.append(speed_fcd)
            fc_prev   = fc
        else:
            fc_prev   = fc
            
    fcs      = np.array(fc_stack)
    speed_ts = np.array(speed_stack)
    FCD = np.corrcoef(fcs)
    return FCD, fcs, speed_ts

