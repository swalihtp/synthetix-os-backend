from integrations.services.website_intelligence import WebsiteIntelligenceService
from integrations.services.scraping_strategy_planner import ScrapingStrategyPlanner
from integrations.services.extraction_engine import ExtractionEngine
from integrations.services.content_parser import ContentParser


class MarketIntelligencePipeline:

    def __init__(self):

        self.website_analyzer = WebsiteIntelligenceService()
        self.strategy_planner = ScrapingStrategyPlanner()
        self.extraction_engine = ExtractionEngine()
        self.content_parser = ContentParser()

    def execute(self, url):

        # STEP 1
        website_profile = self.website_analyzer.analyze(url)

        # STEP 2
        strategy = self.strategy_planner.decide(website_profile)

        # STEP 3
        raw_data = self.extraction_engine.run(url, strategy)

        # STEP 4
        intelligence = self.content_parser.parse(
            raw_data=raw_data,
            profile=website_profile,
        )

        return {
            "website_profile": website_profile,
            "strategy": strategy,
            "raw_data": raw_data,
            "intelligence": intelligence,
        }