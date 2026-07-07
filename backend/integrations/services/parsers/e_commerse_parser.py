from bs4 import BeautifulSoup

from .generic_parser import GenericParser


class EcommerceParser(GenericParser):

    def parse(self, raw_data):

        base = super().parse(raw_data)

        html = raw_data.get("html")

        if not html:
            return base

        soup = BeautifulSoup(html, "html.parser")

        products = []

        possible_products = soup.find_all(
            class_=[
                "product",
                "product-card",
                "product-item",
            ]
        )

        for product in possible_products:

            products.append({"title": product.get_text(" ", strip=True)[:300]})

        base["products"] = products[:50]

        return base
