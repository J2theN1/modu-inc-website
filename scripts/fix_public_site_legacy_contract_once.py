from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected one marker in {path}, found {count}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "index.html",
    '''        <a class="btn btn-primary" href="mailto:contact@moduindustries.ca">contact@moduindustries.ca</a>\n''',
    '''        <div class="contact-actions">\n            <a class="btn btn-primary" href="mailto:contact@moduindustries.ca">contact@moduindustries.ca</a>\n            <a href="mailto:contact@moduindustries.ca?subject=Support%20request">Support request</a>\n            <a href="mailto:contact@moduindustries.ca?subject=Security%20report">Security report</a>\n        </div>\n''',
)

replace_once(
    "privacy.html",
    '''<h2>Website data</h2><p>The public website does not provide an account login, payment form, embedded customer database, first-party analytics script, advertising tracker, or third-party font resource. It uses system fonts supplied by the visitor’s device.</p><p>Web hosting, DNS, and content-delivery providers may process ordinary request information such as IP address, browser or user-agent data, requested path, timestamp, and security signals to deliver and protect the site.</p>''',
    '''<h2>Website data</h2><p>The public website does not provide an account login, payment form, embedded customer database, first-party analytics script, advertising tracker, or third-party font resource. It uses system fonts supplied by the visitor’s device.</p><p>An earlier version of this site loaded Google Fonts. The current published site does not request Google Fonts or another third-party font service.</p><p>Web hosting, DNS, and content-delivery providers may process ordinary request information such as IP address, browser or user-agent data, requested path, timestamp, and security signals to deliver and protect the site.</p>''',
)

replace_once(
    "styles.css",
    '''.contact-panel p:last-child { color: var(--muted); }\n''',
    '''.contact-panel p:last-child { color: var(--muted); }\n.contact-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 0.75rem 1rem; }\n.contact-actions > a:not(.btn) { color: var(--muted); font-size: 0.86rem; }\n''',
)
