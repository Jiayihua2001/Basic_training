---
layout: default
parent: "HPC Onboard"
title: "linux_basic"
nav_order: 3            # 2,3,4 for the others
---

## **🔧 Basic Linux Commands**

### **📂 File & Directory Operations**

* `pwd`: Print current working directory
* `ls -l`: List directory contents in detail
* `cd <dir>`: Change directory
* `mkdir <dir>`: Make directory
* `rm <file>`: Remove file
* `rm -r <dir>`: Remove directory recursively
* `cp <src> <dest>`: Copy file or directory
* `mv <src> <dest>`: Move or rename file

### **📄 File Viewing & Editing**

* `cat <file>`: View file content
* `less <file>`: Scroll through file
* `head -n <N> <file>`: View first N lines
* `tail -n <N> <file>`: View last N lines
* `nano <file>`: Easy-to-use terminal text editor
* `vim <file>`: Advanced editor 

### **🔍 Search & Filter**

* `grep 'pattern' <file>`: Search for pattern in file

  * e.g., `grep 'ERROR' logfile.txt`
* `find <path> -name "<pattern>"`: Search for files

### **🌐 Network & Remote**

* `ping <host>`: Test connectivity
* `scp <src> user@host:<dest>`: Secure copy to/from remote

  * e.g., `scp file.txt your_name@trace.cmu.edu:/dest/on/trace`
  * e.g., `scp -rf target_dir your_name@bridges2.psc.edu:/dest/on/bridges`

* `ssh user@host`: Secure shell into remote machine in ternimal
    * e.g., `ssh user_name@trace.cmu.edu`
    * e.g., `ssh user_name@bridges2.psc.edu`
    * e.g., `ssh user_name@arjuna-local.lan.local.cmu.edu`


### **📦 Package Management (Ubuntu/Debian)**

* `sudo apt update`: Update package lists
* `sudo apt install <package>`: Install software
* `sudo apt remove <package>`: Uninstall software

---

## **📝 Shell Scripting (.sh Files)**

### **🔤 Language: Bash**

* Default shell scripting language on Linux
* Scripts start with a "shebang" to specify the interpreter:

```bash
#!/bin/bash
```

### **🧠 Basic Script Structure**

```bash
#!/bin/bash

# This is a comment
echo "Hello, World!"   # Print to console

# Variables
name="Alice"
echo "My name is $name"

# Conditionals
if [ "$name" = "Alice" ]; then
    echo "Hi Alice!"
else
    echo "You're not Alice."
fi

# Loops
for i in {1..5}; do
    echo "Iteration $i"
done

# Functions
greet() {
    echo "Hello $1"
}

greet "Bob"
```

### **🔧 Running a Script**

Make it executable:

```bash
chmod +x script.sh
./script.sh
```


## **📦 Virtual Environment: `conda` and `pip`**

### **🛠 Why Use Virtual Environments?**

They isolate dependencies for each project, avoiding conflicts between different Python packages or versions.

---


### **🐍 `conda` (Anaconda/Miniconda) Basics**

#### **🔧 Environment Management**

* Create new environment:

  ```bash
  conda create --name myenv python=3.10
  ```
* Activate environment:

  ```bash
  conda activate myenv
  ```
* Deactivate environment:

  ```bash
  conda deactivate
  ```
* List environments:

  ```bash
  conda env list
  ```
* Remove environment:

  ```bash
  conda remove --name myenv --all
  ```
* Clean cache:

  ```bash
  conda clean --all
  ```
    

#### **📦 Package Management**

* Install package:

  ```bash
  conda install <package>
  ```
* Install from specific channel (e.g., conda-forge):

  ```bash
  conda install -c conda-forge <package>
  ```
* List installed packages:

  ```bash
  conda list
  ```
* Update package:

  ```bash
  conda update <package>
  ```
* Remove package:

  ```bash
  conda remove <package>
  ```
---

### **🐍 `pip` Basics (Python’s Default Package Installer)**

#### **📦 Install & Manage Python Packages**

* Install a package:

  ```bash
  pip install <package>
  ```
* Upgrade a package:

  ```bash
  pip install --upgrade <package>
  ```
* Uninstall a package:

  ```bash
  pip uninstall <package>
  ```
* List installed packages:

  ```bash
  pip list
  ```
* Save environment to `requirements.txt`:

  ```bash
  pip freeze > requirements.txt
  ```
* Install from `requirements.txt`:

  ```bash
  pip install -r requirements.txt
  ```

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
conda activate your_env        # Activate required environment
srun python myscript.py        # Run job using srun
```

---

### **🚀 Running Tasks with `srun`**

* Run a task in parallel:

  ```bash
  srun -n 4 ./my_program
  ```

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


