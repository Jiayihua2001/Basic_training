---
layout: default
parent: "VASP"
grand_parent: "Tutorials"
title: "Calculation Types"
nav_order: 2
---

# Tutorial 2 — Calculation Types

## 📖 Learning objectives

* Recognise the calculation types you will run in the rest of the VASP tutorials (SCF, DOS, band, OPT) and the modifiers that combine with them (SOC, DFT+U, HSE).
* Read and write a sensible `INCAR` for the Marom-group setup (`EDIFF = 1E-6`, `GGA_COMPAT = .FALSE.`, no `NBANDS`).
* Pick reasonable `KPAR` / `NCORE` values for Perlmutter.

---

## 2.1 The shared "general" INCAR block

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
KPAR       = 4           # k-point parallelism (1 k-group per 4 MPI ranks)
NCORE      = 1           # auto-reset to 1 by VASP when OpenMP / GPU is on; harmless
```

Notes on the choices:

* `EDIFF = 1E-6` — see [VASP wiki / EDIFF](https://www.vasp.at/wiki/index.php/EDIFF). Convergence is roughly quadratic, so the cost of going from `1E-5` to `1E-6` is small.
* `GGA_COMPAT = .FALSE.` — see [VASP wiki / GGA_COMPAT](https://www.vasp.at/wiki/index.php/GGA_COMPAT).
* `ENCUT = 400` works for In/As. Always check `ENMAX` in your `POTCAR`s and pick `ENCUT ≥ 1.3 × max(ENMAX)` if you are scanning lattice constants.
* **No `NBANDS`** — the [VASP default](https://www.vasp.at/wiki/index.php/NBANDS) is `max((NELECT+2)/2 + max(NIONS/2, 3), ⌊0.6 · NELECT⌋)`. SOC doubles it internally. Override only if VASP warns "too few bands".

### Picking `KPAR` and `NCORE` on Perlmutter

The Marom group [Perlmutter sbatch template](../../../HPC%20Onboard/Perlmutter/#vasp-sbatch-templates) uses **16 MPI ranks/node × 8 OpenMP threads** on CPU and **4 MPI ranks/node × 1 OMP × 4 GPUs** on GPU. The [VASP wiki](https://www.vasp.at/wiki/index.php/NCORE) notes that `NCORE` is automatically forced to 1 whenever OpenMP threading or GPU acceleration is active, so the only knob you really tune is `KPAR`:

| Run                         | Ranks total | KPAR | Ranks per k-group | NCORE |
|-----------------------------|------------:|-----:|------------------:|------:|
| CPU 1 node (Tutorials 3 & 4)| 16          | 4    | 4                 | 1     |
| CPU 2 nodes (HSE fallback)  | 32          | 8    | 4                 | 1     |
| GPU 1 node, 4 GPUs (HSE)    | 4           | 4    | 1                 | 1     |

`KPAR` must divide both the rank count and the number of irreducible k-points. For CPU runs without OpenMP (legacy or pure-MPI workflows) you would set `NCORE ≈ √(ranks per k-group)` instead; that is the only situation where `NCORE > 1` actually does anything.

---

## 2.2 Calculation types

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

## 2.3 Modifiers

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

## 2.4 Workflow at a glance

```
scf/   --INCAR/POSCAR/POTCAR/KPOINTS--> CHGCAR (and optionally WAVECAR for HSE)
   │
   ├── cp CHG* ../band/        ──> band/   sbatch ─► EIGENVAL, PROCAR
   └── cp CHG* ../dos/         ──> dos/    sbatch ─► DOSCAR, PROCAR
```

For HSE swap `CHG*` for `WAVECAR`. The bulk-InAs tutorials (Tutorial_3 PBE, Tutorial_4 PBE+SOC, Tutorial_5 HSE) all follow this pattern.

---

## 2.5 Sanity-check before you submit

* `grep TITEL POTCAR` matches the species order in `POSCAR` line 6.
* `INCAR` contains `EDIFF = 1E-6`, `GGA_COMPAT = .FALSE.`, and no `NBANDS` line.
* `KPOINTS` makes sense for the calculation type (grid for SCF/DOS/OPT, line-mode for band, zero-weight scheme for HSE band).
* Submission script loads `vasp/6.4.3-cpu` and uses `vasp_ncl` if you set `LSORBIT = .TRUE.`.

When all of those check out, move on to [Tutorial 3 — Bulk InAs (PBE)](../Tutorial_3/).
