"""
Tests for RAG Engine Chunking and Metadata Preservation
"""

import unittest
from modules.video_assistant.rag_engine import build_documents_from_segments
from modules.video_assistant.transcriber import format_timestamp

class TestRAGEngine(unittest.TestCase):
    def test_format_timestamp(self):
        self.assertEqual(format_timestamp(0), "00:00")
        self.assertEqual(format_timestamp(65), "01:05")
        self.assertEqual(format_timestamp(3665), "01:01:05")

    def test_chunking_preserves_metadata(self):
        segments = [
            {"index": 0, "start": 0.0, "end": 15.0, "text": "Welcome to the first segment."},
            {"index": 1, "start": 15.5, "end": 35.0, "text": "This is the second segment."},
            {"index": 2, "start": 36.0, "end": 60.0, "text": "Finally this is the third segment."},
        ]

        docs = build_documents_from_segments(segments, source_name="Test Source", target_chunk_words=10)
        self.assertGreater(len(docs), 0)

        first_doc = docs[0]
        self.assertIn("start_time", first_doc.metadata)
        self.assertIn("end_time", first_doc.metadata)
        self.assertIn("time_tag", first_doc.metadata)
        self.assertEqual(first_doc.metadata["start_time"], 0.0)
        self.assertEqual(first_doc.metadata["source"], "Test Source")
        self.assertIn("[00:00 -", first_doc.page_content)

if __name__ == "__main__":
    unittest.main()
