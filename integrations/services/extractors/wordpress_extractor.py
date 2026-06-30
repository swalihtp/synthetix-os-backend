import requests

from urllib.parse import urljoin

from .base import BaseExtractor


class WordPressExtractor(BaseExtractor):

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    def extract(self, url):

        api_url = urljoin(url, "/wp-json/wp/v2/posts?per_page=10")

        response = requests.get(
            api_url,
            headers=self.HEADERS,
            timeout=20,
        )

        if response.status_code != 200:
            return {
                "success": False,
                "message": "WordPress API unavailable",
                "status_code": response.status_code,
            }

        return {
            "success": True,
            "type": "wordpress",
            "posts": response.json(),
        }
