from bs4 import BeautifulSoup

from .generic_parser import GenericParser


class BlogParser(GenericParser):

    def parse(self, raw_data):

        base = super().parse(raw_data)

        html = raw_data.get("html")

        if not html:
            return base

        soup = BeautifulSoup(html, "html.parser")

        articles = []

        for article in soup.find_all("article"):

            title_tag = article.find(["h1", "h2", "h3"])
            link_tag = article.find("a", href=True)
            time_tag = article.find("time")

            articles.append(
                {
                    "title": (
                        title_tag.get_text(" ", strip=True) if title_tag else None
                    ),
                    "url": (link_tag["href"] if link_tag else None),
                    "published_at": (
                        time_tag.get_text(" ", strip=True) if time_tag else None
                    ),
                }
            )

        base["articles"] = articles[:20]
