---
layout: default
parent: "HPC Onboard"
title: "Arjuna"
nav_order: 1
---
Currently 24 nodes are in use for you to access.

## Logging In to Arjuna

- **Network Access:** Connect to CMU Wi‑Fi or use the [CMU VPN](https://www.cmu.edu/computing/services/endpoint/network-access/vpn/how-to/index.html) if you're off campus.

- **SSH Login:**
  ```bash
  ssh <AndrewID>@arjuna-local.lan.local.cmu.edu
````

---

- **FHI-aims Submission Script:**  
  You can download the `submit.sh` file for FHI-aims on Trace using the link below:  
  [📥 Download `submit.sh` for FHI-aims on Trace](submit.sh)

## Transferring Files Between Local and Arjuna

### From Arjuna to Local

```bash
# Single file
scp <AndrewID>@arjuna-local.lan.local.cmu.edu:<remote_file> <local_destination>

# Directory
scp -r <AndrewID>@arjuna-local.lan.local.cmu.edu:<remote_dir> <local_destination>
```

### From Local to Arjuna

```bash
# Single file
scp <local_file> <AndrewID>@arjuna-local.lan.local.cmu.edu:<remote_destination>

# Directory
scp -r <local_dir> <AndrewID>@arjuna-local.lan.local.cmu.edu:<remote_destination>
```

---

For more detailed information, please refer to the official [Arjuna User Guide](https://arjunacluster.github.io/ArjunaUsers/getting_started/).

