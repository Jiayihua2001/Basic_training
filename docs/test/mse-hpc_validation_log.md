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

## Bottom line

Every exercise and assignment of Tutorials 1–3 runs end-to-end on MSE-HPC with the shared binary. All issues a student would hit were found and fixed in the docs/bundle (see lists above). Two flaky-node incidents (c015, c017) and two mid-run job deaths during the 180-job wave were recovered by resubmission — worth mentioning to mse-it, and students should know: if `aims.out` stops growing for minutes, cancel and resubmit (check `squeue` first so you don't double-submit into the same folder).
