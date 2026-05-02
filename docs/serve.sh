#!/bin/bash
# Start the Just-the-Docs site locally with live-reload + incremental rebuilds.
#
# Usage:   bash serve.sh                # http://localhost:4000
#          bash serve.sh --port 4001    # extra flags forwarded to jekyll
#
# Most edits hot-reload automatically. Restart only after changing:
#   _config.yml | Gemfile | Gemfile.lock | theme overrides under _includes/_layouts

set -e
cd "$(dirname "$0")"

# Activate the conda env created by setup_dev.sh.
# Run `bash setup_dev.sh` first if you've never set this up.
CONDA_BASE="${CONDA_BASE:-/global/common/software/nersc/pe/conda/26.1.0/Miniforge3-25.11.0-1}"
# shellcheck disable=SC1091
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate basic-training-jekyll

# First-run safety net: install gems into docs/vendor/bundle/ if missing.
if [ ! -d vendor/bundle ]; then
    bundle config set --local path 'vendor/bundle'
    bundle install
fi

exec bundle exec jekyll serve --livereload --incremental "$@"
