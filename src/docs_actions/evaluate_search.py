"""Module for evaluating search queries."""

from typing import Any

from .api_client import APIClient


def evaluate_search(api_url: str, api_key: str, search_query: str) -> dict[str, Any]:
    """Evaluate a search query using the private API.

    Args:
        api_url: Base URL for the API
        api_key: Authentication key for the API
        search_query: The query to evaluate

    Returns:
        Dictionary containing the evaluation results

    Raises:
        requests.exceptions.RequestException: If the API request fails

    """
    client = APIClient(api_url, api_key)
    payload = {"query": search_query}
    return client.post("evaluate_search", payload)
