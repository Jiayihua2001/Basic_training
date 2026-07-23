# Maintainer records (not part of the published site)

Jekyll builds the website from `docs/` only — nothing in this folder is published.
It is versioned here so the port's QA trail and the build recipe survive with the repo.

- `mse-hpc_validation_log.md` — chronological log of the full tutorial validation on
  MSE-HPC: every exercise/assignment executed, issues found, fixes, and the
  240507→250822 version-switch campaign.
- `mse-hpc_issue_review.md` — companion deep-dive: one section per issue (symptom →
  root cause → fix → verification).
- `aims-250822-BUILD_NOTES.md` + `aims-250822-initial_cache.intel-classic.cmake` —
  the exact recipe for the shared course binary
  (`/mnt/beegfs/27-735/programs/fhi-aims.250822/`). The build trees and the spack
  compiler tree were deleted in the 2026-07-23 cleanup; a rebuild starts from these.
- `run_tests.sh` — physics regression tests (Si band gap, Fe k-convergence with/without
  smearing). Location-independent; run it from anywhere on the cluster.
