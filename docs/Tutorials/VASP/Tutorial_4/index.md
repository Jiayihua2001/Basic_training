---
layout: default
parent: "VASP"
grand_parent: "Tutorials"
title: "Bulk InAs (PBE+SOC)"
nav_order: 4
---

# Tutorial 4 — Bulk InAs (PBE+SOC)

## 📖 Learning objectives

* Add spin-orbit coupling (SOC) to the InAs workflow.
* Understand why SOC requires the **non-collinear** binary `vasp_ncl`.
* See the SOC-induced splitting of the InAs valence band (the "split-off" Γ⁷ band).

> SOC is essential for any heavy-element semiconductor (In, Sb, Bi, Pb, …) and changes the band structure qualitatively, not just quantitatively. PBE+SOC is the minimum acceptable level of theory for InAs.

---

## 4.1 What changes vs. Tutorial_3

| Aspect | PBE (Tutorial_3) | PBE+SOC (this tutorial) |
|--------|-----------------|--------------------------|
| Binary | `vasp_std` | **`vasp_ncl`** |
| INCAR additions | — | `LSORBIT = .TRUE.`, `MAGMOM = 6*0` |
| Wave-function size | 1 spin channel | 2 spinor components — VASP doubles `NBANDS` internally |
| Cost | × 1 | ≈ × 4–8 (more bands, complex orbitals) |
| Symmetry | full point group | reduced — set `ISYM = -1` only if the run aborts on symmetry |

The folder layout, KPOINTS, and POTCAR are identical to Tutorial_3.

---

## 4.2 Prepare the tree

Reuse the InAs POSCAR and POTCAR from Tutorial_3:

```bash
mkdir -p $SCRATCH/InAs/pbe-soc/{scf,dos,band}
cd       $SCRATCH/InAs/pbe-soc
cp $SCRATCH/InAs/pbe/POSCAR  scf/  &&  cp scf/POSCAR dos/  &&  cp scf/POSCAR band/
cp $SCRATCH/InAs/pbe/POTCAR  scf/  &&  cp scf/POTCAR dos/  &&  cp scf/POTCAR band/
```

---

## 4.3 Generate the INCARs

```bash
cd scf
python ~/bin/incar.py --scf  --soc --encut 400
python ~/bin/kpoints.py --grid -d 7 7 7

cd ../dos
python ~/bin/incar.py --dos  --soc --encut 400
python ~/bin/kpoints.py --grid -d 15 15 15

cd ../band
python ~/bin/incar.py --band --soc --encut 400
python ~/bin/kpoints.py --band -c GXWLGK -n 50
```

Each `INCAR` ends with the SOC block:

```text
LSORBIT = .TRUE.
MAGMOM  = 6*0          # 3 components per atom; 2 atoms => 6 zeros
```

* `MAGMOM` for SOC is **3 numbers per atom** (m_x, m_y, m_z). Using `6*0` for non-magnetic InAs is the simplest choice.
* For magnetic systems specify a non-zero starting moment (e.g. `0 0 2.5 0 0 -2.5` for an antiferromagnetic pair). `incar.py --soc --magmom "0 0 2.5 0 0 -2.5"` writes that for you.
* Setting `ISYM = -1` disables symmetrisation — only do this if VASP aborts with a symmetry error. With clean InAs and `MAGMOM = 6*0` you should not need it.

---

## 4.4 Submit

📥 `submit.sh` — same Perlmutter CPU template as Tutorial_3 but the binary is **`vasp_ncl`** because `LSORBIT = .TRUE.`:

```bash
#!/bin/bash
#SBATCH -J InAs_pbe_soc
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

cd scf
srun -n 16 -c 16 --cpu_bind=cores vasp_ncl > vasp.out

efermi=$(awk '/E-fermi/ {print $3}' OUTCAR | tail -n 1)
emin=$(echo "$efermi - 3.0" | bc -l)
emax=$(echo "$efermi + 3.0" | bc -l)
sed -i "s/EMIN   = emin/EMIN   = $emin/" ../dos/INCAR
sed -i "s/EMAX   = emax/EMAX   = $emax/" ../dos/INCAR

cp CHG CHGCAR ../band/
cp CHG CHGCAR ../dos/

cd ../band
srun -n 16 -c 16 --cpu_bind=cores vasp_ncl > vasp.out

cd ../dos
srun -n 16 -c 16 --cpu_bind=cores vasp_ncl > vasp.out
```

SOC roughly quadruples the runtime relative to Tutorial_3 (more bands, complex spinor orbitals); 30 min on 1 node is still plenty for this 2-atom cell.

---

## 4.5 Plot and analyse

VASPKIT (recommended for the quick look):

```bash
cd ../band
vaspkit -task 211       # picks up LSORBIT automatically
cd ../dos
vaspkit -task 111
```

`vaspvis` works the same way as in Tutorial 3; it transparently handles `LSORBIT = .TRUE.`:

```python
from vaspvis import Band, Dos

Band(folder="band/", projected=False).plot_plain(output="InAs_soc_band.png")
Dos(folder="dos/").plot_plain(output="InAs_soc_dos.png")
```

### What you should see

* The valence band that was three-fold degenerate at Γ in pure PBE now **splits** into a four-fold heavy-/light-hole pair (Γ⁸) and a lower **split-off** band (Γ⁷). The InAs split-off energy is ≈ 0.39 eV experimentally.
* The conduction-band minimum stays at Γ; the gap is still much smaller than experiment because PBE-level self-interaction error is not fixed by SOC alone.
* Far from Γ, SOC is a small perturbation — the band shapes look very similar to Tutorial_3.

---

## 4.6 Assignment

* **(5 points)** Run the PBE+SOC SCF/DOS/band workflow and submit the converged outputs.
* **(10 points)** Overlay the PBE and PBE+SOC band structures in a single figure (use `vaspkit` or your favourite plotter). Identify the split-off band and report the Γ⁷–Γ⁸ splitting at Γ. Compare with the experimental value.
* **(5 points)** Compare the DOS at and below the Fermi level between PBE and PBE+SOC. Where do you see the largest changes, and why?
* **(5 points)** Quote the wall-time difference between Tutorial_3 and Tutorial_4. Where is the extra cost spent (use the `OUTCAR` "Total CPU time" breakdown).

Once SOC is satisfying, move on to [Tutorial 5 — Bulk InAs (HSE)](../Tutorial_5/) to fix the band-gap problem.
