#!/usr/bin/env bash
# Build and publish to Hostinger shared hosting (ssh alias `hostinger`, same account as mynursewhitney.com).
# FIRST DEPLOY: the docroot holds the old WordPress site. Back it up on the host first, e.g.
#   ssh hostinger 'tar czf ~/backups/bamteamservices-wordpress-$(date +%F).tgz -C domains/bamteamservices.com public_html'
# --delete makes the docroot match dist/ exactly.
set -euo pipefail
cd "$(dirname "$0")/.."
DOCROOT="domains/bamteamservices.com/public_html/"

npx astro build
rsync -az --delete dist/ "hostinger:$DOCROOT"
echo "Deployed to https://bamteamservices.com"
