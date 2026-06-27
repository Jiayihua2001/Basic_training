# Basic Training — Noa Marom Research Group

Onboarding documentation for new group members. The content lives in `docs/`, is built with the [Just the Docs](https://just-the-docs.github.io/just-the-docs/) Jekyll theme, and is published to GitHub Pages:

**https://jiayihua2001.github.io/Basic_training/**

## What's inside

- **HPC Onboard** — getting started on the group's clusters (Trace, Arjuna, NERSC Perlmutter) plus Linux, Slurm, and Python-environment basics.
- **Tutorials**
  - **FHI-aims** (organic / molecular materials) — H₂ → periodic solids → 2D & surfaces.
  - **VASP** (inorganic / quantum materials, on Perlmutter) — bulk InAs at PBE → PBE+SOC → HSE06, with the SOC / HSE / DFT+U methodology and parallel-execution details.
- **Utilities** — the tools and helper scripts the tutorials use: VASPKIT, vaspvis, OgreInterface, BayesianOpt4dftu, ASE / pymatgen, the `incar.py` / `kpoints.py` / `potcar.sh` helpers, and AI coding assistants.

The aim is not a fixed recipe but the workflow, programming logic, and physics needed to do independent research.

## Local preview

```bash
cd docs
bundle install
bundle exec jekyll serve     # serves http://localhost:4000/Basic_training/
```

The site rebuilds and deploys automatically on every push to `main` via `.github/workflows/ci.yml`.

## License

Released under the [MIT License](LICENSE). Built from the [just-the-docs template](https://github.com/just-the-docs/just-the-docs-template).
