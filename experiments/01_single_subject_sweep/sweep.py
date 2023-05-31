from tvb_inversion.parameters import SimSeq, Metric
from tvb_inversion.utils import load_params, run_single
from src.data_features.fc import compute_fcd
from src.simulation import tavg_to_bold
from tvb.simulator.lab import *
from src.data.data_loader import Synthetic
from tvb.simulator.backend.nb_mpr import NbMPRBackend
import numpy as np
import sys

def init_seq(params, values):
    dset = Synthetic()
    conn = dset.load_connectivity(dset.subjects[0])
    conn.speed = np.r_[np.inf]
    conn.configure() # to compute number of connections etc. to be shown below

    return SimSeq(
        template = simulator.Simulator(
            model=models.MontbrioPazoRoxin(
                J = np.r_[14.5],
                eta = np.r_[-4.6],
                tau  = np.r_[1.0],
                Delta = np.r_[0.7]
            ),
            connectivity=conn,
            coupling=coupling.Linear(),
            integrator=integrators.HeunStochastic(
                dt=0.01,
                noise=noise.Additive(nsig=0.037*np.r_[1,2])
            ),
            monitors=[monitors.TemporalAverage(period=.1)],
            simulation_length=30_000
        ).configure(),
        params=params,
        values=values
    )


def init_metrics():
    return [BoldFCD()]
    
    
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
            log.error("NaN in the simulated time series")
            return np.array([None]*self.n_vals) # there should be a better way
        bold_t, bold_d = tavg_to_bold(t, y, tavg_period=1.) # TODO check for NaN and skip next steps in that case
        if np.any(np.isnan(bold_d)): 
            log.error("NaN in the simulated BOLD")
            return np.array([None]*self.n_vals) # there should be a better way
  
        return np.array(
            [bold_t, bold_d, *self.compute_summary_statistics(bold_d)], dtype=object
        )# this is abuse
  




# ---- Do not change below here

def main(i_sim, params_file, results_folder):
    params, values = load_params(params_file)
    seq = init_seq(params, values)
    metrics = init_metrics()
    print('running sim ', i_sim)
    run_single(seq, i_sim, metrics, backend=NbMPRBackend, checkpoint_dir=results_folder)

def seq_length(params_file):
    params, values = load_params(params_file)
    return len(values)
    
       
if __name__ == '__main__':
    if len(sys.argv) == 2:
        print(seq_length(sys.argv[1]))
        sys.exit(0)
    elif len(sys.argv) != 4:
        print('usage: sweep.py item params.npz result_folder')
        sys.exit(1)
    item, params_file, results_folder = sys.argv[1:]
    item = int(item)
    main(item, params_file, results_folder)
