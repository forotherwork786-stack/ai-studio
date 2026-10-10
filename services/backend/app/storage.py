from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class GenerationJob:
    task_id: str = field(default_factory=lambda: str(uuid4()))
    task_type: str = 'image'
    model_name: str = 'Stable Diffusion 1.5'
    prompt: str = ''
    status: str = 'Waiting'
    progress: float | None = None
    output_path: str | None = None
    error: str | None = None

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
        }

    @classmethod
    def from_request(cls, payload: dict[str, Any]) -> 'GenerationJob':
        return cls(
            task_type=str(payload.get('task_type', 'image')),
            model_name=str(payload.get('model_name', 'Stable Diffusion 1.5')),
            prompt=str(payload.get('prompt', '')),
            status='Waiting',
        )
