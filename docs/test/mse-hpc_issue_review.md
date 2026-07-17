# MSE-HPC migration — detailed issue review

Companion to `mse-hpc_validation_log.md`. One section per issue: the symptom a student would hit, the root cause, the exact fix, and how the fix was verified. Grouped by layer:

- **A. Cluster / environment** (found while deploying FHI-aims on MSE-HPC)
- **B. Helper scripts** in `Tutorials_files.zip`
- **C. Tutorial web pages** (`docs/`)
- **D. FHI-aims version-behavior gotchas** (documented in the tutorials rather than "fixed" — they are properties of the new code version)
- **E. Operational incidents** (cluster-side, not code)

---

## A. Cluster / environment issues

### A1. `module load` silently does nothing in batch jobs (and Lmod doesn't exist on compute nodes)

- **Symptom:** a submit script with `module load intel-oneapi-…` runs, but the compiler/MPI is missing: `ifx: command not found`, or MPI libraries not found at runtime. On compute nodes even the fallback `$LMOD_CMD` path (`/opt/ohpc/admin/lmod/...`) does not exist.
- **Root cause:** the `module` shell function is initialized only for interactive login shells on the head node. SLURM batch shells on compute nodes never get it, and the Lmod installation itself is not shared to the compute-node image.
- **Fix:** `aims_env.sh` (shipped in the shared install, sourced by `submit.sh` inside the job) sets up the toolchain by **sourcing the vendor environment scripts via absolute BeeGFS paths** — no `module` involved:
  ```bash
  _OMPI=/home/.spack-system/opt/spack/linux-broadwell/openmpi-5.0.8-…
  export PATH="$_OMPI/bin:$PATH"; export LD_LIBRARY_PATH="$_OMPI/lib:$LD_LIBRARY_PATH"
  source …/intel-oneapi-mkl-2024.2.2-…/mkl/2024.2/env/vars.sh
  ```
- **Verified:** tested in a scrubbed environment (`env -i bash -c 'source aims_env.sh; …'`) and in real sbatch jobs on multiple compute nodes.

### A2. Every MPI job aborts in `MPI_Init` under SLURM (`openib` / `vader` components)

- **Symptom:** any `mpirun`/`srun` job dies instantly with
  `A requested component was not found … Framework: btl, Component: openib`, then
  `*** An error occurred in MPI_Init`, `mca_base_framework_open on ompi_bml failed → "Not found"`.
  The same binary + mpirun works fine on the head node.
- **Root cause:** the cluster's site configuration injects `OMPI_MCA_btl=openib,self,vader` (plus `OMPI_MCA_btl_openib_if_include=ibs1`) into every SLURM job's environment. That component list is for **Open MPI ≤ 4**: in Open MPI 5 `openib` was removed and `vader` was renamed `sm`. With no valid transport in the list, `MPI_Init` finds no BTL and aborts.
- **Fix:** `aims_env.sh` overrides the injected values with components this build actually has:
  ```bash
  export OMPI_MCA_btl="self,sm,tcp"   # self+sm intra-node, tcp inter-node
  export OMPI_MCA_pml="ob1"
  unset OMPI_MCA_btl_openib_if_include OMPI_MCA_btl_openib_warn_default_gid_prefix
  ```
- **Verified:** the identical job that failed (H₂, 28 ranks) completes after the override; ~460 subsequent jobs ran with it. Note: inter-node traffic is TCP (this Open MPI has no OFI/UCX/PSM2 for OmniPath) — irrelevant for the single-node tutorial jobs, suboptimal for large multi-node work.

### A3. Intel `ifx` rejects the pristine FHI-aims source → GNU toolchain

- **Symptom:** build fails at ~91% with `error #5145: Invalid blank/tab` in `src/rt-tddft/*.f90` (continued string literals).
- **Root cause:** MSE-HPC has only the LLVM-based `ifx` 2025 (classic `ifort` was dropped from oneAPI 2025). `ifx` is stricter about a legacy free-form continuation style used in a handful of rt-tddft files; `ifort` and `gfortran` both accept it.
- **Wrong fix, reverted:** an initial attempt patched the 19 offending continuation lines. That worked but violates the no-source-modification principle (breaks provenance and future updates) and was fully reverted (rt-tddft re-extracted from the tarball).
- **Right fix:** build the **unmodified** source with the **GNU toolchain**, exactly mirroring the group's official *NERSC Perlmutter Cray-GNU* recipe: `mpif90`(gfortran 11.5) with `-O3 -fallow-argument-mismatch -ffree-line-length-none`, MKL for BLAS/LAPACK/ScaLAPACK via the GNU interface (`mkl_gf_lp64` + `mkl_blacs_openmpi_lp64`). Recipe stored as `initial_cache.mse-hpc.cmake` in the shared folder.
- **Verified:** clean configure + full build from pristine source; binary links spglib/libxc/ELPA/ScaLAPACK/s-dftd3 (checked with `nm`); physics validation below.

### A4. Compute nodes have no C++ development headers

- **Symptom:** compiling on a compute node fails with `icpx/g++: error: C++ header location not resolved` (no `/usr/include/c++`).
- **Root cause:** the compute-node OS image ships compiler *runtimes* (libstdc++.so) but not the development headers; only the head node has the full toolchain.
- **Fix / practice:** the one-time build runs on the **head node** (throttled: `-j 16` of 56 cores, `renice +19`); the resulting binary runs on all nodes (runtime libs are present). Documented in `BUILD_NOTES.md`. Students never compile.
- **Verified:** binary executes on c001–c042 nodes across the simulation.

### A5. cmake 4.x cannot configure the bundled libraries

- **Symptom:** `CMake Error: Compatibility with CMake < 3.5 has been removed` from bundled subprojects (spglib/ELPA-era CMakeLists with `cmake_minimum_required(VERSION 3.0/3.1)`).
- **Root cause:** cmake 4 removed compatibility shims the old bundled build files rely on.
- **Fix:** pin `cmake<4` (3.31.x) in the `ase_env` conda environment; noted in `BUILD_NOTES.md` rebuild instructions.
- **Verified:** configure passes with 3.31.10, fails with 4.4.0.

---

## B. Helper-script issues (in `Tutorials_files.zip`)

### B1. `distance_generator.py` silently dropped the documented 1.0 Å endpoint

- **Symptom:** Tutorial 1 says "bond lengths from 0.5 Å to 1.0 Å at a step 0.1"; the helper creates only `H2_0.5 … H2_0.9`. A careful student notices the missing point; a careless one plots a curve that stops at 0.9.
- **Root cause:** `np.arange(0.5, 1.0, 0.1)` **excludes** the upper bound. The in-code comment even said "use `np.arange(0.5, 1.1, 0.1)` to include 1.0" — the code didn't match its own comment.
- **Fix:**
  ```python
  # before
  distances = np.arange(0.5, 1.0, 0.1)
  # after  (upper bound 1.05 so the 1.0 endpoint survives float rounding)
  distances = np.arange(0.5, 1.05, 0.1)
  ```
- **Verified:** regenerated set contains `H2_1.0`; its energy (−30.359 eV) sits correctly on the dissociation curve.

### B2. `Automation.py --plot_k_grid` produced scrambled convergence plots

- **Symptom:** the k-point convergence plot connects points in random order ("spaghetti"), and the derivative panel |dE/dn| is computed between *wrong neighbor pairs* — a student can't identify the converged k from it.
- **Root cause:** the function iterated `os.listdir()` (arbitrary order: 10, 11, 12, 4, 5, …), appending x and y independently; also `int(dirname)` was outside the `try`, so any non-numeric directory crashed it.
- **Fix:** collect `(k, E)` pairs, `pairs.sort()` before plotting; catch `ValueError/FileNotFoundError/OSError` per directory.
- **Verified:** ran in Si (4–12), Na, Fe BCC/FCC (10–18) kpts folders — monotonic/ordered plots; non-numeric sibling dirs ignored.

### B3. `Automation.py --Fe_grid_search`: "magnetic" scans were silently non-magnetic (worst bug of the set)

- **Symptom:** a student following §2.3 (magnetic vs non-magnetic Fe lattice scans) gets **identical energies for both** in BCC — the "ferromagnetic" curve is actually the non-magnetic one. The assignment's central comparison (LDA vs PBE ground state of Fe) silently produces wrong conclusions.
- **Root cause:** the script appended `initial_moment 2` **only for FCC** (and only once, at end-of-file). For BCC, `spin collinear` ran with zero initial moment → SCF converges to the non-magnetic solution. (The doc's claim "ASE includes initial_moment automatically" is only true for elements where ASE carries a default magnetic moment.)
- **Fix (two iterations):**
  1. Detect the magnetic case from `control.in` (`spin collinear`, comment-safe parsing) and insert `initial_moment 2` after **every** atom line, both lattices.
  2. Refinement discovered during simulation: ASE's `bulk('Fe')` *itself* writes `initial_moment 2.3`, so blind insertion created a duplicate line per atom (FHI-aims tolerated it — verified — but it's wrong). Final version inserts only when the next line isn't already an `initial_moment`:
  ```python
  magnetic = <control.in contains "spin collinear">
  ...
  if line.lstrip().startswith("atom") and "initial_moment" not in next_line:
      f.write("initial_moment 2\n")
  ```
- **Verified:** magnetic runs converge to m ≈ 2.0–2.6 μB (BCC) and the mag/non-mag curves now differ exactly as they should; PBE ground state comes out FM-BCC with a = 2.832 Å, m = 2.19 μB (exp 2.87 Å / 2.22 μB).

### B4. `Automation.py` Fe scans dropped the documented 4.5 Å endpoint

- **Symptom:** doc says "scan 2.0–4.5 Å, step 0.25"; folders stop at 4.25.
- **Root cause:** same `np.arange` end-exclusion as B1, in both `make_Fe_grid_search` and `plot_Fe_grid_search` (the two must stay consistent — the plot builds its x-axis from the same `arange`).
- **Fix:** upper bounds 4.55 in both places (0.25 steps are exact in binary, so folder names stay clean: `4.5`).
- **Verified:** 11 BCC / 7 FCC points per combo, including 4.5; plot reads them all.

### B5. `Automation.py --plot_Fe_grid_search` crashed on unconverged points

- **Symptom:** if any single lattice point lacks a converged energy (see D6 — magnetic FCC at stretched *a* genuinely fails SCF), the plot function appended nothing for it, mis-aligning x and y (`ValueError` or silently shifted curve).
- **Fix:** per-point energy extraction with explicit skip + warning:
  `Warning: no converged energy in 3.5/aims.out - skipping this point (SCF may not have converged; try a larger smearing …)`.
- **Verified:** ran on the LDA/FCC/mag folder while its 3.5 Å point was still unconverged — correct plot from the remaining points plus the warning.

### B6. `Surfaces.py` distance scans dropped the 4.5 Å endpoint

- **Symptom:** Tutorial 3 Assignment 2 says "scan 3.0 to 4.5 Å, step 0.1"; the scan created 15 folders (3.0–4.4). The binding-curve minimum (~3.3–3.5 Å) is unaffected, but the deliverable doesn't match the assignment text.
- **Root cause:** same `arange` pattern in two places — the default range (`np.arange(3.0, 4.5, 0.1)`) and the CLI path (`np.arange(args.distance_min, args.distance_max, args.distance_step)`). (The height-scan code path already handled its endpoint correctly — inconsistency within the same file.)
- **Fix:** default → `np.arange(3.0, 4.55, 0.1)`; CLI → `np.arange(min, max + step/2, step)` (half-step guard avoids a duplicated point from float drift).
- **Verified:** 16 folders per scan (d_3.00 … d_4.50); backfilled the six already-running scans with the missing 4.5 point.

### B7. Bundle hygiene: dead placeholder files

- **Symptom:** `Tutorial_2/` in the zip contained **0-byte** `control.in` and `submit.sh`. A student reasonably assumes those are the files to use (they're not — `write_control.py` generates control.in; `~/submit.sh` comes from setup) and gets confusing failures (`Automation.py` would even accept the empty files and submit empty jobs).
- **Fix:** removed the empty files (and stray `.DS_Store`s) from the bundle.
- **Verified:** re-zipped bundle contains 43 real files; `Automation.py`'s explicit existence checks now fail fast with a clear message if a student forgets to create control.in.

### B8. Cluster-selection layer of the bundle (from the migration itself)

- `setup_utils.sh`: `arjuna` option replaced by `mse-hpc` (usage text + validation).
- New `utils/mse-hpc/submit.sh`: 28 MPI ranks / 1 node / `compute` partition; sources the **shared** `aims_env.sh`; runs the **shared** binary from `/mnt/beegfs/27-735/programs/fhi-aims.250822/`.
- New `utils/mse-hpc/write_control.py`: `BASE_SPECIES_PATH` → shared `species_defaults/defaults_2020`.
- `utils/arjuna/` removed.
- **Verified:** fresh-unzip + `bash setup_utils.sh mse-hpc` + every tutorial command in sequence (that's the whole simulation).

---

## C. Tutorial web-page issues

### C1. Tutorial 2 sent students to an Arjuna-only path

- **Was:** "Always copy the Tutorials to your working directory first from `/home/27735A_group/shared/example`" — that path exists only on Arjuna (dead cluster).
- **Now:** points to the `Tutorials_files` bundle from the Quick Onboard.

### C2. Stale "activate your `aims_env`" step (Tutorial 1)

- **Was:** "Before submitting jobs, please make sure you have activated your `aims_env`" — an Arjuna-era manual step; there is no such conda env in the new workflow, and a student would go hunting for one.
- **Now:** "`submit.sh` loads the FHI-aims runtime environment automatically inside the job…" (true on both Trace and MSE-HPC — both submit scripts source their `aims_env.sh`).

### C3. DOS example: wrong energy-reference comment, then an FHI-aims mesh rule (Tutorial 2)

- **Was:** `output dos_tetrahedron -18.0 0.0 2000` with the comment "*2000 points from −18 eV up to the Fermi level*".
- **The real defect is the comment, not the range:** the `emin/emax` of `output dos`/`output dos_tetrahedron` are on FHI-aims' **absolute Kohn–Sham energy scale, not relative to E_F**. FHI-aims writes two files per run: `KS_DOS_total_raw*.dat` (absolute; spans exactly emin…emax) and `KS_DOS_total*.dat` (shifted so E_F = 0; spans emin−μ…emax−μ — the one `aimsplot.py` plots). Verified empirically on the Si run: μ = −5.602 eV, raw file spans −18.00…10.00, shifted file spans −12.40…+15.60. So the *original* −18…0 window actually plotted −12.4…+5.6 eV around E_F (the conduction band **was** visible); but a student reading "up to the Fermi level" would completely misunderstand what the numbers mean and mis-choose windows for other systems.
- **Second issue found while fixing:** widening the window to `-18.0 10.0` while keeping 2000 points makes FHI-aims **abort** — `dos_tetrahedron` requires a mesh ≤ 0.01 eV between points (28 eV / 2000 = 0.014 eV). Caught because the Si band job died with exactly that error.
- **Final (per review decision):** the **original range `-18.0 0.0 2000` is kept** — since the window is absolute, it already covers the gap region (≈ −12.4…+5.6 eV around E_F for Si) and satisfies the mesh rule (0.009 eV/pt). Only the **comment** is corrected: it now states the absolute-scale convention, the raw-vs-shifted output files, and the ≤ 0.01 eV mesh rule for anyone widening the window.
- **Verified:** Si band runs pass with both the original and the widened window (validation used the wide one); both DOS files show the expected ranges; `aimsplot.py` renders the shifted one.

### C4. New tips added to the pages for the version-behavior gotchas (details in section D)

- Tutorial 1: tiny-systems MPI-task tip (D2); `initial_charge` requirement for IP/EA (D1).
- Tutorial 2: SCAN/HSE06 relaxation tips (D3); per-point smearing note for frustrated metallic SCF (D6).
- Tutorial 3: "vac 10 Å refusing to run *is* the data point" note (D5).

### C5. Cluster-migration edits (for completeness)

- `docs/index.md` (Quick Onboard): Trace/**MSE-HPC** track, `setup_utils.sh mse-hpc`.
- `docs/HPC Onboard/index.md`: MSE-HPC bullet replaces Arjuna.
- **New page** `docs/HPC Onboard/MSE-HPC/index.md`: login, transfer, hardware table, shared FHI-aims location (no compilation for students), `ase_env` setup, downloadable `submit.sh`.
- `docs/HPC Onboard/Arjuna/` deleted; `linux_basic` ssh example updated; `README.md` cluster list updated.
- All Arjuna references gone except the intentional "replacing the now-deprecated Arjuna".

---

## D. FHI-aims 250822 behavior changes / gotchas

> **Post-review policy change:** these were originally handled with explanatory tip boxes. Per review, the tutorials now **route around them** so students never hit the errors; the long explanations were removed. Current state per item:
> - **D1**: the `initial_charge ±1.` line is simply part of the instructions now (one short clause of why; the version-history sentence removed).
> - **D2**: the dissociation scan now includes a **6.0 Å reference point** (doc + `distance_generator.py`), so the bond energy comes straight off the plot and no single-atom run is ever needed; the tiny-systems tip box was removed.
> - **D3**: §3.3 now *prescribes* the working method per functional (LDA/PBE: cell relax; SCAN: energy-vs-a scan; HSE06: start from the PBE geometry) instead of offering workaround tips.
> - **D5**: all vacuum series now **start at 15 Å** (Tutorial 3 §1.4, Assignment 1, §2.3, and the `Surfaces.py` default), so the dipole-correction refusal at 10 Å can't occur; the note about it was removed.
> - **D6**: the per-point smearing advice is now a single line in the existing smearing box.
> - **D4**: kept as a one-line comment in the DOS example (it only matters if a student widens the window).
>
> The subsections below are kept as the *reference record* of what the underlying behaviors are and how they were diagnosed.

### D1. Charged calculations now **stop** without `initial_charge` (breaks the old IP/EA recipe)

- **Symptom:** every IP/EA run (`charge +1.`/`-1.` in control.in) aborts immediately:
  `* Error: Initial charge and total charge of the system are inconsistent. Selected charge in control.in: 1.0000 / Sum of initial charges in geometry.in: 0.0000 … we stop here by default`.
- **Why now:** the Arjuna/Trace-era versions (221103/240507) only warned; 250822 makes it a hard stop (there *is* an escape hatch, `override_initial_charge_check .true.`, but the code's own advice — initialize the density near the target charge — is better practice and better pedagogy).
- **Fix in the tutorial:** the instruction "add `initial_moment 1` after the first atom" now reads "add `initial_moment 1` **and** `initial_charge 1.`" (−1. for EA), with a sentence explaining the version behavior.
- **Verified:** all four runs (IP/EA × vertical/adiabatic) complete; **vertical IP 11.130 eV vs experiment ≈ 11.15 eV**; orderings correct (adiabatic IP < vertical IP; adiabatic EA > vertical EA).

### D2. Single atoms crash on a full node (`n_basis too small for this processor grid`)

- **Symptom:** an H-atom run on the standard 28-task node dies:
  `Tasks: 28 split into 7 X 4 BLACS grid … ERROR: n_basis = 5 too small for this processor grid`.
- **Why:** ScaLAPACK cannot block-distribute a 5×5 problem over a 7×4 process grid. H₂ (10 basis fns) squeaks by; one atom doesn't. Students hit this if they compute the H reference for the bond energy (Assignment 1 effectively needs it, or a wide-separation H₂).
- **Fix in the tutorial:** Tip added — for tiny systems reduce tasks in the copied `submit.sh` (`#SBATCH -n 4`, `mpirun -np 4`).
- **Verified:** H on 4 tasks: −12.1214 eV; sanity: 2×E(H) = −24.2427 eV vs H₂ at 6 Å = −24.2440 eV (consistent dissociation limit).

### D3. SCAN (meta-GGA) unit-cell relaxation fails — RESOLVED by switching the exercise to r²SCAN

> **Final resolution (per review):** the Ge exercise's meta-GGA rung now uses **r²SCAN** (`override_warning_libxc .true.` + `xc libxc MGGA_X_R2SCAN+MGGA_C_R2SCAN`, via the bundled libxc) instead of SCAN. Candidates tried on the deployed 240507 binary, all through the exact tutorial workflow (cell relax from 5.5 Å): **native `rscan` crashes reproducibly** (exit 1 mid-SCF); **TPSS works** but overestimates a (5.728 Å, +0.070 vs exp); **r²SCAN works cleanly** — 4 BFGS steps / ~70 s → **a = 5.689 Å** (+0.031 vs exp 5.658, SCAN-class accuracy, matches r²SCAN literature), stress consistent with its own E(a) surface (mini-scan minimum 5.683–5.69 ✓, the SCAN pathology absent), and it even gives a pedagogically *better* gap ladder (Ge gap: LDA/PBE ≈ 0 → r²SCAN 0.314 → HSE06 0.498 → exp 0.693 eV). `bfgs` and `trm` land bit-identically. Docs (§3.2/§3.3) and `dir_tree.sh` (`Ge/R2SCAN/`) updated; the E(a)-scan workaround text removed. Validated runs: `Tutorial_2/Ge/R2SCAN/{relax,band,ea_consistency_check}` in the workspace.

The record below documents the original SCAN failure and its diagnosis (still relevant: it is why SCAN itself must not be used here).

- **Symptom:** Ge `relax_unit_cell fixed_angles` with `xc scan` aborts: `trusted_descent: Too many uphill relaxation steps` — from the 5.5 Å start *and* from the PBE-relaxed geometry.
- **Root cause (established by a 7-variant experiment, per review requests to try other optimizers/settings):** tested `trm` vs `bfgs`, raised uphill tolerances (`energy_tolerance 1e-3` + `aggregated_energy_tolerance 1e-2`), `light` vs `intermediate` vs `tight` species defaults, and `sc_accuracy_stress 1e-3` (explicit stress self-consistency, on light and tight) — **all seven fail identically**, and in every case the optimizer drives the cell the *wrong way* (a: 5.5 → ≈5.497, away from the 5.68 minimum; the sc_accuracy_stress runs end bit-identically to those without it, so the stress *value* — not its convergence — is at fault). Decisive check: the code's **own energies** give E(5.68) < E(5.60), i.e. FHI-aims' **analytical stress under meta-GGAs contradicts its own energy surface**. This is an implementation limitation of the meta-GGA stress tensor — no relaxation-side setting can fix it. (Test record: `Tutorial_2/Ge/SCAN/relax_opt_test/` in the validation workspace.)
- **Fix in the tutorial:** §3.3 prescribes the **energy-vs-a scan** for SCAN (single points 5.60–5.80 Å step 0.02, take the minimum) — which is also the community-standard way to get meta-GGA lattice constants for exactly this reason. HSE06: relax from the PBE geometry (that *does* work — 3 BFGS steps, 14 min; HSE stress is fine).
- **Verified:** SCAN E(a) fit → **a = 5.682 Å** (SCAN literature ≈ 5.67–5.68); full Ge ladder LDA 5.632 < exp 5.658 < SCAN 5.682 < HSE06 5.711 < PBE 5.765 Å.
- **Not a 250822 regression — verified directly against 240507:** aims **240507 was built on MSE-HPC from the group's source** (same GNU recipe; `~/software/fhi-aims.240507/`) and the reproducer rerun on it: `relax_geometry trm|bfgs` + `relax_unit_cell` both abort with the same 5 uphill steps and a **bit-identical wrong-direction endpoint (a → 5.49617)**. The meta-GGA stress failure is version-independent. This matches the archival evidence: last year's student solution (240507 era; `~/docs/student_solution/privratskywilliam_HW2.pdf`, Assignment 3) reads *"(SCAN xc functional skipped because of technical difficulties)"* — the old tutorial never actually completed SCAN, and the reworked §3.3 (energy-vs-a scan) closes a gap students previously skipped. Their completed numbers cross-validate the MSE-HPC port almost exactly: Ge a(LDA) 5.633 vs 5.632, a(PBE) 5.771 vs 5.765, a(HSE06) 5.709 vs 5.711, Si a 5.408 vs 5.408.
- **Side-investigation (Ge semilocal gap, both versions, measured):** with `atomic_zora scalar` — 240507: LDA 0.115 / PBE 0.045 eV; 250822: 0.00 / 0.00 eV (small version difference; both ≪ exp 0.693 eV, so the assignment's teaching point is identical). Without relativity (needs `override_relativity .true.` on 250822): 0.458 / 0.261 eV. Keyword behavior: a **missing** `relativistic` line makes 240507 default to `atomic_zora scalar` with a warning; an **explicit `relativistic none`** is refused by **both** versions for Ge (relativity mandate). Consequently my earlier speculation that the student's nonzero gaps (0.36/0.477 eV) came from omitting ZORA is **disproven** — they could not have run Ge non-relativistically on 240507 without an explicit override. Their exact values match none of the six measured conditions (overall/direct gap × ZORA/none × version); most plausibly they were read from band plots/files or computed with a different SCF k-mesh. Their qualitative conclusion (semilocal ≪ experiment, HSE06 much closer) is unaffected.

### D4. `dos_tetrahedron` requires ≤0.01 eV energy mesh

Covered in C3 — documented so students who widen the window scale the points.

### D5. `use_dipole_correction` refuses small vacuum (TCNQ, 10 Å)

- **Symptom:** the vac_10 point of the TCNQ vacuum series stops:
  `A surface dipole determined close to the atoms of a slab will not be accurate … please use a larger vacuum spacing … Stopping the calculation as a safety precaution.`
- **Why:** with a tall molecule-on-slab system, 10 Å leaves no clean vacuum plateau for the dipole-correction plane. This is a *physics guard*, not a bug.
- **Fix in the tutorial:** note added — the refusal **is** the convergence-test answer for that point.
- **Verified:** 15–50 Å all run; total energy converges to ≤1.3 meV steps by 25 Å.

### D6. Metallic SCF/k-grid behavior (teaching points, intentionally left in)

- Na and (folded-Dirac) graphene show few-meV k-convergence **oscillation** instead of monotonic convergence — the assignments explicitly prompt students to notice this.
- **Magnetic FCC Fe at stretched a (3.5 Å) genuinely fails SCF** (hit the 1000-iteration cap): competing spin states. Doc note added: raise the broadening for that point only (`gaussian 0.2` converged it). Related robustness fix in B5.
- Ge with scalar relativity is **gapless in LDA/PBE/SCAN (0.00 eV)** — the classic semilocal failure; only HSE06 reopens the gap (0.50 eV here; exp 0.693 eV). This is the intended Jacob's-ladder lesson of the exercise, verified end-to-end.

---

## E. Operational incidents (cluster-side)

### E1. Flaky nodes: c015, c017 (and two mid-wave deaths)

- **Symptom:** a job runs but `aims.out` stops growing for minutes (c015: hung at MPI startup with 0-byte output; c017: hung mid-initialization; two of the 180 TCNQ jobs died mid-SCF the same way).
- **Handling:** cancel + resubmit (optionally `--exclude=<node>`); all four recoveries succeeded immediately on other nodes.
- **Action item:** worth reporting to `mse-it@andrew.cmu.edu`. Student guidance is in the validation log: *if `aims.out` stops growing for minutes, cancel and resubmit.*

### E2. Self-inflicted: duplicate submission race (process lesson)

- **What happened:** during the wave I flagged `hollowx/h_3.1` as dead (no completion, stale tail) and resubmitted — but the original job was still alive and both jobs then wrote `aims.out` in the same folder.
- **Handling:** cancelled both, cleaned the folder, resubmitted once — clean result.
- **Lesson (also in the log):** before resubmitting a "stuck" job, check `squeue` for a job whose working directory is that folder (`squeue -u $USER -o "%i %Z"`), or check that the jobID in `job_*.out` is no longer queued.

---

### E3. Shared-conda setup gotchas (post-review, while restoring the create-your-own-env pedagogy)

- **Decision:** students create their **own** `ase_env` (the old Arjuna pedagogy — env creation is part of the training), with the class providing only a shared, read-only **base conda** (`/mnt/beegfs/27-735/programs/miniforge3`, replacing Arjuna's miniconda module; base also carries `cmake<4` for rebuilds).
- **Gotcha 1:** a custom `.condarc` in the install root **replaces** Miniforge's bundled one — losing the `conda-forge` channel default, after which every `conda create` fails with "no channels configured". The shared `.condarc` must restate `channels: [conda-forge]` alongside the `envs_dirs`/`pkgs_dirs` pins.
- **Gotcha 2:** "read-only" is only true for non-owners — a `conda create -n` run *by the install's owner* happily created the env **inside the shared install** (my first test did exactly that, silently re-introducing a name collision for students). The `.condarc` pin (`envs_dirs: [~/.conda/envs]`) makes placement deterministic for everyone, owner included.
- **Verified as a true student:** clean shell → `conda create -n ase_env` lands in `~/.conda/envs/ase_env`, shared `envs/` stays empty, pip stack installs, `setup_utils.sh` prints `Python check: OK`, and an H₂ FHI-aims job submitted through that environment completes.

## Verification summary (what proves the whole thing works)

| Check | Result |
|---|---|
| Repo integration harness `docs/test/run_tests.sh` on MSE-HPC | **11/11 PASS** (Si gap 0.615 eV indirect, direct 2.516 eV at Γ; Fe ± smearing) |
| Repo doc linter `docs/test_docs.sh` | **40/40 PASS** |
| Tutorial 1 (all exercises) | H₂ curve incl. 1.0 Å; tiers/species monotonic; relax d=0.764 Å; serine 180° min; IP/EA vs exp ✓ |
| Tutorial 2 (all exercises) | Si a=5.408 Å, gap 0.542 eV indirect; Na metal; Fe FM-BCC a=2.832 Å m=2.19 μB; Ge 4-functional ladder + gaps |
| Tutorial 3 (all exercises) | k/vacuum conv; AA/AB × PBE/TS/MBD binding curves + 0.01 Å fine scans; bilayer band; TCNQ 180-point matrix (6 sites × 10 heights × 3 functionals), site ordering & magnitudes vs literature ✓ |
| Every helper script exercised in real student use | `setup_utils.sh`, `write_control.py` (both modes), `distance_generator.py`, `get_distance.py`, `extract_traj_frame.py`, `Automation.py` (all 5 modes), `Surfaces.py` (10 modes), `aimsplot.py` (incl. spin-polarized) |
| Total compute | ~460 jobs, all on compute nodes, queue drained clean |
