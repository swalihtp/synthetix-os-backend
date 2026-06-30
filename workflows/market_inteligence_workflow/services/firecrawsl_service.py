from firecrawl import Firecrawl
import os
from dotenv import load_dotenv

load_dotenv()

firecrawl = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))

def crawl_company_site(website):

    pages = [
        website,
        f"{website}/about",
        f"{website}/products",
        f"{website}/services",
        f"{website}/pricing",
        f"{website}/blog",
    ]

    content = {}

    for page in pages:

        try:

            response = firecrawl.scrape_url(page)

            content[page] = response

        except Exception:

            continue

    return content

