---
layout: default
parent: "HPC Onboard"
title: "MSE-HPC"
nav_order: 1
---

# MSE-HPC

**MSE-HPC** is the Carnegie Mellon Materials Science & Engineering department cluster. It is the group's cluster for the **FHI-aims (organic / molecular)** tutorials, replacing the now-deprecated Arjuna.

Hardware / scheduler at a glance:

| | |
|---|---|
| Compute nodes | 43 × dual–socket Intel **Broadwell**, **28 cores** / node, 128 GB RAM |
| Partition | `compute` (default), 3-day max wall time |
| Scheduler | SLURM (default account — no `-A` flag needed) |
| Modules | Lmod + Spack (`module avail`) |
| Home | `/home/$USER` (BeeGFS parallel filesystem, shared across all nodes) |
| Toolchain for FHI-aims | Intel `ifort` (classic) + Intel MPI + Intel MKL (ScaLAPACK) |

> ⚠️ The head node (`mse-hpc-head`) is for editing, compiling, and submitting only — **never run calculations on it**. Submit to the compute nodes with `sbatch`/`srun`.

---

## Logging In to MSE-HPC

- **Network Access:** Connect to CMU Wi-Fi or use the [CMU VPN](https://www.cmu.edu/computing/services/endpoint/network-access/vpn/how-to/index.html) if you're off campus.

- **SSH Login:**
  ```bash
  ssh <AndrewID>@mse-hpc-head.materials.local.cmu.edu
  ```

---

## Transferring Files Between Local and MSE-HPC

### From MSE-HPC to Local

```bash
# Single file
scp <AndrewID>@mse-hpc-head.materials.local.cmu.edu:<remote_file> <local_destination>

# Directory
scp -r <AndrewID>@mse-hpc-head.materials.local.cmu.edu:<remote_dir> <local_destination>
```

### From Local to MSE-HPC

```bash
# Single file
scp <local_file> <AndrewID>@mse-hpc-head.materials.local.cmu.edu:<remote_destination>

# Directory
scp -r <local_dir> <AndrewID>@mse-hpc-head.materials.local.cmu.edu:<remote_destination>
```

---

## Software Modules

MSE-HPC uses **Lmod** (backed by Spack). Useful commands:

```bash
module avail                 # list available modules
module load <module_name>    # load one (e.g. intel-oneapi-mpi)
module list                  # show what's loaded
module purge                 # unload everything
```

> The FHI-aims `submit.sh` does **not** rely on `module load` — it sources the
> compiler / MPI / MKL environment directly (via `aims_env.sh`), because
> `module load` is not available inside batch jobs on the compute nodes. You only
> need `module` for interactive work.

---

## FHI-aims on MSE-HPC

**You do not need to compile anything.** The group maintains a single shared, pre-built FHI-aims that every member can use directly from the BeeGFS filesystem:

```text
/mnt/beegfs/27-735/programs/fhi-aims.250822/
├── build/aims.250822.ifort.scalapack.mpi.x   # the MPI executable
├── aims_env.sh                          # sets up the Intel MPI + MKL runtime
├── intel-classic-2021.13-rt/            # Intel Fortran runtime libs (used by aims_env.sh)
└── species_defaults/                    # basis sets (used by write_control.py)
```

The tutorial's `submit.sh` and `write_control.py` already point at this location (they are installed for you by `setup_utils.sh` — see the [Quick Onboard](../../)), so there is nothing to install or build. Just make sure you can read it:

```bash
ls /mnt/beegfs/27-735/programs/fhi-aims.250822/build/aims.250822.ifort.scalapack.mpi.x
```

If that path is ever missing or moved, only two files need updating — `AIMS_DIR` in `submit.sh` and `BASE_SPECIES_PATH` in `write_control.py`.

---

## Python environment (for the helper scripts)

The tutorial helper scripts (`write_control.py`, `Automation.py`, `Surfaces.py`, `aimsplot.py`) need Python with **ASE**. MSE-HPC has no conda module, so the class provides a shared **base conda** (read-only — it plays the role of the conda module on the group's other clusters), and **you create your own environment with it**. Creating and managing your environment is part of the training — the commands are explained in [virtual_env](../virtual_env):

```bash
# every session (best: add this line to your ~/.bashrc):
source /mnt/beegfs/27-735/programs/miniforge3/etc/profile.d/conda.sh

# ONE TIME — create your own environment. Because the shared install is
# read-only, conda automatically puts it in ~/.conda/envs/ase_env:
conda create -n ase_env python=3.10
conda activate ase_env
pip install ase matplotlib numpy scipy spglib

# every later session:
conda activate ase_env
```

(Installing your own [Miniforge](https://github.com/conda-forge/miniforge) in your home instead also works — the helper scripts only care that `import ase` succeeds in whatever Python is active.)

---

## FHI-aims Submission Script

Download the MSE-HPC `submit.sh` for FHI-aims here:
[📥 Download `submit.sh` for FHI-aims on MSE-HPC](submit.sh)

It requests one full compute node (28 MPI ranks), sources the shared `aims_env.sh`, and runs the shared FHI-aims binary. `setup_utils.sh mse-hpc` installs the right copy to `~/aims_utils/submit.sh` for you (see the [Quick Onboard](../../)).

---

## Preparation before computation

- **Log in to MSE-HPC**
  ```bash
  ssh <AndrewID>@mse-hpc-head.materials.local.cmu.edu
  ```
- **Activate your Python (ASE) environment** (create it once first — see above)
  ```bash
  source /mnt/beegfs/27-735/programs/miniforge3/etc/profile.d/conda.sh
  conda activate ase_env
  ```
- **FHI-aims is already available** — the shared install (see above) is used
  automatically. `submit.sh` sources its `aims_env.sh` for you, so you do **not**
  need to load any modules by hand before `sbatch ~/aims_utils/submit.sh`.

For general SLURM usage see [slurm_basic](../slurm_basic); for questions, contact `mse-it@andrew.cmu.edu`.
