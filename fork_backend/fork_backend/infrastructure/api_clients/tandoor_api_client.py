"""Tandoor API client for food and recipe search functionality"""

import os
from typing import List, Dict, Any, Optional
import httpx
from fork_backend.core.logging import get_logger

log = get_logger()


class TandoorAPIClient:
    """Client for interacting with the Tandoor API"""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the Tandoor API client.

        :param base_url: Base URL for the Tandoor API (e.g., https://tandoor.example.com)
        :param api_key: API key for authentication
        """
        self.base_url = base_url or os.getenv("TANDOOR_API_URL")
        self.api_key = api_key or os.getenv("TANDOOR_API_KEY")

        if not self.base_url:
            raise ValueError("Tandoor API base URL is required")

        if not self.api_key:
            raise ValueError("Tandoor API key is required")

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )

    async def search_recipes(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for recipes in Tandoor.

        :param query: Search query string
        :param limit: Maximum number of results to return
        :return: List of recipes matching the query
        """
        try:
            response = await self.client.get(
                "/api/recipe/",
                params={
                    "query": query,
                    "page_size": limit
                }
            )
            response.raise_for_status()
            data = response.json()

            # Handle paginated response
            if isinstance(data, dict) and "results" in data:
                return data["results"]
            elif isinstance(data, list):
                return data
            else:
                return []

        except httpx.HTTPStatusError as e:
            log.error("HTTP error occurred while searching recipes: %s", str(e))
            raise
        except httpx.RequestError as e:
            log.error(
                "Request error occurred while searching recipes: %s", str(e))
            raise
        except Exception as e:
            log.error(
                "Unexpected error occurred while searching recipes: %s", str(e))
            raise

    async def get_recipe_details(self, recipie_id: int) -> Dict[str, Any]:
        """
        Search for recipes in Tandoor.

        :param recipie_id: Tandoor id of the recipie
        :return: Dict with detailed info about the recipie
        """
        try:
            response = await self.client.get(
                f"/api/recipe/{recipie_id}/")
            response.raise_for_status()
            data = response.json()

            return data

        except httpx.HTTPStatusError as e:
            log.error("HTTP error occurred while getting recipes: %s", str(e))
            raise
        except httpx.RequestError as e:
            log.error("Request error occurred while getting recipes: %s", str(e))
            raise
        except Exception as e:
            log.error(
                "Unexpected error occurred while getting recipes: %s", str(e))
            raise

    async def close(self):
        """Close the HTTP client connection"""
        await self.client.aclose()
