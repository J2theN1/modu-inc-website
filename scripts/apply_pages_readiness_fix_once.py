from __future__ import annotations

from pathlib import Path


path = Path('.github/workflows/domain-health-probe.yml')
text = path.read_text(encoding='utf-8')
old = '''          echo '=== PAGES API ==='
          pages_json="$({
            curl --fail-with-body --silent --show-error \\
              -H 'Accept: application/vnd.github+json' \\
              -H "Authorization: Bearer $GH_TOKEN" \\
              -H 'X-GitHub-Api-Version: 2022-11-28' \\
              "https://api.github.com/repos/$REPOSITORY/pages"
          })" || failed=1
          printf '%s\\n' "$pages_json" \\
            | python3 -c 'import json,sys; p=json.load(sys.stdin); print(json.dumps({k:p.get(k) for k in ("status","html_url","cname","https_enforced","protected_domain_state","pending_domain_unverified_at","https_certificate")},sort_keys=True))' \\
            || failed=1
          PAGES_JSON="$pages_json" python3 - "$domain" <<'PY' || failed=1
          import json
          import os
          import sys

          expected = sys.argv[1]
          payload = json.loads(os.environ["PAGES_JSON"])
          if payload.get("status") != "built":
              raise SystemExit("Pages is not built")
          if payload.get("cname") != expected:
              raise SystemExit("Pages custom domain mismatch")
          PY
'''
new = '''          echo '=== PAGES API ==='
          pages_ready=0
          pages_json=''
          for attempt in {1..18}; do
            pages_json="$({
              curl --fail-with-body --silent --show-error \\
                -H 'Accept: application/vnd.github+json' \\
                -H "Authorization: Bearer $GH_TOKEN" \\
                -H 'X-GitHub-Api-Version: 2022-11-28' \\
                "https://api.github.com/repos/$REPOSITORY/pages"
            })" || pages_json=''
            if [[ -n "$pages_json" ]]; then
              printf '%s\\n' "$pages_json" \\
                | python3 -c 'import json,sys; p=json.load(sys.stdin); print(json.dumps({k:p.get(k) for k in ("status","html_url","cname","https_enforced","protected_domain_state","pending_domain_unverified_at","https_certificate")},sort_keys=True))' \\
                || true
              if PAGES_JSON="$pages_json" python3 - "$domain" <<'PY'
          import json
          import os
          import sys

          expected = sys.argv[1]
          payload = json.loads(os.environ["PAGES_JSON"])
          if payload.get("status") != "built":
              raise SystemExit(1)
          if payload.get("cname") != expected:
              raise SystemExit(1)
          PY
              then
                pages_ready=1
                break
              fi
            fi
            echo "Pages not ready yet (attempt $attempt/18)"
            sleep 10
          done
          if [[ "$pages_ready" -ne 1 ]]; then
            echo 'Pages did not reach built state within readiness window'
            failed=1
          fi
'''
count = text.count(old)
if count != 1:
    raise SystemExit(f'expected one Pages API block, found {count}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
