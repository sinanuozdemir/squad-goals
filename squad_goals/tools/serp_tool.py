# SerpAPI tool
try:
    from serpapi import GoogleSearch
except ImportError:
    raise ImportError('Please install serpapi with "pip install google-search-results"')
import os

from .base_tool import BaseTool


class SerpTool(BaseTool):
    def __init__(self, api_key=None, **kwargs):
        if not api_key:
            api_key = os.getenv("SERP_API_KEY")
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self.name = "SerpAPI Tool"
        self.description = "This tool uses SerpAPI to get search results from Google"
        self.engine = 'google'
        super().__init__(self.name, self.description, **kwargs)

    def _search(self, query: str, **kwargs) -> dict:

        params: dict = {
            "engine": self.engine,
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en",
            "q": query,
            "api_key": self.api_key
        }
        params.update(kwargs)

        search = GoogleSearch(params)
        return search.get_dict()

    def run(self, query: str) -> list:
        '''
        :param query: The search query e.g. query="Python programming" or query="Coffee site:wikipedia.org"
        '''
        response = self._search(query)
        if 'organic_results' not in response:
            return []
        return [dict(title=r['title'], link=r['link'], snippet=r['snippet']) for r in response['organic_results']]
