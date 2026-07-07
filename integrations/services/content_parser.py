from integrations.services.parsers.generic_parser import GenericParser
from integrations.services.parsers.news_parser import NewsParser
from integrations.services.parsers.blog_parser import BlogParser
from integrations.services.parsers.e_commerse_parser import EcommerceParser


class ContentParser:

    def parse(self, raw_data, profile):

        website_type = profile.get("website_type")

        if website_type == "blog":
            parser = BlogParser()

        elif website_type == "ecommerce":
            parser = EcommerceParser()

        elif website_type == "news":
            parser = NewsParser()

        else:
            parser = GenericParser()

        return parser.parse(raw_data)