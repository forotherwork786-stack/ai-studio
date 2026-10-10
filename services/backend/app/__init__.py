import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

import app.storage as storage
from app.storage import initialize_database, list_generation_history, list_projects, log_generation, save_project


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.test_db = Path(tempfile.mkdtemp()) / 'test_ai_studio.db'
        os.environ['AI_STUDIO_DB_PATH'] = str(self.test_db)
        storage.DB_PATH = self.test_db

    def test_initialize_database_creates_tables(self):
        initialize_database()
        conn = sqlite3.connect(str(self.test_db))
        try:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('projects', 'generation_history')"
            ).fetchall()
            self.assertEqual(len(tables), 2)
        finally:
            conn.close()

    def test_project_and_generation_logging(self):
        initialize_database()
        project_id = save_project('Test Project', '/tmp/project', 'Example description')
        self.assertGreater(project_id, 0)
        log_generation('task-123', 'image', 'Stable Diffusion 1.5', 'A test prompt', 'Preparing', '/tmp/output.png')
        projects = list_projects()
        history = list_generation_history()
        self.assertTrue(any(project['name'] == 'Test Project' for project in projects))
        self.assertTrue(any(item['task_id'] == 'task-123' for item in history))


if __name__ == '__main__':
    unittest.main()
