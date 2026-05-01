---
layout: default
parent: "Tutorials"
title: "VASP"
nav_order: 2
has_children: true
---

# VASP Tutorials

These tutorials introduce the VASP workflow used by the quantum-materials subgroup. They walk you through bulk InAs in three stages — pure PBE, PBE with spin-orbit coupling, and HSE06 with SOC — so you see how each ingredient changes the predicted band gap.

## Quick guide

- [Tutorial_1](./Tutorial_1/) — VASP basics: input/output files, calculation types, and the standard INCAR/KPOINTS blocks.
- [Tutorial_2](./Tutorial_2/) — Bulk InAs (PBE): the SCF → DOS → band-structure workflow.
- [Tutorial_3](./Tutorial_3/) — Bulk InAs (PBE+SOC): the same workflow with `vasp_ncl`.
- [Tutorial_4](./Tutorial_4/) — Bulk InAs (HSE06+SOC): hybrid-functional band structure with the zero-weight k-point scheme.

## Before you start

1. You have a NERSC account and `vasp6` group access — see [HPC Onboard / Perlmutter](../../HPC%20Onboard/Perlmutter/).
2. The helper scripts `incar.py`, `kpoints.py`, `potcar.sh` are on your `PATH`. Download them from the [Utilities page](../../Utilities/) and edit `potcar.sh` to point at your local `potpaw_PBE` repository.
3. Optional but recommended: install [VASPKIT](https://vaspkit.com/) to streamline KPOINTS/POTCAR/INCAR generation and band/DOS post-processing.
4. Install a structure viewer — [VESTA](https://jp-minerals.org/vesta/en/) is the easiest for VASP `POSCAR`/`CHGCAR`, [OVITO](https://www.ovito.org/) is good for trajectories.

> The InAs tutorials are adapted from Derek Dardzinski's [Marom-group docs](https://derekdardzinski.github.io/marom_group_docs/) with updated INCAR conventions (see below) and current Perlmutter / VASP 6.4.3 usage.

## Conventions used in these tutorials

Every INCAR you write here will share three conventions, each motivated by the [VASP wiki](https://www.vasp.at/wiki/):

* **`EDIFF = 1E-6`** — tighter than the default `1E-4`. Per the wiki, "1E-6 is likely the best compromise" between accuracy and cost; this is also a prerequisite for cleanly differentiable forces.
* **`GGA_COMPAT = .FALSE.`** — restores the full Bravais-lattice symmetry of the gradient field. The default `.TRUE.` exists only for backward compatibility, and is explicitly **not** recommended for magnetic-anisotropy calculations.
* **No explicit `NBANDS`** — let VASP pick `max((NELECT+2)/2 + max(NIONS/2, 3), ⌊0.6·NELECT⌋)`. SOC doubles the count internally (spinors). Override only if you see "too few bands" warnings or are doing GW/RPA.

The parallelisation tags (`KPAR = 4`, `NCORE = 4`) assume the standard 1-node Perlmutter launch (64 MPI ranks × 2 OpenMP threads). Update them when you change node count — see [HPC Onboard / Perlmutter](../../HPC%20Onboard/Perlmutter/#picking-kpar-and-ncore).
