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

1. [VASP Basics](./Tutorial_1/) — input files (INCAR / POSCAR / KPOINTS / POTCAR) and the output files you actually look at.
2. [Calculation Descriptions](./Tutorial_2/) — SCF / DOS / band / OPT calculation blocks plus the SOC, HSE, and DFT+U modifiers, the shared general INCAR block, and Perlmutter parallelisation.
3. [Bulk InAs (PBE)](./Tutorial_3/) — the SCF → DOS → band-structure workflow on a CPU node.
4. [Bulk InAs (PBE+SOC)](./Tutorial_4/) — the same workflow with `vasp_ncl` and `LSORBIT = .TRUE.`.
5. [Bulk InAs (HSE)](./Tutorial_5/) — hybrid-functional band structure with the zero-weight k-point scheme; GPU build recommended.

## Before you start

1. You have a NERSC account and `vasp6` group access — see [HPC Onboard / Perlmutter](../../HPC%20Onboard/Perlmutter/).
2. The helper scripts `incar.py`, `kpoints.py`, `potcar.sh` are on your `PATH`. Download them from the [Utilities page](../../Utilities/) and edit `potcar.sh` to point at your local `potpaw_PBE` repository — on Perlmutter use `/global/cfs/cdirs/m3578/shared_folder/Pseudopotentials/potpaw_PBE`.
3. Optional but recommended: install [VASPKIT](https://vaspkit.com/) for input-file generation and built-in band/DOS plotting, and [vaspvis](https://github.com/caizefeng/vaspvis) for publication-quality band/DOS figures from the Python side.
4. Install a structure viewer — [VESTA](https://jp-minerals.org/vesta/en/) is the easiest for VASP `POSCAR`/`CHGCAR`, [OVITO](https://www.ovito.org/) is good for trajectories.
