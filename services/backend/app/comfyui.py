from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from typing import Any, Dict, List

try:
    import psutil
except Exception:  # pragma: no cover - optional dependency for small environments
    psutil = None


@dataclass
class HardwareSummary:
    platform: str
    cpu_model: str
    cpu_cores: int
    ram_total_gb: float
    ram_available_gb: float
    gpu_name: str
    gpu_vram_gb: float | None
    storage_total_gb: float
    storage_free_gb: float
    resource_profile: str
    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'platform': self.platform,
            'cpu_model': self.cpu_model,
            'cpu_cores': self.cpu_cores,
            'ram_total_gb': round(self.ram_total_gb, 2),
            'ram_available_gb': round(self.ram_available_gb, 2),
            'gpu_name': self.gpu_name,
            'gpu_vram_gb': self.gpu_vram_gb,
            'storage_total_gb': round(self.storage_total_gb, 2),
            'storage_free_gb': round(self.storage_free_gb, 2),
            'resource_profile': self.resource_profile,
            'warnings': self.warnings,
        }


def detect_cpu_model() -> str:
    system = platform.system()
    if system == 'Windows':
        return platform.processor() or 'Unknown x86 CPU'
    if system == 'Darwin':
        return platform.processor() or 'Apple Silicon / Unknown'
    return platform.processor() or 'Unknown Linux CPU'


def detect_cpu_cores() -> int:
    if psutil is not None:
        try:
            return psutil.cpu_count(logical=True) or os.cpu_count() or 1
        except Exception:
            pass
    return os.cpu_count() or 1


def detect_ram() -> tuple[float, float]:
    if psutil is not None:
        try:
            mem = psutil.virtual_memory()
            total_gb = mem.total / (1024 ** 3)
            available_gb = mem.available / (1024 ** 3)
            return round(total_gb, 2), round(available_gb, 2)
        except Exception:
            pass
    return 8.0, 4.0


def detect_gpu() -> tuple[str, float | None]:
    candidates = [
        os.getenv('GPU_NAME'),
        os.getenv('CUDA_VISIBLE_DEVICES'),
        'NVIDIA GPU',
        'Apple Metal GPU',
        'Integrated GPU',
        'Unknown GPU',
    ]
    name = next((value for value in candidates if value), 'Unknown GPU')
    return name, 8.0 if 'NVIDIA' in name or 'Metal' in name else None


def detect_storage() -> tuple[float, float]:
    total = 250.0
    free = 120.0
    if psutil is not None:
        try:
            usage = psutil.disk_usage('/')
            total = usage.total / (1024 ** 3)
            free = usage.free / (1024 ** 3)
        except Exception:
            pass
    return round(total, 2), round(free, 2)


def choose_resource_profile(total_ram_gb: float) -> str:
    if total_ram_gb < 8:
        return 'Low Resource Mode'
    if total_ram_gb < 16:
        return 'Balanced Mode'
    if total_ram_gb < 32:
        return 'Balanced Mode'
    return 'Quality Mode'


def build_hardware_summary() -> HardwareSummary:
    cpu_model = detect_cpu_model()
    total_cores = detect_cpu_cores()
    total_ram, available_ram = detect_ram()
    gpu_name, gpu_vram = detect_gpu()
    total_storage, free_storage = detect_storage()
    profile = choose_resource_profile(total_ram)
    warnings: List[str] = []

    if total_ram < 8:
        warnings.append('System RAM is below 8 GB; prefer smaller image sizes and lower-step generations.')
    if total_storage < 50:
        warnings.append('Storage is limited. Downloaded models and batches should be kept small.')
    if gpu_vram is None:
        warnings.append('GPU VRAM is not detected. CPU or low-memory workflows should be preferred.')

    return HardwareSummary(
        platform=platform.platform(),
        cpu_model=cpu_model,
        cpu_cores=total_cores,
        ram_total_gb=total_ram,
        ram_available_gb=available_ram,
        gpu_name=gpu_name,
        gpu_vram_gb=gpu_vram,
        storage_total_gb=total_storage,
        storage_free_gb=free_storage,
        resource_profile=profile,
        warnings=warnings,
    )


def build_generation_plan(model_name: str, ram_total_gb: float, gpu_vram_gb: float | None) -> Dict[str, Any]:
    if not model_name or not model_name.strip():
        raise ValueError('Model name is required.')

    target = {
        'model': model_name,
        'recommended_mode': 'Low Resource Mode' if ram_total_gb < 16 else 'Balanced Mode',
        'allow_gpu': gpu_vram_gb is not None and gpu_vram_gb >= 4,
        'max_resolution': '512x512' if ram_total_gb < 16 else '1024x1024',
        'notes': [],
    }

    if gpu_vram_gb is None:
        target['notes'].append('No reliable VRAM value detected. Prefer CPU-safe workflows and smaller resolutions.')
    if ram_total_gb < 8:
        target['notes'].append('This system is below the preferred minimum for large AI workflows.')
    if ram_total_gb >= 16 and (gpu_vram_gb is None or gpu_vram_gb >= 4):
        target['notes'].append('Sufficient memory detected for standard local image generation. Keep batch sizes moderate.')

    return target
