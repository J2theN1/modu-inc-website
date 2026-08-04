#!/usr/bin/env bash
set -euo pipefail

REPO="$HOME/Projects/github/modu-inc-website"
BRANCH="feat/public-workflow-demo"
WT="/tmp/modu-public-workflow-demo"
LOG="/tmp/modu-public-workflow-demo.log"
UNIT="modu-public-workflow-demo-gate"

if systemctl --user is-active --quiet "$UNIT.service"; then
  echo "UNIT_ALREADY_ACTIVE=$UNIT.service"
  exit 0
fi
systemctl --user reset-failed "$UNIT.service" 2>/dev/null || true

git -C "$REPO" fetch origin "$BRANCH" --quiet
TARGET_SHA="$(git -C "$REPO" rev-parse "origin/$BRANCH")"
[[ "$TARGET_SHA" =~ ^[0-9a-f]{40}$ ]] || { echo "INVALID_TARGET_SHA=$TARGET_SHA" >&2; exit 20; }
if [ -e "$WT" ]; then
  git -C "$REPO" worktree remove --force "$WT" 2>/dev/null || rm -rf "$WT"
fi
git -C "$REPO" worktree add --force --detach "$WT" "origin/$BRANCH" >/dev/null

cat > /tmp/run-public-workflow-demo-inner.sh <<'INNER'
#!/usr/bin/env bash
set -euo pipefail
WT="$1"
TARGET_SHA="$2"
BRANCH="$3"
cd "$WT"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || exit 30
python3 scripts/apply_public_workflow_demo_once.py
python3 -m unittest -q tests.test_public_site
python3 -m json.tool demo-workflow.json >/dev/null
git diff --check
rm -f scripts/apply_public_workflow_demo_once.py
rm -f scripts/run_public_workflow_demo_gate_pc_once.sh
git add -A
git diff --cached --check
git config user.name 'modu-integration-bot'
git config user.email 'modu-integration-bot@users.noreply.github.com'
git commit -m 'Publish inspectable workflow evidence demo'
git push origin "HEAD:$BRANCH"
echo "VERIFIED_COMMIT=$(git rev-parse HEAD)"
INNER
chmod 700 /tmp/run-public-workflow-demo-inner.sh
: > "$LOG"
chmod 600 "$LOG"
systemd-run --user \
  --no-block \
  --unit="$UNIT" \
  --property=Type=oneshot \
  --property=TimeoutStartSec=10min \
  --property=StandardOutput=append:"$LOG" \
  --property=StandardError=append:"$LOG" \
  /tmp/run-public-workflow-demo-inner.sh "$WT" "$TARGET_SHA" "$BRANCH" >/dev/null

echo "TARGET_SHA=$TARGET_SHA"
echo "UNIT=$UNIT.service"
echo "LOG=$LOG"
echo "ACTIVE=$(systemctl --user is-active "$UNIT.service" || true)"
