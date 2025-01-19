from typing import Optional

import requests
from bs4 import BeautifulSoup

from .base_tool import BaseTool


def scrape_linkedin(url):
    # Define the user-agent
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Make the HTTP GET request
    response = requests.get(url, headers=headers)

    # Check for successful response
    if response.status_code != 200:
        print(f"Failed to fetch the homepage. Status code: {response.status_code}")
        return

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract SEO-relevant elements
    seo_data = {}

    # Title tag
    title_tag = soup.find("title")
    seo_data["title"] = title_tag.text if title_tag else "Title tag not found"

    # Meta description
    meta_description = soup.find("meta", attrs={"name": "description"})
    seo_data["meta_description"] = meta_description["content"] if meta_description else "Meta description not found"

    # Header tags (H1, H2, H3)
    headers = {"h1": [], "h2": [], "h3": []}
    for level in headers.keys():
        headers[level] = [header.text.strip() for header in soup.find_all(level)]
    seo_data["headers"] = headers

    # Links (internal and external)
    links = []
    for link in soup.find_all("a", href=True):
        href = link["href"].strip()
        text = link.text.strip()
        links.append({"href": href, "text": text})
    seo_data["links"] = links

    return seo_data


class FirecrawlSearchTool(BaseTool):

    def __init__(self,
                 name: str = "Firecrawl web search tool",
                 description: str = "Search webpages using Firecrawl and return the results",
                 api_key: Optional[str] = None, **kwargs):

        try:
            from firecrawl import FirecrawlApp  # type: ignore
        except ImportError:
            raise ImportError(
                "`firecrawl` package not found, please run `pip install firecrawl-py`"
            )
        if not api_key:  # look for env var
            import os
            api_key = os.getenv('FIRECRAWL_API_KEY')
        if not api_key:
            raise ValueError("Firecrawl API key is required")

        self.firecrawl = FirecrawlApp(api_key=api_key)
        super().__init__(name=name, description=description, **kwargs)

    def run(
            self,
            website_url: str,
            what_to_return: Optional[str] = 'markdown'
            # 'markdown' to get the text of the page, 'links' to get the links on the page only
    ):
        '''
        :param website_url: The URL of the website to scrape
        :param what_to_return: 'markdown' to get the text of the page, 'links' to get the links on the page only
        '''
        if 'linkedin.co' in website_url and what_to_return == 'markdown':
            print("Scraping LinkedIn...")
            return scrape_linkedin(website_url)
        response = self.firecrawl.scrape_url(
            website_url, params={'formats': ['markdown', 'links']}
        ).get(what_to_return)
        if type(response) in (str,):
            # replace (data:image/....) with ()
            import re
            response = re.sub(r'\(data:image/.*?\)', '()', response)
        return response
