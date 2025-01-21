import os
from typing import Optional

import requests

from .base_tool import BaseTool


def scrape_linkedin(url):
    def generate_text_blob(data):
        excluded_keys = {'id', 'urn', 'username', 'profilePicture', 'position', 'backgroundImage',
                         'multiLocaleFirstName',
                         'multiLocaleLastName', 'multiLocaleHeadline', 'supportedLocales'}

        def format_education(education):
            return f"{education.get('degree', '')} in {education.get('fieldOfStudy', '')} from {education.get('schoolName', '')}"

        def format_position(position):
            start_year = position.get('start', {}).get('year', '')
            end_year = position.get('end', {}).get('year', '')
            if end_year == 0:
                end_year = 'Present'
            return (f"{position.get('title', '')} at {position.get('companyName', '')} "
                    f"({start_year} - {end_year}): {position.get('description', '')}")

        def format_skills(skills):
            return ', '.join(skill.get('name', '') for skill in skills)

        def format_languages(languages):
            return ', '.join(
                f"{lang.get('name', '')} ({lang.get('proficiency', 'Proficiency not specified')})" for lang in
                languages)

        def format_honors(honors):
            return "\n".join(
                f"{honor.get('title', '')}: {honor.get('description', '')} ({honor.get('issuer', '')}, {honor.get('issuedOn', {}).get('year', '')})"
                for honor in honors)

        def format_volunteering(volunteering):
            return "\n".join(
                f"{vol.get('title', '')} at {vol.get('companyName', '')} ({vol.get('start', {}).get('year', '')} - {vol.get('end', {}).get('year', 'Present')})"
                for vol in volunteering)

        text_blob = []

        for key, value in data.items():
            if key in excluded_keys:
                continue
            elif key == 'geo':
                text_blob.append(f"Location: {value.get('full', '')}")
            elif key == 'summary':
                text_blob.append(f"Summary: {value}")
            elif key == 'headline':
                text_blob.append(f"Headline: {value}")
            elif key == 'educations':
                educations = "\n".join(format_education(edu) for edu in value)
                text_blob.append(f"Education:\n{educations}")
            elif key == 'fullPositions':
                positions = "\n".join(format_position(pos) for pos in value)
                text_blob.append(f"Positions:\n{positions}")
            elif key == 'skills':
                text_blob.append(f"Skills: {format_skills(value)}")
            elif key == 'languages':
                text_blob.append(f"Languages: {format_languages(value)}")
            elif key == 'honors':
                text_blob.append(f"Honors:\n{format_honors(value)}")
            elif key == 'volunteering':
                text_blob.append(f"Volunteering:\n{format_volunteering(value)}")
            else:
                # Handle any other keys
                if isinstance(value, list):
                    items = "\n".join(str(item) for item in value)
                    text_blob.append(f"{key.capitalize()}:\n{items}")
                elif isinstance(value, dict):
                    details = "\n".join(f"{k}: {v}" for k, v in value.items())
                    text_blob.append(f"{key.capitalize()} Details:\n{details}")
                else:
                    text_blob.append(f"{key.capitalize()}: {value}")

        return "\n\n".join(text_blob)

    scrape_url = "https://linkedin-data-api.p.rapidapi.com/get-profile-data-by-url"

    querystring = {"url": url}

    headers = {
        "x-rapidapi-key": os.getenv('RAPID_API_KEY'),
        "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com"
    }

    response = requests.get(scrape_url, headers=headers, params=querystring)
    return generate_text_blob(response.json())


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
            if os.getenv('RAPID_API_KEY') is None:
                raise ValueError("RAPID_API_KEY environment variable is required for LinkedIn scraping")
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
