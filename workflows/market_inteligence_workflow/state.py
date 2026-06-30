from typing import TypedDict, List, Dict, Any


class MarketIntelligenceState(TypedDict, total=False):

    company_name: str
    company_description: str
    industry: str
    company_website: str

    competitors: List[str]

    document_ids: List[str]
    document_contents: List[str]

    website_content: Dict[str, Any]

    company_profile: Dict[str, Any]

    research_gaps: List[str]

    additional_research: Dict[str, Any]
    
    enriched_company_profile: Dict

    discovered_competitors: List[Dict]

    competitor_profiles: List[Dict]

    market_trends: List[Dict]

    swot: Dict[str, Any]

    recommendations: List[str]

    executive_summary: str

    report_markdown: str

    sources: List[Dict]

