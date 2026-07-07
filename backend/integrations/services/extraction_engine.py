from integrations.services.extractors.requests_extractor import RequestsBS4Extractor

from integrations.services.extractors.nextjs_extractor import NextJSExtractor

from integrations.services.extractors.wordpress_extractor import WordPressExtractor

from integrations.services.extractors.playwright_extractor import PlaywrightExtractor


class ExtractionEngine:

    EXTRACTOR_MAP = {
        "requests_bs4": RequestsBS4Extractor,
        "nextjs_json_extractor": NextJSExtractor,
        "wordpress_api": WordPressExtractor,
        "playwright": PlaywrightExtractor,
        "playwright_stealth": PlaywrightExtractor,
    }

    def run(self, url, strategy):

        tool = strategy["primary_tool"]

        extractor_class = self.EXTRACTOR_MAP.get(tool)

        if not extractor_class:
            raise Exception(f"No extractor found for {tool}")

        extractor = extractor_class()

        return extractor.extract(url)
