from tavily import TavilyClient
import os
import logging

logger = logging.getLogger(__name__)
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def web_search(query: str, max_results: int = 5):
    """
    Search the web using Tavily API
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of search results with content
    """
    if not query or not query.strip():
        logger.warning("Empty search query provided")
        return []
    
    try:
        response = client.search(
            query=query,
            max_results=max_results
        )
        
        if not response or "results" not in response:
            logger.warning(f"No results from Tavily API for query: {query}")
            return []

        results = response["results"]
        
        # Filter out results without content
        valid_results = [r for r in results if isinstance(r, dict) and r.get("content")]
        
        if not valid_results:
            logger.warning(f"Search returned results but none have content for query: {query}")
            return []
            
        return valid_results
        
    except Exception as e:
        logger.error(f"Web search failed for query '{query}': {str(e)}")
        raise