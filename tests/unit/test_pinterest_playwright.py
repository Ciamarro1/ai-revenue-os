import os
import unittest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
from src.execution.publisher.pinterest_playwright import PinterestPlaywrightPublisher

class TestPinterestPlaywrightPublisher(unittest.TestCase):
    def setUp(self):
        self.publisher = PinterestPlaywrightPublisher(openrouter_key="mock_key")

    def test_has_session_false_by_default(self):
        # Garante que sem o arquivo de sessão, ele retorne False
        self.publisher.session_path = Path("config/sessions/non_existent.json")
        self.assertFalse(self.publisher.has_session())

    @patch("src.execution.publisher.pinterest_playwright.sync_playwright")
    def test_publish_raises_filenotfound_when_no_session(self, mock_playwright):
        payload = {
            "media_path": "output_test.jpg",
            "title": "Test Title",
            "description": "Test Desc"
        }
        self.publisher.session_path = Path("config/sessions/non_existent.json")
        with self.assertRaises(FileNotFoundError):
            self.publisher.publish(payload)

    @patch("src.execution.publisher.pinterest_playwright.sync_playwright")
    @patch("src.execution.publisher.pinterest_playwright.requests.post")
    @patch("builtins.open", new_callable=mock_open, read_data=b"dummy_image_data")
    def test_vision_fallback_query(self, mock_file, mock_post, mock_playwright):
        # Mocking requests.post response for OpenRouter Vision Model
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"x": 100, "y": 200, "selector": "#publish"}'
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        # Test _query_vision_model
        res = self.publisher._query_vision_model(Path("output_test.jpg"), "Find publish button")
        self.assertIsNotNone(res)
        self.assertEqual(res["x"], 100)
        self.assertEqual(res["y"], 200)
        self.assertEqual(res["selector"], "#publish")

if __name__ == "__main__":
    unittest.main()
