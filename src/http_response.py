from httpx import Response
from parsel import Selector



class ResponseWrapper:
    """
    A wrapper class for the HTTP response.
    """
    not_allowed_domains = ["facebook.com", "twitter.com", "linkedin.com", "instagram.com", "tiktok.com", "youtube.com"]


    def __init__(self, response: Response):
        self.response = response
        self.url = str(response.url)


    def __repr__(self):
        return f"ResponseWrapper({self.response})"


    def __str__(self):
        return f"ResponseWrapper({self.response})"


    @property
    def json(self):
        try:
            return self.response.json()
        except:
            return None

    @property
    def text(self):
        return self.response.text


    @property
    def selector(self):
        return Selector(response.text)
