---
layout: default
parent: "VASP"
grand_parent: "Tutorials"
title: "VASP Basics"
nav_order: 1
---

# VASP Basics
Here we will learn about the basic input and output files for VASP.

## Input Files
### INCAR
The <a href="https://www.vasp.at/wiki/index.php/INCAR" target="_black">INCAR</a> file contains the set of instructions and user-defined parameters to determine the type of calculation that VASP performs. For our research, we will have six main INCAR files for the six main types of calculations that we perform (i.e. self-consistent field (SCF), density of states (DOS), band structure (Band), structural optimization (OPT), wave function visualization (WF), and scanning tunneling microscopy simulations (STM)). There are also five different variations that can be added onto each type of calculation (e.g. DFT+U, spin-orbit coupling (SOC), spin-polarized (SP), slab, hybrid (HSE)). In the next sections, each INCAR file will be shown, and the important parameters will be highlighted.

### KPOINTS
The <a href="https://www.vasp.at/wiki/index.php/KPOINTS" target="_black">KPOINTS</a> file determines how the Brillouin zone is sampled. For our purposes, we will have four different types of KPOINTS files for the following types of calculations: SCF/DOS/WF/STM, PBE Band, HSE Band, and unfolded Band calculations.

### POSCAR
The <a href="https://www.vasp.at/wiki/index.php/POSCAR" target="_black">POSCAR</a> file contains the actual structure that we want to calculate. This can be generated in many different ways, which will be discussed in a later section

### POTCAR
The <a href="https://www.vasp.at/wiki/index.php/POTCAR" target="_black">POTCAR</a> file includes all the pseudopotential information for each element, and can be easily generated using a shell script

## Output Files
### CHG and CHGCAR
The <a href="https://www.vasp.at/wiki/index.php/CHG" target="_black">CHG</a> and <a href="https://www.vasp.at/wiki/index.php/CHG" target="_black">CHGCAR</a> file contain the structure and a 3D FFT grid of the charge density calculated during an SCF calculation. For Band, DOS, WF, and STM calculations, the CHG and CHGCAR files are read in as inputs are are used to calculate the eigenvalues.

### WAVECAR
The <a href="https://www.vasp.at/wiki/index.php/WAVECAR" target="_black">WAVECAR</a> is a binary file that contains the information about the wave function. The file can usually be quite large for structures with many atoms (on the order of 100’s of GBs) so we avoid writing it unless absolutely necessary (e.g. unfolded Band, WF, and STM calculations).

### OSZICAR
The <a href="https://www.vasp.at/wiki/index.php/OSZICAR" target="_black">OSZICAR</a> file shows us the convergence of our calculations. We can use this to check on the status of our calculations while they are running

### OUTCAR
The <a href="https://www.vasp.at/wiki/index.php/OUTCAR" target="_black">OUTCAR</a> file contains all the outputs from the calculation. We typically don’t look into this file too much, but you can get some useful parameters from it such as the Fermi energy.
