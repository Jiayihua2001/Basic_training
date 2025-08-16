#!/bin/sh
#SBATCH -J exercise
#SBATCH -n 1
#SBATCH -p cpu
#SBATCH -N 1
#SBATCH -A marom

ulimit -s unlimited
ulimit -v unlimited
# Directory for aims binary and the env
AIMS_DIR="/home/27735A_group/shared/fhi_aims_2023/aims_bin/"
AIMS_BIN="$AIMS_DIR/aims.221103.scalapack.mpi.x"
AIMS_ENV="$AIMS_DIR/aims_env.sh"

source $AIMS_ENV

export OMP_NUM_THREADS=1
mpirun -np 1 $AIMS_BIN > aims.out
