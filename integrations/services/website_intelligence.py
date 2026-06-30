import re
import json
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class WebsiteIntelligenceService:
    """
    Analyze a website and determine:
    - framework
    - rendering type
    - ecommerce/blog/saas
    - anti-bot protection
    - scraping strategy
    """

    COMMON_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    def analyze(self, url: str) -> dict:

        normalized_url = self._normalize_url(url)

        result = {
            "url": normalized_url,
            "domain": urlparse(normalized_url).netloc,
            "status_code": None,
            "framework": None,
            "platform": None,
            "website_type": None,
            "rendering_type": "static",
            "anti_bot": None,
            "has_api": False,
            "uses_graphql": False,
            "requires_browser": False,
            "recommended_tool": "requests_bs4",
            "signals": [],
        }

        try:

            response = httpx.get(
                normalized_url,
                headers=self.COMMON_HEADERS,
                timeout=20,
                follow_redirects=True,
            )

            result["status_code"] = response.status_code

            html = response.text

            soup = BeautifulSoup(html, "html.parser")

            # ---------------------------------------------------
            # FRAMEWORK DETECTION
            # ---------------------------------------------------

            framework = self.detect_framework(html)

            if framework:
                result["framework"] = framework
                result["signals"].append(f"framework:{framework}")

            # ---------------------------------------------------
            # PLATFORM DETECTION
            # ---------------------------------------------------

            platform = self.detect_platform(html)

            if platform:
                result["platform"] = platform
                result["signals"].append(f"platform:{platform}")

            # ---------------------------------------------------
            # WEBSITE CATEGORY
            # ---------------------------------------------------

            website_type = self.detect_website_type(html)

            result["website_type"] = website_type

            # ---------------------------------------------------
            # DYNAMIC RENDERING DETECTION
            # ---------------------------------------------------

            dynamic = self.detect_dynamic_rendering(html, soup)

            if dynamic:
                result["rendering_type"] = "javascript"
                result["requires_browser"] = True
                result["signals"].append("dynamic_rendering")

            # ---------------------------------------------------
            # API DETECTION
            # ---------------------------------------------------

            has_api = self.detect_api_usage(html)

            result["has_api"] = has_api

            if has_api:
                result["signals"].append("api_detected")

            # ---------------------------------------------------
            # GRAPHQL DETECTION
            # ---------------------------------------------------

            graphql = self.detect_graphql(html)

            result["uses_graphql"] = graphql

            if graphql:
                result["signals"].append("graphql_detected")

            # ---------------------------------------------------
            # ANTI BOT DETECTION
            # ---------------------------------------------------

            anti_bot = self.detect_anti_bot(response)

            if anti_bot:
                result["anti_bot"] = anti_bot
                result["signals"].append(f"anti_bot:{anti_bot}")

            # ---------------------------------------------------
            # SCRAPER STRATEGY
            # ---------------------------------------------------

            result["recommended_tool"] = self.select_scraping_strategy(result)

            return result

        except Exception as e:

            result["error"] = str(e)

            return result

    # =========================================================
    # NORMALIZATION
    # =========================================================

    def _normalize_url(self, url):

        if not url.startswith(("http://", "https://")):
            return f"https://{url}"

        return url

    # =========================================================
    # FRAMEWORK DETECTION
    # =========================================================

    def detect_framework(self, html):

        framework_patterns = {
            "nextjs": [
                "__NEXT_DATA__",
                "/_next/",
            ],
            "react": [
                "react-root",
                "data-reactroot",
                "react-dom",
            ],
            "vue": [
                "__VUE__",
                "vue.js",
            ],
            "angular": [
                "ng-version",
                "angular.js",
            ],
            "nuxt": [
                "__NUXT__",
            ],
        }

        html_lower = html.lower()

        for framework, patterns in framework_patterns.items():

            for pattern in patterns:

                if pattern.lower() in html_lower:
                    return framework

        return None

    # =========================================================
    # PLATFORM DETECTION
    # =========================================================

    def detect_platform(self, html):

        platform_patterns = {
            "shopify": [
                "cdn.shopify.com",
                "Shopify.theme",
            ],
            "wordpress": [
                "wp-content",
                "wp-json",
            ],
            "woocommerce": [
                "woocommerce",
            ],
            "magento": [
                "Magento",
            ],
            "wix": [
                "wix.com",
            ],
        }

        html_lower = html.lower()

        for platform, patterns in platform_patterns.items():

            for pattern in patterns:

                if pattern.lower() in html_lower:
                    return platform

        return None

    # =========================================================
    # WEBSITE CATEGORY DETECTION
    # =========================================================

    def detect_website_type(self, html):

        html_lower = html.lower()

        ecommerce_keywords = [
            "add to cart",
            "checkout",
            "buy now",
            "product",
            "shopping cart",
            "wishlist",
        ]

        blog_keywords = [
            "blog",
            "author",
            "published",
            "comments",
            "article",
        ]

        saas_keywords = [
            "pricing",
            "dashboard",
            "free trial",
            "book demo",
            "sign in",
        ]

        ecommerce_score = sum(keyword in html_lower for keyword in ecommerce_keywords)

        blog_score = sum(keyword in html_lower for keyword in blog_keywords)

        saas_score = sum(keyword in html_lower for keyword in saas_keywords)

        scores = {
            "ecommerce": ecommerce_score,
            "blog": blog_score,
            "saas": saas_score,
        }

        highest = max(scores, key=scores.get)

        if scores[highest] == 0:
            return "general"

        return highest

    # =========================================================
    # DYNAMIC RENDERING DETECTION
    # =========================================================

    def detect_dynamic_rendering(self, html, soup):

        body_text = soup.get_text(strip=True)

        script_count = len(soup.find_all("script"))

        indicators = 0

        # Root app containers
        if soup.find(id="root") or soup.find(id="app"):
            indicators += 1

        # Too many scripts
        if script_count > 15:
            indicators += 1

        # Very little body text
        if len(body_text) < 500:
            indicators += 1

        # Next.js
        if "__NEXT_DATA__" in html:
            indicators += 2

        return indicators >= 2

    # =========================================================
    # API DETECTION
    # =========================================================

    def detect_api_usage(self, html):

        api_patterns = [
            "/api/",
            "graphql",
            "axios",
            "fetch(",
            ".json",
        ]

        html_lower = html.lower()

        return any(pattern.lower() in html_lower for pattern in api_patterns)

    # =========================================================
    # GRAPHQL DETECTION
    # =========================================================

    def detect_graphql(self, html):

        graphql_patterns = [
            "graphql",
            "__apollo_state__",
            "apollo-client",
        ]

        html_lower = html.lower()

        return any(pattern.lower() in html_lower for pattern in graphql_patterns)

    # =========================================================
    # ANTI BOT DETECTION
    # =========================================================

    def detect_anti_bot(self, response):

        headers = {k.lower(): v.lower() for k, v in response.headers.items()}

        server = headers.get("server", "")

        if "cloudflare" in server:
            return "cloudflare"

        if "akamai" in server:
            return "akamai"

        if "perimeterx" in str(headers):
            return "perimeterx"

        return None

    # =========================================================
    # STRATEGY SELECTION
    # =========================================================

    def select_scraping_strategy(self, profile):

        if profile["anti_bot"] == "cloudflare":
            return "playwright_stealth"

        if profile["rendering_type"] == "javascript":

            if profile["uses_graphql"]:
                return "playwright_graphql_interceptor"

            return "playwright"

        if profile["platform"] == "shopify":
            return "shopify_parser"

        return "requests_bs4"
