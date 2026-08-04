from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PAGES = ("company.html", "security.html", "support.html", "privacy.html")


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag != "a":
            return
        attributes = dict(attrs)
        if "href" in attributes:
            self.hrefs.append(attributes["href"])


class PublicTrustPagesTest(unittest.TestCase):
    def test_required_pages_exist(self) -> None:
        for page in PAGES:
            with self.subTest(page=page):
                self.assertTrue((ROOT / page).is_file())

    def test_home_page_links_all_trust_pages_and_role_addresses(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        parser = LinkParser()
        parser.feed(html)
        for page in PAGES:
            with self.subTest(page=page):
                self.assertIn(page, parser.hrefs)
        self.assertIn("MODU INDUSTRIES LTD.", html)
        self.assertIn("mailto:contact@moduindustries.ca?subject=Security%20report", html)
        self.assertIn("mailto:contact@moduindustries.ca?subject=Support%20request", html)
        self.assertNotIn("security@moduindustries.ca", html)
        self.assertNotIn("support@moduindustries.ca", html)

    def test_each_page_identifies_company_and_canonical_domain(self) -> None:
        for page in PAGES:
            html = (ROOT / page).read_text(encoding="utf-8")
            with self.subTest(page=page):
                self.assertIn("MODU INDUSTRIES LTD.", html)
                self.assertIn("moduindustries.ca", html)
                self.assertIn("styles.css", html)

    def test_privacy_notice_is_scoped_to_public_site(self) -> None:
        html = (ROOT / "privacy.html").read_text(encoding="utf-8").casefold()
        self.assertIn("public website", html)
        self.assertIn("google fonts", html)
        self.assertIn("email", html)
        self.assertNotIn("all modu products", html)

    def test_security_page_does_not_claim_unearned_certification(self) -> None:
        html = (ROOT / "security.html").read_text(encoding="utf-8").casefold()
        prohibited = (
            "soc 2 certified",
            "iso 27001 certified",
            "hipaa compliant",
            "government security clearance",
            "guaranteed secure",
        )
        for claim in prohibited:
            with self.subTest(claim=claim):
                self.assertNotIn(claim, html)
        self.assertIn("responsible disclosure", html)
        self.assertIn("contact@moduindustries.ca?subject=security%20report", html)
        self.assertNotIn("security@moduindustries.ca", html)


if __name__ == "__main__":
    unittest.main()
