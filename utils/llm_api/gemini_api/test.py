import unittest
from unittest.mock import patch, Mock
from utils.llm_api.gemini_api.gemini_api import ask_gemini
import requests
import os

API_KEY = os.getenv("GEMINI_API")


class TestGeminiAPI(unittest.TestCase):
    @patch('requests.post')
    def test_successful_response(self, mock_post):
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Test response from Gemini'}]
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Call function
        result = ask_gemini("Test question", API_KEY)

        # Assert results
        self.assertEqual(result, "Test response from Gemini")
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_error_on_invalid_response_structure(self, mock_post):
        # Setup invalid response structure
        mock_response = Mock()
        mock_response.json.return_value = {'wrong': 'structure'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = ask_gemini("Test question", API_KEY)
        self.assertEqual(result, "ERROR")

    @patch('requests.post')
    def test_http_error_returns_error(self, mock_post):
        # Simulate HTTP error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_post.return_value = mock_response

        result = ask_gemini("Test question", API_KEY)
        self.assertEqual(result, "ERROR")

    @patch('requests.post')
    def test_connection_error_returns_error(self, mock_post):
        # Simulate network error
        mock_post.side_effect = requests.exceptions.ConnectionError

        result = ask_gemini("Test question", API_KEY)
        self.assertEqual(result, "ERROR")


if __name__ == '__main__':
    unittest.main()
