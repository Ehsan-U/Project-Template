from base64 import b64decode
import os
from typing import Dict, Tuple
from tenacity import AsyncRetrying, stop_after_attempt, wait_random_exponential
from httpx import AsyncClient, Response
from src.logger import logger



class Request:
    """
    Represents an asynchronous HTTP request.

    Attributes:
        ZYTE_ENDPOINT (str): The endpoint URL for the Zyte API.

    Args:
        client: The httpx Async client
        url (str): The URL of the request.
        method (str, optional): The HTTP method of the request. Defaults to "GET".
        headers (Dict, optional): The headers of the request. Defaults to None.
        cookies (Dict, optional): The cookies of the request. Defaults to None.
        params (Dict, optional): The query parameters of the request. Defaults to None.
        data (Dict, optional): The request body data. Defaults to None.
        json (Dict, optional): The request body JSON. Defaults to None.
        verify (bool, optional): Whether to verify SSL certificates. Defaults to True.
        proxies (Dict, optional): The proxies to use for the request. Defaults to None.
        follow_redirect (bool): Allow to follow redirect e.g HTTP 302
        auth (Tuple, optional): The authentication credentials. Defaults to None.
        zyte (bool): Allow to use Zyte
        zyte_api_key (str): The API key for accessing the Zyte API.
        browser (bool, optional): Whether to use browser rendering for the request. Defaults to False.

    Methods:
        send: Sends the request asynchronously and returns the response.
        prepare_zyte_payload: Prepares the payload for the zyte request.
    """

    TIMEOUT: int = 60
    RETRIES: int = 3
    USER_AGENT: str = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ZYTE_ENDPOINT: str = "https://api.zyte.com/v1/extract"

    def __init__(
            self,
            url: str, 
            client: AsyncClient = None,
            method: str = "GET", 
            headers: Dict = None,
            cookies: Dict = None,
            params: Dict = None,
            data: Dict = None,
            json: Dict = None,
            verify: bool = False,
            proxies: Dict = None,
            timeout: int = None,
            follow_redirect: bool = True,
            auth: Tuple = None,
            zyte: bool = False,
            zyte_api_key: str = None,
            browser: bool = False
        ):
        self.url = url
        self.client = client
        self.method = method
        self.headers = headers
        self.cookies = cookies
        self.params = params
        self.data = data
        self.json = json
        self.verify = verify
        self.proxies = proxies
        self.timeout = timeout or self.TIMEOUT
        self.follow_redirect = follow_redirect
        self.auth = auth
        self.zyte = zyte
        self.zyte_api_key = zyte_api_key or os.getenv("ZYTE_API_KEY")
        self.browser = browser


    def __repr__(self):
        return f"{self.__class__.__name__}(url={self.url}, method={self.method})"


    async def send(self) -> Response:
        """
        Sends the HTTP request asynchronously.
        """
        if not self.zyte:
            async for attempt in AsyncRetrying(stop=stop_after_attempt(self.RETRIES), wait=wait_random_exponential(multiplier=1, min=3, max=10), reraise=True):
                with attempt:
                    response = await self.client.request(
                        url=self.url, 
                        method=self.method, 
                        headers=self.headers, 
                        cookies=self.cookies, 
                        params=self.params, 
                        data=self.data, 
                        json=self.json,
                        auth=self.auth,
                        timeout=self.timeout,
                        follow_redirects=self.follow_redirect
                    )
                    if response.status_code not in [200, 403]:
                        response.raise_for_status()
                    logger.debug(f"Request sent to {self.url}: {response.status_code}")
                    return response
        else:
            json_payload = self.prepare_zyte_payload()
            async for attempt in AsyncRetrying(stop=stop_after_attempt(self.RETRIES), wait=wait_random_exponential(multiplier=1, min=4, max=10), reraise=True):
                with attempt:
                    response = await self.client.request(
                        method="POST",
                        url=self.ZYTE_ENDPOINT,
                        auth=(self.zyte_api_key, ""), 
                        json=json_payload,
                        timeout=self.timeout
                    )
                    if response.status_code not in [200, 403]:
                        response.raise_for_status()
                    logger.debug(f"Request sent to {self.url}: {response.status_code}")

                    if self.browser:
                        http_response_body = response.json()["browserHtml"]
                    else:
                        http_response_body = b64decode(response.json()["httpResponseBody"]).decode()

                    return Response(
                        status_code=response.status_code, 
                        request=self.client.build_request(url=self.url, method=self.method), 
                        text=http_response_body
                    )
        

    def prepare_zyte_payload(self) -> dict:
        """
        Prepares the payload for the zyte request.
        """

        if self.browser:
            return {"url": self.url, "browserHtml": True}
        else:
            return {
                "url": self.url,
                "httpResponseBody": True,
                "httpRequestMethod": self.method
            }

    
