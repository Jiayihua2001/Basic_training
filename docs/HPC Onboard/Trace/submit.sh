#!/bin/sh
#SBATCH -J test 
#SBATCH -n 128 
#SBATCH -p batch
#SBATCH -t 1:00:00
#SBATCH -N 1 
#SBATCH -A marom
 
ulimit -s unlimited
ulimit -v unlimited
# Directory for aims binary and the env 
AIMS_DIR="/trace/group/marom/shared/programs/fhi_aims_latest/aims_bin"
AIMS_BIN="$AIMS_DIR/aims.240507.scalapack.mpi.x"
AIMS_ENV="$AIMS_DIR/aims_env.sh"

source $AIMS_ENV

export OMP_NUM_THREADS=1
mpirun -np 128 $AIMS_BIN > aims.out
