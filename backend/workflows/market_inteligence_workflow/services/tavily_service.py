from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def discover_competitors(company_profile):

    industry = company_profile["industry"]

    subcategory = company_profile["subcategory"]

    queries = [
        f"top {subcategory} companies",
        f"best {subcategory} software",
        f"{subcategory} competitors",
        f"{industry} market leaders",
    ]

    results = []

    for query in queries:

        response = tavily.search(query=query, max_results=5)

        results.extend(response["results"])

    return results


def research_competitor(competitor):

    queries = [
        f"{competitor['name']} products",
        f"{competitor['name']} pricing",
        f"{competitor['name']} services",
        f"{competitor['name']} target customers",
    ]

    results = []

    for query in queries:

        response = tavily.search(query=query, max_results=5)

        results.extend(response["results"])

    return results


def research_market_trends(company_profile):

    industry = company_profile["industry"]

    subcategory = company_profile["subcategory"]

    queries = [
        f"{industry} trends",
        f"{subcategory} trends",
        f"{industry} outlook",
        f"{industry} opportunities",
        f"{subcategory} innovation",
    ]

    results = []

    for query in queries:

        response = tavily.search(query=query, max_results=5)

        results.extend(response["results"])

    return results


def perform_gap_research(company_name, company_profile, gaps):

    queries = []

    for gap in gaps:

        if gap == "pricing":

            queries.append(f"{company_name} pricing")

        elif gap == "products":

            queries.append(f"{company_name} products")

        elif gap == "target_customers":

            queries.append(f"{company_name} customers")

        elif gap == "geography":

            queries.append(f"{company_name} markets")

    ...
