import os

try:
    from fastapi import FastAPI
except ImportError as exc:
    raise RuntimeError('FastAPI required. Run: pip install -r requirements.txt') from exc

from .coordinator import GenerationCoordinator
from .comfyui_integration import ComfyUIIntegration
from .generator import LocalImageGenerator
from .hardware import build_generation_plan, build_hardware_summary
from .jobs import GenerationJob
from .storage import initialize_database, list_generation_history, list_projects, log_generation, save_project

app = FastAPI(
    title='AI Studio Backend',
    version='0.1.0',
    description='Local AI image and video generation with free, open models.',
)

comfyui = ComfyUIIntegration()
generator = LocalImageGenerator()
coordinator = GenerationCoordinator()


@app.on_event('startup')
def startup_event():
    initialize_database()


@app.get('/health')
def health():
    return {
        'status': 'ok',
        'service': 'ai-studio-backend',
        'version': '0.1.0',
    }


@app.get('/hardware/summary')
def hardware_summary():
    return build_hardware_summary().to_dict()


@app.get('/models')
def list_models():
    return [
        {
            'id': 'sd15',
            'name': 'Stable Diffusion 1.5',
            'type': 'image',
            'size_gb': 4.0,
            'status': 'ready_for_install',
            'license': 'CreativeML Open RAIL-M',
            'requirements': comfyui.get_model_requirements('sd-v1-5.ckpt'),
        },
        {
            'id': 'sdxl',
            'name': 'Stable Diffusion XL',
            'type': 'image',
            'size_gb': 7.0,
            'status': 'ready_for_install',
            'license': 'CreativeML Open RAIL-M',
            'requirements': comfyui.get_model_requirements('sd-xl.safetensors'),
        },
        {
            'id': 'wan21',
            'name': 'Wan 2.1 T2V 1.3B',
            'type': 'video',
            'size_gb': 2.5,
            'status': 'planned',
            'license': 'Open-weight',
            'notes': 'Video generation support planned for Phase 4.',
        },
    ]


@app.get('/comfyui/status')
def comfyui_status():
    return comfyui.get_status()


@app.get('/generation/can-proceed')
def generation_can_proceed(model_name: str = 'sd-v1-5.ckpt', width: int = 512, height: int = 512):
    return coordinator.can_generate_image(model_name, width, height)


@app.get('/generation/defaults')
def generation_defaults(profile: str = 'Balanced Mode'):
    return coordinator.get_optimized_settings(profile)


@app.post('/projects')
def create_project(payload: dict):
    from fastapi import HTTPException
    name = str(payload.get('name', '')).strip()
    path = str(payload.get('path', '')).strip()
    description = payload.get('description')
    try:
        project_id = save_project(name, path, description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {'id': project_id, 'name': name, 'path': path, 'description': description}


@app.get('/projects')
def read_projects():
    return list_projects()


@app.get('/jobs')
def read_jobs():
    return list_generation_history()


@app.post('/generate/validate')
def validate_generation_request(payload: dict):
    """Validate a generation request before execution."""
    request = generator.build_generation_request(
        task_id=payload.get('task_id', 'test'),
        model_name=payload.get('model_name', 'Stable Diffusion 1.5'),
        prompt=payload.get('prompt', ''),
        negative_prompt=payload.get('negative_prompt'),
        width=payload.get('width', 512),
        height=payload.get('height', 512),
        steps=payload.get('steps', 20),
        guidance_scale=payload.get('guidance_scale', 7.5),
        seed=payload.get('seed'),
        resource_profile=payload.get('resource_profile', 'Balanced Mode'),
    )
    return request


@app.post('/generate')
def create_generation_job(payload: dict):
    """Create and queue a generation job."""
    from fastapi import HTTPException
    import asyncio

    model_name = str(payload.get('model_name', 'Stable Diffusion 1.5')).strip()
    prompt = str(payload.get('prompt', '')).strip()
    if not prompt:
        raise HTTPException(status_code=400, detail='Prompt cannot be empty.')

    checks = coordinator.can_generate_image(
        model_name,
        payload.get('width', 512),
        payload.get('height', 512),
    )

    job = GenerationJob.from_request(payload)
    job.status = 'Preparing'
    job.progress = 0.05

    if not checks['can_proceed']:
        job.status = 'Failed'
        job.error = ' '.join(checks['errors']) or 'Generation not available on this system.'
        log_generation(job.task_id, job.task_type, job.model_name, job.prompt, job.status)
        return {
            'job': job.to_dict(),
            'checks': checks,
            'status': 'failed',
        }

    request = generator.build_generation_request(
        task_id=job.task_id,
        model_name=model_name,
        prompt=prompt,
        negative_prompt=payload.get('negative_prompt'),
        width=payload.get('width', 512),
        height=payload.get('height', 512),
        steps=payload.get('steps', 20),
        guidance_scale=payload.get('guidance_scale', 7.5),
        seed=payload.get('seed'),
        resource_profile=payload.get('resource_profile', 'Balanced Mode'),
    )

    if not request['valid']:
        job.status = 'Failed'
        job.error = request['error']
        log_generation(job.task_id, job.task_type, job.model_name, job.prompt, job.status)
        return {
            'job': job.to_dict(),
            'request': request,
            'status': 'failed',
        }

    job.status = 'Waiting'
    job.output_path = request['output_path']
    log_generation(job.task_id, job.task_type, job.model_name, job.prompt, job.status, job.output_path)

    return {
        'job': job.to_dict(),
        'request': request,
        'checks': checks,
        'status': 'queued',
        'message': 'Generation job queued. In production, the queue manager will process this job.',
    }


@app.get('/history')
def generation_history():
    return list_generation_history()
