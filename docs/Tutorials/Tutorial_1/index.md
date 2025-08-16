---
layout: default
parent: "Tutorials"
title: "Tutorial_1"
nav_order: 1            # 2,3,4 for the others
---

# Tutorial 1 : H₂ Binding, Convergence, and Relaxation

## 📖 Learning objectives:
- FHI-aims basic
- submitting jobs on Trace or Arjuna.
- numerical convergence & scaling
- structure optimization.

> **Notation used**
> - Distances are in Å
> - Activate your virtual env if the python script needs ase. If you don't have one, go [create one](../../HPC%20Onboard/virtual_env) !

---
##  FHI-aims basic

**FHI-aims** is an all-electron, DFT-based electronic structure code designed for:
- Molecules and periodic systems
- High-accuracy total energy and force calculations
- Materials simulations including structure relaxation, molecular dynamics, and property evaluation

FHI-aims uses numeric atom-centered orbitals and supports a wide range of functionals, dispersion corrections, and parallel execution on HPC clusters.
For detailed settings, please check [FHI-aims Manual](chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://fhi-aims.org/uploads/documents/FHI-aims.221103_1.pdf)


### 📁 Required Files in a FHI-aims Calculation

- `geometry.in`: Defines the atomic structure of the system.
- `control.in`: Specifies the calculation settings, must include species orbit definitions appended at the end (copied from species_defaults/)
- `submit.sh`: A SLURM batch script to run FHI-aims on HPC.

---

## EX1: H2 binding energy evaluation
### 1. Activate your virtual env. Generate `control.in` Files by `write_control.py` script(under utils directory):

before running `write_control.py`, please change the `BASE_SPECIES_PATH` in the script to the correct path of FHI-aims species directory on the HPC you use.
-BASE_SPECIES_PATH on Trace: /trace/group/marom/shared/programs/fhi_aims_latest/fhi-aims.240507/species_defaults/defaults_2020/
-BASE_SPECIES_PATH on Arjuna: /home/marom_group/programs/fhi_aims_2023/fhi-aims.221103/species_defaults/defaults_2020/

  ```bash
  python write_control.py --elements H --species_default light
  ```
  Run ``python write_control.py --help`` for full flag descriptions.
### 2. Generate `geometry.in` Files at Different H–H Distances

Use the helper script `distance_generator.py` to create H₂ geometries with bond lengths from 0.5 Å to 1.0 Å:
  ```bash
  python distance_generator.py
  ```

You can optionally [**visualize the structures**](../../Utilities/) using:

* **Jmol** for orbital inspection
* **OVITO** for 3D structural visualization


### 3. Run FHI-aims Calculations
The help script also help paste `control.in` and `submit.sh` in each folder. Then you can enter each folder, submit the job by :
  ```bash 
  sbatch submit.sh
  ```

Submit each folder to your cluster, You’ll know the run is finished when:

* You see `Have a nice day.` at the end of `aims.out`
* Or check status on HPC with:

  ```bash
  squeue -u <your_username>
  ```

### 5. Extract Energies & Plot Dissociation Curve

After runs finish,run this command under the created `H2_binding_energy` path:

```bash
grep '| Total energy of the DFT / Hartree-Fock s.c.f. calculation' */aims.out > energies.txt
```
**TODO**: After get the energies (eV), you could try to plot the dissociation curve to visualize it, try to plot it using matplotlib!.

Now, you have successdully set up a simple DFT workflow to evaluate the **H₂ binding energy** by generating a **dissociation curve** !

## EX2:  Numerical convergence & scaling

Compare **basis tiers 1–3** and species defaults **light / intermediate / tight** to analyze accuracy vs cost.
- The basis functions are classified in “tiers” (i.e., levels of importance). Not all basis functions are enabled by default. Rather, some are commented out using the “ # ” symbol. 
  - You can select the basis tiers by leaving the one you want uncomment in `control.in` files.
- Species defaults control the numerical integration grids, cutoff radii, and other internal accuracy parameters. light is the fastest, tight is the most accurate.
  - You can change the species defaults by changing the param `--species_default` when preparing `control.in` files using `write_control.py`

To evaluate the cost, grep the time of each runs:
  ```bash
  grep '| Total time                                  :' */aims.out > times.txt
  ```
**TODO**: You will get 2 kinds of time (max(cpu_time) and wall_clock(cpu1)), use wall_clock for evaluation. Try to write a loop to run and make a table to compare the accuracy and cost between different basis tier and species default.

---

## EX3: Structure optimization/relaxation

Try to pick the run with the lowest-energy, Put the `geometry` and `submit.sh` in the `1/relaxation` folder. Then add this command to the `control.in` file for non-periodic relaxation: 
  ```text
  relax_geometry bfgs 1e-2
  ```
**TODO**:
- Try to compare the difference between the `control.in` for single point energy and relaxtion.
- Try to make a “relaxation movie” in **OVITO** from FHI-aims output by excuting `extract_traj_frame.py` help script, then drag the output `.xyz` file in **OVITO**.

### Final H–H Distance

After relaxation, check final structure `geometry.in.next_step` use visulization tool or use python to execute the following code:
```python
from ase.io import read
ase_atoms = read("path/to/geometry.in.next_step",format="aims")
distance = ase_atoms.get_distance(0, 1)
```

Compare the H–H bond length to:
* Literature value: \~0.741 Å (experimental)

---


