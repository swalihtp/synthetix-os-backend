from pydantic import BaseModel
from typing import List


class PlannerResponse(BaseModel):
    content: str


class MarketResearchResponse(BaseModel):
    content: str


class CompetitorAnalysisResponse(BaseModel):
    content: str


class TrendAnalysisResponse(BaseModel):
    content: str


class SentimentAnalysisResponse(BaseModel):
    content: str


class SWOTAnalysisResponse(BaseModel):
    content: str


class SWOTAnalysis(BaseModel):

    strengths: List[str]

    weaknesses: List[str]

    opportunities: List[str]

    threats: List[str]

class ReportGenerationResponse(BaseModel):

    company_name: str

    executive_summary: str

    market_overview: str

    competitor_analysis: str

    industry_trends: str

    customer_sentiment: str

    swot_analysis: SWOTAnalysis

    strategic_recommendations: List[str]

    conclusion: str