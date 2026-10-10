from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EngineConfig:
    name: str
    type: str
    working: bool = False
    notes: str = 'Engine ready for local configuration.'


def get_available_engines() -> list[EngineConfig]:
    return [
        EngineConfig(name='ComfyUI', type='image', working=True, notes='Recommended local workflow for SD 1.5 and related models.'),
        EngineConfig(name='Diffusers', type='image', working=False, notes='Planned for advanced model pipelines.'),
        EngineConfig(name='Video Engine Adapter', type='video', working=False, notes='Video model integration in roadmap.'),
    ]
