import requests
import os
import logging

logger = logging.getLogger(__name__)
BASE_URL = os.getenv("AI_SERVICE_URL")


def post_request(endpoint, payload):
    """
    Make a POST request to the AI service with error handling
    
    Args:
        endpoint: API endpoint path
        payload: Request payload dictionary
        
    Returns:
        Response JSON
        
    Raises:
        HTTPError: If the request fails
    """
    if not BASE_URL:
        raise ValueError("AI_SERVICE_URL environment variable not set")
    
    url = f"{BASE_URL}{endpoint}"
    logger.debug(f"Making POST request to {url} with payload: {payload}")
    
    try:
        response = requests.post(url, json=payload, timeout=(10, 600))
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error {e.response.status_code}: {e.response.text}")
        # Try to parse error details from response
        try:
            error_details = e.response.json()
            logger.error(f"Error details: {error_details}")
        except:
            pass
        raise
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise


# Planner
def generate_plan(prompt):
    payload = {"prompt": prompt}

    return post_request("/api/market-inteligence/generate-plan", payload)


# Market Research
def analyze_market(prompt, context):
    payload = {"prompt": prompt, "context": context}

    return post_request("/api/market-inteligence/analyze-market", payload)


# Competitor Analysis
def analyze_competitors(prompt, context, competitors_data_from_scraping=None):
    payload = {
        "prompt": prompt,
        "context": context,
        "competitors_data_from_scraping": competitors_data_from_scraping,
    }

    return post_request("/api/market-inteligence/analyze-competitors", payload)


# Trend Analysis
def analyze_trend(prompt, context):
    payload = {"prompt": prompt, "context": context}

    return post_request("/api/market-inteligence/analyze-trends", payload)


# Sentiment Analysis
def analyze_sentiment(prompt, context):
    payload = {"prompt": prompt, "context": context}

    return post_request("/api/market-inteligence/analyze-sentiment", payload)


# SWOT Analysis
def analyze_swot(prompt, context):
    payload = {"prompt": prompt, "context": context}

    return post_request("/api/market-inteligence/analyze-swot", payload)


# Report Generation
def prepare_report(prompt):
    payload = {"prompt": prompt}
    return post_request("/api/market-inteligence/generate-report", payload)


def summarize_content(content, company=None):

    payload = {
        "content": content,
        "company": company,
    }

    return post_request("/api/summarize", payload)
