#!/bin/bash
#SBATCH --job-name=sweep_job
#SBATCH --account=ich042
#SBATCH --nodes=1
#SBATCH --ntasks=12
#SBATCH --cpus-per-task=1
#SBATCH --mem=62G
#SBATCH --time=00:30:00
#SBATCH --partition=normal
#SBATCH --constraint=gpu
#SBATCH --output="logs/slurm-%j.out"
#SBATCH --error="logs/slurm-%j.err"

srun="srun --exclusive -N1 -n1 -c1 -G0 --mem=5G"
parallel="parallel -N1 --delay .2 -j $SLURM_NTASKS --joblog runtask.log --resume"
echo $parallel
echo $srun

module load daint-gpu

source /scratch/snx3000/bp000275/virtual_ndd_brain/env/bin/activate
n_tasks=`python sweep.py params.npz`

$parallel "$srun python sweep.py {1} params.npz results > logs/parallel_{1}.log" ::: `seq 0 $((n_tasks-1))`

# debug with sacct -j XXX --format=JobID,Start,End,Elapsed,REQCPUS,NodeList,ALLOCTRES%40
# TODO: resume-failed or retry-failed
