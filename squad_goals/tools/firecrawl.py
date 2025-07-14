import os
import re
import json
from typing import Optional

import requests

from .base_tool import BaseTool


def scrape_linkedin(url):
    """
    Scrape LinkedIn content using Piloterr API
    Supports different LinkedIn content types: profiles, companies, posts, jobs, products
    """
    piloterr_api_key = os.getenv('PILOTERR_API_KEY')
    if not piloterr_api_key:
        raise ValueError("PILOTERR_API_KEY environment variable is required for LinkedIn scraping")
    
    headers = {"x-api-key": piloterr_api_key}
    
    try:
        # LinkedIn company page
        if "/company/" in url.lower():
            response = requests.get(
                "https://piloterr.com/api/v2/linkedin/company/info",
                headers=headers,
                params={"query": url}
            )
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        
        # LinkedIn profile page
        elif "/in/" in url.lower():
            response = requests.get(
                "https://piloterr.com/api/v2/linkedin/advanced/profile/info",
                headers=headers,
                params={"query": url}
            )
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        
        # LinkedIn post
        elif "/posts/" in url.lower() or "/activity/" in url.lower():
            response = requests.get(
                "https://piloterr.com/api/v2/linkedin/post/info",
                headers=headers,
                params={"query": url}
            )
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        
        # LinkedIn job
        elif "/jobs/view/" in url.lower():
            # Extract job ID from URL
            job_id_match = re.search(r"/jobs/view/(?:[^-/]+(?:-[^-/]+)*-)?(\d+)", url)
            
            if job_id_match:
                job_id = job_id_match.group(1)
                query_param = job_id
            else:
                # Fallback to using the full URL if we can't extract the ID
                query_param = url
            
            response = requests.get(
                "https://piloterr.com/api/v2/linkedin/job/info",
                headers=headers,
                params={"query": query_param}
            )
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        
        # LinkedIn product
        elif "/products/" in url.lower():
            response = requests.get(
                "https://piloterr.com/api/v2/linkedin/product/info",
                headers=headers,
                params={"query": url}
            )
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        
        else:
            raise ValueError(f"Unsupported LinkedIn URL type: {url}")
            
    except requests.RequestException as e:
        raise Exception(f"Error scraping LinkedIn with Piloterr: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Error decoding Piloterr response: {str(e)}")


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
            if os.getenv('PILOTERR_API_KEY') is None:
                raise ValueError("PILOTERR_API_KEY environment variable is required for LinkedIn scraping")
            return scrape_linkedin(website_url)
        response = self.firecrawl.scrape_url(
            website_url, params={'formats': ['markdown', 'links']}
        ).get(what_to_return)
        if type(response) in (str,):
            # replace (data:image/....) with ()
            import re
            response = re.sub(r'\(data:image/.*?\)', '()', response)
        return response
