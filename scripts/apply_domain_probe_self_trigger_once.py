from __future__ import annotations

from pathlib import Path

path = Path('.github/workflows/domain-health-probe.yml')
text = path.read_text(encoding='utf-8')
old = '''  push:
    branches: [main]
    paths:
      - "*.html"
      - styles.css
      - robots.txt
      - sitemap.xml
      - CNAME
'''
new = '''  push:
    branches: [main]
    paths:
      - "*.html"
      - styles.css
      - robots.txt
      - sitemap.xml
      - CNAME
      - .github/workflows/domain-health-probe.yml
'''
count = text.count(old)
if count != 1:
    raise SystemExit(f'expected one push paths block, found {count}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
