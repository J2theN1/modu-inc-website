from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one marker in {path}, found {count}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "demo.html",
    '    <link rel="stylesheet" href="styles.css">\n',
    '    <link rel="stylesheet" href="styles.css">\n    <link rel="stylesheet" href="demo.css">\n',
)

replace_once(
    "index.html",
    '    <a href="product.html">Product</a>\n    <a href="evidence.html">Evidence</a>\n',
    '    <a href="product.html">Product</a>\n    <a href="demo.html">Demo</a>\n    <a href="evidence.html">Evidence</a>\n',
)
replace_once(
    "index.html",
    '                <a class="btn btn-primary" href="product.html">Explore the product</a>\n                <a class="btn btn-secondary" href="evidence.html">Review public evidence</a>\n',
    '                <a class="btn btn-primary" href="product.html">Explore the product</a>\n                <a class="btn btn-secondary" href="demo.html">Inspect the workflow demo</a>\n                <a class="btn btn-secondary" href="evidence.html">Review public evidence</a>\n',
)
replace_once(
    "index.html",
    '<p class="footer-legal"><a href="product.html">Product</a> · <a href="evidence.html">Evidence</a>',
    '<p class="footer-legal"><a href="product.html">Product</a> · <a href="demo.html">Demo</a> · <a href="evidence.html">Evidence</a>',
)

replace_once(
    "evidence.html",
    '    <a href="product.html">Product</a>\n    <a href="evidence.html">Evidence</a>\n',
    '    <a href="product.html">Product</a>\n    <a href="demo.html">Demo</a>\n    <a href="evidence.html">Evidence</a>\n',
)
replace_once(
    "evidence.html",
    '<p><a href="pitch-deck.html">Technical pitch →</a> · <a href="product.html">Product boundary →</a></p>',
    '<p><a href="demo.html">Inspectable workflow demo →</a> · <a href="demo-workflow.json">Machine-readable trace ↗</a> · <a href="pitch-deck.html">Technical pitch →</a> · <a href="product.html">Product boundary →</a></p>',
)
replace_once(
    "evidence.html",
    '<p class="footer-legal"><a href="product.html">Product</a> · <a href="evidence.html">Evidence</a>',
    '<p class="footer-legal"><a href="product.html">Product</a> · <a href="demo.html">Demo</a> · <a href="evidence.html">Evidence</a>',
)

replace_once(
    "sitemap.xml",
    '  <url><loc>https://moduindustries.ca/product.html</loc></url>\n',
    '  <url><loc>https://moduindustries.ca/product.html</loc></url>\n  <url><loc>https://moduindustries.ca/demo.html</loc></url>\n',
)

replace_once(
    "tests/test_public_site.py",
    '    "product.html",\n    "evidence.html",\n',
    '    "product.html",\n    "demo.html",\n    "evidence.html",\n',
)
replace_once(
    "tests/test_public_site.py",
    'from pathlib import Path\nimport re\n',
    'from pathlib import Path\nimport json\nimport re\n',
)
replace_once(
    "tests/test_public_site.py",
    '''    def test_cname_is_preserved(self) -> None:\n        self.assertEqual((ROOT / "CNAME").read_text(encoding="utf-8").strip(), "moduindustries.ca")\n\n''',
    '''    def test_public_demo_trace_is_machine_readable_and_bounded(self) -> None:\n        trace_path = ROOT / "demo-workflow.json"\n        self.assertTrue(trace_path.is_file(), "machine-readable workflow trace missing")\n        payload = json.loads(trace_path.read_text(encoding="utf-8"))\n        self.assertEqual(payload["classification"], "synthetic public demonstration")\n        self.assertEqual(\n            [step["state"] for step in payload["trace"]],\n            [\n                "authorized",\n                "executing",\n                "executing",\n                "gate_presented",\n                "gate_satisfied",\n                "resuming",\n                "submitted",\n                "completed",\n            ],\n        )\n        rendered = json.dumps(payload).casefold()\n        for forbidden in ("password_value", "cookie_value", "otp_value", "recovery_code"):\n            self.assertNotIn(forbidden, rendered)\n        demo_text = parse_page(ROOT / "demo.html").text.casefold()\n        self.assertIn("synthetic", demo_text)\n        self.assertIn("not claim a customer deployment", demo_text)\n\n    def test_cname_is_preserved(self) -> None:\n        self.assertEqual((ROOT / "CNAME").read_text(encoding="utf-8").strip(), "moduindustries.ca")\n\n''',
)
