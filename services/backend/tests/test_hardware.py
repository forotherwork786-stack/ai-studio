from __future__ import annotations

from typing import List

try:
    from fastapi import FastAPI
except Exception as exc:  # pragma: no cover - dependency is installed in the project environment
    raise RuntimeError('FastAPI is required. Install dependencies from services/backend/requirements.txt') from exc

from .hardware import build_generation_plan, build_hardware_summary

app = FastAPI(title='AI Studio Backend', version='0.1.0')


@app.get('/health')
def health() -> dict:
    return {'status': 'ok', 'service': 'ai-studio-backend'}


@app.get('/hardware/summary')
def hardware_summary() -> dict:
    return build_hardware_summary().to_dict()


@app.get('/models')
def list_models() -> List[dict]:
    return [
        {
            'id': 'sd15',
            'name': 'Stable Diffusion 1.5',
            'type': 'image',
            'status': 'ready_for_install',
            'license': 'CreativeML Open RAIL-M',
        },
        {
            'id': 'wan21',
            'name': 'Wan 2.1 T2V 1.3B',
            'type': 'video',
            'status': 'planned',
            'license': 'Open-weight license check required',
        },
    ]


@app.post('/generation/plan')
def generation_plan(payload: dict) -> dict:
    model_name = str(payload.get('model_name', '')).strip()
    ram_total = float(payload.get('ram_total_gb', 8.0))
    gpu_vram = payload.get('gpu_vram_gb')
    if gpu_vram is not None:
        gpu_vram = float(gpu_vram)
    return build_generation_plan(model_name, ram_total, gpu_vram)
