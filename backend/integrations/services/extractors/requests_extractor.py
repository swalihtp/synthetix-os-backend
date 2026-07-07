import requests

from .base import BaseExtractor


class RequestsBS4Extractor(BaseExtractor):

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    def extract(self, url):

        session = requests.Session()

        session.headers.update(self.HEADERS)

        response = session.get(
            url,
            timeout=20,
            allow_redirects=True,
        )

        return {
            "success": True,
            "type": "html",
            "status_code": response.status_code,
            "final_url": response.url,
            "html": response.text,
            "headers": dict(response.headers),
        }
