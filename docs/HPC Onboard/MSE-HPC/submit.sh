#!/bin/bash
#SBATCH -J aims_job          # Job name
#SBATCH -N 1                 # Number of nodes
#SBATCH -n 28                # MPI tasks = cores on one MSE-HPC compute node
#SBATCH -p compute           # MSE-HPC partition (the default)
#SBATCH -t 01:00:00          # Wall-time limit (increase for longer runs)
#SBATCH -o job_%j.out        # SLURM stdout -> job_<jobid>.out
#SBATCH --exclude=c001,c015,c017  # known-flaky nodes (jobs hang; as of 2026-07) — remove once mse-it fixes them

ulimit -s unlimited

# --- FHI-aims: pre-built, shared group install on MSE-HPC -------------------
# The group maintains ONE shared FHI-aims build; you do not compile anything.
AIMS_DIR="/mnt/beegfs/27-735/programs/fhi-aims.250822"
AIMS_BIN="$AIMS_DIR/build/aims.250822.ifort.scalapack.mpi.x"
AIMS_ENV="$AIMS_DIR/aims_env.sh"

# Load the Intel compiler runtime + Intel MPI + MKL. aims_env.sh sets these up directly,
# so it works in batch jobs without `module load` (unavailable on compute nodes).
source "$AIMS_ENV"

export OMP_NUM_THREADS=1
mpirun -np 28 "$AIMS_BIN" > aims.out
