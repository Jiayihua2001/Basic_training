---
layout: default
parent: "VASP"
grand_parent: "Tutorials"
title: "Bulk InAs (HSE)"
nav_order: 5
---

# Tutorial 5 — Bulk InAs (HSE06 + SOC)

## 📖 Learning objectives

* Run an HSE06 hybrid-functional SCF, band, and DOS workflow combined with SOC.
* Understand the **zero-weight k-point scheme** that VASP requires for hybrid band structures, and how VASPKIT (`-task 251`) builds it for you.
* See HSE06 + SOC reproduce the experimental InAs band gap.

> HSE06 calculations are typically 50–100× more expensive than PBE because the exchange operator is computed over all k-point pairs. Always pre-converge the structure and the k-mesh at the PBE level first.

---

## 5.1 What changes vs. Tutorial_4

| Aspect | PBE+SOC (Tutorial_4) | HSE+SOC (this tutorial) |
|--------|----------------------|--------------------------|
| Functional | PBE | HSE06 (`AEXX = 0.25`, `HFSCREEN = 0.2`) |
| Pre-converged file passed downstream | `CHGCAR` | **`WAVECAR`** (you must set `LWAVE = .TRUE.` in the SCF) |
| `ALGO` | `Fast` everywhere | `Fast` for SCF, **`Damped`** for non-self-consistent band/DOS |
| `ICHARG` for band/DOS | 11 (read CHGCAR) | 0 (read WAVECAR) |
| KPOINTS for band | line-mode | **IBZKPT (weight > 0) + line-mode (weight = 0)** |
| Ranks (recommended) | 64 (1 node) | 128 (2 nodes) |

---

## 5.2 Prepare the tree and copy POSCAR/POTCAR

```bash
mkdir -p $SCRATCH/InAs/hse/{scf,dos,band}
cd       $SCRATCH/InAs/hse
cp $SCRATCH/InAs/pbe/POSCAR  scf/ &&  cp scf/POSCAR dos/ &&  cp scf/POSCAR band/
cp $SCRATCH/InAs/pbe/POTCAR  scf/ &&  cp scf/POTCAR dos/ &&  cp scf/POTCAR band/
```

---

## 5.3 Generate the INCARs

```bash
cd scf
python ~/bin/incar.py --scf  --soc --hse --encut 400
python ~/bin/kpoints.py --grid -d 7 7 7

cd ../dos
python ~/bin/incar.py --dos  --soc --hse --encut 400
python ~/bin/kpoints.py --grid -d 11 11 11    # HSE-DOS uses a smaller grid than PBE-DOS

cd ../band
python ~/bin/incar.py --band --soc --hse --encut 400
# KPOINTS for HSE band — see 4.4
```

`scf/INCAR` ends with the HSE block (and the `--scf` overrides set `LWAVE = .TRUE.`):

```text
LHFCALC  = .TRUE.
HFSCREEN = 0.2
AEXX     = 0.25
PRECFOCK = Fast
TIME     = 0.4
```

`band/INCAR` and `dos/INCAR` add `ALGO = Damped` automatically (overriding the `ALGO = Fast` from the general block) and set `ICHARG = 0` so eigenvalues are recomputed from the SCF `WAVECAR`.

---

## 5.4 The HSE band-structure KPOINTS file

VASP cannot do a pure non-self-consistent hybrid run, because the exact-exchange operator depends on **all** occupied orbitals. The standard workaround: combine the SCF irreducible mesh (`IBZKPT`) — which carries the orbitals needed to evaluate the exchange — with the line-mode k-path you actually want to plot, **at zero weight** so it does not contribute to the exchange integral.

After the SCF step finishes, run **one** of the following from `band/`:

### Option A — VASPKIT (recommended)

```bash
cd ../band
vaspkit -task 251       # interactive: pick the path in fractional coords (G-X-W-L-G-K)
```

VASPKIT reads `../scf/IBZKPT`, asks for the path and the number of intermediate points, and writes a `KPOINTS` file with weights `>0` for the SCF mesh and `0` for the band path.

### Option B — `kpoints.py`

```bash
cd ../band
python ~/bin/kpoints.py --band --hse -c GXWLGK -n 40 --ibzkpt ../scf/IBZKPT
```

The output looks like:

```text
Automatically generated mesh
   230
Reciprocal lattice
   0.00000000   0.00000000   0.00000000     1
   0.14285714   0.00000000   0.00000000     4
   ...                                      (IBZKPT lines, weights > 0)
   0.34615385   0.34615385   0.69230769     0
   0.37500000   0.37500000   0.75000000     0     (line-mode points, weight 0)
```

> The number of weight-0 points equals `n_segments × pts_per_segment`. Plot only the zero-weight points; VASPKIT's `-task 213` already does this.

---

## 5.5 Submit

HSE is dominated by the exact-exchange operator; the **GPU build** is much faster than the CPU build for this kind of workload, so use the GPU script when you can. Both variants follow the [Perlmutter sbatch templates](../../../HPC%20Onboard/Perlmutter/#vasp-sbatch-templates).

### GPU (recommended)

📥 `submit.sh` — 1 node, 4 A100 GPUs, 4 MPI ranks (1 per GPU):

```bash
#!/bin/bash
#SBATCH -J InAs_hse
#SBATCH -A m3578              # update to your repo if different
#SBATCH -N 1
#SBATCH -C gpu
#SBATCH -G 4
#SBATCH -q regular
#SBATCH --exclusive
#SBATCH -t 02:00:00
#SBATCH -o slurm-%j.out

module load vasp/6.4.3-gpu
export NCCL_IGNORE_CPU_AFFINITY=1

# OpenMP settings:
export OMP_NUM_THREADS=1
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

# 1) HSE SCF (writes WAVECAR because incar.py sets LWAVE = .TRUE. for --scf --hse)
cd scf
srun -n 4 -c 32 --cpu_bind=cores --gpu-bind=none -G 4 vasp_ncl > vasp.out

# 2) Pull Fermi energy and patch dos/INCAR
efermi=$(awk '/E-fermi/ {print $3}' OUTCAR | tail -n 1)
emin=$(echo "$efermi - 3.0" | bc -l)
emax=$(echo "$efermi + 3.0" | bc -l)
sed -i "s/EMIN   = emin/EMIN   = $emin/" ../dos/INCAR
sed -i "s/EMAX   = emax/EMAX   = $emax/" ../dos/INCAR

# 3) Hand the WAVECAR to band/ and dos/
cp WAVECAR ../band/
cp WAVECAR ../dos/

# 4) Build the HSE band KPOINTS (after IBZKPT exists), then run band
cd ../band
python ~/bin/kpoints.py --band --hse -c GXWLGK -n 40 --ibzkpt ../scf/IBZKPT
srun -n 4 -c 32 --cpu_bind=cores --gpu-bind=none -G 4 vasp_ncl > vasp.out

# 5) HSE DOS
cd ../dos
srun -n 4 -c 32 --cpu_bind=cores --gpu-bind=none -G 4 vasp_ncl > vasp.out
```

For the GPU build, `KPAR = 4` (one k-group per GPU) is the natural choice and `NCORE` is auto-reset to 1 by VASP. Generate the INCARs with `incar.py --kpar 4 --ncore 1 ...`.

### CPU (alternative)

If GPU nodes are full, fall back to CPU on **2 nodes** (32 ranks × 8 OpenMP threads):

```bash
#SBATCH -N 2
#SBATCH -C cpu
#SBATCH -t 04:00:00
module load vasp/6.4.3-cpu
export OMP_NUM_THREADS=8
srun -n 32 -c 16 --cpu_bind=cores vasp_ncl > vasp.out
```

In the INCAR set `KPAR = 8` so each k-group has 4 MPI ranks (`incar.py --kpar 8 --ncore 1 ...`).

A GPU HSE+SOC run for the InAs primitive cell finishes in roughly 10–20 minutes per step; the equivalent 2-node CPU run takes 1–2 h.

---

## 5.6 Plot and analyse

```bash
cd ../band
vaspkit -task 213           # plots an HSE band, dropping the IBZKPT weighted points
cd ../dos
vaspkit -task 111
```

`vaspvis` is built specifically to handle the HSE zero-weight scheme and is the easiest path to publication-quality figures:

```python
from vaspvis import Band, Dos

Band(folder="band/", projected=False, hse=True).plot_plain(output="InAs_hse_band.png")
Dos(folder="dos/").plot_plain(output="InAs_hse_dos.png")
```

Setting `hse=True` tells `vaspvis` to drop the IBZKPT-weighted points and plot only the line-mode segment.

### What you should see

* HSE06 + SOC opens the gap to ≈ **0.39 eV**, in good agreement with the 0.354 eV experimental value at room temperature.
* The Γ⁷ split-off splitting is essentially unchanged from Tutorial_4 — SOC and HSE address different parts of the error.
* Compared to PBE+SOC, the HSE conduction band is shifted up nearly rigidly while the valence band shifts only slightly; this is the characteristic behaviour of the "scissor" correction that hybrids supply.

---

## 5.7 Assignment

* **(5 points)** Run the HSE06+SOC SCF/DOS/band chain and report the band gap. Compare with the PBE+SOC value from Tutorial_4 and the experimental gap.
* **(10 points)** Overlay PBE+SOC and HSE+SOC bands in one figure. Comment on which features are well captured by PBE+SOC, and which require HSE.
* **(5 points)** Time the HSE+SOC step against PBE+SOC for the same system. How does the cost scale with `AEXX = 0.25` vs. `0.0` (a quick sanity check — set `AEXX = 0.0` and re-run the SCF only)?
* **(5 points)** Use VASPKIT task **912** to estimate the electron and heavy-/light-hole effective masses near Γ. Compare with the standard textbook values (m_e ≈ 0.023 m₀, m_hh ≈ 0.41 m₀, m_lh ≈ 0.026 m₀).

When you can reproduce the experimental gap to within 50 meV you have completed the VASP basic-training track. Move on to fitting **PBE+U** parameters to this HSE reference, or to thin-film and interface calculations using the same workflow but a slab POSCAR.
