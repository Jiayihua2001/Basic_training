---
layout: default
title: "Utilities"
nav_order: 4
has_children: true
---

# Utilities

This section collects the tools and helper scripts that the tutorials reference. They fall into four buckets:

- **Automation platforms** — GIMS for FHI-aims, VASPKIT for VASP.
- **Visualisation tools** — Jmol, OVITO, VESTA.
- **Python libraries** — ASE and pymatgen for structure manipulation, DFT setup, and post-processing.
- **VASP helper scripts** — `incar.py`, `kpoints.py`, `potcar.sh` (used in the VASP tutorials).

---

## GIMS

[The Graphical Interface for Materials Simulation (GIMS)](https://gims.ms1p.org/static/index.html#) is a web-based platform that automates common FHI-aims tasks:

- Building crystal structures from scratch or from a database.
- Generating `control.in` files (band structure, DOS, relaxation workflows).
- Post-processing band/DOS data with built-in plots.

GIMS is great for new users who want to skip manual setup, and for experienced users who want to streamline routine workflows.

---

## VASPKIT

[VASPKIT](https://vaspkit.com/) is a command-line interface that automates many VASP pre- and post-processing steps. It is the recommended companion to the VASP tutorials.

### Installation

1. Download the latest binary from [SourceForge](https://sourceforge.net/projects/vaspkit/files/).
2. Add the binary to your `PATH`.
3. Copy the bundled `how_to_set_environment_variable` to `~/.vaspkit` and edit the POTCAR paths inside.

```bash
# typical .bashrc additions
export PATH="$HOME/vaspkit/bin:$PATH"
```

### Most-used menus

Run `vaspkit` and pick a numbered task — they all also accept the `-task <id>` flag for batch use.

| Task | Purpose                                                                               |
|------|---------------------------------------------------------------------------------------|
| 101  | INCAR templates (static / relax / HSE / DFT+U / phonon …)                             |
| 102  | KPOINTS — Monkhorst-Pack / Γ-centred grids                                            |
| 103  | POTCAR (default recommended PAW)                                                      |
| 104  | POTCAR (user-specified PAW per element)                                               |
| 251  | **HSE band-structure KPOINTS** — auto-builds the IBZKPT + zero-weight path scheme     |
| 303  | High-symmetry k-path along the Setyawan-Curtarolo convention (3D PBE band)            |
| 302  | High-symmetry k-path for 2D materials                                                 |
| 211  | Plot PBE band structure from `EIGENVAL` / `vasprun.xml`                               |
| 213  | Plot HSE band structure (handles the zero-weight points automatically)                |
| 111  | Total / projected DOS                                                                 |
| 911  | Band-gap finder                                                                       |
| 912  | Effective-mass calculator                                                             |

In the [VASP tutorials](../Tutorials/VASP/) we use VASPKIT mainly for tasks **102**, **251**, **303**, **211**, and **213**.

---

## Visualisation Tools

### 🔹 [Jmol](http://jmol.sourceforge.net/)
- Java-based interactive viewer for molecules and crystals.
- Reads `.xyz`, `.cif`, `.in`, and many other formats.
- Best for quick views of geometries and orbitals.

### 🔹 [OVITO](https://www.ovito.org/)
- Open Visualization Tool for atomistic simulations.
- Strong for periodic systems and MD trajectories.
- Reads `.xyz`, `.cfg`, `.lammps`, `.in`, and more.
- Scriptable in Python for analysis and animations.

### 🔹 [VESTA](https://jp-minerals.org/vesta/en/)
- 3D visualisation tool aimed at crystal structures, volumetric data, and morphology.
- Reads VASP `POSCAR`/`CONTCAR`, `CHGCAR`, `LOCPOT`, `PARCHG`, plus `.cif`, `.xsf`, `.xyz`, FHI-aims `.in`, and many more.
- Excellent for inspecting unit cells, drawing isosurfaces of charge density / spin density, building supercells, and exporting publication-quality images.
- Recommended companion for the VASP tutorials when checking POSCAR/CONTCAR after relaxation and visualising CHGCAR/PARCHG outputs.

---

## Python Libraries for Materials Analysis

### 🔸 [ASE (Atomic Simulation Environment)](https://wiki.fysik.dtu.dk/ase/)
- Build, manipulate, and visualise atoms and molecules.
- Interfaces with most DFT codes (e.g., GPAW, VASP, FHI-aims).
- Good for scripting calculations and automating workflows.

```bash
pip install ase
```

### 🔸 [pymatgen (Python Materials Genomics)](https://pymatgen.org/)
- Rich toolkit for parsing, analysing, and generating structures.
- Developed by the Materials Project.
- Excellent `.cif`, `.vasp`, `.poscar` support; required by `kpoints.py` below.

```bash
pip install pymatgen
```

---

## VASP helper scripts

These three small utilities are used throughout the [VASP tutorials](../Tutorials/VASP/). Drop them into `~/` (or wherever is on your `PATH`).

| Script | Purpose | Download |
|--------|---------|----------|
| `incar.py`  | Build an INCAR for SCF / DOS / band / OPT, optionally combined with SOC, HSE, or DFT+U. Defaults set: `EDIFF = 1E-6`, `GGA_COMPAT = .FALSE.`, no `NBANDS` (let VASP decide). | [📥 incar.py](scripts/incar.py)  |
| `kpoints.py` | Write Γ-centred grids, line-mode band paths, or HSE zero-weight KPOINTS using pymatgen's `HighSymmKpath`. | [📥 kpoints.py](scripts/kpoints.py) |
| `potcar.sh` | Concatenate a POTCAR from a local `potpaw_PBE` repository (handles `.gz`/`.Z`). | [📥 potcar.sh](scripts/potcar.sh)  |

Quick install:

```bash
mkdir -p ~/bin
curl -L -o ~/bin/incar.py    <docs URL>/Utilities/scripts/incar.py
curl -L -o ~/bin/kpoints.py  <docs URL>/Utilities/scripts/kpoints.py
curl -L -o ~/bin/potcar.sh   <docs URL>/Utilities/scripts/potcar.sh
chmod +x ~/bin/*.py ~/bin/potcar.sh
echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc
```

> Both `incar.py --help` and `kpoints.py --help` list every flag. Edit `potcar.sh` once to point at your `potpaw_PBE` directory; on Perlmutter the group typically keeps it under `/global/common/software/<repo>/`.

> The Marom-group VASP scripts and the FHI-aims tutorial helpers (`write_control.py`, `Automation.py`, `Surfaces.py`, `aimsplot.py`) are conceptually similar — they wrap argparse around the parts of the workflow that don't change. Use VASPKIT when you want a richer interactive menu.
