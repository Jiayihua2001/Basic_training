#!/bin/bash
#SBATCH -J basic_training
#SBATCH -A m3578
#SBATCH -N 1
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -t corresponding_time

module load vasp/6.4.3-cpu

#OpenMP settings:
export OMP_NUM_THREADS=8
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

srun -n 16 -c 16 --cpu_bind=cores corresponding_vasp_binary