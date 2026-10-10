from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException

from .coordinator import GenerationCoordinator
from .comfyui_integration import ComfyUIIntegration
from .generator import LocalImageGenerator
from .hardware import build_generation_plan, build_hardware_summary
from .jobs import GenerationJob
from .model_manager import model_manager
from .queue import GenerationQueue, QueueEntry, queue_manager
from .storage import initialize_database, list_generation_history, list_projects, log_generation, save_project

app = FastAPI(
    title='AI Studio Backend',
    version='0.1.0',
    description='Local AI image and video generation studio backend.',
)

comfyui = ComfyUIIntegration()
generator = LocalImageGenerator()
coordinator = GenerationCoordinator()


@app.on_event('startup')
def startup_event() -> None:
    initialize_database()


@app.get('/health')
def health() -> dict[str, Any]:
    return {'status': 'ok', 'service': 'ai-studio-backend', 'version': '0.1.0'}


@app.get('/hardware/summary')
def hardware_summary() -> dict[str, Any]:
    return build_hardware_summary().to_dict()


@app.get('/models')
def list_models() -> list[dict[str, Any]]:
    return model_manager.list_known_models()


@app.get('/models/recommendations')
def model_recommendations(ram_total_gb: float = 8.0, gpu_vram_gb: float | None = None) -> list[dict[str, Any]]:
    return model_manager.get_recommendations(ram_total_gb, gpu_vram_gb)


@app.post('/models/import')
def import_model(payload: dict[str, Any]) -> dict[str, Any]:
    source_path = str(payload.get('source_path', '')).strip()
    model_id = payload.get('model_id')
    if not source_path:
        raise HTTPException(status_code=400, detail='source_path is required.')
    return model_manager.import_model(source_path, model_id)


@app.get('/models/{model_id}/compatibility')
def model_compatibility(model_id: str, ram_total_gb: float = 8.0, gpu_vram_gb: float | None = None) -> dict[str, Any]:
    return model_manager.check_compatibility(model_id, ram_total_gb, gpu_vram_gb)


@app.get('/comfyui/status')
def comfyui_status() -> dict[str, Any]:
    return comfyui.get_status()


@app.get('/generation/can-proceed')
def generation_can_proceed(model_name: str = 'sd-v1-5.ckpt', width: int = 512, height: int = 512) -> dict[str, Any]:
    return coordinator.can_generate_image(model_name, width, height)


@app.get('/generation/defaults')
def generation_defaults(profile: str = 'Balanced Mode') -> dict[str, Any]:
    return coordinator.get_optimized_settings(profile)


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


@app.get('/queue')
def get_queue() -> list[dict[str, Any]]:
    return queue_manager.list()


@app.get('/queue/{task_id}')
def get_queue_item(task_id: str) -> dict[str, Any]:
    job = queue_manager.get(task_id)
    if job is None:
        raise HTTPException(status_code=404, detail='Task not found.')
    return job.to_dict()


@app.post('/queue/{task_id}/cancel')
def cancel_queue_item(task_id: str) -> dict[str, Any]:
    try:
        job = queue_manager.cancel(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return job.to_dict()


@app.post('/queue/{task_id}/retry')
def retry_queue_item(task_id: str) -> dict[str, Any]:
    try:
        job = queue_manager.retry(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return job.to_dict()


@app.post('/generate/validate')
def validate_generation_request(payload: dict[str, Any]) -> dict[str, Any]:
    request = generator.build_generation_request(
        task_id=str(payload.get('task_id', 'test-task')),
        model_name=str(payload.get('model_name', 'Stable Diffusion 1.5')),
        prompt=str(payload.get('prompt', '')),
        negative_prompt=payload.get('negative_prompt'),
        width=int(payload.get('width', 512)),
        height=int(payload.get('height', 512)),
        steps=int(payload.get('steps', 20)),
        guidance_scale=float(payload.get('guidance_scale', 7.5)),
        seed=payload.get('seed'),
        resource_profile=str(payload.get('resource_profile', 'Balanced Mode')),
    )
    return request


@app.post('/generate')
def create_generation_job(payload: dict[str, Any]) -> dict[str, Any]:
    model_name = str(payload.get('model_name', 'Stable Diffusion 1.5')).strip()
    prompt = str(payload.get('prompt', '')).strip()
    if not prompt:
        raise HTTPException(status_code=400, detail='Prompt cannot be empty.')

    checks = coordinator.can_generate_image(model_name, int(payload.get('width', 512)), int(payload.get('height', 512)))
    job = GenerationJob.from_request(payload)
    job.status = 'Preparing'
    job.progress = 0.05

    if not checks['can_proceed']:
        job.status = 'Failed'
        job.error = ' '.join(checks['errors']) or 'Generation not available on this system.'
        log_generation(job.task_id, job.task_type, job.model_name, job.prompt, job.status)
        queue_manager.add(QueueEntry(
            task_id=job.task_id,
            task_type=job.task_type,
            model_name=job.model_name,
            prompt=job.prompt,
            status=job.status,
            progress=job.progress,
            output_path=job.output_path,
            error=job.error,
            created_at=datetime.utcnow().isoformat(),
        ))
        return {'job': job.to_dict(), 'checks': checks, 'status': 'failed'}

    request = generator.build_generation_request(
        task_id=job.task_id,
        model_name=model_name,
        prompt=prompt,
        negative_prompt=payload.get('negative_prompt'),
        width=int(payload.get('width', 512)),
        height=int(payload.get('height', 512)),
        steps=int(payload.get('steps', 20)),
        guidance_scale=float(payload.get('guidance_scale', 7.5)),
        seed=payload.get('seed'),
        resource_profile=str(payload.get('resource_profile', 'Balanced Mode')),
    )
    if not request['valid']:
        job.status = 'Failed'
        job.error = request['error']
        log_generation(job.task_id, job.task_type, job.model_name, job.prompt, job.status)
        return {'job': job.to_dict(), 'request': request, 'status': 'failed'}

    queue_entry = QueueEntry(
        task_id=job.task_id,
        task_type=job.task_type,
        model_name=job.model_name,
        prompt=job.prompt,
        status='Waiting',
        progress=0.0,
        output_path=request['output_path'],
        created_at=datetime.utcnow().isoformat(),
    )
    queue_manager.add(queue_entry)
    job.output_path = request['output_path']
    log_generation(job.task_id, job.task_type, job.model_name, job.prompt, queue_entry.status, job.output_path)

    return {
        'job': job.to_dict(),
        'request': request,
        'checks': checks,
        'status': 'queued',
        'message': 'Generation job queued. Awaiting processing in the local queue manager.',
    }


@app.get('/history')
def generation_history() -> list[dict[str, Any]]:
    return list_generation_history()


@app.post('/comfyui/validate-model')
def validate_model(payload: dict[str, Any]) -> dict[str, Any]:
    model_name = str(payload.get('model_name', '')).strip()
    try:
        return comfyui.validate_model_available(model_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post('/generation/plan')
def generation_plan(payload: dict[str, Any]) -> dict[str, Any]:
    model_name = str(payload.get('model_name', '')).strip()
    ram_total = float(payload.get('ram_total_gb', 8.0))
    gpu_vram = payload.get('gpu_vram_gb')
    if gpu_vram is not None:
        gpu_vram = float(gpu_vram)
    return build_generation_plan(model_name, ram_total, gpu_vram)
