"""
Tests for Cache & Duplicate Detection
"""

import unittest
from modules.video_assistant.cache_manager import CacheManager

class TestCacheManager(unittest.TestCase):
    def test_url_hash_deterministic(self):
        url1 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        url2 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        url_diff = "https://www.youtube.com/watch?v=other12345"

        h1 = CacheManager.get_source_hash(url1)
        h2 = CacheManager.get_source_hash(url2)
        h_diff = CacheManager.get_source_hash(url_diff)

        self.assertEqual(h1, h2)
        self.assertNotEqual(h1, h_diff)
        self.assertEqual(len(h1), 16)

    def test_cache_save_and_load(self):
        test_source = "https://www.youtube.com/watch?v=test_caching_xyz"
        dummy_data = {
            "title": "Test Video Title",
            "summary": "Test Summary Content",
            "action_items": "1. Do work",
            "key_decisions": "1. Deploy VISTA",
            "open_questions": "None",
            "transcript": "Hello world",
        }

        # Save
        source_hash = CacheManager.save_result(test_source, dummy_data)
        self.assertTrue(source_hash)

        # Load
        loaded = CacheManager.load_cached_result(test_source)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["title"], "Test Video Title")
        self.assertEqual(loaded["source_hash"], source_hash)
        self.assertTrue(loaded.get("cached"))

if __name__ == "__main__":
    unittest.main()
