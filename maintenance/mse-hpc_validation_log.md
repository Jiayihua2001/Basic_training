# MSE-HPC full-tutorial validation log

Student-workflow simulation of the FHI-aims (organic) tutorials on MSE-HPC, run 2026-07-16.
Workspace: `~/Tutorials_files` (fresh unzip of `docs/Tutorials_files.zip`), helpers installed by `setup_utils.sh mse-hpc`, shared binary `/mnt/beegfs/27-735/programs/fhi-aims.250822/build/aims.250822.scalapack.mpi.x`.

## Issues found & fixed during review (before simulation)

1. `Tutorial_2/index.md` — pointed students at the Arjuna-only path `/home/27735A_group/shared/example`; now points at the `Tutorials_files` bundle.
2. `Tutorial_1/index.md` — "activate your `aims_env`" was an Arjuna-era manual step; `submit.sh` now sources the runtime automatically (Trace and MSE-HPC), text updated.
3. `distance_generator.py` — `np.arange(0.5, 1.0, 0.1)` silently dropped the documented 1.0 Å endpoint → now 0.5–1.0 inclusive.
4. `Automation.py plot_k_grid()` — collected energies in `os.listdir` order → scrambled plot and wrong dE/dn; now sorts (k, E) pairs.
5. `Automation.py make_Fe_grid_search()` — wrote `initial_moment` only for FCC (and only once at file end), so "magnetic BCC" scans silently converged non-magnetic; now detects `spin collinear` in control.in and adds `initial_moment 2` after every atom line, for both lattices.
6. `Automation.py` — Fe lattice scans dropped the documented 4.5 Å endpoint; ranges fixed (make + plot).

## Build review

- Binary built from **pristine** source, GNU recipe per FHI-aims wiki "NERSC Perlmutter" Cray-GNU CPU cache (adapted: MKL instead of libsci). `USE_SPGLIB` no longer exists in 250822 — spglib builds unconditionally and is linked (verified: 63 spglib symbols; libxc/ELPA/ScaLAPACK/s-dftd3 also present).
- Provenance recorded in `/mnt/beegfs/27-735/programs/fhi-aims.250822/BUILD_NOTES.md` (+ `initial_cache.mse-hpc.cmake`, tarball sha256).

## Issues found & fixed DURING the student simulation

7. **IP/EA charged runs stop in FHI-aims ≥ ~2024**: `Error: Initial charge and total charge of the system are inconsistent` — newer versions require the summed `initial_charge` in `geometry.in` to match `charge` in `control.in` (older Arjuna/Trace versions only warned). Doc now instructs adding `initial_charge 1.` / `-1.` next to `initial_moment 1`; validated.
8. **Single-atom runs crash on a full node**: `n_basis = 5 too small for this processor grid` (H atom, 28 tasks). Added a Tip to Tutorial 1: reduce MPI tasks (e.g. `-n 4`) for tiny systems; validated (H atom on 4 tasks: −12.1214 eV).
9. **ASE writes `initial_moment 2.3` for bulk Fe by itself** — `Automation.py` magnetic fix adjusted to only add `initial_moment` when the atom doesn't already carry one (FHI-aims tolerated the duplicate, but clean now).
10. **`Surfaces.py` distance scans dropped the documented 4.5 Å endpoint** (same `np.arange` pattern); fixed (default + CLI path), 4.5 Å points backfilled.
11. **Doc DOS example widened to show the conduction band** (−18…+10 eV) — initially with 2000 pts, which FHI-aims rejects (`dos_tetrahedron` needs ≤ 0.01 eV mesh); corrected to 3001 pts and documented the density rule.
12. **Flaky nodes**: c015 hung at MPI startup, c017 hung mid-init (output stopped growing); jobs cancelled/resubmitted elsewhere, both fine. Report to mse-it.

## Tutorial 1 results (all LDA/light unless noted)

- **EX1 H₂ dissociation** (0.5–1.0 Å, now incl. endpoint): min −30.9251 eV at 0.8 Å; E(H)=−12.1214 eV (4 tasks) → bond energy −6.68 eV, eq. length ≈ 0.77–0.80 Å (exp 0.741; LDA overbinds — teaching point). Plot: `section_1/binding_energy/assignment_results/`.
- **EX2 species defaults** at 0.8 Å: light −30.92505, intermediate −30.93256, tight −30.93941 (monotonic). **Tiers** (from light): t1 −30.92505, t2 −30.93870, t3 −30.93913 (converging).
- **EX3 relaxation**: E=−30.94469 eV, final d(H–H)=0.764 Å (`get_distance.py` ✓, `extract_traj_frame.py` → trajectory.xyz ✓).
- **Serine conformers** (relaxed): 180° global min; ΔE = 5.68 (300°), 25.43 (60°) kJ/mol. Plot in `section_2/conformers/assignment_results/`.
- **Fumaronitrile IP/EA** (E0 = −7098.7569): vertical IP **11.13 eV** (exp ≈ 11.15 ✓), adiabatic IP 11.04 eV, vertical EA 1.43 eV; adiabatic EA rerun after node hang.

## Tutorial 2 results

- **Si**: k-conv 4→12 monotonic, converged k=8–10; relaxed a = **5.408 Å** (exp 5.43 ✓ LDA); band+DOS: gap **0.542 eV indirect** (VBM Γ), smallest direct 2.54 eV at Γ — textbook Si LDA. `--plot_k_grid` (fixed) ✓, `--get_lattice_constant` ✓, `aimsplot.py` ✓.
- **Na**: metallic k-conv oscillation ±5 meV (intended teaching point; assignment prompts the discussion); relax k=12 + gaussian 0.1; band+DOS fine (no gap, finite DOS at E_F).
- **Fe**: k=16; full 72-point matrix done. PBE ground state = **FM BCC**, relaxed a = **2.832 Å**, moment **2.19 μB** (exp 2.87 / 2.22 ✓). Spin-polarized band run produces band1xxx/band2xxx and aimsplot handles them ✓. **Found**: magnetic FCC at stretched a (3.5 Å) hits the 1000-SCF limit — rerun with `gaussian 0.2` converges; doc note added; `plot_Fe_grid_search` made robust to missing points.
- **Ge** (k=10): lattice-constant ladder is textbook — **LDA 5.632 < exp 5.658 < SCAN 5.682 < HSE06 5.711 < PBE 5.765 Å**. **Found**: SCAN + light grids + `relax_unit_cell` aborts (`Too many uphill relaxation steps`) even from the PBE geometry → doc now prescribes the energy-vs-a scan for SCAN (parabola fit ✓). HSE06 relax from the PBE geometry finishes in 3 BFGS steps / 14 min (doc tip added). Gaps: PBE/SCAN = 0.00 eV (the known semilocal Ge gap collapse with scalar relativity — Jacob's-ladder teaching point); HSE06 band run submitted.
- **Assignment 4** (sparse vs dense k): Si SCF-estimated gap 0.605 eV (k=4³) vs 0.507 eV (k=10³); band-overlay figure produced.
- Repo integration harness `docs/test/run_tests.sh` submitted on MSE-HPC (si_bandgap, fe_kconv ±smearing).

## Tutorial 3 results (EX1 bilayer)

- `--build_bilayer` ✓; 2D k-conv 6–22 (semimetal few-meV oscillation; k=16 used); vacuum 15–50 Å flat to µeV → 15–20 Å fine (dipole correction ✓).
- Binding curves (E_bilayer − 2·E_mono, per 4-atom cell): **PBE** essentially unbound (−7/−9 meV, d_eq 3.9–4.1 Å); **PBE+TS** −138 (AA)/−160 (AB) meV at 3.5/3.4 Å; **PBE+MBD** −85/−100 meV at 3.6/3.4 Å. **AB < AA everywhere** ✓; MBD closest to DMC-quality expectations. `--plot_binding_curve` ✓; fine scans (0.01 Å) around minima running.
- **Fixed**: `Surfaces.py` distance scans dropped the 4.5 Å endpoint (arange, default + CLI); folder naming already 2-dp clean.
- AB bilayer relaxed at MBD equilibrium; Γ-M-K-Γ band + DOS submitted.

## Tutorial 3 results (EX2 TCNQ) — complete

- 7×7 slab (98 C) + TCNQ = 118 atoms; vacuum series (TCNQ system, `--EX_step 2`) converges by **25 Å**; **vac 10 Å refuses to run** — `use_dipole_correction` safety stop (doc note added: that failure is the data point). k-grid 2–8: sub-meV/atom oscillation (folded semimetal); 4×4×1 used.
- Full assignment matrix (6 configs × 10 heights × 3 functionals = 180 single points, 118 atoms each, ~5 min/job on 28 cores):
  - **PBE**: E_ads −0.13…−0.16 eV at 3.7 Å (weak/flat — no vdW).
  - **PBE+TS**: −1.38…−1.49 eV at 3.3–3.4 Å; strongest site **bridge-y −1.486 eV** (compare PBE+vdW literature ✓).
  - **PBE+MBD**: −1.03…−1.12 eV at 3.3–3.4 Å (≈25% weaker than TS — many-body screening, textbook).
  - Site ordering consistent across vdW methods: y-orientation > x; bridge-y ≳ hollow-y > top-y.
  - Wall-time per point nearly identical (PBE 314 s / TS 319 s / MBD 292 s) — useful for the cost-vs-accuracy discussion.
- Helpers validated in real use: `--build_graphene_slab`, `--build_molecule tcnq`, `--place_tcnq_on_graphene` (geometry spot-checked: planar TCNQ at exact height), `--create_height_scan`, `--plot_height_scan`, `--make_k_grid_2d`/`--plot_k_grid_2d`, `--vacuum_series`/`--plot_vacuum`, `--distance_scan`/`--plot_binding_curve`.

## Post-review additions (2026-07-16, after user review)

- **Python environment (final design, per review — old pedagogy preserved):** the class provides a shared, read-only **base conda** at `/mnt/beegfs/27-735/programs/miniforge3` (plays the role of Arjuna's `miniconda3` module; its base env also carries `cmake<4` for FHI-aims rebuilds), and **each student creates their own `ase_env`** with it, exactly as the `virtual_env` lesson teaches. A `.condarc` in the shared install pins `envs_dirs`/`pkgs_dirs` to `~/.conda/`, so `conda create -n ase_env` deterministically lands in the student's home for everyone. `setup_utils.sh` checks for ASE after installing the helpers and prints the create-your-own-env recipe if missing. Two gotchas found while setting this up: (1) writing that `.condarc` clobbered Miniforge's own one and with it the `conda-forge` channel default — channels must be restated; (2) before the `.condarc` pin, env creation by the install's *owner* landed inside the shared install (it's only read-only for others). **Verified as a real student**: clean shell → source shared conda → `conda create -n ase_env` (landed in `~/.conda/envs/ase_env`, shared install untouched) → `pip install` stack → `setup_utils.sh` reports OK → `write_control.py` + H₂ submission through that env completes.
- **DOS energy-window convention documented**: `output dos*` emin/emax are on FHI-aims' **absolute** KS scale (not E_F-relative); aims writes raw (absolute) + shifted (E_F=0) files and `aimsplot.py` plots the shifted one. Verified on the Si run (μ=−5.602 eV: raw −18…10, shifted −12.40…+15.60). Per review decision the **original `-18.0 0.0 2000` range is kept** (it already covers the gap on the absolute scale); only the misleading "up to the Fermi level" comment was corrected.

- **Gotcha policy (review round 2):** the D-class gotchas are now routed around instead of explained — dissociation scan includes a 6.0 Å reference (bond energy off the plot, no single-atom runs; verified: E(6.0 Å) = −24.244019 eV, identical to the manual check), §3.3 prescribes per-functional lattice methods, all vacuum series start at 15 Å (docs + `Surfaces.py` default; folder generation retested), tip boxes removed.

- **Historical cross-check (student solution, aims 240507 era):** last year's HW2 states SCAN was *"skipped because of technical difficulties"* — the SCAN cell-relaxation failure predates 250822 and was silently skipped rather than solved; the new §3.3 E(a)-scan workflow closes that gap. The student's completed numbers match this port's results almost exactly (Ge a: LDA 5.633/5.632, PBE 5.771/5.765, HSE06 5.709/5.711; Si a: 5.408/5.408).
- **Direct 240507 A/B test (user-provided source, built on MSE-HPC with the same GNU recipe):** SCAN `relax_unit_cell` fails **bit-identically** on 240507 (abort after 5 uphill steps, a → 5.49617) — version-independent stress bug, confirming the archival evidence. Ge gap side-checks: ZORA gaps are 0.115/0.045 eV (240507) vs 0.00/0.00 (250822); explicit `relativistic none` is refused by both versions; a missing keyword makes 240507 silently default to atomic_zora. Test record: `~/aims240507_tests/`, binary at `~/software/fhi-aims.240507/build/`.

## Repo integration harness (docs/test/run_tests.sh)

**11/11 PASS** on MSE-HPC (Si LDA gap 0.615 eV indirect + direct 2.516 eV at Γ; Fe with/without smearing).

## Switch to FHI-aims 240507 as the tutorial binary (per review) + full re-validation

The tutorial's shared binary was switched to **240507** (the same version the group runs on Trace and that last year's course used), built from the user-provided source with the identical GNU recipe → `/mnt/beegfs/27-735/programs/fhi-aims.240507/` (the 250822 install remains alongside for reference). `submit.sh`, `write_control.py`, the MSE-HPC page, and the bundle were repointed. Species defaults differ between the two versions only for Mn (unused by the tutorials).

**The entire tutorial suite was then re-run on 240507** (516 leaf runs — every T1/T2/T3 exercise incl. the 180-point TCNQ matrix — plus the docs/test harness) and compared number-for-number against the archived 250822 workspace (`~/Tutorials_files_250822_ref`):

- **Bit-identical** (to ~1e-9 eV): all T1 energies (H₂ curve incl. 6.0 Å, tiers/species, relaxation, serine, all four IP/EA values), all k-convergence sets, Si/Na/Fe/Ge relaxed lattice constants, Fe matrix minima and magnetic moment (2.18797 μB), Si gaps (0.542/0.605/0.507), Ge HSE06 a (5.7107) and gap (0.4977), TCNQ vacuum series, bilayer AB minima (PBE −9.0 / TS −160.4 / MBD −100.0 meV at 3.91/3.35/3.39 Å), and **all 18 TCNQ adsorption minima**.
- **Known, expected differences only:** Ge semilocal SCF-estimated gaps (240507: LDA 0.115 / PBE 0.045 / SCAN 0.088 eV vs 250822: 0.000 — both "essentially gapless", same teaching point); SCAN E(a) fit minimum 5.678 vs 5.682 Å (4 mÅ; meta-GGA energies differ slightly between versions). SCAN `relax_unit_cell` fails identically on both (as established earlier).
- Harness: **11/11 PASS on 240507**.
- Operational: compute node **c001 turned flaky mid-validation** (81 jobs killed across two waves, signal-53 deaths before any output); it is now in `submit.sh`'s exclude list (`--exclude=c001,c015,c017`) and all affected runs were resubmitted cleanly. The flaky-node set is dynamic — mse-it should investigate c001/c015/c017 (+ c013/c022 down).

**Verdict: no inconsistencies.** The tutorials, helper scripts, docs, and all recorded numbers are valid as-is on the 240507 binary.

## Helper install location: `~/aims_utils/` (per review)

`setup_utils.sh` no longer scatters the 5 helpers across the top of each student's home — they install into a single folder **`~/aims_utils/`** (still per-student and writable, since students are meant to read and edit them, especially `submit.sh`). All 52 command references across the four tutorial pages plus the Quick Onboard / FHI-aims index prose were updated (`python ~/aims_utils/write_control.py`, `cp ~/aims_utils/submit.sh .`, `sbatch ~/aims_utils/submit.sh`, …). The script warns about legacy loose copies from the old layout instead of deleting them. Verified by a fresh unzip → setup → verbatim Tutorial 1 run (H₂@0.8 = −30.925050488 eV, bit-identical).

## Meta-GGA swap: SCAN → r²SCAN (per review)

The Ge exercise's meta-GGA is now **r²SCAN** via the bundled libxc (`override_warning_libxc .true.` + `xc libxc MGGA_X_R2SCAN+MGGA_C_R2SCAN`). Unlike SCAN, its **unit-cell relaxation works** in the exact tutorial workflow (bfgs or trm, 4 steps, ~70 s from a=5.5): **a = 5.689 Å** (+0.031 vs exp; SCAN-class), stress verified consistent with its E(a) surface, Ge gap **0.314 eV** (making the full ladder LDA/PBE ≈0 → r²SCAN 0.31 → HSE06 0.50 → exp 0.693 — a cleaner Jacob's-ladder story than SCAN's 0.09). Rejected candidates: native `rscan` (reproducible crash in 240507), TPSS (works but a=5.728, +0.070). Docs §3.2/§3.3 and `dir_tree.sh` updated; E(a)-scan workaround removed from the student path.

## Classic-ifort experiment (per review request)

Classic `ifort` (2021.13.1, the final release) does not exist anywhere on MSE-HPC but was installed via spack (`intel-oneapi-compilers-classic`, user tree `~/spack-user`). FHI-aims 240507 builds from **pristine source** with it (mpiifort `-O3 -ip -fp-model precise`, icx/icpx for C/C++, MKL, Intel MPI) — including rt-tddft, confirming ifx's rejection was purely a compiler-strictness matter. Binary: `~/software/fhi-aims.240507/build_ifort/`, submit variant `~/aims_utils/submit_ifort.sh`.

**Full tutorial re-run on the ifort binary (507 leaf runs, `~/Tutorials_ifort`) vs the gfortran deployment:**
- **Results: max |ΔE| = 1.1×10⁻⁸ eV, median 0** across all 507 matched runs; every lattice constant, gap, binding/adsorption minimum identical (r²SCAN relax: bit-identical 5.68912789 Å). Intel MPI works under sbatch (`I_MPI_FABRICS=shm`, unset the injected `I_MPI_OFI_PROVIDER=mlx`).
- **SCAN differential:** ifort-compiled SCAN `relax_unit_cell` fails **bit-identically** (a → 5.49617268) — three toolchains now agree; definitively an FHI-aims meta-GGA stress implementation issue, not a compiler artifact. r²SCAN choice re-validated.
- **Speed (same-node A/B benchmark, best-of-two):** parity. The dominant workload (118-atom TCNQ single points, 89% of tutorial compute) runs **6–10% faster with ifort** (290–298 s vs 308–319 s); sub-30 s jobs are noise-dominated (up to 3× run-to-run variance on the *same* binary); trivial jobs start much faster under Intel MPI (collective latency).
- **Recommendation:** keep the deployed **gfortran + Open MPI** binary — science output is identical, the ≤10% edge on big jobs doesn't outweigh depending on a discontinued compiler (classic ifort is EOL) in the class toolchain. The ifort build is kept for reference.

## Canonical binary switched to the classic-Intel build (per review)

Following the ifort experiment's results, `build/aims.240507.ifort.scalapack.mpi.x` is now the **canonical tutorial binary** (the GNU build stays alongside as reference, env preserved as `aims_env_gnu.sh`). Accessibility for every student was the gating concern and is verified: the binary is linked `-static-intel` and its remaining shared-library deps all resolve from world-readable `/home/.spack-system` paths via the rewritten shared `aims_env.sh` (Intel runtime + Intel MPI with `I_MPI_FABRICS=shm`, site-injected `I_MPI_OFI_PROVIDER` unset) — clean-shell `ldd` shows zero private-home dependencies. `submit.sh` (bundle, `~/aims_utils`, docs download) and the MSE-HPC page repointed; fresh-unzip smoke test reproduces H₂ = −30.934556449 eV with the aims.out header confirming `mpiifort (Intel)`.

## Three-way end-to-end speed retest (full tutorial × 3 toolchains, identical conditions)

Three complete tutorial campaigns (~507 runs each) ran back-to-back on the idle cluster via one parametrized wave script (`~/speedtest_campaign.sh`; workspaces `~/speedtest_{gnu,ifort,intel2021}`):

| | gfortran + OpenMPI | ifort 2021.13 (static) + IntelMPI | **all-classic 2021.10 (dynamic) + IntelMPI** |
|---|---|---|---|
| campaign wall | 1 h 23 m 42 s | 1 h 24 m 31 s | 1 h 20 m 22 s |
| total compute | 19.65 node-h | 18.88 node-h (−3.9%) | 19.54 node-h (−0.5%) |
| TCNQ 118-atom median | 314.8 s | 295.7 s (1.06×) | 296.2 s (1.06×) |
| max |ΔE| vs gnu | — | 1.1×10⁻⁸ eV | 4.7×10⁻⁷ eV |

Conclusions: all three toolchains are **scientifically identical** (≤0.5 µeV over 507 runs each) and **wall-clock equivalent** for the tutorial; both Intel variants carry the same reproducible ~6% edge on the dominant 118-atom jobs; small-job categories are noise. The **all-classic 2021.10 variant** (`build/aims.240507.intel2021.scalapack.mpi.x` + `aims_env_intel2021.sh`) meets the design goals set in review: ifort+icc+icpc all classic 2021.10 (spack), Intel MPI 2021.17, same MKL, **zero 2025-oneAPI components**, **fully dynamic linking** with the complete classic runtime redistributed to the world-readable `intel-classic-2021.10-rt/` folder and the binary's private-home RPATH stripped (patchelf) — student-view `ldd` fully clean; smoke run bit-identical (−30.934556449 eV, header `ifort 2021.10.0`).

## Static-vs-dynamic linking A/B (hypothesis test for the campaign compute-total differences)

To test whether `-static-intel` vs `-shared-intel` explains the small-job compute differences between campaigns, the 2021.13 build was relinked fully dynamic (same objects, only the link step redone; smoke run bit-identical) and benchmarked against the static 2021.13 and dynamic 2021.10 binaries with same-node interleaved reps (TCNQ 118-atom ×8/arm on c014+c016; Si 12×12×12 k-grid ×15/arm on c018; per-job `mpirun` wall AND aims-internal time recorded; all 69 runs bit-identical energies per workload).

Result: **linking mode has no measurable effect.** Big-job internal medians S/D/C = 248.0/250.5/252.0 s (S and D identical means, 249.5 s); startup overhead (wall − internal) medians 47/43/43 s — static is not faster to launch; all differences are inside within-arm scatter. The decisive observation: the identical small job on the same node with the same binary varies **2–37 s internal time** rep to rep, and ~4% of small runs stall for 6–7 min (392 s and 427 s stalls reproduced on healthy c018 during this benchmark). BeeGFS/OS jitter, not toolchain or linking, sets small-job timing on this cluster; only the 118-atom medians measure binary speed, and there all Intel variants agree. (Benchmark TCNQ ≈ 250 s on a 3-node-quiet cluster vs ≈ 296 s under 40-node campaign load — same binaries; the gap is filesystem contention, further confirming I/O dominates the noise.)

## Final deployment decision (2026-07-17)

One and only one binary ships for the course: **`build/aims.240507.ifort.scalapack.mpi.x` = classic ifort 2021.13, fully dynamic linking** (same objects as the validated static build, relinked `-shared-intel`; bit-identical energies). Its classic Fortran runtime is redistributed in the world-readable `intel-classic-2021.13-rt/` folder, the build-host RPATH is stripped, and `aims_env.sh` now uses only MKL + Intel MPI + that runtime dir (no oneAPI-2025 compiler runtime). Verified from the student's perspective: permission sweep over every path component, compute-node `ldd` with zero private/missing paths, and an H₂ smoke through the unmodified `submit.sh` reproducing the reference energy exactly. Removed by this decision: the `fhi-aims.250822/` sibling install, the gfortran 240507 binary (+ `aims_env_gnu.sh` + GNU cmake cache), the static 2021.13 binary, and the all-classic 2021.10 binary (+ its env, cmake cache, and `intel-classic-2021.10-rt/`). The three-toolchain validation record above stands as the evidence base for this consolidation.

## Final student-path pass on the single canonical binary (2026-07-18)

With the consolidated deployment (one binary, dynamic ifort 2021.13) and the shared conda base, the entire organic tutorial was run once more exactly as a student would: fresh `Tutorials_files.zip` unpack, `setup_utils.sh mse-hpc`, `ase_env` deleted and recreated per the onboarding instructions (ase 3.29.0 into `~/.conda/envs`), all 507 jobs through the unmodified `submit.sh`. **All 507 runs completed and reproduce the three-campaign reference values bit-exactly** (H₂, IP/EA, lattice constants, gaps, binding minima; the one previously-unverified point — light/tier-3 — filled in and matches last year's student to 8 decimals). One job wedged at MPI startup and timed out twice (c020, then c026 — same signature as c015; single events, watch-list rather than exclude-list) and completed on resubmission. Every tutorial plotting utility (`Automation.py`, `Surfaces.py`, `aimsplot.py`) was exercised headlessly against this workspace to produce the instructor-solution figures — all work as documented. Doc polish from this pass: `intel-classic-2021.13-rt/` shown in the onboarding install tree, `__pycache__` stripped from the zip, a numeric ΔE < 1 meV convergence criterion added to Tutorial 3.

## Version switch: 250822 becomes the canonical binary (2026-07-19)

FHI-aims 250822 was built with the **identical toolchain** (classic ifort 2021.13, `mpiicx`/`mpiicpx`, Intel MPI 2021.17, MKL 2024.2, `-O3 -ip -fp-model precise`, fully dynamic, RPATH-stripped) and run through the complete tutorial campaign (507 runs). Versus the 240507 references: **505/507 runs agree to ≤7×10⁻⁸ eV**; Ge LDA/PBE band eigenvalues at Γ/L are identical to 4 decimals — including the zero-gap band inversion — proving the previously "documented" Ge-gap version difference (0.115 vs 0.00 eV) was a gap-*printout* artifact, not physics; HSE06 gives the identical gap with only the band-file Fermi-zero convention differing. The single genuine difference is **Ge r²SCAN**, computed through the newer libxc bundled with 250822: a constant total-energy shift (~1.87 eV, irrelevant), a = 5.6891 → 5.6913 Å, gap 0.314 → 0.305 eV — below any pedagogical threshold. Speed is identical (18.62 vs 18.88 node-h total; TCNQ 118-atom medians within 1%; campaign wall 5054 s, mid-band). Species_defaults are identical between versions for every element the tutorials use.

Since the user's switch condition ("same results") was met, `/mnt/beegfs/27-735/programs/fhi-aims.250822/` is now the one shared install (binary + `aims_env.sh` + `intel-classic-2021.13-rt/` + `species_defaults/`, RPATH stripped, permissions audited, student-path smokes bit-exact); `submit.sh` (installed, downloadable, and zip copies), `write_control.py`, and the onboarding page are repointed; the instructor solutions, reference values, and all figures regenerate from the 250822 campaign workspace (now `~/Tutorials_files`); the 240507 shared install is removed, with binary + build objects retained in the maintainer tree for rollback. Also corrected in this pass: the Ge semilocal gap is **exactly zero** (s-band inversion, bands touch at Γ; the occupied-state count jumps 32→33 there in the band files) — the earlier "0.115/0.045 eV indirect Γ→L" reference values were occupation-bookkeeping artifacts, now reported as L-valley offsets above the touching point; r²SCAN/HSE06 reopen genuine *direct* gaps at Γ (0.305/0.498 eV), while experiment is indirect Γ→L — size fixed, character not.

## Bottom line

Every exercise and assignment of Tutorials 1–3 runs end-to-end on MSE-HPC with the shared binary. All issues a student would hit were found and fixed in the docs/bundle (see lists above). Two flaky-node incidents (c015, c017) and two mid-run job deaths during the 180-job wave were recovered by resubmission — worth mentioning to mse-it, and students should know: if `aims.out` stops growing for minutes, cancel and resubmit (check `squeue` first so you don't double-submit into the same folder).

## Final state after the 2026-07-23 cleanup

The whole deployment was consolidated to its minimal final form. Shared area
(`/mnt/beegfs/27-735/programs/`): exactly `fhi-aims.250822/` and `miniforge3/`.
Maintainer home: `~/Basic_training` (this repo; maintainer records now in
`maintenance/`, outside the published Jekyll source), `~/Tutorials_files` (the
canonical 545-run workspace from the 2026-07-20 fully literal assignment
execution — its findings ledger lives in the private canvas repo,
`records/literal_run_findings.md`), `~/aims_utils`, `~/canvas` (one private git
repo: handouts + instructor solutions + grading + records), `~/texlive`. Deleted:
all build material — both FHI-aims maintainer source trees, build objects, the
240507 rollback binary, and the spack tree carrying classic ifort 2021.13 (19 GB).
The rebuild recipe survives as `maintenance/aims-250822-BUILD_NOTES.md` +
`aims-250822-initial_cache.intel-classic.cmake`.

**Post-deletion re-verification of the shared binary** (the spack tree held the
compiler that built it, so prove nothing at runtime pointed there): `ldd` under
`aims_env.sh` resolves every library from the system-wide spack
(`/home/.spack-system`, mse-it's) or the redistributed
`intel-classic-2021.13-rt/` inside the install — zero paths into any user home,
zero "not found". H₂ smoke through the unmodified student `submit.sh`:
−30.925050488 eV, bit-identical to the campaign reference. One incident during
the smoke: first submission wedged at MPI startup on **c014** (R for 5+ min, 0-byte
outputs — the c015 signature; single event, added to the watch list alongside
c020/c026/c034/c035); resubmission excluding it completed normally on c016.

## Post-cleanup full-campaign retest (2026-07-23, user request)

The complete tutorial campaign (507 runs) was rerun via `speedtest_campaign.sh` in a
throwaway BeeGFS workspace (`/mnt/beegfs/27-735/.validation_tmp`; head-node `/tmp` is
node-local and invisible to compute nodes) — the first consumer of the repo-tracked
`Tutorials_files/` → `make_zip.sh` bundle. **All 507 completed, zero MPI wedges,
zero unconverged.**

**Results vs the canonical literal workspace (`~/Tutorials_files`):** every pair with
identical inputs (order-independent compare) is **bit-identical — ΔE = 0.0 exactly (85
runs)**. The remaining 421 pairs differ only through *protocol drift* — the campaign
script's recipe predates a few final-doc judgment calls (Fe grids `gaussian 0.1`/`16³`
vs `0.2`/`14³`; Si/Na relax k-grids; bilayer scans `k 16×16×1` vs converged `12×12×1`;
TCNQ slabs vacuum 25 Å vs converged 20 Å; convergence-series composition). Physics-level
equivalence verified for every drift group: Fe a_min identical for all 8 states (2.75
BCC / 3.50 FCC), relaxed BCC-mag a and moment agree (2.831 Å conv, 2.19 μB); Si relax a
5.408 both (sparse-k 5.420 story intact); H₂ relaxation and all four IP/EA numbers
bit-identical; Ge HSE06 gap 0.498 eV at Γ in both; TCNQ best site bridge-y at h = 3.3 Å
for TS/MBD in both with E_ads within 13 meV (the vacuum choice); bilayer AB < AA for
every functional with minima within 0.01–0.10 Å and E_b within 15 meV/cell (k-grid
sensitivity — consistent with the solutions' grader tolerance).

**Speed:** campaign wall 5694 s (vs 5054 s on 07-19 — queue-noise band); aims-internal
total 18.10 node-h (vs 18.88 — ~4% faster, i.e. unchanged within noise); TCNQ
118-atom-class median 293.9 s (vs ≈296 s — <1%). The binary and environment perform
identically after the cleanup and compiler-tree restoration.

Workspace deleted after the verdict.
