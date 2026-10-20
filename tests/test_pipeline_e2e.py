"""
End-to-End Pipeline Verification Test
Creates a sample synthetic audio tone, verifies Whisper transcription,
Ollama insights generation, ChromaDB vector indexing, and export generation.
"""

import os
import wave
import struct
import math
import unittest
from pathlib import Path

from config import TEMP_DIR
from modules.video_assistant.downloader import chunk_audio_if_needed
from modules.video_assistant.transcriber import transcribe_audio
from modules.video_assistant.summarizer import generate_full_insights, is_llm_available
from modules.video_assistant.rag_engine import build_or_get_vector_store, ask_rag_question
from modules.video_assistant.exporter import export_as_markdown, export_as_pdf

class TestE2EPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Generate a 3-second 16kHz mono WAV file containing a simple tone
        cls.test_wav_path = str(TEMP_DIR / "synthetic_test.wav")
        sample_rate = 16000
        duration_sec = 3
        frequency = 440.0  # A4 note

        with wave.open(cls.test_wav_path, "w") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            for i in range(int(sample_rate * duration_sec)):
                sample = int(32767.0 * 0.3 * math.sin(2.0 * math.pi * frequency * (i / sample_rate)))
                wav_file.writeframes(struct.pack("<h", sample))

    def test_01_whisper_transcription_runs(self):
        # Faster-Whisper on synthetic audio
        result = transcribe_audio(
            wav_path=self.test_wav_path,
            language="english",
            model_size="tiny",  # Use tiny for ultra-fast verification
        )
        self.assertIn("text", result)
        self.assertIn("formatted_text", result)
        self.assertIn("segments", result)
        self.assertGreaterEqual(result["duration"], 2.0)

    def test_02_ollama_insights_and_rag(self):
        # Sample realistic transcript to test insights & RAG without depending on audio speech content
        sample_transcript = (
            "Welcome everyone. Today we are finalizing the Q3 architecture for project VISTA. "
            "First, Ketan confirmed that we will deploy ChromaDB for persistent vector search by Friday. "
            "Second, the team decided to integrate Faster-Whisper as the primary speech engine for low latency. "
            "Third, John raised a question about whether we should support Sarvam AI for Hinglish audio."
        )

        segments = [
            {"index": 0, "start": 0.0, "end": 6.5, "text": "Welcome everyone. Today we are finalizing the Q3 architecture for project VISTA."},
            {"index": 1, "start": 7.0, "end": 14.5, "text": "First, Ketan confirmed that we will deploy ChromaDB for persistent vector search by Friday."},
            {"index": 2, "start": 15.0, "end": 22.0, "text": "Second, the team decided to integrate Faster-Whisper as the primary speech engine for low latency."},
            {"index": 3, "start": 22.5, "end": 30.0, "text": "Third, John raised a question about whether we should support Sarvam AI for Hinglish audio."},
        ]

        # Test Insights
        insights = generate_full_insights(sample_transcript)
        self.assertIn("title", insights)
        self.assertIn("summary", insights)
        self.assertIn("action_items", insights)
        self.assertIn("key_decisions", insights)
        self.assertIn("open_questions", insights)

        # Test RAG Vector Store & LCEL Querying
        source_hash = "test_e2e_hash"
        vector_store = build_or_get_vector_store(
            source_hash=source_hash,
            segments=segments,
            source_name="VISTA Q3 Meeting",
        )
        self.assertIsNotNone(vector_store)

        answer, citations = ask_rag_question(
            vector_store=vector_store,
            question="Who is deploying ChromaDB and what is the deadline?",
            k=2,
        )
        self.assertIsInstance(answer, str)
        self.assertGreater(len(answer), 5)
        self.assertGreater(len(citations), 0)
        self.assertIn("time_tag", citations[0])

        # Test Export
        report_data = {
            "title": insights["title"],
            "source": "synthetic_test_source",
            "duration": 30.0,
            "transcript": sample_transcript,
            "formatted_transcript": "\n".join([f"[{s['start']} - {s['end']}] {s['text']}" for s in segments]),
            "summary": insights["summary"],
            "action_items": insights["action_items"],
            "key_decisions": insights["key_decisions"],
            "open_questions": insights["open_questions"],
        }
        md = export_as_markdown(report_data)
        self.assertIn("VISTA Video Intelligence Report", md)

        pdf_path = str(TEMP_DIR / "e2e_test_report.pdf")
        export_as_pdf(report_data, pdf_path)
        self.assertTrue(os.path.exists(pdf_path))

if __name__ == "__main__":
    unittest.main()
