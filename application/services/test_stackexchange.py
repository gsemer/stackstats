import asyncio
import unittest
from unittest.mock import AsyncMock
from datetime import datetime

from domain.models import Answer, Comment
from application.services.stackexchange import StackExchangeService


class StackExchangeServiceTestCase(unittest.TestCase):

    def setUp(self):
        
        self.answers = [
            Answer(1, 1, 10, True),
            Answer(2, 2, 10, False),
            Answer(3, 3, 10, True),
            Answer(4, 4, 10, True),
            Answer(5, 5, 10, False),
            Answer(6, 6, 10, True),
            Answer(7, 7, 10, True),
            Answer(8, 8, 10, False),
            Answer(9, 9, 10, True),
            Answer(10, 10, 10, True),
        ]

        self.comments = [
            Comment(1, 1), Comment(2, 1),
            Comment(3, 2), Comment(4, 2), 
            Comment(5, 3), Comment(6, 3),
            Comment(7, 4), Comment(8, 4),
            Comment(9, 5), Comment(10, 5), 
            Comment(11, 6), Comment(12, 6),
            Comment(13, 7), Comment(14, 7),
            Comment(15, 8), Comment(16, 8), 
            Comment(17, 9), Comment(18, 9),
            Comment(19, 10), Comment(20, 10),
        ]

        self.statistics = {
            "total_accepted_answers": 7,
            "accepted_answers_average_score": 7.0,
            "average_answers_per_question": 1.0,
            "top_ten_answers_comment_count": {
                "1": 2,
                "2": 2,
                "3": 2,
                "4": 2,
                "5": 2,
                "6": 2,
                "7": 2,
                "8": 2,
                "9": 2,
                "10": 2
            }
        }

        self.expected_statistics = self.statistics

    def test_stackstats(self):
        mock_client = AsyncMock()
        mock_client.fetch_answers.return_value = self.answers
        mock_client.fetch_comments.return_value = self.comments

        mock_cache = AsyncMock()
        mock_cache.get.return_value = None
        mock_cache.set.return_value = None

        mock_calculator = AsyncMock()
        mock_calculator.compute_statistics.return_value = self.statistics

        service = StackExchangeService(
            client=mock_client,
            cache=mock_cache,
            calculator=mock_calculator
        )

        since_dt = datetime.fromisoformat("2016-03-09T10:00:00")
        until_dt = datetime.fromisoformat("2016-03-09T11:00:00")

        since_ts = int(since_dt.timestamp())
        until_ts = int(until_dt.timestamp())

        actual_statistics = asyncio.run(service.stackstats(since=since_ts, until=until_ts))

        self.assertEqual(self.expected_statistics, actual_statistics)
