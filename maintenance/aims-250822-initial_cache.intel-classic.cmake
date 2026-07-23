# FHI-aims 240507 — canonical MSE-HPC build (classic Intel, fully dynamic)
# Fortran: classic ifort 2021.13 (spack intel-oneapi-compilers-classic) via mpiifort
# C/C++  : LLVM icx/icpx via Intel MPI wrappers (classic icc no longer exists)
# Math   : MKL (Intel interface + Intel MPI BLACS)
# This mirrors the group's traditional Trace recipe (-O3 -ip -fp-model precise -diag-disable=10448).
# Fully dynamic linking: Intel Fortran runtime ships in intel-classic-2021.13-rt/;
# after building, strip the build-host RPATH (patchelf --remove-rpath) so all
# libs resolve via aims_env.sh's LD_LIBRARY_PATH.
set(TARGET_NAME aims.250822.ifort.scalapack.mpi.x CACHE STRING "")
set(CMAKE_EXE_LINKER_FLAGS "-shared-intel" CACHE STRING "")

set(CMAKE_Fortran_COMPILER mpiifort CACHE STRING "")
set(CMAKE_Fortran_FLAGS "-O3 -ip -fp-model precise -diag-disable=10448" CACHE STRING "")
set(Fortran_MIN_FLAGS "-O0 -fp-model precise" CACHE STRING "")

set(CMAKE_C_COMPILER mpiicx CACHE STRING "")
set(CMAKE_C_FLAGS "-O3 -fp-model precise -std=gnu99" CACHE STRING "")
set(CMAKE_CXX_COMPILER mpiicpx CACHE STRING "")
set(CMAKE_CXX_FLAGS "-O3 -fp-model precise" CACHE STRING "")

set(LIB_PATHS "$ENV{MKLROOT}/lib/intel64" CACHE STRING "")
set(LIBS "mkl_scalapack_lp64 mkl_blacs_intelmpi_lp64 mkl_intel_lp64 mkl_sequential mkl_core" CACHE STRING "")

set(USE_MPI ON CACHE BOOL "")
set(USE_SCALAPACK ON CACHE BOOL "")
set(USE_SPGLIB ON CACHE BOOL "")
set(USE_LIBXC ON CACHE BOOL "")
set(USE_HDF5 OFF CACHE BOOL "")
set(USE_RLSY ON CACHE BOOL "")
