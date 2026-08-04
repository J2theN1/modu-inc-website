from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import json
import re
import unittest
from urllib.parse import urlparse
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://moduindustries.ca"
REQUIRED_PAGES = {
    "index.html",
    "product.html",
    "demo.html",
    "evidence.html",
    "company.html",
    "security.html",
    "support.html",
    "privacy.html",
    "pitch-deck.html",
}
TRUST_LINKS = {
    "company.html",
    "security.html",
    "support.html",
    "privacy.html",
}
BANNED_HOME_CLAIMS = {
    "as capable as the big names",
    "90+ api routes",
    "100+ commands",
    "healthcare",
    "government & public sector",
}
TRACKER_MARKERS = {
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "google-analytics.com",
    "googletagmanager.com",
    "facebook.net",
    "segment.com",
    "hotjar.com",
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.in_title = False
        self.meta: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.scripts: list[dict[str, str]] = []
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: value or "" for key, value in attrs}
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            self.meta.append(attributes)
        elif tag in {"a", "link"}:
            self.links.append({"tag": tag, **attributes})
        elif tag == "script":
            self.scripts.append(attributes)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        normalized = " ".join(data.split())
        if normalized:
            self.text_parts.append(normalized)

    @property
    def title(self) -> str:
        return " ".join(part.strip() for part in self.title_parts if part.strip())

    @property
    def text(self) -> str:
        return " ".join(self.text_parts)

    def meta_content(self, *, name: str | None = None, property_name: str | None = None) -> str:
        for item in self.meta:
            if name is not None and item.get("name", "").casefold() == name.casefold():
                return item.get("content", "").strip()
            if (
                property_name is not None
                and item.get("property", "").casefold() == property_name.casefold()
            ):
                return item.get("content", "").strip()
        return ""

    def canonical(self) -> str:
        for item in self.links:
            if item.get("tag") == "link" and item.get("rel", "").casefold() == "canonical":
                return item.get("href", "").strip()
        return ""


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


def local_target(source: Path, href: str) -> Path | None:
    value = href.strip()
    if not value or value.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc:
        return None
    route = parsed.path
    if not route:
        return None
    if route.startswith("/"):
        route = route[1:]
    candidate = (ROOT / route).resolve()
    if route.endswith("/"):
        candidate = candidate / "index.html"
    if candidate.suffix == "":
        candidate = candidate / "index.html"
    return candidate


class PublicSiteContractTests(unittest.TestCase):
    def test_required_pages_exist(self) -> None:
        for name in sorted(REQUIRED_PAGES):
            with self.subTest(page=name):
                self.assertTrue((ROOT / name).is_file(), f"missing public page: {name}")

    def test_metadata_and_navigation(self) -> None:
        titles: set[str] = set()
        canonicals: set[str] = set()
        for name in sorted(REQUIRED_PAGES):
            path = ROOT / name
            self.assertTrue(path.is_file(), f"missing public page: {name}")
            parser = parse_page(path)
            with self.subTest(page=name):
                self.assertTrue(parser.title, "title is missing")
                self.assertNotIn(parser.title, titles, "title is duplicated")
                titles.add(parser.title)

                description = parser.meta_content(name="description")
                self.assertGreaterEqual(len(description), 40, "description is too short")

                canonical = parser.canonical()
                expected = f"{ORIGIN}/" if name == "index.html" else f"{ORIGIN}/{name}"
                self.assertEqual(canonical, expected)
                self.assertNotIn(canonical, canonicals, "canonical is duplicated")
                canonicals.add(canonical)

                self.assertTrue(parser.meta_content(property_name="og:title"), "og:title missing")
                self.assertTrue(parser.meta_content(property_name="og:description"), "og:description missing")
                self.assertEqual(parser.meta_content(property_name="og:url"), expected)

                hrefs = {
                    item.get("href", "").split("#", 1)[0]
                    for item in parser.links
                    if item.get("tag") == "a"
                }
                for trust_page in TRUST_LINKS:
                    self.assertIn(trust_page, hrefs, f"missing trust navigation link: {trust_page}")

    def test_no_third_party_fonts_or_trackers(self) -> None:
        for name in sorted(REQUIRED_PAGES):
            source = (ROOT / name).read_text(encoding="utf-8").casefold()
            with self.subTest(page=name):
                for marker in TRACKER_MARKERS:
                    self.assertNotIn(marker, source, f"third-party request marker found: {marker}")

    def test_homepage_avoids_unsupported_claims(self) -> None:
        source = parse_page(ROOT / "index.html").text.casefold()
        for phrase in BANNED_HOME_CLAIMS:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, source)
        self.assertIn("local-first ai and device-orchestration platform", source)
        self.assertIn("active research and development", source)

    def test_local_links_resolve(self) -> None:
        for name in sorted(REQUIRED_PAGES):
            source = ROOT / name
            parser = parse_page(source)
            for item in parser.links:
                if item.get("tag") != "a":
                    continue
                href = item.get("href", "")
                target = local_target(source, href)
                if target is None:
                    continue
                with self.subTest(page=name, href=href):
                    self.assertTrue(target.is_file(), f"broken local link from {name}: {href}")

    def test_robots_and_sitemap(self) -> None:
        robots = ROOT / "robots.txt"
        sitemap = ROOT / "sitemap.xml"
        self.assertTrue(robots.is_file(), "robots.txt missing")
        self.assertTrue(sitemap.is_file(), "sitemap.xml missing")
        robots_text = robots.read_text(encoding="utf-8")
        self.assertRegex(robots_text, r"(?im)^User-agent:\s*\*$")
        self.assertRegex(robots_text, r"(?im)^Allow:\s*/$")
        self.assertIn(f"Sitemap: {ORIGIN}/sitemap.xml", robots_text)

        root = ET.fromstring(sitemap.read_text(encoding="utf-8"))
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locations = {item.text for item in root.findall("sm:url/sm:loc", namespace)}
        expected = {
            f"{ORIGIN}/" if name == "index.html" else f"{ORIGIN}/{name}"
            for name in REQUIRED_PAGES
        }
        self.assertEqual(locations, expected)

    def test_public_demo_trace_is_machine_readable_and_bounded(self) -> None:
        trace_path = ROOT / "demo-workflow.json"
        self.assertTrue(trace_path.is_file(), "machine-readable workflow trace missing")
        payload = json.loads(trace_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["classification"], "synthetic public demonstration")
        self.assertEqual(
            [step["state"] for step in payload["trace"]],
            [
                "authorized",
                "executing",
                "executing",
                "gate_presented",
                "gate_satisfied",
                "resuming",
                "submitted",
                "completed",
            ],
        )
        rendered = json.dumps(payload).casefold()
        for forbidden in ("password_value", "cookie_value", "otp_value", "recovery_code"):
            self.assertNotIn(forbidden, rendered)
        demo_text = parse_page(ROOT / "demo.html").text.casefold()
        self.assertIn("synthetic", demo_text)
        self.assertIn("not claim a customer deployment", demo_text)

    def test_cname_is_preserved(self) -> None:
        self.assertEqual((ROOT / "CNAME").read_text(encoding="utf-8").strip(), "moduindustries.ca")

    def test_homepage_has_structured_data(self) -> None:
        source = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('type="application/ld+json"', source)
        self.assertRegex(source, re.compile(r'"@type"\s*:\s*"Organization"'))
        self.assertRegex(source, re.compile(r'"legalName"\s*:\s*"MODU INDUSTRIES LTD\."'))


if __name__ == "__main__":
    unittest.main()
