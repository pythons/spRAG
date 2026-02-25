import os
import shutil
import sqlite3
import unittest

from dsrag.database.chat_thread.sqlite_db import SQLiteChatThreadDB


class TestSQLiteChatThreadDB(unittest.TestCase):
    def setUp(self):
        self.storage_directory = os.path.expanduser("~/test__sqlite_chat_thread_dsrag")
        if os.path.exists(self.storage_directory):
            shutil.rmtree(self.storage_directory)
        self.db = SQLiteChatThreadDB(storage_directory=self.storage_directory)

    def tearDown(self):
        if os.path.exists(self.storage_directory):
            shutil.rmtree(self.storage_directory)

    def test_round_trip_chat_thread_with_status(self):
        params = {
            "thread_id": "thread_1",
            "supp_id": "supp_1",
            "kb_ids": ["kb_a"],
            "model": "gpt-4o-mini",
            "temperature": 0.2,
            "system_message": "sys",
            "auto_query_model": "gpt-4o-mini",
            "auto_query_guidance": "",
            "target_output_length": "medium",
            "max_chat_history_tokens": 8000,
            "rse_params": {"preset": "balanced"},
        }
        self.db.create_chat_thread(params)
        interaction = {
            "user_input": {"content": "hello", "timestamp": "1"},
            "model_response": {"content": "world", "timestamp": "2", "citations": [], "status": "finished"},
            "relevant_segments": [],
            "search_queries": [],
        }
        self.db.add_interaction("thread_1", interaction)

        thread = self.db.get_chat_thread("thread_1")
        self.assertEqual(thread["params"]["kb_ids"], ["kb_a"])
        self.assertEqual(thread["interactions"][0]["model_response"]["status"], "finished")
        self.assertEqual(thread["interactions"][0]["model_response"]["content"], "world")

    def test_legacy_json_fallback_does_not_crash(self):
        params = {
            "thread_id": "thread_2",
            "supp_id": "",
            "kb_ids": ["kb_b"],
            "model": "gpt-4o-mini",
            "temperature": 0.2,
            "system_message": "",
            "auto_query_model": "gpt-4o-mini",
            "auto_query_guidance": "",
            "target_output_length": "medium",
            "max_chat_history_tokens": 8000,
            "rse_params": {},
        }
        self.db.create_chat_thread(params)

        conn = sqlite3.connect(self.db.db_path)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO interactions (
                thread_id, message_id, user_input, user_input_timestamp, model_response,
                model_response_timestamp, relevant_segments, search_queries, citations, model_response_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "thread_2",
                "m1",
                "legacy user",
                "10",
                "legacy model",
                "11",
                "not-json",
                "not-json",
                "not-json",
                "finished",
            ),
        )
        conn.commit()
        conn.close()

        thread = self.db.get_chat_thread("thread_2")
        self.assertEqual(thread["interactions"][0]["search_queries"], [])
        self.assertEqual(thread["interactions"][0]["relevant_segments"], [])
        self.assertEqual(thread["interactions"][0]["model_response"]["citations"], [])
