---
layout: default
parent: "HPC Onboard"
title: "Perlmutter"
nav_order: 3
---

# NERSC Perlmutter

Perlmutter is the HPE Cray EX system at the National Energy Research Scientific Computing Center (NERSC). It is the cluster of choice for the quantum-materials subgroup and hosts the VASP build used in the [VASP tutorials](../../Tutorials/VASP/). Refer to the official NERSC documentation for anything not covered here:

- [Perlmutter overview](https://docs.nersc.gov/systems/perlmutter/)
- [Connecting to NERSC](https://docs.nersc.gov/connect/)
- [Running jobs (Slurm)](https://docs.nersc.gov/jobs/)
- [VASP at NERSC](https://docs.nersc.gov/applications/vasp/)

---

## Architecture (CPU partition)

* **CPU nodes:** 3,072. Each node has two AMD EPYC 7763 (Milan) CPUs → **128 physical cores / 256 hyper-threads** and 512 GB of DDR4.
* **GPU nodes** (not used in these tutorials): 1,792 nodes, four NVIDIA A100 each.

The VASP tutorials assume the CPU partition with `--constraint=cpu`.

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

Run all VASP jobs from `$SCRATCH`. Move finished CHGCAR/WAVECAR files you want to keep to `$CFS` before they age out.

Transfer data with `scp` or `rsync` (use `sshproxy` for password-less transfers):

```bash
rsync -avz local_dir/ <username>@perlmutter.nersc.gov:$SCRATCH/dest/
```

---

## VASP modules

```bash
module avail vasp                 # list available builds
module load vasp/6.4.3-cpu        # tutorials use this build
which vasp_std                    # confirm it loaded
```

Each module exposes three executables — pick the one that matches your INCAR:

| Binary      | Use it for                                                  |
|-------------|-------------------------------------------------------------|
| `vasp_std`  | Standard k-point set (most calculations)                    |
| `vasp_gam`  | Γ-point only (large supercells, gas-phase reference cells)  |
| `vasp_ncl`  | Non-collinear / spin-orbit (`LSORBIT = .TRUE.`)             |

---

## Slurm essentials on Perlmutter

Every CPU job must request `--constraint=cpu`, an allocation, and a QOS:

| QOS           | Use                                  | Wall-time     |
|---------------|--------------------------------------|---------------|
| `debug`       | quick tests, < 30 min                | up to 30 min  |
| `regular`     | normal production                    | up to 24 h    |
| `interactive` | live shell on a compute node         | up to 4 h     |

Quick checks before submitting:

```bash
sacctmgr show user $USER -p           # which repos you can charge
iris balance                          # remaining node-hours
sqs                                   # NERSC wrapper around squeue
```

---

## VASP sbatch template (Perlmutter CPU)

NERSC's recommended hybrid OpenMP/MPI launch is **64 MPI ranks per node × 2 OpenMP threads** (`-c 4` because Perlmutter exposes two hyper-threads per physical core; never run on hyper-threads — `--cpu-bind=cores` enforces that). Adjust the binary (`vasp_std` ↔ `vasp_ncl`) and the parallelisation tags inside `INCAR` to match the calculation.

📥 [Download `submit.sh`](submit.sh)

```bash
#!/bin/bash
#SBATCH -J vasp_job
#SBATCH -A <your_repo>          # e.g. m4055
#SBATCH -C cpu
#SBATCH -q regular              # use 'debug' for quick tests
#SBATCH -N 1
#SBATCH -t 02:00:00
#SBATCH -o slurm-%j.out

module load vasp/6.4.3-cpu

export OMP_NUM_THREADS=2
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

# 1 node × 64 MPI ranks × 2 OpenMP threads = 128 cores used
srun -n 64 -c 4 --cpu-bind=cores vasp_std > vasp.out
```

For SOC calculations swap `vasp_std` → `vasp_ncl`. For HSE start with **2 nodes** (`#SBATCH -N 2`, `srun -n 128 ...`).

### Picking `KPAR` and `NCORE`

NERSC and the [VASP wiki](https://www.vasp.at/wiki/index.php/KPAR) recommend combining k-point, band, and plane-wave parallelism. For **64 ranks on 1 node**:

* `KPAR` must divide both the total MPI rank count and the number of irreducible k-points. `KPAR = 4` (16 ranks per k-group) is a safe default for the InAs tutorials.
* `NCORE` ≈ √(ranks per k-group). With 16 ranks per group, `NCORE = 4` works well.

For **128 ranks on 2 nodes** (HSE), use `KPAR = 8`, `NCORE = 4`. These values are pre-set in the example INCARs in the [VASP tutorials](../../Tutorials/VASP/).

> When you change the node count, update `KPAR`/`NCORE` together so the totals still divide cleanly. Mismatched values silently fall back to less-efficient layouts.

---

## Common pitfalls

* **No `-C cpu`** — the job will be rejected by Slurm.
* **Charge density file mix-ups** — when you copy `CHG*` or `WAVECAR` between `scf/`, `band/`, and `dos/`, make sure the source job actually wrote them (`LCHARG = .TRUE.` and `LWAVE = .TRUE.` respectively).
* **Out-of-quota** — if `$SCRATCH` is full your job will be rejected at submit time. Run `myquota` before submitting.
