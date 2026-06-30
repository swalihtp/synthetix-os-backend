from workflows.market_inteligence_workflow.services.firecrawsl_service import crawl_company_site


def crawl_company_website_node(state):

    website = state.get("company_website")

    if not website:
        return {"website_content": {}}

    content = crawl_company_site(website)
    
    serialized_website_content = {}

    for url, doc in content.items():
        serialized_website_content[url] = {
            "markdown": doc.markdown,
            "metadata": doc.metadata.model_dump()
                if hasattr(doc.metadata, "model_dump")
                else {}
        }

    return {"website_content": serialized_website_content}
