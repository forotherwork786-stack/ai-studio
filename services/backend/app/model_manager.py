from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


_STATUS_ORDER = ['Waiting', 'Preparing', 'Loading Model', 'Generating', 'Processing', 'Completed', 'Failed', 'Cancelled']


@dataclass
class QueueEntry:
    task_id: str
    task_type: str
    model_name: str
    prompt: str
    status: str = 'Waiting'
    progress: float | None = None
    output_path: str | None = None
    error: str | None = None
    created_at: str = ''
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            'task_id': self.task_id,
            'task_type': self.task_type,
            'model_name': self.model_name,
            'prompt': self.prompt,
            'status': self.status,
            'progress': self.progress,
            'output_path': self.output_path,
            'error': self.error,
            'created_at': self.created_at,
            'metadata': self.metadata,
        }


class GenerationQueue:
    """In-memory queue used to manage generation requests safely and predictably."""

    def __init__(self, max_concurrency: int = 1):
        self.max_concurrency = max(1, min(max_concurrency, 4))
        self._jobs: dict[str, QueueEntry] = {}
        self.active = 0

    def add(self, task: QueueEntry) -> QueueEntry:
        if task.task_id in self._jobs:
            raise ValueError(f'Job {task.task_id} already exists.')
        self._jobs[task.task_id] = task
        return task

    def list(self) -> list[dict[str, Any]]:
        return [job.to_dict() for job in self._jobs.values()]

    def get(self, task_id: str) -> QueueEntry | None:
        return self._jobs.get(task_id)

    def cancel(self, task_id: str) -> QueueEntry:
        entry = self._jobs.get(task_id)
        if entry is None:
            raise KeyError(f'Job {task_id} not found.')
        entry.status = 'Cancelled'
        if self.active > 0 and entry.status == 'Generating':
            self.active -= 1
        return entry

    def retry(self, task_id: str) -> QueueEntry:
        entry = self._jobs.get(task_id)
        if entry is None:
            raise KeyError(f'Job {task_id} not found.')
        entry.status = 'Waiting'
        entry.error = None
        entry.progress = None
        return entry

    def update_status(self, task_id: str, status: str, progress: float | None = None, output_path: str | None = None, error: str | None = None) -> QueueEntry:
        entry = self._jobs.get(task_id)
        if entry is None:
            raise KeyError(f'Job {task_id} not found.')
        if status not in _STATUS_ORDER:
            raise ValueError(f'Unsupported status: {status}')
        entry.status = status
        if progress is not None:
            entry.progress = max(0.0, min(1.0, progress))
        if output_path is not None:
            entry.output_path = output_path
        if error is not None:
            entry.error = error
        return entry

    def can_enqueue(self) -> bool:
        return self.active < self.max_concurrency


queue_manager = GenerationQueue(max_concurrency=1)
