from .ai_client import ai_client

def build_company_profile(
    company_name, company_description, documents, website_content
):

    payload = {
        "company_name": company_name,
        "company_description": company_description,
        "documents": documents,
        "website_content": website_content,
    }

    result = ai_client.execute(task="company_profile",payload=payload)
    return result
    


def detect_research_gaps(company_profile):
    
    result = ai_client.execute(task="research_gap_detection",payload=company_profile)
    return result



def analyze_competitor(competitor_data):
    
    result = ai_client.execute(task="competitor_analysis",payload=competitor_data)
    return result




def analyze_market_trends(trend_data):

    result = ai_client.execute(task="market_trends", payload=trend_data)
    return result

def generate_swot(company_profile, competitors, trends):

    return ai_client.execute(
        task="swot",
        payload={
            "company_profile": company_profile,
            "competitors": competitors,
            "trends": trends,
        },
    )


def generate_recommendations(company_profile, competitors, trends, swot):

    return ai_client.execute(
        task="recommendations",
        payload={
            "company_profile": company_profile,
            "competitors": competitors,
            "trends": trends,
            "swot": swot,
        },
    )


def generate_executive_summary(company_profile, competitors, trends, swot):

    return ai_client.execute(
        task="executive_summary",
        payload={
            "company_profile": company_profile,
            "competitors": competitors,
            "trends": trends,
            "swot": swot,
        },
    )


def generate_market_report(
    company_profile, competitors, trends, swot, recommendations, executive_summary
):

    return ai_client.execute(
        task="market_report",
        payload={
            "company_profile": company_profile,
            "competitors": competitors,
            "trends": trends,
            "swot": swot,
            "recommendations": recommendations,
            "executive_summary": executive_summary,
        },
    )
