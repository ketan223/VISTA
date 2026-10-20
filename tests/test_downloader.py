"""
Tests for Downloader & Media Validation
"""

import unittest
from modules.video_assistant.downloader import is_valid_youtube_url, validate_local_file

class TestDownloader(unittest.TestCase):
    def test_valid_youtube_urls(self):
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "http://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
            "https://youtube.com/embed/dQw4w9WgXcQ",
        ]
        for url in valid_urls:
            self.assertTrue(is_valid_youtube_url(url), f"Should be valid: {url}")

    def test_invalid_youtube_urls(self):
        invalid_urls = [
            "https://vimeo.com/123456",
            "https://google.com",
            "",
            None,
            "not a url",
            "ftp://youtube.com/watch?v=123",
        ]
        for url in invalid_urls:
            self.assertFalse(is_valid_youtube_url(url), f"Should be invalid: {url}")

    def test_local_file_validation_missing(self):
        valid, msg = validate_local_file("non_existent_file.mp4")
        self.assertFalse(valid)
        self.assertIn("not found", msg.lower())

if __name__ == "__main__":
    unittest.main()
