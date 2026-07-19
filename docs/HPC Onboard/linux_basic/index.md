---
layout: default
parent: "HPC Onboard"
title: "Linux Basics"
nav_order: 4            # 2,3,4 for the others
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
  * e.g., `scp -r target_dir your_name@bridges2.psc.edu:/dest/on/bridges`

* `ssh user@host`: Secure shell into remote machine in terminal
    * e.g., `ssh user_name@trace.cmu.edu`
    * e.g., `ssh user_name@bridges2.psc.edu`
    * e.g., `ssh user_name@mse-hpc-head.materials.local.cmu.edu`


### **📦 Package Management (Ubuntu/Debian)**

> **Note:** On HPC clusters you typically do **not** have `sudo` privileges. Use `module load` for system-provided software and `conda`/`pip` for Python packages. The commands below apply only to personal Linux machines where you have root access.

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

## Next steps

The remaining onboarding topics have their own pages:

- **Python environments (`conda` / `pip`)** — see [Virtual Environments](../virtual_env/).
- **Submitting and monitoring jobs** — see [Slurm Basics](../slurm_basic/).
