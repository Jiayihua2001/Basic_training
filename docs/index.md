---
layout: default
title: "Quick Onboard"
nav_order: 1            # 2,3,4 for the others
has_children: true
---

Welcome to the Basic Training Document for Noa Marom's Research Group

This guide provides essential tutorials and utility scripts to help you get started.
Before beginning your training journey, please:

1. **Download** all the necessary files here:
   👉 <a href="Tutorials_files.zip" download>📥 Download Tutorial Files</a>

2. **Unzip and add the directory to your HPC, then enter it:**
   ```bash
   cd Tutorials_files
   ```
2. **Run the setup script** to configure your environment:
   - If you are on Trace:
     ```bash
     bash setup_utils.sh trace
     ```
   - If you are on Arjuna:
     ```bash
     bash setup_utils.sh arjuna
     ```

If you are doing the VASP tutorials instead, follow the [Perlmutter onboarding](HPC%20Onboard/Perlmutter/) and the [VASP tutorials](Tutorials/VASP/) — `setup_utils.sh` only covers the FHI-aims tooling.



