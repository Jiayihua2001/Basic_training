---
layout: default
parent: "Tutorials"
title: "Tutorial_2"
nav_order: 2            # 2,3,4 for the others
---

# Tutorial 2 – Simple Organic Molecules

## Learning Objectives
- Visualising,comparing and Stability-ranking of conformers. 
- Vertical vs adiabatic IP & EA, and how to compute them. 

---

## EX1: Conformers

<img src="../../images/butane.png"
     alt="butane"
     width="450">

- Make a folder for each [butane conformers](https://www.masterorganicchemistry.com/2020/05/29/newman-projection-of-butane-and-gauche-conformation/) (named by different dihedral angle. `60.in`,`180.in`,`300.in`) and rename each `.in` files to `geometry.in`. Try to prepare `control.in` by reading from `geometry.in` this time by `write_control.py`:

  ```bash
  python write_control.py --input_geometry --species_default light 
  ```
then add this line for non-periodic relaxation:
```text
relax_geometry trm 1e-2
```
- Then copy `submit.sh` to each folders, submit the jobs and grep the energy after DFT calculations finished, same as [Turotial_1](../Tutorial_2/).

**TODO**: Compute **ΔE = E – E<sub>min</sub>**. Plot ΔE vs dihedral angle → identify global minimum among local minimums.

---


## EX2:  Compute IP & EA of fumaronitrile.

---
Here is the structure of **fumaronitrile**: 

<img src="../../images/fumaronitrile.PNG"
     alt="fumaronitrile"
     width="200">
---

###  IP & EA
- IP(Ionization Potential):  Energy required to remove 1 e⁻, E<sub>N-1</sub> − E<sub>N</sub>

- EA(Electron Affinity) : Energy released / required to add 1 e⁻, E<sub>N</sub> − E<sub>N+1</sub>


### Vertical & Adiabatic
- Vertical (V): Energy difference between the excited state and the ground state while the geometry is held constant.
- Adiabatic (A): Energy difference between the excited state after post-excitation relaxation and the ground state. 

<img src="../../images/vertical_adiabatic.PNG"
     alt="vertical_adiabatic plot"
     width="450">

[Figure1](https://pubs.acs.org/doi/10.1021/jp501974p): Vertical (∆E_ve) versus adiabatic (∆E_ad) energies. 

---

### 1.  Relax neutral molecule, get E(0).
Rename `fumaronitrile.in` to `geometry.in`, try to relax it, you already know how to do that!

### 2.  Adiabatic & Vertical **IP**

Key edits in `control.in` (adiabatic):

```
spin             collinear
charge           +1.
fixed_spin_moment 1
```
Delete `relax_geometry` for **vertical** calculation.

### 3.  **EA** is analogous (charge –1).

### 4.  Extract & compute
Compute each single point energy of each runs, grep E(+1) and E(–1), compute ΔE_ip and ΔE_ea.
```
ΔE_ip  = E(+1) – E(0)
ΔE_ea  = E(0) – E(–1)
```
**TODO**: Compare the IP and EA of fumaronitrile you obtained using PBE+MBD to experimental values, CCSD(T) reference values, and values obtained using
other electronic structure methods from [research paper](https://pubs.acs.org/doi/10.1021/acs.jctc.5b00875). Note that all the computed values reported in these papers are vertical values.
---
