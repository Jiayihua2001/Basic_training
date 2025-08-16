---
layout: default
parent: "HPC Onboard"
title: "Trace"
nav_order: 4
---

## Logging In to Trace

- **Network Access:** Connect to CMU Wi‑Fi or use the [CMU VPN](https://www.cmu.edu/computing/services/endpoint/network-access/vpn/how-to/index.html) if you're off campus.

- **SSH Login:**
  ```bash
  ssh <AndrewID>@trace.cmu.edu
````
---
## Local and Group Directories

- **Group Directory:**  
  `trace/group/marom/<your_user_name>`

- **FHI-aims Submission Script:**  
  You can download the `submit.sh` file for FHI-aims on Trace using the link below:  
  [📥 Download `submit.sh` for FHI-aims on Trace](submit.sh)

---

## Common Commands

To check available modules:
```bash
module avail
```
To load a specific module:
```bash
module load <module_name>
```
## Transferring Files Between Local and Trace

### From Trace to Local

```bash
# Single file
scp <AndrewID>@trace.cmu.edu:<remote_file> <local_destination>

# Directory
scp -r <AndrewID>@trace.cmu.edu:<remote_dir> <local_destination>
```

### From Local to Trace

```bash
# Single file
scp <local_file> <AndrewID>@trace.cmu.edu:<remote_destination>

# Directory
scp -r <local_dir> <AndrewID>@trace.cmu.edu:<remote_destination>
```

---

For more detailed information, please refer to the introduction [TRACE](https://www.cmu.edu/engineering/trace/index.html) and [PSC](https://www.psc.edu/).

