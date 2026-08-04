#!/usr/bin/env bash
set -euo pipefail

REPO="J2theN1/modu-inc-website"
BRANCH="fix/pages-build-readiness"
WORKDIR="/tmp/modu-inc-website-pages-readiness"

rm -rf "$WORKDIR"
gh repo clone "$REPO" "$WORKDIR" -- --branch "$BRANCH" --single-branch --depth 1
cd "$WORKDIR"

python3 scripts/apply_pages_readiness_fix_once.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
git diff --check
test "$(cat CNAME)" = "moduindustries.ca"
grep -Fq 'for attempt in {1..18}' .github/workflows/domain-health-probe.yml
grep -Fq 'pages_ready=1' .github/workflows/domain-health-probe.yml

rm -f scripts/apply_pages_readiness_fix_once.py
rm -f scripts/run_pages_readiness_fix_once.sh

git add -A
git config user.name 'modu-integration-bot'
git config user.email 'modu-integration-bot@users.noreply.github.com'
git commit -m 'ci: wait for GitHub Pages deployment readiness'
git push origin HEAD:"$BRANCH"

echo "VERIFIED_HEAD=$(git rev-parse HEAD)"
echo "SITE_TESTS=PASS"
