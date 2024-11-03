from typing import Optional

from .base_tool import BaseTool


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
            what_to_return: Optional[str] = 'markdown'  # 'markdown' to get the text of the page, 'links' to get the links on the page only
    ):
        '''
        :param website_url: The URL of the website to scrape
        :param what_to_return: 'markdown' to get the text of the page, 'links' to get the links on the page only
        '''
        response = self.firecrawl.scrape_url(
            website_url, params={'formats': ['markdown', 'links']}
        ).get(what_to_return)
        if type(response) in (str,):
            # replace (data:image/....) with ()
            import re
            response = re.sub(r'\(data:image/.*?\)', '()', response)
        return response
