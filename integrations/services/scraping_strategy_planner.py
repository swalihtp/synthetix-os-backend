from typing import Dict, Any


class ScrapingStrategyPlanner:
    """
    Decides the best scraping strategy
    based on website intelligence profile.
    """

    def decide(self, profile: Dict[str, Any]) -> Dict[str, Any]:

        strategy = {
            "primary_tool": None,
            "fallback_tool": None,
            "use_browser": False,
            "use_api": False,
            "use_stealth": False,
            "requires_proxy": False,
            "pagination_strategy": "standard",
            "extraction_method": "html_parsing",
            "parallel_requests": 5,
            "notes": [],
        }

        # =====================================================
        # ANTI BOT
        # =====================================================

        if profile.get("anti_bot"):

            strategy.update({
                "primary_tool": "playwright_stealth",
                "fallback_tool": "playwright",
                "use_browser": True,
                "use_stealth": True,
                "requires_proxy": True,
                "parallel_requests": 1,
                "notes": [
                    "Anti-bot protection detected"
                ]
            })

            return strategy

        # =====================================================
        # SHOPIFY
        # =====================================================

        if profile.get("platform") == "shopify":

            strategy.update({
                "primary_tool": "shopify_parser",
                "fallback_tool": "playwright",
                "use_api": True,
                "extraction_method": "shopify_json",
                "parallel_requests": 10,
                "notes": [
                    "Shopify platform detected"
                ]
            })

            return strategy

        # =====================================================
        # WORDPRESS
        # =====================================================

        if profile.get("platform") == "wordpress":

            strategy.update({
                "primary_tool": "wordpress_api",
                "fallback_tool": "requests_bs4",
                "use_api": True,
                "extraction_method": "wordpress_rest_api",
                "parallel_requests": 10,
                "notes": [
                    "WordPress REST API available"
                ]
            })

            return strategy

        # =====================================================
        # NEXTJS
        # =====================================================

        if profile.get("framework") == "nextjs":

            strategy.update({
                "primary_tool": "nextjs_json_extractor",
                "fallback_tool": "playwright",
                "use_browser": False,
                "use_api": True,
                "extraction_method": "__NEXT_DATA__",
                "parallel_requests": 8,
                "notes": [
                    "Next.js embedded JSON detected"
                ]
            })

            return strategy

        # =====================================================
        # GRAPHQL
        # =====================================================

        if profile.get("uses_graphql"):

            strategy.update({
                "primary_tool": "graphql_interceptor",
                "fallback_tool": "playwright",
                "use_api": True,
                "extraction_method": "graphql",
                "parallel_requests": 5,
                "notes": [
                    "GraphQL endpoint detected"
                ]
            })

            return strategy

        # =====================================================
        # JAVASCRIPT HEAVY
        # =====================================================

        if profile.get("rendering_type") == "javascript":

            strategy.update({
                "primary_tool": "playwright",
                "fallback_tool": "selenium",
                "use_browser": True,
                "parallel_requests": 2,
                "notes": [
                    "JavaScript rendering required"
                ]
            })

            return strategy

        # =====================================================
        # STATIC HTML
        # =====================================================

        strategy.update({
            "primary_tool": "requests_bs4",
            "fallback_tool": "scrapy",
            "parallel_requests": 20,
            "notes": [
                "Static HTML website"
            ]
        })

        return strategy