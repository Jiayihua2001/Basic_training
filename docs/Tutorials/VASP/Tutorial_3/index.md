---
layout: default
parent: "VASP"
grand_parent: "Tutorials"
title: "Tutorial_3"
nav_order: 3
---

# Tutorial 3 — Bulk InAs (PBE+SOC)

## 📖 Learning objectives

* Add spin-orbit coupling (SOC) to the InAs workflow.
* Understand why SOC requires the **non-collinear** binary `vasp_ncl`.
* See the SOC-induced splitting of the InAs valence band (the "split-off" Γ⁷ band).

> SOC is essential for any heavy-element semiconductor (In, Sb, Bi, Pb, …) and changes the band structure qualitatively, not just quantitatively. PBE+SOC is the minimum acceptable level of theory for InAs.

---

## 3.1 What changes vs. Tutorial_2

| Aspect | PBE (Tutorial_2) | PBE+SOC (this tutorial) |
|--------|-----------------|--------------------------|
| Binary | `vasp_std` | **`vasp_ncl`** |
| INCAR additions | — | `LSORBIT = .TRUE.`, `MAGMOM = 6*0` |
| Wave-function size | 1 spin channel | 2 spinor components — VASP doubles `NBANDS` internally |
| Cost | × 1 | ≈ × 4–8 (more bands, complex orbitals) |
| Symmetry | full point group | reduced — set `ISYM = -1` only if the run aborts on symmetry |

The folder layout, KPOINTS, and POTCAR are identical to Tutorial_2.

---

## 3.2 Prepare the tree

Reuse the InAs POSCAR and POTCAR from Tutorial_2:

```bash
mkdir -p $SCRATCH/InAs/pbe-soc/{scf,dos,band}
cd       $SCRATCH/InAs/pbe-soc
cp $SCRATCH/InAs/pbe/POSCAR  scf/  &&  cp scf/POSCAR dos/  &&  cp scf/POSCAR band/
cp $SCRATCH/InAs/pbe/POTCAR  scf/  &&  cp scf/POTCAR dos/  &&  cp scf/POTCAR band/
```

---

## 3.3 Generate the INCARs

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

## 3.4 Submit

📥 `submit.sh`:

```bash
#!/bin/bash
#SBATCH -J InAs_pbe_soc
#SBATCH -A <repo>
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH -t 01:00:00
#SBATCH -o slurm-%j.out

module load vasp/6.4.3-cpu
export OMP_NUM_THREADS=2
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

cd scf
srun -n 64 -c 4 --cpu-bind=cores vasp_ncl > vasp.out

efermi=$(awk '/E-fermi/ {print $3}' OUTCAR | tail -n 1)
emin=$(echo "$efermi - 3.0" | bc -l)
emax=$(echo "$efermi + 3.0" | bc -l)
sed -i "s/EMIN   = emin/EMIN   = $emin/" ../dos/INCAR
sed -i "s/EMAX   = emax/EMAX   = $emax/" ../dos/INCAR

cp CHG CHGCAR ../band/
cp CHG CHGCAR ../dos/

cd ../band
srun -n 64 -c 4 --cpu-bind=cores vasp_ncl > vasp.out

cd ../dos
srun -n 64 -c 4 --cpu-bind=cores vasp_ncl > vasp.out
```

Note **`vasp_ncl`** instead of `vasp_std`. SOC roughly quadruples the runtime relative to Tutorial_2; budget ~5–10 minutes of wall time on 1 node.

---

## 3.5 Plot and analyse

```bash
cd ../band
vaspkit -task 211       # picks up LSORBIT automatically
cd ../dos
vaspkit -task 111
```

### What you should see

* The valence band that was three-fold degenerate at Γ in pure PBE now **splits** into a four-fold heavy-/light-hole pair (Γ⁸) and a lower **split-off** band (Γ⁷). The InAs split-off energy is ≈ 0.39 eV experimentally.
* The conduction-band minimum stays at Γ; the gap is still much smaller than experiment because PBE-level self-interaction error is not fixed by SOC alone.
* Far from Γ, SOC is a small perturbation — the band shapes look very similar to Tutorial_2.

---

## 3.6 Assignment

* **(5 points)** Run the PBE+SOC SCF/DOS/band workflow and submit the converged outputs.
* **(10 points)** Overlay the PBE and PBE+SOC band structures in a single figure (use `vaspkit` or your favourite plotter). Identify the split-off band and report the Γ⁷–Γ⁸ splitting at Γ. Compare with the experimental value.
* **(5 points)** Compare the DOS at and below the Fermi level between PBE and PBE+SOC. Where do you see the largest changes, and why?
* **(5 points)** Quote the wall-time difference between Tutorial_2 and Tutorial_3. Where is the extra cost spent (use the `OUTCAR` "Total CPU time" breakdown).

Once SOC is satisfying, move on to [Tutorial_4 — Bulk InAs (HSE06)](../Tutorial_4/) to fix the band-gap problem.
