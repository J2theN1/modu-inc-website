#!/usr/bin/env bash
set -euo pipefail

REPO="J2theN1/modu-inc-website"
BRANCH="feat/public-product-evidence"
WORKDIR="/tmp/modu-inc-website-public-evidence"

rm -rf "$WORKDIR"
gh repo clone "$REPO" "$WORKDIR" -- --branch "$BRANCH" --single-branch --depth 1
cd "$WORKDIR"

test "$(git branch --show-current)" = "$BRANCH"
test -f scripts/apply_public_product_evidence_once.py
test -f tests/test_public_site.py

python3 scripts/apply_public_product_evidence_once.py
python3 -m unittest -v tests.test_public_site
python3 -m py_compile tests/test_public_site.py
git diff --check
test "$(cat CNAME)" = "moduindustries.ca"

rm -f .github/workflows/public-product-evidence-once.yml
rm -f scripts/apply_public_product_evidence_once.py
rm -f scripts/run_public_product_evidence_once.sh

git add -A
git config user.name 'modu-integration-bot'
git config user.email 'modu-integration-bot@users.noreply.github.com'
git commit -m 'site: publish public product evidence'
git push origin HEAD:"$BRANCH"

echo "VERIFIED_HEAD=$(git rev-parse HEAD)"
echo "SITE_TESTS=PASS"
