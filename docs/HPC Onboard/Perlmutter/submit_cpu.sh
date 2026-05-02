#!/bin/bash
#SBATCH -J basic_training
#SBATCH -A m3578
#SBATCH -N 1
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -t HH:MM:SS              # CHANGE: wall-time, e.g. 02:00:00

module load vasp/6.4.3-cpu

# OpenMP settings (16 MPI ranks * 8 threads = 128 physical cores)
export OMP_NUM_THREADS=8
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

srun -n 16 -c 16 --cpu_bind=cores VASP_BINARY    # CHANGE: vasp_std / vasp_ncl / vasp_gam
