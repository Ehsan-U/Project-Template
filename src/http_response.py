from httpx import Response
from parsel import Selector



class ResponseWrapper:
    """
    A wrapper class for the HTTP response.
    """
    not_allowed_domains = ["facebook.com", "twitter.com", "linkedin.com", "instagram.com", "tiktok.com", "youtube.com"]


    def __init__(self, response: Response):
        self.response = response
        self.selector = Selector(response.text)
        self.url = str(response.url)


    def __repr__(self):
        return f"ResponseWrapper({self.response})"


    def __str__(self):
        return f"ResponseWrapper({self.response})"
