---
layout: default
title: "Quick Onboard"
nav_order: 1            # 2,3,4 for the others
has_children: true
---

# Basic Training — Noa Marom Research Group

**The goal of this training is not to memorise a fixed recipe.** It is to help you understand the *workflow*, the *programming logic*, and the *underlying physics* well enough to carry out independent research — on new systems, with new techniques (new functionals, new corrections), and with analysis pipelines you implement yourself. The tutorials walk through concrete calculations, but treat every script and input file as something to read, question, and eventually rewrite for your own problem.

Pick the track that matches your project:

---

## 🧪 Organic / molecular materials

*(CSP, GATOR, Organic Interface, singlet-fission (SF) subgroups.)* These projects use the all-electron code **FHI-aims** on **Trace** or **Arjuna**.

1. **Download** the tutorial files:
   👉 <a href="Tutorials_files.zip" download>📥 Download Tutorial Files</a>

2. **Unzip, copy to your HPC, and enter the directory:**
   ```bash
   cd Tutorials_files
   ```

3. **Run the setup script** to install the FHI-aims helper scripts (`write_control.py`, `Automation.py`, `Surfaces.py`, `aimsplot.py`, `submit.sh`) into your `~`:
   - On Trace:&nbsp;&nbsp;`bash setup_utils.sh trace`
   - On Arjuna: `bash setup_utils.sh arjuna`

4. Work through the [FHI-aims tutorials](Tutorials/FHI-aims/) — H₂ → periodic solids → 2D/surfaces.

New to the clusters? Start with [HPC Onboard](HPC%20Onboard/) for Trace/Arjuna, Linux, Slurm, and Python environments.

---

## 💎 Inorganic / quantum materials

*(Quantum-materials (QM) subgroup.)* These projects use the plane-wave + PAW code **VASP** on **NERSC Perlmutter**.

1. **Get access:** a NERSC account in the `m3578` allocation and the `vasp6` Unix group — see the [Perlmutter onboarding](HPC%20Onboard/Perlmutter/).

2. **Install the VASP helper scripts** `incar.py`, `kpoints.py`, `potcar.sh` from the [Utilities page](Utilities/), and point `potcar.sh` at `/global/cfs/cdirs/m3578/shared_folder/Pseudopotentials/potpaw_PBE`.

3. **Install the supporting tools** (all on the [Utilities page](Utilities/)): [VASPKIT](Utilities/#vaspkit) for input generation and post-processing, [vaspvis](Utilities/#vaspvis) for figures, and the group's QM packages [OgreInterface](Utilities/#ogreinterface) (slabs/interfaces) and [BayesianOpt4dftu](Utilities/#bayesianopt4dftu) (DFT+U *U*-fitting).

4. Work through the [VASP tutorials](Tutorials/VASP/) — bulk InAs at PBE → PBE+SOC → HSE06, building toward DFT+U fitting.

> `setup_utils.sh` only installs the FHI-aims tooling. The inorganic track installs its tools from the [Utilities page](Utilities/) instead.
