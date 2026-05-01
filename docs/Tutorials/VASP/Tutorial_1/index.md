---
layout: default
parent: "VASP"
grand_parent: "Tutorials"
title: "Tutorial_1"
nav_order: 1
---

# Tutorial 1 — VASP Basics

## 📖 Learning objectives

* Understand the four core VASP input files and the most useful output files.
* Recognise the calculation types you will run in the rest of the VASP tutorials (SCF, DOS, band, OPT) and the modifiers that combine with them (SOC, DFT+U, HSE).
* Read and write a sensible `INCAR` for the Marom-group setup (`EDIFF = 1E-6`, `GGA_COMPAT = .FALSE.`, no `NBANDS`).
* Pick reasonable `KPAR` / `NCORE` values for Perlmutter.

> Throughout this section we link directly to the [VASP wiki](https://www.vasp.at/wiki/) — make a habit of looking up every tag you set.

---

## 1.1 Input files

A VASP calculation is fully specified by **four files**.

| File | Purpose | How to generate |
|------|---------|-----------------|
| `INCAR`   | Tags that select the calculation type and numerical parameters | `incar.py` (or VASPKIT task 101) |
| `POSCAR`  | Unit cell vectors and atom positions | Materials Project, `vaspvis`, `pymatgen`, ASE, or by hand |
| `KPOINTS` | Brillouin-zone sampling: grid for SCF/DOS/OPT, line-mode path for band | `kpoints.py` (or VASPKIT 102/251/302/303) |
| `POTCAR`  | PAW pseudopotentials, **one block per element** in the same order as line 6 of `POSCAR` | `potcar.sh` (or VASPKIT 103/104) |

> **POTCAR ordering is silent and dangerous.** If the species order in `POTCAR` does not match line 6 of `POSCAR`, VASP will run happily but give nonsense. Always sanity-check with `grep TITEL POTCAR` against your POSCAR.

---

## 1.2 Output files you will look at

| File | What is in it | Used by |
|------|---------------|---------|
| `OUTCAR` | Everything: forces, stresses, Fermi energy, timing, version, warnings | Anything; your first stop when something breaks |
| `OSZICAR`| One line per electronic / ionic step (energy, ΔE, magnetisation) | Live-monitor convergence: `tail -f OSZICAR` |
| `CHG` / `CHGCAR` | Self-consistent charge density (small / large precision). Written when `LCHARG = .TRUE.` | Read by non-self-consistent DOS and band runs (`ICHARG = 11`) |
| `WAVECAR`| Plane-wave coefficients of the KS orbitals. Can be **huge**; written when `LWAVE = .TRUE.` | HSE band/DOS, STM, wave-function visualisation |
| `IBZKPT` | List of irreducible k-points with their weights | Required input for HSE band-structure KPOINTS |
| `EIGENVAL`/`PROCAR`/`DOSCAR` | Eigenvalues, lm-projected weights, total/projected DOS | Plotting (VASPKIT, pymatgen, sumo) |
| `CONTCAR`| Final atomic positions after a relaxation | Restart relaxations: `cp CONTCAR POSCAR` |

---

## 1.3 The shared "general" INCAR block

Every INCAR in these tutorials starts with the same general block. Generate it with `python incar.py --scf` (or `--dos`, `--band`, `--opt`); the calculation-specific block follows.

```text
# --- general -----------------------------------------------------------------
ALGO       = Fast        # Davidson + RMM-DIIS mixture
PREC       = Normal      # Precision level
EDIFF      = 1E-6        # SCF break condition (VASP-wiki: 1E-6 best compromise)
NELM       = 500         # Max electronic steps
ENCUT      = 400         # Plane-wave cutoff (eV); ENMAX from POTCAR is the floor
LASPH      = .TRUE.      # Non-spherical gradient corrections
GGA_COMPAT = .FALSE.     # Restore full Bravais lattice symmetry; required for MAE
SIGMA      = 0.05        # Smearing width (eV)

# --- parallelisation (Perlmutter 1-node CPU defaults) -----------------------
KPAR       = 4           # k-point parallelism
NCORE      = 4           # MPI ranks collaborating on one band; ~sqrt(ranks per k-group)
```

Notes on the choices:

* `EDIFF = 1E-6` — see [VASP wiki / EDIFF](https://www.vasp.at/wiki/index.php/EDIFF). Convergence is roughly quadratic, so the cost of going from `1E-5` to `1E-6` is small.
* `GGA_COMPAT = .FALSE.` — see [VASP wiki / GGA_COMPAT](https://www.vasp.at/wiki/index.php/GGA_COMPAT).
* `ENCUT = 400` works for In/As. Always check `ENMAX` in your `POTCAR`s and pick `ENCUT ≥ 1.3 × max(ENMAX)` if you are scanning lattice constants.
* **No `NBANDS`** — the [VASP default](https://www.vasp.at/wiki/index.php/NBANDS) is `max((NELECT+2)/2 + max(NIONS/2, 3), ⌊0.6 · NELECT⌋)`. SOC doubles it internally. Override only if VASP warns "too few bands".

### Picking `KPAR` and `NCORE` on Perlmutter

The recommended Perlmutter launch is **64 MPI ranks/node × 2 OpenMP threads** (`-c 4`). For 1 node you have 64 ranks total:

| Nodes | Ranks | KPAR | Ranks per k-group | NCORE | Comment |
|------:|------:|-----:|------------------:|------:|--------|
| 1     | 64    | 4    | 16                | 4     | safe default |
| 2     | 128   | 8    | 16                | 4     | HSE / large k-mesh |
| 4     | 256   | 8    | 32                | 4 or 8| larger systems |

`KPAR` must divide both the rank count and the number of irreducible k-points. `NCORE ≈ √(ranks per k-group)` is the rule of thumb from the [VASP wiki](https://www.vasp.at/wiki/index.php/NCORE).

---

## 1.4 Calculation types

Each block below is what `incar.py` appends to the general block.

### Self-Consistent Field (`--scf`)
Converges the charge density from a superposition of atomic densities. Produces `CHG`, `CHGCAR`, and (with `LWAVE = .TRUE.`) `WAVECAR` for downstream calculations.

```text
ICHARG = 2
ISMEAR = 0          # Gaussian smearing during self-consistency
LCHARG = .TRUE.
LWAVE  = .FALSE.    # set .TRUE. only when you need WAVECAR (HSE)
LREAL  = .FALSE.    # reciprocal-space projectors; switch to Auto for > ~30 atoms
```

### Density of States (`--dos`)
Non-self-consistent eigenvalue evaluation on a denser grid, using a converged `CHGCAR` from the SCF step.

```text
ICHARG = 11
ISMEAR = -5         # tetrahedron with Bloechl correction
LCHARG = .FALSE.
LWAVE  = .FALSE.
LORBIT = 11         # lm-decomposed PROCAR / DOSCAR
NEDOS  = 3001
EMIN   = emin       # filled in at submit time from the SCF Fermi level
EMAX   = emax
```

### Band structure (`--band`)
Same as DOS but the KPOINTS file is a line-mode path along high-symmetry points.

```text
ICHARG = 11
ISMEAR = 0
LCHARG = .FALSE.
LWAVE  = .FALSE.
LORBIT = 11
```

### Ionic optimisation (`--opt`)
Relaxes ions (and optionally cell shape/volume) until forces fall below `|EDIFFG|`.

```text
ICHARG = 2
ISMEAR = 0
LCHARG = .FALSE.
LWAVE  = .FALSE.
IBRION = 2          # conjugate gradient
NSW    = 50         # max ionic steps
EDIFFG = -1E-2      # force convergence (eV/A); negative => force criterion
ISIF   = 3          # relax positions, cell shape, volume
```

---

## 1.5 Modifiers

Combine these flags with one of the four calculation types above.

### Spin-orbit coupling (`--soc`)

```text
LSORBIT = .TRUE.
MAGMOM  = 6*0       # 3 components per atom; "N*0" is shorthand for non-magnetic
```

Run **`vasp_ncl`** for SOC calculations. The default `NBANDS` is doubled internally to accommodate spinors.

### HSE06 hybrid (`--hse`)

```text
LHFCALC  = .TRUE.
HFSCREEN = 0.2      # range-separation parameter, 1/A
AEXX     = 0.25     # 25% exact exchange (HSE06 standard)
PRECFOCK = Fast     # softer FFT mesh in the exchange routine
TIME     = 0.4      # damping time-step
```

* For HSE **SCF** keep `ALGO = Fast` and add `LWAVE = .TRUE.` so you can re-use the WAVECAR.
* For HSE **band/DOS** override to `ALGO = Damped` and `ICHARG = 0` (eigenvalues recomputed from `WAVECAR`). The KPOINTS file must be the zero-weight scheme — see [VASP wiki / Hybrid functionals: band-structure calculations](https://www.vasp.at/wiki/index.php/Hybrid_functional_calculations:_band_structure).

`incar.py --band --hse` already applies these overrides.

### DFT+U (Dudarev) (`--dftu`)

```text
LDAU     = .TRUE.
LDAUTYPE = 2
LDAUL    =  2  -1   # one l-quantum number per species in POSCAR order; -1 disables
LDAUU    =  4.5 0.0
LDAUJ    =  0.0 0.0
LMAXMIX  =  4       # 4 for d, 6 for f
```

The Marom group typically tunes `LDAUU` against an HSE reference using Bayesian optimisation; document the reference whenever you set a non-trivial U.

---

## 1.6 Workflow at a glance

```
scf/   --INCAR/POSCAR/POTCAR/KPOINTS--> CHGCAR (and optionally WAVECAR for HSE)
   │
   ├── cp CHG* ../band/        ──> band/   sbatch ─► EIGENVAL, PROCAR
   └── cp CHG* ../dos/         ──> dos/    sbatch ─► DOSCAR, PROCAR
```

For HSE swap `CHG*` for `WAVECAR`. Tutorial_2 (PBE), Tutorial_3 (PBE+SOC), and Tutorial_4 (HSE) all follow this pattern.

---

## 1.7 Sanity-check before you submit

* `grep TITEL POTCAR` matches the species order in `POSCAR` line 6.
* `INCAR` contains `EDIFF = 1E-6`, `GGA_COMPAT = .FALSE.`, and no `NBANDS` line.
* `KPOINTS` makes sense for the calculation type (grid for SCF/DOS/OPT, line-mode for band, zero-weight scheme for HSE band).
* Submission script loads `vasp/6.4.3-cpu` and uses `vasp_ncl` if you set `LSORBIT = .TRUE.`.

When all of those check out, move on to [Tutorial_2 — Bulk InAs (PBE)](../Tutorial_2/).
