from typing import Dict
from httpx import Response
from parsel import Selector



class ResponseWrapper:
    """
    A wrapper class for the HTTP response.
    """
    not_allowed_domains = ["facebook.com", "twitter.com", "linkedin.com", "instagram.com", "tiktok.com", "youtube.com"]


    def __init__(self, response: Response):
        self.response = response
        self.url = str(response.url) if response else None


    def __repr__(self) -> str:
        return f"ResponseWrapper({self.response})"


    def __str__(self) -> str:
        return f"ResponseWrapper({self.response})"


    @property
    def is_successful(self) -> bool:
        return self.response is not None
    

    def json(self) -> Dict:
        if self.is_successful:
            return self.response.json()
        else:
            return {}


    @property
    def text(self) -> str:
        if self.is_successful:
            return self.response.text
        return ''


    @property
    def selector(self) -> Selector:
        if self.is_successful:
            return Selector(self.text)
