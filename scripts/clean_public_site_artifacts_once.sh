#!/usr/bin/env bash
set -euo pipefail

REPO="J2theN1/modu-inc-website"
BRANCH="feat/public-product-evidence"
WORKDIR="/tmp/modu-inc-website-public-evidence-clean"

rm -rf "$WORKDIR"
gh repo clone "$REPO" "$WORKDIR" -- --branch "$BRANCH" --single-branch --depth 1
cd "$WORKDIR"

rm -rf tests/__pycache__
cat > .gitignore <<'EOF'
__pycache__/
*.py[cod]
.DS_Store
EOF

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_public_site
git diff --check
test "$(cat CNAME)" = "moduindustries.ca"

rm -f scripts/clean_public_site_artifacts_once.sh
git add -A
git config user.name 'modu-integration-bot'
git config user.email 'modu-integration-bot@users.noreply.github.com'
git commit -m 'chore: keep generated artifacts out of the site repository'
git push origin HEAD:"$BRANCH"

echo "CLEAN_HEAD=$(git rev-parse HEAD)"
echo "SITE_TESTS=PASS"
