#!/usr/bin/env bash
set -euo pipefail

REPO="J2theN1/modu-inc-website"
BRANCH="fix/domain-probe-self-trigger"
WORKDIR="/tmp/modu-inc-website-domain-self-trigger"

rm -rf "$WORKDIR"
gh repo clone "$REPO" "$WORKDIR" -- --branch "$BRANCH" --single-branch --depth 1
cd "$WORKDIR"

python3 scripts/apply_domain_probe_self_trigger_once.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
git diff --check
test "$(cat CNAME)" = "moduindustries.ca"
python3 - <<'PY'
from pathlib import Path
text = Path('.github/workflows/domain-health-probe.yml').read_text(encoding='utf-8')
needle = '''  push:
    branches: [main]
    paths:
      - "*.html"
      - styles.css
      - robots.txt
      - sitemap.xml
      - CNAME
      - .github/workflows/domain-health-probe.yml
'''
if needle not in text:
    raise SystemExit('push self-trigger path missing')
PY

rm -f scripts/apply_domain_probe_self_trigger_once.py
rm -f scripts/run_domain_probe_self_trigger_once.sh

git add -A
git config user.name 'modu-integration-bot'
git config user.email 'modu-integration-bot@users.noreply.github.com'
git commit -m 'ci: trigger domain probe for workflow changes'
git push origin HEAD:"$BRANCH"

echo "VERIFIED_HEAD=$(git rev-parse HEAD)"
echo "SITE_TESTS=PASS"
