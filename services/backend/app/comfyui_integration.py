from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ComfyUIIntegration:
    """Manages ComfyUI workflow generation and execution for local AI model inference."""

    def __init__(self, comfyui_path: str | None = None):
        self.comfyui_path = Path(comfyui_path) if comfyui_path else self._detect_comfyui_path()
        self.is_available = self.comfyui_path.exists() if self.comfyui_path else False

    def _detect_comfyui_path(self) -> Path | None:
        """Attempt to detect ComfyUI installation path."""
        candidates = [
            Path.home() / 'ComfyUI',
            Path.home() / 'AI' / 'ComfyUI',
            Path('/opt/ComfyUI'),
            Path('C:\\ComfyUI') if Path('C:\\').exists() else None,
        ]
        for candidate in candidates:
            if candidate and candidate.exists():
                return candidate
        return None

    def get_status(self) -> Dict[str, Any]:
        """Get current ComfyUI integration status."""
        return {
            'available': self.is_available,
            'path': str(self.comfyui_path) if self.comfyui_path else None,
            'message': 'ComfyUI is ready.' if self.is_available else 'ComfyUI not found. Local generation disabled.',
        }

    def build_sd15_workflow(
        self,
        prompt: str,
        negative_prompt: str | None = None,
        width: int = 512,
        height: int = 512,
        steps: int = 20,
        guidance_scale: float = 7.5,
        seed: int | None = -1,
    ) -> Dict[str, Any]:
        """Build a Stable Diffusion 1.5 workflow JSON for ComfyUI."""
        if not prompt:
            raise ValueError('Prompt cannot be empty.')

        workflow = {
            '1': {
                'class_type': 'CheckpointLoaderSimple',
                'inputs': {'ckpt_name': 'sd-v1-5.ckpt'},
            },
            '2': {
                'class_type': 'CLIPTextEncode',
                'inputs': {
                    'text': prompt,
                    'clip': ['1', 1],
                },
            },
            '3': {
                'class_type': 'CLIPTextEncode',
                'inputs': {
                    'text': negative_prompt or '',
                    'clip': ['1', 1],
                },
            },
            '4': {
                'class_type': 'KSampler',
                'inputs': {
                    'seed': seed if seed and seed > 0 else 42,
                    'steps': steps,
                    'cfg': guidance_scale,
                    'sampler_name': 'euler',
                    'scheduler': 'normal',
                    'denoise': 1.0,
                    'model': ['1', 0],
                    'positive': ['2', 0],
                    'negative': ['3', 0],
                    'latent_image': ['5', 0],
                },
            },
            '5': {
                'class_type': 'EmptyLatentImage',
                'inputs': {
                    'width': width,
                    'height': height,
                    'batch_size': 1,
                },
            },
            '6': {
                'class_type': 'VAEDecode',
                'inputs': {
                    'samples': ['4', 0],
                    'vae': ['1', 2],
                },
            },
            '7': {
                'class_type': 'SaveImage',
                'inputs': {
                    'images': ['6', 0],
                    'filename_prefix': 'ai-studio',
                },
            },
        }
        return workflow

    def validate_model_available(self, model_name: str = 'sd-v1-5.ckpt') -> Dict[str, Any]:
        """Check if a specific model file is available in ComfyUI."""
        if not self.is_available:
            return {
                'available': False,
                'message': 'ComfyUI not found. Cannot validate model.',
            }

        model_path = self.comfyui_path / 'models' / 'checkpoints' / model_name
        return {
            'available': model_path.exists(),
            'path': str(model_path) if model_path.exists() else None,
            'message': f'Model {model_name} is available.' if model_path.exists() else f'Model {model_name} not found in {model_path.parent}',
        }

    def get_model_requirements(self, model_name: str = 'sd-v1-5.ckpt') -> Dict[str, Any]:
        """Return estimated hardware requirements for a model."""
        requirements = {
            'sd-v1-5.ckpt': {
                'vram_min_gb': 2.0,
                'vram_recommended_gb': 4.0,
                'ram_min_gb': 8.0,
                'ram_recommended_gb': 16.0,
                'storage_required_gb': 4.0,
                'notes': 'Stable Diffusion 1.5 runs well on most hardware with 8GB+ RAM and 2GB+ VRAM.',
            },
            'sd-xl.safetensors': {
                'vram_min_gb': 6.0,
                'vram_recommended_gb': 12.0,
                'ram_min_gb': 16.0,
                'ram_recommended_gb': 32.0,
                'storage_required_gb': 7.0,
                'notes': 'SDXL requires more memory and is suitable for higher-end systems.',
            },
        }
        return requirements.get(model_name, {
            'vram_min_gb': 2.0,
            'vram_recommended_gb': 4.0,
            'ram_min_gb': 8.0,
            'ram_recommended_gb': 16.0,
            'storage_required_gb': 4.0,
            'notes': 'Model requirements unknown. Check the specific model documentation.',
        })
