#!/usr/bin/env bash
set -euo pipefail

REPO="J2theN1/modu-inc-website"
BRANCH="feat/public-product-evidence"
WORKDIR="/tmp/modu-inc-website-public-evidence-contract"

rm -rf "$WORKDIR"
gh repo clone "$REPO" "$WORKDIR" -- --branch "$BRANCH" --single-branch --depth 1
cd "$WORKDIR"

python3 scripts/fix_public_site_legacy_contract_once.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
git diff --check
test "$(cat CNAME)" = "moduindustries.ca"

rm -f scripts/fix_public_site_legacy_contract_once.py
rm -f scripts/run_public_site_contract_fix_once.sh

git add -A
git config user.name 'modu-integration-bot'
git config user.email 'modu-integration-bot@users.noreply.github.com'
git commit -m 'site: preserve public trust contact disclosures'
git push origin HEAD:"$BRANCH"

echo "VERIFIED_HEAD=$(git rev-parse HEAD)"
echo "SITE_TESTS=PASS"
