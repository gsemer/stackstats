import unittest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from fastapi import status

from main import app
from schemas.response import StackStatsResponse
from api.dependencies import get_service


class StackExchangeTestCase(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app=app)

        self.url = "/api/v1/stackstats"

        self.mock_result = {
            "total_accepted_answers": 15,
            "accepted_answers_average_score": 7.7,
            "average_answers_per_question": 10.8,
            "top_ten_answers_comment_count": {
                "35886878": 6,
                "35886534": 6,
                "35887225": 3,
                "35886846": 8,
                "35886445": 6,
                "35886464": 0,
                "35887798": 2,
                "35888272": 3,
                "35887145": 3,
                "35887226": 1
            }
        }
        self.expected_result = StackStatsResponse(**self.mock_result)

        def override_get_service():
            stack_service_mock = AsyncMock()
            stack_service_mock.stackstats.return_value = self.mock_result
            return stack_service_mock

        app.dependency_overrides[get_service] = override_get_service
    
    def tearDown(self):
        app.dependency_overrides.clear()
        self.client.close()

    def test_stackstats_200(self):
        """
        Valid datetime range returns 200 and corrects statistics.
        """
        
        params = {
            "since": "2016-03-09T10:00:00",
            "until": "2016-03-09T11:00:00"
        }

        response = self.client.get(self.url, params=params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        actual_response = StackStatsResponse(**response.json())
        self.assertEqual(actual_response, self.expected_result)

    def test_stackstats_400(self):
        """
        Invalid datetime range (since > until) returns 400.
        """
        
        params = {
            "since": "2016-03-09T11:00:00",
            "until": "2016-03-09T10:00:00"
        }

        response = self.client.get(self.url, params=params)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("'since' must be before 'until'", response.text)

    def test_stackstats_422(self):
        """
        Non-datetime 'since' or 'until' values return 422 validation error.
        """

        params = {
            "since": "non-datetime-field",
            "until": "2016-03-09T10:00:00"
        }

        response = self.client.get(self.url, params=params)
        
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_CONTENT)
        self.assertIn("Input should be a valid datetime or date", response.text)
