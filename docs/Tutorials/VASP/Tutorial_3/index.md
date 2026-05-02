---
layout: default
parent: "VASP"
grand_parent: "Tutorials"
title: "Bulk InAs (PBE)"
nav_order: 3
---

# Tutorial 3 — Bulk InAs (PBE)

## 📖 Learning objectives

* Run a complete SCF → DOS → band-structure workflow on a bulk semiconductor.
* Use `incar.py` and either `kpoints.py` or VASPKIT to generate the input files.
* Submit a multi-step job on Perlmutter that pipes the SCF Fermi energy into the DOS `INCAR`.
* See first-hand why plain PBE underestimates the InAs band gap.

> **Notation**
> * Lattice constants and bond lengths are in Å.
> * `<repo>` stands for your NERSC allocation (e.g. `m4055`); update each `submit.sh`.
> * Working directory: anywhere under `$SCRATCH`.

---

## 3.1 Set up the working tree

InAs has the zinc-blende structure (FCC, two atoms in the primitive cell). Make a fresh tree:

```bash
mkdir -p $SCRATCH/InAs/pbe/{scf,dos,band}
cd       $SCRATCH/InAs/pbe
```

### POSCAR

Two-atom primitive cell, lattice parameter from Materials Project (`a` ≈ 6.0584 Å, primitive vectors `a/2 (eᵢ + eⱼ)`):

```text
In As
1.0
   0.000000   3.029200   3.029200
   3.029200   0.000000   3.029200
   3.029200   3.029200   0.000000
In As
1 1
direct
   0.000000   0.000000   0.000000
   0.250000   0.250000   0.250000
```

Save it as `POSCAR` in the run directory and copy it into `scf/`, `dos/`, `band/`. View it in [VESTA](https://jp-minerals.org/vesta/en/) (`File → Import`) to confirm In and As sit at the FCC and tetrahedral interstitial sites.

### POTCAR

```bash
bash potcar.sh In As
grep TITEL POTCAR
# Expected:
#   TITEL = PAW_PBE In 08Apr2002
#   TITEL = PAW_PBE As 22Sep2009
```

The species order on line 6 of `POSCAR` (`In As`) must match the `TITEL` order. Copy `POTCAR` into `scf/`, `dos/`, `band/`.

---

## 3.2 SCF step

Inside `scf/`:

```bash
cd scf
python ~/bin/incar.py --scf --encut 400
python ~/bin/kpoints.py --grid -d 7 7 7      # or: vaspkit -task 102 (Gamma 7 7 7)
```

Resulting **`scf/INCAR`** (calc-specific block only — the [general block](../Tutorial_2/#21-the-shared-general-incar-block) is on top):

```text
ICHARG = 2
ISMEAR = 0
LCHARG = .TRUE.
LWAVE  = .FALSE.
LREAL  = .FALSE.
```

`scf/KPOINTS`:

```text
Automatic kpoint scheme
0
Gamma
7 7 7
```

A 7×7×7 Γ-centred grid is plenty for this 2-atom cell. Once you are familiar, run a quick convergence test on `ENCUT` and the k-grid before trusting the gap.

---

## 3.3 DOS step

Inside `dos/`:

```bash
cd ../dos
python ~/bin/incar.py --dos --encut 400
python ~/bin/kpoints.py --grid -d 15 15 15   # or: vaspkit -task 102 (Gamma 15 15 15)
```

`dos/INCAR` calc-specific block:

```text
ICHARG = 11
ISMEAR = -5
LCHARG = .FALSE.
LWAVE  = .FALSE.
LORBIT = 11
NEDOS  = 3001
EMIN   = emin     # replaced at submission time
EMAX   = emax
```

The placeholder `emin`/`emax` is rewritten by the submission script (next section) using the Fermi energy from the SCF `OUTCAR`, ±3 eV.

---

## 3.4 Band-structure step

Inside `band/`:

```bash
cd ../band
python ~/bin/incar.py --band --encut 400
python ~/bin/kpoints.py --band -c GXWLGK -n 50
# or, equivalently, with VASPKIT:
#    vaspkit -task 303    (then choose the Setyawan-Curtarolo path)
```

`band/INCAR` calc-specific block:

```text
ICHARG = 11
ISMEAR = 0
LCHARG = .FALSE.
LWAVE  = .FALSE.
LORBIT = 11
```

`band/KPOINTS` (line-mode along Γ-X-W-L-Γ-K, 50 points/segment) is auto-generated. The first few lines look like:

```text
Line_mode KPOINTS file
50
Line_mode
Reciprocal
0.0   0.0   0.0   ! G
0.5   0.0   0.5   ! X

0.5   0.0   0.5   ! X
0.5   0.25  0.75  ! W
...
```

> **Heads-up:** the `Line-mode` style uses **fractional reciprocal-lattice coordinates** of the *primitive* cell. If you start from a conventional cell (e.g. cubic 8-atom InAs) the coordinates change.

---

## 3.5 Submit the chained job

📥 Save the script below as `submit.sh` in the parent directory (`$SCRATCH/InAs/pbe/`). It follows the Marom-group [Perlmutter CPU template](../../../HPC%20Onboard/Perlmutter/#vasp-sbatch-templates): 16 MPI ranks × 8 OpenMP threads (= 128 physical cores on one CPU node).

```bash
#!/bin/bash
#SBATCH -J InAs_pbe
#SBATCH -A m3578              # update to your repo if different
#SBATCH -N 1
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -t 00:30:00
#SBATCH -o slurm-%j.out

module load vasp/6.4.3-cpu

# OpenMP settings:
export OMP_NUM_THREADS=8
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

# 1) SCF
cd scf
srun -n 16 -c 16 --cpu_bind=cores vasp_std > vasp.out

# 2) Pull Fermi energy and patch dos/INCAR
efermi=$(awk '/E-fermi/ {print $3}' OUTCAR | tail -n 1)
emin=$(echo "$efermi - 3.0" | bc -l)
emax=$(echo "$efermi + 3.0" | bc -l)
sed -i "s/EMIN   = emin/EMIN   = $emin/" ../dos/INCAR
sed -i "s/EMAX   = emax/EMAX   = $emax/" ../dos/INCAR

# 3) Hand the converged charge density to band/ and dos/
cp CHG CHGCAR ../band/
cp CHG CHGCAR ../dos/

# 4) Band
cd ../band
srun -n 16 -c 16 --cpu_bind=cores vasp_std > vasp.out

# 5) DOS
cd ../dos
srun -n 16 -c 16 --cpu_bind=cores vasp_std > vasp.out
```

Submit:

```bash
sbatch submit.sh
sqs -u $USER          # follow the queue
tail -f scf/OSZICAR   # live-monitor SCF convergence
```

The whole chain finishes in a few minutes for 2 atoms on 1 node. If the `band/` or `dos/` step warns *"Charge file is empty"*, the SCF step did not write `CHG*` — check that the SCF `INCAR` had `LCHARG = .TRUE.`.

---

## 3.6 Plotting and analysis

Use [`vaspvis`](https://github.com/caizefeng/vaspvis) — it is the recommended plotting toolchain for the VASP tutorials.

```python
from vaspvis import Band, Dos

Band(folder="band/", projected=False).plot_plain(output="InAs_pbe_band.png")
Dos(folder="dos/").plot_plain(output="InAs_pbe_dos.png")
```

> If you do not have `vaspvis` available, `vaspkit -task 211` (band) and `vaspkit -task 111` (DOS) will export the same data into ASCII tables you can plot manually.

For reference, here are the figures from a converged run:

<img src="../../../images/vasp/pbe_bands_plot.png" alt="InAs PBE band structure along Γ-X-W-L-Γ-K" width="450">

<img src="../../../images/vasp/pbe_dos_plot.png" alt="InAs PBE total density of states" width="450">

*(Figures reproduced from [marom_group_docs](https://github.com/DerekDardzinski/marom_group_docs), AGPLv3.)*

### What you should see

* The valence-band maximum (VBM) and conduction-band minimum (CBM) both at Γ → InAs is a **direct-gap** semiconductor.
* The PBE band gap is ≈ **0 eV** (sometimes faintly negative depending on lattice constant). Experiment: 0.354 eV at 300 K. This is the well-known "PBE underestimates band gaps" problem caused by self-interaction error.
* The DOS is roughly zero between ≈ −3 eV and the Fermi level on the valence side and zero just above it on the conduction side.

---

## 3.7 Assignment

* **(5 points)** Write the InAs `POSCAR` and check the structure in VESTA. Capture a screenshot.
* **(5 points)** Run a quick `ENCUT` convergence (300, 350, 400, 450 eV at fixed 7×7×7 grid) and a k-point convergence (5³, 7³, 9³, 11³ at fixed `ENCUT = 400`). Plot total energy vs each parameter and explain your choice.
* **(10 points)** Plot the PBE band structure and DOS for converged settings. Quote your computed band gap (or "metallic" if the bands cross). Compare with the experimental value (0.354 eV) and explain the discrepancy in one paragraph.
* **(5 points)** Inspect `EIGENVAL` and identify the band index of the VBM and CBM. Why do these matter for SOC and HSE later?

When you are happy with the PBE result, move on to [Tutorial 4 — Bulk InAs (PBE+SOC)](../Tutorial_4/).
