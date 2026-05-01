---
layout: default
parent: "VASP"
grand_parent: "Tutorials"
title: "VASP Basics"
nav_order: 1
---

# Tutorial 1 — VASP Basics

## 📖 Learning objectives

* Understand the four core VASP input files and the most useful output files.

> Throughout this section we link directly to the [VASP wiki](https://www.vasp.at/wiki/) — make a habit of looking up every tag you see.

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

Continue with [Tutorial 2 — Calculation Types](../Tutorial_2/) to see the INCAR blocks for SCF / DOS / band / OPT and the modifiers (SOC, HSE, DFT+U).
