---
layout: default
title: "Utilities"
nav_order: 4            # 2,3,4 for the others
has_children: true
---
This section provides essential tools and scripts to support your workflow in materials simulation and analysis. It includes:

-  **Utility scripts** explanation of the utilities scripts included in the tutorial package.
-  **Visualization tools** to inspect molecular and crystal structures
-  **Python packages** for structure manipulation, DFT setup, and post-processing

##  Visualization Tools

These tools are useful for visualizing molecules and periodic crystal structures during or after DFT or MD simulations.

### 🔹 [Jmol](http://jmol.sourceforge.net/)
- Java-based interactive viewer for molecules and crystals.
- Supports `.xyz`, `.cif`,`.in`, and many other file formats.
- Ideal for quick viewing of geometries and orbitals.

### 🔹 [OVITO](https://www.ovito.org/)
- Open Visualization Tool for atomistic simulations.
- Especially suited for periodic systems and MD trajectories.
- Supports `.xyz`, `.cfg`, `.lammps`,`.in` and more.
- Offers scripting via Python for analysis and animations.



##  Python Libraries for Materials Analysis

### 🔸 [ASE (Atomic Simulation Environment)](https://wiki.fysik.dtu.dk/ase/)
- Build, manipulate, and visualize atoms and molecules.
- Interfaces with most DFT codes (e.g., GPAW, VASP, FHI-aims).
- Good for scripting calculations and automating workflows.

```bash
pip install ase
````

### 🔸 [pymatgen (Python Materials Genomics)](https://pymatgen.org/)

* Rich toolkit for parsing, analyzing, and generating structures.
* Developed by the Materials Project.
* Excellent `.cif`, `.vasp`, `.poscar` support.

```bash
pip install pymatgen
```