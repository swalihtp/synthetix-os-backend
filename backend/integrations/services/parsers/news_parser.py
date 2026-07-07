from bs4 import BeautifulSoup

from .generic_parser import GenericParser


class NewsParser(GenericParser):

    def parse(self, raw_data):

        base = super().parse(raw_data)

        html = raw_data.get("html")

        if not html:
            return base

        soup = BeautifulSoup(html, "html.parser")

        headlines = []

        for h in soup.find_all(["h1", "h2", "h3"]):

            text = h.get_text(" ", strip=True)

            if len(text) > 20:
                headlines.append(text)

        base["headlines"] = headlines[:30]

        return base
