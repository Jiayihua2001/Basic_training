---
layout: default
parent: "HPC Onboard"
title: "virtual_env"
nav_order: 6            # 2,3,4 for the others
---


## **📦 Virtual Environment: `conda` and `pip`**

### Quick start: Try to setup your Virtual environment
---

  ```bash
  conda create -n ase_env python=3.10
  conda activate ase_env
  pip install ase matplotlib numpy
  ```
---

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
    
---

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

