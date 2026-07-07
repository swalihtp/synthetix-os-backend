import json
import re

from bs4 import BeautifulSoup

from .base_parser import BaseParser


class GenericParser(BaseParser):

    def parse(self, raw_data):

        html = raw_data.get("html")

        if not html:
            return raw_data

        soup = BeautifulSoup(html, "html.parser")

        return {
            "metadata": self.extract_metadata(soup),
            "headings": self.extract_headings(soup),
            "links": self.extract_links(soup),
            "social_links": self.extract_social_links(soup),
            "emails": self.extract_emails(html),
            "json_ld": self.extract_json_ld(soup),
        }

    # =====================================================
    # METADATA
    # =====================================================

    def extract_metadata(self, soup):

        return {
            "title": (
                soup.title.string.strip()
                if soup.title and soup.title.string
                else None
            ),
            "meta_description": self.get_meta(
                soup,
                "description"
            ),
            "og_title": self.get_meta(
                soup,
                "og:title"
            ),
            "og_description": self.get_meta(
                soup,
                "og:description"
            ),
            "og_image": self.get_meta(
                soup,
                "og:image"
            ),
        }

    # =====================================================
    # HEADINGS
    # =====================================================

    def extract_headings(self, soup):

        headings = []

        for tag in soup.find_all(["h1", "h2", "h3"]):

            text = tag.get_text(" ", strip=True)

            if text:
                headings.append(text)

        return headings[:30]

    # =====================================================
    # LINKS
    # =====================================================

    def extract_links(self, soup):

        links = []

        for a in soup.find_all("a", href=True):

            text = a.get_text(" ", strip=True)

            links.append({
                "text": text,
                "href": a["href"],
            })

        return links[:100]

    # =====================================================
    # SOCIAL LINKS
    # =====================================================

    def extract_social_links(self, soup):

        social_domains = [
            "facebook.com",
            "twitter.com",
            "x.com",
            "linkedin.com",
            "instagram.com",
            "youtube.com",
        ]

        social_links = []

        for a in soup.find_all("a", href=True):

            href = a["href"]

            if any(domain in href for domain in social_domains):
                social_links.append(href)

        return list(set(social_links))

    # =====================================================
    # EMAILS
    # =====================================================

    def extract_emails(self, html):

        pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

        return list(set(re.findall(pattern, html)))

    # =====================================================
    # JSON LD
    # =====================================================

    def extract_json_ld(self, soup):

        structured_data = []

        scripts = soup.find_all(
            "script",
            type="application/ld+json"
        )

        for script in scripts:

            try:

                if script.string:
                    structured_data.append(
                        json.loads(script.string)
                    )

            except Exception:
                pass

        return structured_data

    # =====================================================
    # META HELPER
    # =====================================================

    def get_meta(self, soup, name):

        tag = soup.find(
            "meta",
            attrs={"name": name}
        )

        if not tag:
            tag = soup.find(
                "meta",
                attrs={"property": name}
            )

        if tag:
            return tag.get("content")

        return None