#!/bin/bash
# Regenerate docs/Tutorials_files.zip from the repo's unpacked Tutorials_files/ tree.
# The unpacked tree is the single source of truth — edit files THERE, run this, commit both.
# Run from anywhere; operates on the repo this script lives in.
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
[ -d Tutorials_files ] || { echo "ERROR: $REPO/Tutorials_files not found"; exit 1; }
rm -f docs/Tutorials_files.zip
find Tutorials_files -type f \
  ! -name "*.pyc" ! -path "*__pycache__*" ! -name ".DS_Store" ! -name ".gitkeep" \
  | sort | zip -X -q docs/Tutorials_files.zip -@
# Scaffold dirs students cd into ship empty (git tracks them via .gitkeep; the zip
# carries them as real empty-directory entries instead).
find Tutorials_files -type d | sort | while read -r d; do
  if [ -z "$(find "$d" -mindepth 1 ! -name ".gitkeep" -print -quit)" ]; then
    zip -X -q docs/Tutorials_files.zip "$d/"
  fi
done
unzip -l docs/Tutorials_files.zip | tail -1
echo "OK: docs/Tutorials_files.zip regenerated from Tutorials_files/"
