from __future__ import annotations

import logging
from typing import Any, Dict

from .comfyui_integration import ComfyUIIntegration
from .hardware import build_hardware_summary

logger = logging.getLogger(__name__)


class GenerationCoordinator:
    """Coordinates generation requests across hardware checks, model availability, and engine selection."""

    def __init__(self):
        self.comfyui = ComfyUIIntegration()
        self.hardware = build_hardware_summary()

    def can_generate_image(
        self,
        model_name: str = 'sd-v1-5.ckpt',
        width: int = 512,
        height: int = 512,
        steps: int = 20,
    ) -> Dict[str, Any]:
        """Comprehensive check before attempting image generation."""
        checks = {
            'hardware_ok': True,
            'comfyui_ok': False,
            'model_available': False,
            'can_proceed': False,
            'warnings': [],
            'errors': [],
            'recommendations': [],
        }

        if self.hardware.ram_total_gb < 8:
            checks['warnings'].append(f'System RAM is {self.hardware.ram_total_gb}GB. Minimum recommended is 8GB.')
            checks['recommendations'].append('Use Low Resource Mode with lower resolution (512x512 or less).')

        if self.hardware.gpu_vram_gb is None or self.hardware.gpu_vram_gb < 2:
            checks['warnings'].append('GPU or VRAM not detected. Using CPU mode (slower).')
            checks['recommendations'].append('Consider using a GPU-accelerated device for faster generation.')
        elif self.hardware.gpu_vram_gb < 4:
            checks['warnings'].append(f'Limited VRAM ({self.hardware.gpu_vram_gb}GB). Use smaller models and resolutions.')

        if (width * height) > 1048576:  # 1024x1024
            if self.hardware.ram_total_gb < 16:
                checks['errors'].append('Resolution too high for available system RAM.')
                checks['hardware_ok'] = False
            if self.hardware.gpu_vram_gb and self.hardware.gpu_vram_gb < 4:
                checks['errors'].append('Resolution too high for available VRAM.')
                checks['hardware_ok'] = False

        if not self.comfyui.is_available:
            checks['errors'].append('ComfyUI not found. Install ComfyUI to enable local image generation.')
            checks['comfyui_ok'] = False
        else:
            checks['comfyui_ok'] = True

        if checks['comfyui_ok']:
            model_check = self.comfyui.validate_model_available(model_name)
            if not model_check['available']:
                checks['warnings'].append(f'Model {model_name} not found.')
                checks['recommendations'].append(f'Download {model_name} to the ComfyUI models directory.')
            else:
                checks['model_available'] = True

        checks['can_proceed'] = (
            checks['hardware_ok']
            and checks['comfyui_ok']
            and checks['model_available']
        )

        return checks

    def get_optimized_settings(
        self,
        resource_profile: str = 'Balanced Mode',
    ) -> Dict[str, Any]:
        """Return optimized generation settings based on hardware and profile."""
        profiles = {
            'Low Resource Mode': {
                'width': 512,
                'height': 512,
                'steps': 15,
                'guidance_scale': 7.0,
                'batch_size': 1,
                'sampler': 'euler',
            },
            'Balanced Mode': {
                'width': 768,
                'height': 768,
                'steps': 28,
                'guidance_scale': 7.5,
                'batch_size': 1,
                'sampler': 'euler',
            },
            'Quality Mode': {
                'width': 1024,
                'height': 1024,
                'steps': 40,
                'guidance_scale': 8.0,
                'batch_size': 1,
                'sampler': 'dpm++ 2m karras',
            },
        }
        return profiles.get(resource_profile, profiles['Balanced Mode'])
