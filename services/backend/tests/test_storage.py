from __future__ import annotations

from typing import Any, List

from fastapi import FastAPI, HTTPException

from .comfyui import ComfyUIAdapter
from .hardware import build_generation_plan, build_hardware_summary
from .jobs import GenerationJob
from .storage import initialize_database, list_generation_history, list_projects, log_generation, save_project

app = FastAPI(title='AI Studio Backend', version='0.1.0')

comfyui = ComfyUIAdapter()


@app.on_event('startup')
def startup_event() -> None:
    initialize_database()


@app.get('/health')
def health() -> dict[str, Any]:
    return {'status': 'ok', 'service': 'ai-studio-backend'}


@app.get('/hardware/summary')
def hardware_summary() -> dict[str, Any]:
    return build_hardware_summary().to_dict()


@app.get('/models')
def list_models() -> List[dict[str, Any]]:
    return [
        {
            'id': 'sd15',
            'name': 'Stable Diffusion 1.5',
            'type': 'image',
            'status': 'ready_for_install',
            'license': 'CreativeML Open RAIL-M',
            'notes': 'Small local image model, suitable for low-resource workflows.',
        },
        {
            'id': 'wan21',
            'name': 'Wan 2.1 T2V 1.3B',
            'type': 'video',
            'status': 'planned',
            'license': 'Open-weight license check required',
            'notes': 'Video path remains hardware-dependent and should be evaluated on the target machine.',
        },
    ]


@app.get('/comfyui/status')
def comfyui_status() -> dict[str, Any]:
    return comfyui.get_status()


@app.post('/generation/plan')
def generation_plan(payload: dict[str, Any]) -> dict[str, Any]:
    model_name = str(payload.get('model_name', '')).strip()
    ram_total = float(payload.get('ram_total_gb', 8.0))
    gpu_vram = payload.get('gpu_vram_gb')
    if gpu_vram is not None:
        gpu_vram = float(gpu_vram)
    return build_generation_plan(model_name, ram_total, gpu_vram)


@app.post('/projects')
def create_project(payload: dict[str, Any]) -> dict[str, Any]:
    name = str(payload.get('name', '')).strip()
    path = str(payload.get('path', '')).strip()
    description = payload.get('description')
    try:
        project_id = save_project(name, path, description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {'id': project_id, 'name': name, 'path': path, 'description': description}


@app.get('/projects')
def read_projects() -> list[dict[str, Any]]:
    return list_projects()


@app.get('/jobs')
def read_jobs() -> list[dict[str, Any]]:
    return list_generation_history()


@app.post('/generate')
def create_generation_job(payload: dict[str, Any]) -> dict[str, Any]:
    model_name = str(payload.get('model_name', 'Stable Diffusion 1.5')).strip()
    prompt = str(payload.get('prompt', '')).strip()
    if not prompt:
        raise HTTPException(status_code=400, detail='Prompt cannot be empty.')

    job = GenerationJob.from_request(payload)
    plan = build_generation_plan(model_name, float(payload.get('ram_total_gb', 8.0)), payload.get('gpu_vram_gb'))
    job.status = 'Preparing'
    job.progress = 0.1
    job.output_path = payload.get('output_path')

    log_generation(job.task_id, job.task_type, job.model_name, job.prompt, job.status, job.output_path)

    return {
        'job': job.to_dict(),
        'generation_plan': plan,
        'comfyui': comfyui.get_status(),
    }


@app.get('/history')
def generation_history() -> list[dict[str, Any]]:
    return list_generation_history()


@app.post('/comfyui/validate-model')
def validate_model(payload: dict[str, Any]) -> dict[str, Any]:
    model_name = str(payload.get('model_name', '')).strip()
    try:
        return comfyui.validate_model(model_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
