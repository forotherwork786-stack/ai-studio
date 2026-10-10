from __future__ import annotations

from dataclasses import dataclass, field
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

    def to_dict(self) -> dict:
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
