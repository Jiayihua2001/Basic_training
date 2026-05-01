#!/bin/bash
#SBATCH -J vasp_job
#SBATCH -A <your_repo>          # e.g. m4055
#SBATCH -C cpu
#SBATCH -q regular              # use 'debug' for quick tests
#SBATCH -N 1
#SBATCH -t 02:00:00
#SBATCH -o slurm-%j.out

# VASP 6.4.3 (CPU build) on Perlmutter
module load vasp/6.4.3-cpu

# Hybrid MPI/OpenMP: 64 MPI ranks/node x 2 threads => 128 physical cores used
export OMP_NUM_THREADS=2
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

# Use vasp_ncl for SOC (LSORBIT=.TRUE.); vasp_gam for Gamma-only.
srun -n 64 -c 4 --cpu-bind=cores vasp_std > vasp.out
