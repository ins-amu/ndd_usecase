#!/bin/bash
#SBATCH --job-name=sweep_job
#SBATCH --account=ich042
#SBATCH --ntasks=480
#SBATCH --cpus-per-task=2 
#SBATCH --time=06:00:00
#SBATCH --partition=normal
#SBATCH --constraint=gpu
#SBATCH --output="logs/slurm-%j.out"
#SBATCH --error="logs/slurm-%j.err"

# use -n2 if the nodes have hyperthredding
srun="srun --exclusive -N1 -n1 -G0 --mem=5G"
#parallel="parallel -N1 --delay .2 -j $SLURM_NTASKS --joblog logs/runtask.log --resume"
parallel="parallel -N1 --delay .2 -j $SLURM_NTASKS --joblog logs/runtask.log --retry-failed"
echo $parallel

module load daint-gpu

source /scratch/snx3000/bp000275/virtual_ndd_brain/env/bin/activate
n_tasks=`python sweep.py params.npz`

$parallel "$srun python sweep.py {1} params.npz results > logs/parallel_{1}.log" ::: `seq 0 $((n_tasks-1))`

