from playwright.sync_api import sync_playwright

from .base import BaseExtractor


class PlaywrightExtractor(BaseExtractor):

    def extract(self, url):

        with sync_playwright() as p:

            browser = p.chromium.launch(headless=True)

            page = browser.new_page()

            page.goto(
                url,
                wait_until="networkidle",
                timeout=60000,
            )

            html = page.content()

            title = page.title()

            browser.close()

            return {
                "success": True,
                "type": "html",
                "title": title,
                "html": html,
            }
