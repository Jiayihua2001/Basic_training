#!/bin/bash
# Tear down everything setup_dev.sh created:
#   - the conda env "basic-training-jekyll"
#   - docs/vendor/  (bundled gems)
#   - docs/.bundle/ (bundler local config)
#
# Source files (markdown, _config.yml, Gemfile, Gemfile.lock) are left alone.

set -euo pipefail
cd "$(dirname "$0")"

ENV_NAME="basic-training-jekyll"
CONDA_BASE="/global/common/software/nersc/pe/conda/26.1.0/Miniforge3-25.11.0-1"

if [ -d "$CONDA_BASE" ]; then
    # shellcheck disable=SC1091
    source "$CONDA_BASE/etc/profile.d/conda.sh"
    if conda env list | awk '{print $1}' | grep -qx "$ENV_NAME"; then
        echo "[uninstall] Removing conda env '$ENV_NAME'..."
        conda env remove -y -n "$ENV_NAME"
    else
        echo "[uninstall] conda env '$ENV_NAME' not found -- skipping."
    fi
else
    echo "[uninstall] NERSC conda not found at $CONDA_BASE -- skipping conda step."
fi

for d in vendor .bundle; do
    if [ -e "$d" ]; then
        echo "[uninstall] Removing $d/"
        rm -rf "$d"
    fi
done

echo "[uninstall] Done."
