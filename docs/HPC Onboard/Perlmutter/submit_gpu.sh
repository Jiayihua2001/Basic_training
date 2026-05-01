#!/bin/bash
#SBATCH -J basic_training
#SBATCH -A m3578
#SBATCH -N 1
#SBATCH -C gpu
#SBATCH -G 4
#SBATCH -q regular
#SBATCH --exclusive
#SBATCH -t corresponding_time

module load vasp/6.4.3-gpu

export NCCL_IGNORE_CPU_AFFINITY=1

#OpenMP settings:
export OMP_NUM_THREADS=1
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

srun -n 4 -c 32 --cpu_bind=cores --gpu-bind=none -G 4 corresponding_binary
