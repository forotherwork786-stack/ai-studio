from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv('AI_STUDIO_DB_PATH', Path(__file__).resolve().parents[1] / 'ai_studio.db'))


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    try:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                path TEXT NOT NULL,
                description TEXT
            )
            '''
        )
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS generation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                task_type TEXT NOT NULL,
                model_name TEXT NOT NULL,
                prompt TEXT,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL,
                output_path TEXT
            )
            '''
        )
        conn.commit()
    finally:
        conn.close()


def save_project(name: str, path: str, description: str | None = None) -> int:
    if not name or not name.strip():
        raise ValueError('Project name is required.')
    if not path or not path.strip():
        raise ValueError('Project path is required.')

    conn = get_connection()
    try:
        cursor = conn.execute(
            'INSERT INTO projects (name, created_at, path, description) VALUES (?, datetime("now"), ?, ?)',
            (name.strip(), path.strip(), description.strip() if description else None),
        )
        conn.commit()
        return int(cursor.lastrowid)
    finally:
        conn.close()


def list_projects() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute('SELECT * FROM projects ORDER BY created_at DESC').fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def log_generation(task_id: str, task_type: str, model_name: str, prompt: str, status: str, output_path: str | None = None) -> None:
    conn = get_connection()
    try:
        conn.execute(
            '''
            INSERT INTO generation_history (task_id, task_type, model_name, prompt, created_at, status, output_path)
            VALUES (?, ?, ?, ?, datetime("now"), ?, ?)
            ''',
            (task_id, task_type, model_name, prompt, status, output_path),
        )
        conn.commit()
    finally:
        conn.close()


def list_generation_history() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute('SELECT * FROM generation_history ORDER BY created_at DESC').fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
