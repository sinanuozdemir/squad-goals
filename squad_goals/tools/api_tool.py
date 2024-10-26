# SerpAPI tool
try:
    from serpapi import GoogleSearch
except ImportError:
    raise ImportError('Please install serpapi with "pip install google-search-results"')
from .base_tool import BaseTool
import requests


class APITool(BaseTool):
    def __init__(self, api_url: str, api_key: str, name: str = "API Tool", description: str = "This tool uses an API to get information"):
        self.api_url = api_url
        self.api_key = api_key
        super().__init__(name, description)
