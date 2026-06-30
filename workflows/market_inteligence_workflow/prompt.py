PLANNER_PROMPT = """
You are a market intelligence strategist.

Create a research plan for:
Company: {company}
Industry: {industry}
Objective: {objective}
"""

MARKET_RESEARCH_PROMPT = """
Analyze the market size, opportunities, risks,
and customer segments for:
{company}

Company address:
{address}
"""

COMPETITOR_PROMPT = """
Analyze the company: {company}

Tasks:
1. Identify major competitors
2. Compare strengths and weaknesses
3. Analyze product and pricing positioning
4. Analyze market differentiation
5. Analyze digital presence
6. Identify strategic opportunities
7. Identify threats and risks

Return concise structured business insights.
"""

TREND_PROMPT = """
Analyze emerging market trends, technologies,
and disruptions in:
{industry}
"""

SENTIMENT_PROMPT = """
Analyze customer and public sentiment for:
{company}
"""

SWOT_PROMPT = """
Generate a SWOT analysis for:
{company}
"""

REPORT_PROMPT = """
Generate a detailed, professional market intelligence report for the company using the provided data.
Company:
{company}

Description:
{description}

Market Research:
{market_research}

Competitors:
{competitors}

Trends:
{trends}

Sentiment:
{sentiment}

SWOT:
{swot}
"""

PROFILE_ENRICHMENT = """
You are enriching a company profile.

Current Profile:

{company_profile}

Missing Fields:

{research_gaps}

Research Data:

{additional_research}

Update the profile.

Fill only fields supported by evidence.

Return the complete profile.
"""


