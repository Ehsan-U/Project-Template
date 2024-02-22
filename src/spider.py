import asyncio
from typing import Iterable, List
from httpx import AsyncClient
from asyncio.tasks import Task

from src.http_requests import Request
from src.http_response import ResponseWrapper
from src.utils import logger


class Spider():
    client = AsyncClient()


    async def _get(self, url: str) -> ResponseWrapper:
        try:
            request = Request(client=self.client, url=url, zyte=True)
            response = await request.send()
        except Exception as e:
            logger.error(e)
            response = None
        finally:
            return ResponseWrapper(response)


    def task(self, url: str) -> Task:
        return asyncio.create_task(self._get(url))


    async def execute_tasks(self, tasks: List[Task]) -> Iterable[ResponseWrapper]:
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return responses