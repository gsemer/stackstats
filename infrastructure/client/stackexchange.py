import asyncio
import aiohttp
import logging
from typing import List, Dict, Any
from domain.models import Answer, Comment
from domain.exceptions import StackExchangeClientError
from domain.interfaces import StackExchangeClientInterface
from stackexchange.settings import settings


logger = logging.getLogger("StackExchangeClient")


class StackExchangeClient(StackExchangeClientInterface):
    """
    Async client responsible for communication with the StackExchange API.
    """

    def __init__(
        self,
        key: str,
        base_url: str,
        site: str,
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
    ):
        """
        Args:
            key: StackExchange API key for authenticated requests.
            base_url: Base URL of the StackExchange API.
            site: StackExchange site to query (e.g. 'stackoverflow').
            session: Shared aiohttp ClientSession for HTTP requests.
            semaphore: Semaphore to limit the number of concurrent requests.
        """
        self._key = key
        self._base_url = base_url
        self._site = site
        self._session = session
        self._semaphore = semaphore

    async def _fetch(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a single HTTP GET request with retry logic.

        Retries up to RETRY_ATTEMPTS times on ClientErrors and waits RETRY_WAIT seconds between attempts.

        Args:
            url: The endpoint URL to request.
            params: Query parameters to include in the request.

        Returns:
            Parsed JSON response as a dictionary.

        Raises:
            StackExchangeClientError: If all retry attempts are failed.
        """
        for attempt in range(settings.RETRY_ATTEMPTS):
            try:
                async with self._semaphore:
                    async with self._session.get(url, params=params) as response:
                        response.raise_for_status()
                        return await response.json()
            except aiohttp.ClientError as client_error:
                if attempt == settings.RETRY_ATTEMPTS - 1:
                    raise StackExchangeClientError() from client_error
                await asyncio.sleep(settings.RETRY_WAIT)

    async def fetch_answers(self, since: int, until: int) -> List[Answer]:
        """
        Retrieve all answers from StackOverflow within a Unix timestamp range.

        Paginates through all available results using the StackExchange API.

        Args:
            since: Start of the time range as a Unix timestamp.
            until: End of the time range as a Unix timestamp.

        Returns:
            List of Answer objects within the given time range.
        """

        logger.info("Fetching answers from %s to %s", since, until)

        url = f"{self._base_url}/answers"
        params = {
            "fromdate": since,
            "todate": until,
            "site": self._site,
            "pagesize": settings.PAGE_SIZE,
            "page": 1,
            "order": "desc",
            "sort": "creation",
            "filter": "default",
            "key": self._key
        }

        results: List[Answer] = []

        while True:
            data = await self._fetch(url, params)

            for item in data.get("items", []):
                results.append(
                    Answer(
                        answer_id=item["answer_id"],
                        question_id=item["question_id"],
                        score=item["score"],
                        is_accepted=item.get("is_accepted", False),
                    )
                )

            if not data.get("has_more"):
                break
            
            params["page"] += 1

        logger.info("Fetched %d answers", len(results))
        return results

    async def fetch_comments(self, answer_ids: List[int]) -> List[Comment]:
        """
        Retrieve all comments for a list of answer IDs.

        Sends requests in batches of 100 IDs (StackExchange API limit) and
        paginates through all available results for each batch.

        Args:
            answer_ids: List of answer IDs to fetch comments for.

        Returns:
            List of Comment objects associated with the given answers.
        """

        if not answer_ids:
            return []

        results: List[Comment] = []

        batch_size = 100

        for i in range(0, len(answer_ids), batch_size):

            batch = answer_ids[i:i + batch_size]
            ids = ";".join(map(str, batch))

            url = f"{self._base_url}/answers/{ids}/comments"
            params = {
                "site": self._site,
                "pagesize": settings.PAGE_SIZE,
                "page": 1,
                "key": self._key
            }

            while True:
                data = await self._fetch(url, params)

                for item in data.get("items", []):
                    results.append(
                        Comment(
                            comment_id=item["comment_id"],
                            answer_id=item["post_id"]
                        )
                    )

                if not data.get("has_more"):
                    break

                params["page"] += 1

        logger.info("Fetched %d comments", len(results))
        return results
