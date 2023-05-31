from tvb_inversion.parameters import SimSeq, Metric, ParamGetter
from tvb_inversion.utils import load_params, run_single
from tvb.simulator.backend.nb_mpr import NbMPRBackend
from src.data.data_loader import Synthetic
from src.data_features.summary_statistics import BoldFCD
from tvb.simulator.lab import *
import sys
import numpy as np
# remember to run locally before submission

class ConnectivityGetter(ParamGetter):
    def __call__(self, subj_id):
        return Synthetic().load_connectivity(subj_id)

def init_seq(params, values):
    dset = Synthetic()
    return SimSeq(
        template = simulator.Simulator(
            model=models.MontbrioPazoRoxin(
                J = np.r_[14.5],
                eta = np.r_[-4.6],
                tau  = np.r_[1.0],
                Delta = np.r_[0.7]
            ),
            connectivity=dset.load_connectivity(dset.subjects[0]),
            coupling=coupling.Linear(),
            integrator=integrators.HeunStochastic(
                dt=0.0005,
                noise=noise.Additive(nsig=0.037*np.r_[1,2])
            ),
            monitors=[monitors.TemporalAverage(period=.1)],
            simulation_length=30_000
        ).configure(),
        params=params,
        values=values,
        getters=[ConnectivityGetter(),None]
    )


def init_metrics():
    return [BoldFCD()]

BACKEND=NbMPRBackend

# ---- Do not change below here
# monitor / debug with sacct -j XXX --format=JobID%20,Start%10,End%10,Elapsed,REQCPUS,NodeList,ALLOCTRES%40

def main(i_sim, params_file, results_folder):
    params, values = load_params(params_file)
    seq = init_seq(params, values)
    metrics = init_metrics()
    run_single(seq, i_sim, metrics, backend=BACKEND, checkpoint_dir=results_folder)

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
