import json
import re
import requests

from .base import BaseExtractor


class NextJSExtractor(BaseExtractor):

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    def extract(self, url):

        response = requests.get(
            url,
            headers=self.HEADERS,
            timeout=20,
        )

        html = response.text

        pattern = (
            r'<script id="__NEXT_DATA__" ' r'type="application/json">(.*?)</script>'
        )

        match = re.search(pattern, html)

        if not match:
            return {
                "success": False,
                "message": "__NEXT_DATA__ not found",
            }

        data = json.loads(match.group(1))

        return {
            "success": True,
            "type": "nextjs_json",
            "html": html,
            "data": data,
        }
