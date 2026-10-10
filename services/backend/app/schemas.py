from __future__ import annotations

from pathlib import Path


def ensure_safe_workspace(path: str | Path) -> Path:
    workspace = Path(path)
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


def sanitize_prompt(prompt: str) -> str:
    if not prompt or not prompt.strip():
        raise ValueError('Prompt cannot be empty.')
    return prompt.strip()
