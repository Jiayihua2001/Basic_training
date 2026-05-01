---
layout: default
parent: "HPC Onboard"
title: "slurm_basic"
nav_order: 5            # 2,3,4 for the others
---


## **⚙️ SLURM basic**

SLURM is a job scheduler used on many HPC clusters to allocate resources and manage job execution.

---

### **📄 Submitting Jobs with `sbatch`**

Submit a batch script:

```bash
sbatch job_script.sh
```

Example `job_script.sh`:

```bash
#!/bin/bash
#SBATCH -J job_name            # Job name
#SBATCH -N 1                   # Number of nodes
#SBATCH -n 1                   # Total number of tasks
#SBATCH -p cpu                 # partition, GPU or CPU
#SBATCH --cpus-per-task=2      # Threads per task
#SBATCH --mem=8G               # Memory per node
#SBATCH -t 1:00:00             # Time limit (hh:mm:ss)


module load python/3.10        # Load required module
eval "$(conda shell.bash hook)"  # Initialize conda in non-interactive shell
conda activate your_env        # Activate required environment
srun python myscript.py        # Run job using srun
```

---

### **🚀 Running Tasks with `srun`**

* Launch multiple task copies in parallel (here, 4 copies of `my_program`):

  ```bash
  srun -n 4 ./my_program
  ```

> **Note:** `srun` can be used both inside `sbatch` scripts (to launch the actual computation step) and interactively on the command line for quick tests. The `-n` flag specifies the **number of MPI tasks** (processes), not threads.

### **📊 Job Monitoring**

* View queue:

  ```bash
  squeue
  ```
* Check your jobs only:

  ```bash
  squeue -u $USER
  ```
* Cancel a job:

  ```bash
  scancel <job_id>
  ```


