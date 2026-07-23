# FHI-aims 250822 — MSE-HPC shared install (CANONICAL since 2026-07-19)

One binary is shipped for the course; students never compile.
Shared install: `/mnt/beegfs/27-735/programs/fhi-aims.250822/`
(`build/aims.250822.ifort.scalapack.mpi.x`, `aims_env.sh`, `intel-classic-2021.13-rt/`,
`species_defaults/` — student-facing only; maintainer material lives here.)

- **Source**: `fhi-aims.250822.tar.gz` (this folder's parent), unmodified — no patches.
- **Toolchain**: identical to the retired 240507 canonical — classic ifort 2021.13.1
  (spack, `~zefengc/spack-user`) via `mpiifort`; C/C++ `mpiicx`/`mpiicpx`; Intel MPI
  2021.17; MKL 2024.2; `-O3 -ip -fp-model precise`, fully dynamic (`-shared-intel`),
  build-host RPATH stripped with patchelf. Recipe: `initial_cache.intel-classic.cmake`
  (in this folder). Build env + gentle-build rules: see the 240507 BUILD_NOTES rebuild
  section (same procedure; head node `nice -19 -j4` ONLY).
- **Version-switch validation (2026-07-19)**: full tutorial campaign (507 runs) vs the
  240507 references — 505/507 agree to ≤7×10⁻⁸ eV; Ge LDA/PBE band eigenvalues identical
  to 4 decimals (zero-gap inversion in both versions — the old "0.115 vs 0.00 gap
  difference" was a printout artifact); HSE06 identical gap (Fermi-zero convention in the
  band files differs); only genuine change: Ge r²SCAN via the newer bundled libxc
  (constant total-energy shift ~1.87 eV; a 5.6891→5.6913 Å; gap 0.314→0.305 eV). Speed
  identical (18.62 vs 18.88 node-h; TCNQ medians within 1%). Species_defaults identical
  for all tutorial elements. Smokes through the student path bit-exact.
- **Rollback**: the validated 240507 binary + objects remain in
  `~/software/fhi-aims.240507/build_ifort/`; redeploy per its BUILD_NOTES.
