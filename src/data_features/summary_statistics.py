import numpy as np
from .fc import compute_fcd, compute_fcd_filt
from tvb_inversion.parameters import Metric
from ..simulation import tavg_to_bold

def compute_summary_statistics(bold_d, win_len, win_sp):
    N = bold_d.shape[2]
    NHALF = N//2
    _ , inter_mask = get_masks(N)
    rsFC = compute_fc(bold_d[:,0,:,0].T)        
    HOMO_FC = np.mean(np.diag(rsFC,k=NHALF))
    FCD, _ = compute_fcd(bold_d[:,0,:,0], win_len=win_len, win_sp=win_sp)
    FCD_inter, fc_stack_inter, _ = compute_fcd_filt(bold_d[:,0,:,0], mat_filt=inter_mask, win_len=win_len, win_sp=win_sp )
    FCD_STACK_STD_INTER_TENS  = np.std(fc_stack_inter) # FCD_OSC_OV_INTER_vect
    FCD_VAR_OV_vect           = np.var(np.triu(FCD, k=win_len))
    FCD_VAR_OV_INTER_vect     = np.var(np.triu(FCD_inter, k=win_len))
    FCD_SUBJ_DIFF_VAR_OV_TENS = FCD_VAR_OV_INTER_vect - FCD_VAR_OV_vect # this could be easily done in the final dataframe
    FC_SUM = np.sum(np.abs(rsFC)) - np.trace(np.abs(rsFC))
    FCD_SUM = np.sum(np.abs(np.triu(FCD, k=win_len) + np.tril(FCD, k=-win_len))) 
    return HOMO_FC, FCD, FCD_inter, FCD_STACK_STD_INTER_TENS, FCD_SUBJ_DIFF_VAR_OV_TENS, FC_SUM, FCD_SUM



def get_masks(N):
    intra_mask = np.zeros((N,N), dtype=np.bool)
    N = N//2
    intra_mask[:N,:N] = 1
    intra_mask[N:,N:] = 1
    inter_mask = ~intra_mask
    return intra_mask, inter_mask


class BoldFCD(Metric): # pack all necessary functions to the metric callable
    def compute_summary_statistics(self,bold_d):
        FCD, _ = compute_fcd(bold_d[:,0,:,0], win_len=self.win_len, win_sp=self.win_sp)
        FCD_VAR = np.var(np.triu(FCD, k=self.win_len))
        return [FCD_VAR]

    def __init__(self, win_len=20, win_sp=1):
        self.win_len = win_len
        self.win_sp  = win_sp
        self.n_vals = 9
        self.summary_stats_labels = [ 'FCD_VAR' ]
        self.summary_stats_idx = [2,] # first two are the BOLD time series


    def __call__(self, t, y):
        t *= 10.
        if np.any(np.isnan(y)):
            print("NaN in the simulated time series")
            return np.array([None]*self.n_vals) # there should be a better way
        bold_t, bold_d = tavg_to_bold(t, y, tavg_period=1.) # TODO check for NaN and skip next steps in that case
        if np.any(np.isnan(bold_d)):
            print("NaN in the simulated BOLD")
            return np.array([None]*self.n_vals) # there should be a better way

        return np.array(
            [bold_t, bold_d, *self.compute_summary_statistics(bold_d)], dtype=object
        )# this is abuse

