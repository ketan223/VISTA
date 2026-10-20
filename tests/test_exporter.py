"""
Tests for Markdown and PDF Exporters
"""

import os
import unittest
from pathlib import Path
from modules.video_assistant.exporter import export_as_markdown, export_as_pdf
from config import TEMP_DIR

class TestExporter(unittest.TestCase):
    def setUp(self):
        self.sample_data = {
            "title": "Quarterly Product Strategy",
            "source": "https://youtube.com/watch?v=sample123",
            "duration": 365.0,
            "summary": "1. Launched new feature.\n2. Increased velocity by 40%.",
            "action_items": "1. Deploy release to production - Ketan - Friday",
            "key_decisions": "1. Adopt ChromaDB for local vector storage.",
            "open_questions": "1. When is the next sprint review?",
            "formatted_transcript": "[00:00 - 00:15] Good morning team.\n[00:16 - 00:30] Let's review the milestones.",
        }

    def test_export_as_markdown(self):
        md = export_as_markdown(self.sample_data)
        self.assertIn("# 🎬 VISTA Video Intelligence Report: Quarterly Product Strategy", md)
        self.assertIn("## 📋 Executive Summary", md)
        self.assertIn("Increased velocity by 40%", md)
        self.assertIn("[00:00 - 00:15]", md)

    def test_export_as_pdf(self):
        output_pdf = str(TEMP_DIR / "test_report.pdf")
        res_path = export_as_pdf(self.sample_data, output_pdf)
        self.assertTrue(os.path.exists(res_path))
        self.assertGreater(os.path.getsize(res_path), 500)  # File should have actual content

if __name__ == "__main__":
    unittest.main()
