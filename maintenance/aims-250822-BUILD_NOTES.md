# FHI-aims 250822 — MSE-HPC shared install (CANONICAL since 2026-07-19)

One binary is shipped for the course; students never compile.
Shared install: `/mnt/beegfs/27-735/programs/fhi-aims.250822/`
(`build/aims.250822.ifort.scalapack.mpi.x`, `aims_env.sh`, `intel-classic-2021.13-rt/`,
`species_defaults/` — student-facing only; maintainer material lives here.)

- **Source**: `fhi-aims.250822.tar.gz` (this folder's parent), unmodified — no patches.
- **Toolchain**: classic ifort 2021.13.1 via `mpiifort`; C/C++ `mpiicx`/`mpiicpx`
  (LLVM icx — classic icc no longer exists; its runtime is the system GNU
  libstdc++/libgcc, so the shipped binary needs NO oneAPI components); Intel MPI
  2021.17; MKL 2024.2; `-O3 -ip -fp-model precise`, fully dynamic (`-shared-intel`),
  build-host RPATH stripped with patchelf. Recipe: `initial_cache.intel-classic.cmake`
  (in this folder).
- **Rebuild recipe** (head node, `nice -n 19` + `-j 4` ONLY, one build at a time):
  1. Compiler (restored 2026-07-23 after the cleanup): spack clone at
     `~zefengc/spack-user` (spack 1.3.0.dev0), install tree under `~/.spack/opt/spack/`;
     `intel-oneapi-compilers@2024.2.1` — the last oneAPI bundle shipping classic ifort.
     `.../intel-oneapi-compilers-2024.2.1-r2ojqvw*/compiler/2024.2/bin/ifort`
     = `ifort (IFORT) 2021.13.1 20240703` (use `bin/`, NOT `bin32/`); its
     `compiler/2024.2/lib/` holds the redistributable Fortran runtime
     (`libifcoremt.so.5` etc.) that populates `intel-classic-2021.13-rt/`.
  2. Build env: system spack (`/home/.spack-system`) provides Intel MPI 2021.17
     (`mpiicx`/`mpiicpx`/`mpiifort` wrappers + icx 2025) and MKL 2024.2 (`MKLROOT`);
     prepend the spack classic `bin/` to PATH and set `I_MPI_F90=ifort` so `mpiifort`
     drives classic ifort. Verify before configuring: `mpiifort -v` → ifort 2021.13.1,
     `mpiicx -v` → icx.
  3. `cmake -C initial_cache.intel-classic.cmake <src>` then
     `nice -n 19 cmake --build . -j 4`; afterwards `patchelf --remove-rpath` on the
     binary and smoke-test H₂ through the student `submit.sh`
     (reference: −30.925050488 eV at d = 0.8 Å, pw-lda light).
- **Version-switch validation (2026-07-19)**: full tutorial campaign (507 runs) vs the
  240507 references — 505/507 agree to ≤7×10⁻⁸ eV; Ge LDA/PBE band eigenvalues identical
  to 4 decimals (zero-gap inversion in both versions — the old "0.115 vs 0.00 gap
  difference" was a printout artifact); HSE06 identical gap (Fermi-zero convention in the
  band files differs); only genuine change: Ge r²SCAN via the newer bundled libxc
  (constant total-energy shift ~1.87 eV; a 5.6891→5.6913 Å; gap 0.314→0.305 eV). Speed
  identical (18.62 vs 18.88 node-h; TCNQ medians within 1%). Species_defaults identical
  for all tutorial elements. Smokes through the student path bit-exact.
- **Rollback**: none retained — the 240507 binary, objects, and both maintainer source
  trees were deleted in the 2026-07-23 cleanup. If 250822 ever misbehaves, rebuild
  240507 from source with this same recipe (the campaign comparison above documents
  their equivalence).
