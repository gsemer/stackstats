import logging
from typing import List, Dict, Any

from domain.interfaces import StackExchangeServiceInterface, StackExchangeClientInterface, RedisCacheRepositoryInterface, CalculatorInterface
from domain.models import Answer, Comment


logger = logging.getLogger("stackexchange_api")


class StackExchangeService(StackExchangeServiceInterface):
    """
    Service layer responsible for:
      - fetching data from StackExchange API,
      - caching results,
      - computing statistics via Calculator.
    """

    def __init__(
        self,
        client: StackExchangeClientInterface,
        cache: RedisCacheRepositoryInterface,
        calculator: CalculatorInterface
    ):
        """
        Args:
            client: StackExchange API client for fetching answers and comments.
            cache: Cache repository for storing and retrieving results.
            calculator: Statistics calculator for computing metrics.
        """
        self._client = client
        self._cache = cache
        self._calculator = calculator

    async def stackstats(self, since: int, until: int) -> Dict[str, Any]:
        """
        Compute statistics for a given Unix timestamp range.
        Uses cache if available, otherwise fetches data from the API.

        Args:
            since: Start of the time range as a Unix timestamp.
            until: End of the time range as a Unix timestamp.

        Returns:
            Dictionary containing computed statistics.

        TODO:
            - In production with multiple service instances, consider a Redis distributed
              lock to prevent cache stampedes on concurrent simultaneous requests for the same key.
            - In production, save results in a persistent database in addition to Redis.
        """

        key = f"stackstats:{since}:{until}"
        logger.info("Processing stackstats for key: %s", key)

        # First check outside the lock
        cached = await self._cache.get(key)
        if cached:
            logger.info("Returning cached results")
            return cached

        # Fetch answers from API
        logger.info("Fetching answers from API...")
        answers: List[Answer] = await self._client.fetch_answers(since, until)
        answer_ids = [answer.answer_id for answer in answers]

        # Fetch comments for answers
        logger.info("Fetching comments for %d answers...", len(answer_ids))
        comments: List[Comment] = await self._client.fetch_comments(answer_ids)

        # Compute statistics
        logger.info("Computing statistics...")
        result: Dict[str, Any] = await self._calculator.compute_statistics(answers, comments)

        # Store result in cache
        await self._cache.set(key, result)
        logger.info("Stored results in cache")

        return result
