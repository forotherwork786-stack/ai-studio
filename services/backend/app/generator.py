from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from PIL import Image
except ImportError:
    Image = None

logger = logging.getLogger(__name__)


class LocalImageGenerator:
    """Handles local image generation with support for multiple backends and resource profiles."""

    def __init__(self, output_dir: str | Path = None):
        self.output_dir = Path(output_dir) or Path.home() / '.ai-studio' / 'outputs'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.is_running = False

    def validate_request(
        self,
        prompt: str,
        negative_prompt: str | None = None,
        width: int = 512,
        height: int = 512,
        steps: int = 20,
        guidance_scale: float = 7.5,
        seed: int | None = None,
    ) -> tuple[bool, str | None]:
        """Validate generation parameters against hardware and model capabilities."""
        if not prompt or not prompt.strip():
            return False, 'Prompt cannot be empty.'

        if width < 256 or width > 2048 or height < 256 or height > 2048:
            return False, 'Width and height must be between 256 and 2048.'

        if (width * height) > (1024 * 1024) and not self._has_sufficient_vram():
            return False, 'Resolution too high for available VRAM. Try 512x512 or lower.'

        if steps < 1 or steps > 150:
            return False, 'Steps must be between 1 and 150.'

        if guidance_scale < 1.0 or guidance_scale > 30.0:
            return False, 'Guidance scale must be between 1.0 and 30.0.'

        return True, None

    def _has_sufficient_vram(self) -> bool:
        """Check if system has sufficient VRAM for higher resolutions."""
        try:
            import psutil
            mem = psutil.virtual_memory()
            available_gb = mem.available / (1024 ** 3)
            return available_gb >= 4.0
        except Exception:
            return False

    def build_generation_request(
        self,
        task_id: str,
        model_name: str,
        prompt: str,
        negative_prompt: str | None = None,
        width: int = 512,
        height: int = 512,
        steps: int = 20,
        guidance_scale: float = 7.5,
        seed: int | None = None,
        resource_profile: str = 'Balanced Mode',
    ) -> Dict[str, Any]:
        """Build a generation request object with resource-aware defaults."""
        valid, error = self.validate_request(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            guidance_scale=guidance_scale,
            seed=seed,
        )
        if not valid:
            return {
                'valid': False,
                'error': error,
                'task_id': task_id,
            }

        adjusted_steps = steps
        adjusted_resolution = (width, height)

        if resource_profile == 'Low Resource Mode':
            adjusted_steps = min(steps, 15)
            if width > 768 or height > 768:
                adjusted_resolution = (512, 512)
        elif resource_profile == 'Balanced Mode':
            adjusted_steps = min(steps, 28)
        elif resource_profile == 'Quality Mode':
            adjusted_steps = min(steps, 50)

        output_filename = f'{task_id}_output.png'
        output_path = self.output_dir / output_filename

        return {
            'valid': True,
            'task_id': task_id,
            'model_name': model_name,
            'prompt': prompt.strip(),
            'negative_prompt': negative_prompt.strip() if negative_prompt else None,
            'width': adjusted_resolution[0],
            'height': adjusted_resolution[1],
            'steps': adjusted_steps,
            'guidance_scale': guidance_scale,
            'seed': seed,
            'resource_profile': resource_profile,
            'output_path': str(output_path),
            'notes': [
                f'Using {resource_profile} settings.',
                f'Adjusted resolution: {adjusted_resolution[0]}x{adjusted_resolution[1]}',
                f'Adjusted steps: {adjusted_steps}',
            ] if (adjusted_steps != steps or adjusted_resolution != (width, height)) else [],
        }

    async def generate_placeholder(
        self,
        task_id: str,
        width: int = 512,
        height: int = 512,
        output_path: str | None = None,
    ) -> Dict[str, Any]:
        """Generate a placeholder image for testing (when model/engine is not available).
        
        This is ONLY for testing and development. In production, the actual model must generate output.
        """
        if not Image:
            return {
                'status': 'failed',
                'error': 'PIL/Pillow is not installed. Cannot generate placeholder. Install a real model or Pillow for testing.',
                'task_id': task_id,
            }

        try:
            path = Path(output_path) or self.output_dir / f'{task_id}_output.png'
            path.parent.mkdir(parents=True, exist_ok=True)

            img = Image.new('RGB', (width, height), color=(73, 109, 137))
            img.save(str(path))

            return {
                'status': 'completed',
                'task_id': task_id,
                'output_path': str(path),
                'placeholder': True,
                'note': 'Placeholder image generated for testing. Install a real model for actual AI generation.',
            }
        except Exception as exc:
            return {
                'status': 'failed',
                'error': str(exc),
                'task_id': task_id,
            }

    def get_generation_defaults(self, resource_profile: str = 'Balanced Mode') -> Dict[str, Any]:
        """Get sensible generation defaults for the given resource profile."""
        defaults = {
            'Low Resource Mode': {
                'width': 512,
                'height': 512,
                'steps': 15,
                'guidance_scale': 7.0,
            },
            'Balanced Mode': {
                'width': 768,
                'height': 768,
                'steps': 28,
                'guidance_scale': 7.5,
            },
            'Quality Mode': {
                'width': 1024,
                'height': 1024,
                'steps': 40,
                'guidance_scale': 8.0,
            },
        }
        return defaults.get(resource_profile, defaults['Balanced Mode'])
