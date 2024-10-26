# SerpAPI tool
try:
    from serpapi import GoogleSearch
except ImportError:
    raise ImportError('Please install serpapi with "pip install google-search-results"')
from .base_tool import BaseTool
import os


class SerpTool(BaseTool):
    def __init__(self, api_key=None):
        if not api_key:
            api_key = os.getenv("SERP_API_KEY")
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self.name = "SerpAPI Tool"
        self.description = "This tool uses SerpAPI to get search results from Google"

    def run(self, query: str) -> list:
        params: dict = {
            "engine": 'google',
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en",
            "q": query,
            "api_key": self.api_key
        }

        search = GoogleSearch(params)
        response = search.get_dict()
        if 'organic_results' not in response:
            return []
        return [dict(title=r['title'], link=r['link'], snippet=r['snippet']) for r in response['organic_results']]

