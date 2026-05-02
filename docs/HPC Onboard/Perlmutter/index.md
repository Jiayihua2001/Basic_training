---
layout: default
parent: "HPC Onboard"
title: "Perlmutter"
nav_order: 3
---

# NERSC Perlmutter

Perlmutter is the HPE Cray EX system at the National Energy Research Scientific Computing Center (NERSC). It is the cluster of choice for the quantum-materials subgroup and hosts the VASP builds used in the [VASP tutorials](../../Tutorials/VASP/). Refer to the official NERSC documentation for anything not covered here:

- [Perlmutter architecture](https://docs.nersc.gov/systems/perlmutter/architecture/)
- [Connecting to NERSC](https://docs.nersc.gov/connect/)
- [Running jobs (Slurm)](https://docs.nersc.gov/jobs/)
- [VASP at NERSC](https://docs.nersc.gov/applications/vasp/)

---

## Architecture

| Partition | Nodes | CPU                              | Accelerator        | Memory  | Slurm constraint |
|-----------|------:|----------------------------------|--------------------|--------:|------------------|
| **CPU**   | 3,072 | 2× AMD EPYC 7763 (Milan), 64 c each → 128 physical cores | —          | 512 GB | `-C cpu` |
| **GPU**   | 1,792 | 1× AMD EPYC 7763 (Milan), 64 c   | 4× NVIDIA A100     | 256 GB | `-C gpu` |

Both partitions are exposed in the [VASP tutorials](../../Tutorials/VASP/): SCF/DOS/band runs (Tutorials 3 & 4) target CPU. Tutorial 5 (HSE) is also shown on CPU for accessibility, but the GPU build (`vasp/6.4.3-gpu`) is much faster for exact exchange — the operator maps cleanly onto OpenACC kernels — so switch to it if you can.

---

## Account access

You need an active NERSC user account that is included in an allocation (`-A <repo>`) and in either the `vasp5` or `vasp6` Unix group:

```bash
groups   # confirm vasp6 (or vasp5) is listed
```

If `vasp6` is missing, file a [VASP License Confirmation](https://nersc.servicenowservices.com/sp?id=sc_cat_item&sys_id=d2935b561b032c106c44ebdbac4bcbb6&sysparm_category=e15706fc0a0a0aa7007fc21e1ab70c2f) request through the NERSC help portal.

---

## Logging in

```bash
ssh <username>@perlmutter.nersc.gov
```

You will be prompted for your Iris password followed by your one-time MFA code. To avoid re-authenticating for every connection, configure [`sshproxy`](https://docs.nersc.gov/connect/mfa/#sshproxy) — it caches a 24 h key under `~/.ssh/nersc`:

```bash
ssh -i ~/.ssh/nersc <username>@perlmutter.nersc.gov
```

---

## File systems

| Variable    | Path                                | Quota / lifetime                | Use                                                |
|-------------|-------------------------------------|---------------------------------|----------------------------------------------------|
| `$HOME`     | `/global/homes/<u>/<user>`          | small, permanent, snapshotted   | source code, scripts, configuration                |
| `$SCRATCH`  | `/pscratch/sd/<u>/<user>`           | very large, **purged**, Lustre  | running jobs, checkpoints, working data            |
| `$CFS`      | `/global/cfs/cdirs/<repo>`          | medium, permanent, snapshotted  | shared project data and reference structures       |

Run all VASP jobs in this tutorial from `$SCRATCH`. Move finished files you want to keep to `$CFS` before they age out.

Transfer data with `scp` or `rsync` (use `sshproxy` for password-less transfers):

```bash
rsync -avz local_dir/ <username>@perlmutter.nersc.gov:$SCRATCH/dest/
```

---

## VASP modules

```bash
module avail vasp                 # list available builds
module load vasp/6.4.3-cpu        # CPU build (default for the VASP tutorials)
module load vasp/6.4.3-gpu        # GPU build (faster alternative for HSE)
which vasp_std                    # confirm it loaded
```

Each module exposes three executables — pick the one that matches your INCAR:

| Binary      | Use it for                                                  |
|-------------|-------------------------------------------------------------|
| `vasp_std`  | Standard k-point set (most calculations)                    |
| `vasp_gam`  | Γ-point only (large supercells, gas-phase reference cells)  |
| `vasp_ncl`  | Non-collinear / spin-orbit coupling         |

---

## Slurm essentials on Perlmutter

Every job must request a partition (`-C cpu` or `-C gpu`), an allocation, and a QOS:

| QOS           | Use                                  | Wall-time     |
|---------------|--------------------------------------|---------------|
| `debug`       | quick tests                          | up to 30 min  |
| `regular`     | normal production                    | up to 24 h    |
| `interactive` | live shell on a compute node         | up to 4 h     |

Quick checks before submitting:

```bash
sacctmgr show user $USER -p           # which repos you can charge
sqs                                   # NERSC wrapper around squeue
```

Remaining node-hours used to be available via `iris balance` on the command line; that command is gone. Check the **My Account → CPU / GPU** tab in the [IRIS web portal](https://iris.nersc.gov) instead.

---

## VASP sbatch templates

Two canonical Marom-group templates, based on this [performance guide for running VASP efficiently on Perlmutter](https://drive.google.com/file/d/1hRArOePMcIXI044wm1Hl-p6BK569_vaT/view?usp=sharing). Both leave **two values for you to fill in** before submitting:

- `-t HH:MM:SS` — wall-time. Pick one that fits your calculation; the VASP tutorials suggest concrete values per stage.
- `VASP_BINARY` — `vasp_std` (most calculations), `vasp_ncl` (anything with `LNONCOLLINEAR = .TRUE.`), or `vasp_gam` (Γ-only supercells).

### CPU — `vasp/6.4.3-cpu`

📥 [Download `submit_cpu.sh`](submit_cpu.sh)

1 node × **16 MPI ranks × 8 OpenMP threads** = 128 physical cores. `--cpu_bind=cores` distributes ranks across physical cores (avoiding hyperthreads).

```bash
#!/bin/bash
#SBATCH -J basic_training
#SBATCH -A m3578
#SBATCH -N 1
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -t HH:MM:SS              # CHANGE: wall-time, e.g. 02:00:00

module load vasp/6.4.3-cpu

# OpenMP settings
export OMP_NUM_THREADS=8
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

srun -n 16 -c 16 --cpu_bind=cores VASP_BINARY    # CHANGE: vasp_std / vasp_ncl / vasp_gam
```

### GPU — `vasp/6.4.3-gpu`

📥 [Download `submit_gpu.sh`](submit_gpu.sh)

1 node × **4 MPI ranks** (one per A100) × 1 OMP thread × 4 GPUs. `--exclusive` keeps the whole node so the four GPUs can talk over NVLink without contention; `NCCL_IGNORE_CPU_AFFINITY=1` works around an NCCL/affinity quirk that NERSC documents.

```bash
#!/bin/bash
#SBATCH -J basic_training
#SBATCH -A m3578
#SBATCH -N 1
#SBATCH -C gpu
#SBATCH -G 4
#SBATCH -q regular
#SBATCH --exclusive
#SBATCH -t HH:MM:SS              # CHANGE: wall-time, e.g. 02:00:00

module load vasp/6.4.3-gpu

export NCCL_IGNORE_CPU_AFFINITY=1

# OpenMP settings
export OMP_NUM_THREADS=1
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

srun -n 4 -c 32 --cpu_bind=cores --gpu-bind=none -G 4 VASP_BINARY    # CHANGE: vasp_std / vasp_ncl / vasp_gam
```

### Picking `KPAR` / `NCORE` for these layouts

The [VASP wiki](https://www.vasp.at/wiki/index.php/NCORE) makes one critical point: **`NCORE` is auto-reset to 1 whenever OpenMP or GPU is enabled**. Both templates above use OpenMP/GPU, so the only knob is `KPAR`.

| Run                                       | Ranks total | KPAR | Ranks per k-group | NCORE |
|-------------------------------------------|------------:|-----:|------------------:|------:|
| CPU 1 node (Tutorials 3 & 4)              | 16          | 4    | 4                 | 1     |
| CPU 4 nodes (HSE Tutorial 5)              | 64          | 16   | 4                 | 1     |
| GPU 1 node, 4 GPUs (HSE alternative)      | 4           | 1    | 4                 | 1     |

`KPAR` must divide the rank count, and ideally also the number of irreducible k-points.
