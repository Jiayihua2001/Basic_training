---
layout: default
title: "Utilities"
nav_order: 4
has_children: true
---

# Utilities

This section collects the tools and helper scripts that the tutorials reference. They fall into these buckets:

- **Automation platforms** — GIMS for FHI-aims, VASPKIT for VASP.
- **Visualisation tools** — Jmol, OVITO, VESTA.
- **Python libraries** — ASE and pymatgen for structure manipulation, DFT setup, and post-processing.
- **Marom-group QM packages** — OgreInterface (epitaxial interfaces), BayesianOpt4dftu (DFT+U *U*-fitting), and vaspvis (band/DOS figures).
- **VASP helper scripts** — `incar.py`, `kpoints.py`, `potcar.sh` (used in the VASP tutorials).
- **AI coding assistants** — Claude Code and OpenAI Codex for writing and extending workflow code.

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

**General (non-Perlmutter):** download the latest binary from [SourceForge](https://sourceforge.net/projects/vaspkit/files/), add its `bin/` to your `PATH`, and copy the bundled `how_to_set_environment_variable` to `~/.vaspkit`, editing the POTCAR paths inside so tasks like 103/303 can find your PAW library.

```bash
# typical .bashrc additions
export PATH="$HOME/vaspkit/bin:$PATH"
```

> ⚠️ **On Perlmutter, do _not_ use the SourceForge binary.** The version published on the website is linked against an older glibc and is incompatible with Perlmutter, so it fails to run. The **only** working build is the **1.6.0** copy staged on CFS under `shared_folder`. Install it once and edit `~/.vaspkit` for the POTCAR paths:

```bash
cp -r /global/cfs/cdirs/m3578/shared_folder/vasp_tools/vaspkit.1.6.0 $HOME/opt/   # pick any install root
echo 'export PATH="$HOME/opt/vaspkit.1.6.0/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
which vaspkit       # confirm it's on your PATH
```

### Most-used menus

Run `vaspkit` and pick a numbered task interactively, or call it non-interactively for scripting — every task accepts the `-task <id>` flag:

```bash
vaspkit -task 102 -kpr 0.04     # Γ-centred grid at 0.04 (2π/Å) spacing → 7×7×7 for InAs
```

| Task | Purpose                                                                               |
|------|---------------------------------------------------------------------------------------|
| 101  | INCAR templates (static / relax / HSE / DFT+U / phonon …)                             |
| 102  | KPOINTS grid — Monkhorst-Pack / Γ-centred; set density with `-kpr <spacing>` (0.04 → 7×7×7, 0.019 → 15×15×15 for InAs) |
| 103  | POTCAR (default recommended PAW)                                                      |
| 104  | POTCAR (user-specified PAW per element)                                               |
| 303  | High-symmetry k-path, Setyawan-Curtarolo convention (3D PBE band) → writes `KPATH.in` |
| 302  | High-symmetry k-path for 2D materials                                                 |
| 251  | **HSE band-structure KPOINTS** — IBZKPT mesh + zero-weight path (reads `KPATH.in`)    |
| 211  | Extract/plot PBE band structure from `EIGENVAL` / `vasprun.xml`                       |
| 252  | Extract/plot **HSE** (hybrid) band structure — drops the zero-weight points automatically |
| 111  | Total density of states (112–115 for projected DOS)                                  |
| 911  | Band-gap finder                                                                       |
| 912  | Effective-mass calculator                                                             |

In the [VASP tutorials](../Tutorials/VASP/) we use VASPKIT mainly for tasks **102**, **103**, **303**, **251**, **211**, and **252**.

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

## Marom-group QM packages

Three Python packages maintained in the group are central to inorganic (quantum-materials) work and appear in the workflow around the [VASP tutorials](../Tutorials/VASP/).

### 🔸 [OgreInterface](https://github.com/caizefeng/OgreInterface)
{: #ogreinterface }
- Python package for creating and optimising **lattice-matched and domain-matched epitaxial interfaces**.
- Workflow: lattice/domain matching → interface generation → **surface matching and ranking** → geometry relaxation; it also generates surfaces, computes surface energies, and plots Wulff shapes.
- Surface matching searches the in-plane registry and interfacial distance with **Particle Swarm Optimization (default) or Bayesian Optimization**, scoring candidates with a choice of energy calculator — a machine-learning interatomic potential, an ionic model, or Lennard-Jones.
- Use it to generate the slabs/interfaces you then feed to VASP.

```bash
pip install git+https://github.com/caizefeng/OgreInterface
```

### 🔸 [BayesianOpt4dftu](https://github.com/caizefeng/BayesianOpt4dftu)
{: #bayesianopt4dftu }
- Determines the Hubbard **U** for DFT+U by **Bayesian optimisation** (via the `bayesian-optimization` library), tuning U so the PBE+U band structure and gap match an HSE06 (or experimental) reference — the method behind the [DFT+U section of Tutorial 2](../Tutorials/VASP/Tutorial_2/#adding-dftu-to-a-calculation).
- Driven by a single `bo_dftu` command reading an `input.json`: it runs VASP across iterations, optimises a Δgap / Δband (and optional Δmagnetisation) objective, and writes the optimal U with Gaussian-process mean and acquisition plots.
- Method reference: M. Yu, S. Yang, C. Wu & N. Marom, *npj Comput. Mater.* **6**, 180 (2020).

```bash
pip install git+https://github.com/caizefeng/BayesianOpt4dftu.git
```

### 🔸 [vaspvis](https://github.com/caizefeng/vaspvis)
{: #vaspvis }
- Library for visualising VASP electronic structure: low-level `Band` / `Dos` classes (you supply the matplotlib axis) plus a high-level `standard` module with ~48 ready-made band/DOS styles, and a `utils` module for band-unfolding setup.
- Auto-detects HSE runs and drops the zero-weight seed k-points, so one call plots PBE, PBE+SOC, and HSE bands from `vasprun.xml` / `EIGENVAL` / `PROCAR`.
- Used in the [VASP tutorials](../Tutorials/VASP/) for the figures. Cite: *Phys. Rev. Materials* **5**, 064606 (2021).

```bash
pip install vaspvis
```

Minimum example for a PBE band structure (Tutorials 3–4):

```python
from vaspvis import Band

bs = Band(folder="band/", projected=False)
bs.plot_plain(output="InAs_band.png")
```

For HSE bands (Tutorial 5) the same call works because `vaspvis` reads the IBZKPT-augmented KPOINTS from the run folder and drops the weighted points automatically.

---

## VASP helper scripts

These three small utilities are used throughout the [VASP tutorials](../Tutorials/VASP/). Drop them into `~/` (or wherever is on your `PATH`).

| Script | Purpose | Download |
|--------|---------|----------|
| `incar.py`  | Build an INCAR for SCF / DOS / band / OPT, optionally combined with SOC, HSE, or DFT+U. Defaults set: `EDIFF` auto = 1E-8/atom (snapped to 1/5, ≤ 1E-6), `GGA_COMPAT = .FALSE.`, no `NBANDS` (let VASP decide). | [📥 incar.py](scripts/incar.py)  |
| `kpoints.py` | Write Γ-centred grids, line-mode band paths, or HSE zero-weight KPOINTS using pymatgen's `HighSymmKpath`. | [📥 kpoints.py](scripts/kpoints.py) |
| `potcar.sh` | Concatenate a POTCAR from a local `potpaw_PBE` repository (handles `.gz`/`.Z`). | [📥 potcar.sh](scripts/potcar.sh)  |

Quick install:

```bash
mkdir -p ~/bin
BASE=https://jiayihua2001.github.io/Basic_training
curl -L -o ~/bin/incar.py    $BASE/Utilities/scripts/incar.py
curl -L -o ~/bin/kpoints.py  $BASE/Utilities/scripts/kpoints.py
curl -L -o ~/bin/potcar.sh   $BASE/Utilities/scripts/potcar.sh
chmod +x ~/bin/*.py ~/bin/potcar.sh
echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc
```

> Both `incar.py --help` and `kpoints.py --help` list every flag. Edit `potcar.sh` once to point at your `potpaw_PBE` directory; on Perlmutter the group typically keeps it under `/global/common/software/<repo>/`.

> The Marom-group VASP scripts and the FHI-aims tutorial helpers (`write_control.py`, `automation.py`, `surfaces.py`, `aimsplot.py`) are conceptually similar — they wrap argparse around the parts of the workflow that don't change. Use VASPKIT when you want a richer interactive menu.

---

## AI coding assistants

Research involves a lot of glue code — generating inputs, parsing `OUTCAR` / `vasprun.xml`, batching jobs, plotting. Terminal-based AI coding assistants speed this up and run fine on the Perlmutter **login node**:

- **[Claude Code](https://claude.com/claude-code)** — Anthropic's agentic CLI (`claude`). Good for writing and debugging analysis scripts, extending the helper scripts (`incar.py`, `kpoints.py`), wrangling Slurm submit scripts, and explaining VASP errors. Also available in VS Code / JetBrains and on the web.
- **[OpenAI Codex CLI](https://github.com/openai/codex)** — a comparable terminal agent (`codex`).

Use them to *understand and extend* the workflow, not to skip learning it — the [goal of these tutorials](../) is for you to own the logic, the physics, and the pipeline yourself. Treat generated code like a colleague's: read it, test it, and sanity-check the physics before trusting a number.
