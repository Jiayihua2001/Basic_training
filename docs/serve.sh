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

# Pin to Homebrew Ruby (Apple's system 2.6 is too old for Jekyll 4.3).
export PATH="/opt/homebrew/opt/ruby/bin:$PATH"

# First-run safety net: install gems into docs/vendor/bundle/ if missing.
if [ ! -d vendor/bundle ]; then
    bundle config set --local path 'vendor/bundle'
    bundle install
fi

exec bundle exec jekyll serve --livereload --incremental "$@"
