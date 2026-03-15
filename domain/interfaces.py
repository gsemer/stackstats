from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union

from domain.models import Answer, Comment


class StackExchangeServiceInterface(ABC):
    """Service contract for computing StackExchange statistics."""

    @abstractmethod
    async def stackstats(self, since: int, until: int) -> Dict[str, Any]:
        """Return computed statistics for a given Unix timestamp range."""
        pass


class CalculatorInterface(ABC):
    """Contract for statistics calculation."""

    @abstractmethod
    async def compute_statistics(self, answers: List[Answer], comments: List[Comment]) -> Dict[str, Any]:
        """Compute statistics from answers and comments."""
        pass


class StackExchangeClientInterface(ABC):
    """Contract for StackExchange data retrieval."""

    @abstractmethod
    async def fetch_answers(self, since: int, until: int) -> List[Answer]:
        """Retrieve answers within a time range."""
        pass

    @abstractmethod
    async def fetch_comments(self, answer_ids: List[int]) -> List[Comment]:
        """Retrieve comments for a list of answer IDs."""
        pass


class RedisCacheRepositoryInterface(ABC):
    """Cache abstraction for storing API results."""

    @abstractmethod
    async def get(self, key: str) -> Union[None, Dict]:
        """Retrieve cached value. Returns None if missing."""
        pass

    @abstractmethod
    async def set(self, key: str, value: dict, ttl: int):
        """Store value in cache."""
        pass
