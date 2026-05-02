#!/bin/bash
# Set up the Jekyll dev environment (Linux-friendly).
#
# Creates a conda env "basic-training-jekyll" with Ruby 3.4, installs bundler,
# then installs the Gemfile gems into docs/vendor/bundle/ so nothing leaks into
# system / user gem dirs.
#
# Tear it back down with: bash uninstall_dev.sh
#
# On macOS the original serve.sh path (Homebrew Ruby) still works; this script
# is only needed on Linux machines that don't already have a recent Ruby.

set -euo pipefail
cd "$(dirname "$0")"

ENV_NAME="basic-training-jekyll"
CONDA_BASE="/global/common/software/nersc/pe/conda/26.1.0/Miniforge3-25.11.0-1"

if [ ! -d "$CONDA_BASE" ]; then
    echo "[setup] NERSC conda not found at $CONDA_BASE." >&2
    echo "[setup] Adjust CONDA_BASE in this script for your system, or install Ruby 3.x another way." >&2
    exit 1
fi

# shellcheck disable=SC1091
source "$CONDA_BASE/etc/profile.d/conda.sh"

if ! conda env list | awk '{print $1}' | grep -qx "$ENV_NAME"; then
    echo "[setup] Creating conda env '$ENV_NAME' with Ruby 3.4 + C toolchain (this can take a few minutes)..."
    # ruby for jekyll, c-compiler/make/pkg-config so native gems
    # (bigdecimal, http_parser.rb, ffi, eventmachine, sass-embedded) can build.
    conda create -y -n "$ENV_NAME" -c conda-forge \
        "ruby=3.4" c-compiler cxx-compiler make pkg-config
else
    echo "[setup] conda env '$ENV_NAME' already exists -- reusing it."
fi

conda activate "$ENV_NAME"

if ! command -v bundle >/dev/null 2>&1; then
    echo "[setup] Installing bundler..."
    gem install bundler --no-document
fi

bundle config set --local path 'vendor/bundle'
echo "[setup] Running bundle install (gems land in docs/vendor/bundle/)..."
bundle install

echo
echo "[setup] Done. Start the dev server with:"
echo "    bash serve.sh"
echo
echo "To remove everything this script created:"
echo "    bash uninstall_dev.sh"
