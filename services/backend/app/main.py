from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModelRecord:
    id: str
    name: str
    kind: str
    version: str
    file_size_mb: float | None = None
    source: str = 'Local import'
    license: str = 'Varies'
    status: str = 'available'
    path: str | None = None
    installed: bool = False
    supported_tasks: list[str] = field(default_factory=lambda: ['image'])
    notes: str = ''

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'kind': self.kind,
            'version': self.version,
            'file_size_mb': self.file_size_mb,
            'source': self.source,
            'license': self.license,
            'status': self.status,
            'path': self.path,
            'installed': self.installed,
            'supported_tasks': self.supported_tasks,
            'notes': self.notes,
        }


class ModelManager:
    """Registry for local models and installation compatibility checks."""

    def __init__(self, storage_dir: str | None = None):
        self.storage_dir = storage_dir or '.models'
        self._known_models = {
            'sd15': ModelRecord(
                id='sd15',
                name='Stable Diffusion 1.5',
                kind='image',
                version='1.5',
                file_size_mb=4300,
                source='Official local model source',
                license='CreativeML Open RAIL-M',
                status='available',
                installed=False,
                supported_tasks=['image', 'image-to-image', 'inpaint'],
                notes='Recommended first model for a lightweight local workflow.',
            ),
            'sdxl': ModelRecord(
                id='sdxl',
                name='SDXL',
                kind='image',
                version='1.0',
                file_size_mb=7000,
                source='Official local model source or trusted mirror',
                license='Open-weight / licensing check required',
                status='available',
                installed=False,
                supported_tasks=['image', 'image-to-image'],
                notes='Larger, higher-quality model; requires more memory.',
            ),
            'wan21': ModelRecord(
                id='wan21',
                name='Wan 2.1 T2V 1.3B',
                kind='video',
                version='1.3B',
                file_size_mb=2600,
                source='Open-weight model source',
                license='Open-weight license review required',
                status='available',
                installed=False,
                supported_tasks=['text-to-video', 'image-to-video'],
                notes='Requires more robust hardware and should be checked before use.',
            ),
        }

    def list_known_models(self) -> list[dict[str, Any]]:
        return [record.to_dict() for record in self._known_models.values()]

    def get_model(self, model_id: str) -> ModelRecord | None:
        return self._known_models.get(model_id)

    def import_model(self, source_path: str, model_id: str | None = None) -> dict[str, Any]:
        path = source_path.strip()
        if not path:
            raise ValueError('Source path is required.')

        model = self.get_model(model_id or 'custom') or ModelRecord(
            id=model_id or 'custom',
            name=model_id or 'Custom model',
            kind='image',
            version='custom',
            source='User import',
            license='User responsibility',
            status='imported',
            installed=True,
            path=path,
            supported_tasks=['image'],
            notes='Manual import detected. Compatibility must be checked by the user.',
        )
        model.installed = True
        model.path = path
        model.status = 'imported'
        self._known_models[model.id] = model
        return model.to_dict()

    def get_recommendations(self, ram_total_gb: float, gpu_vram_gb: float | None) -> list[dict[str, Any]]:
        recommendations: list[dict[str, Any]] = []
        for record in self._known_models.values():
            if record.id == 'sd15' and ram_total_gb >= 8:
                recommendations.append({'id': record.id, 'reason': 'Best entry-level local image model.'})
            elif record.id == 'sdxl' and ram_total_gb >= 16 and (gpu_vram_gb is None or gpu_vram_gb >= 8):
                recommendations.append({'id': record.id, 'reason': 'Good quality model for stronger GPUs.'})
            elif record.id == 'wan21' and ram_total_gb >= 16 and (gpu_vram_gb is None or gpu_vram_gb >= 6):
                recommendations.append({'id': record.id, 'reason': 'Video generation candidate for more capable systems.'})
        return recommendations

    def check_compatibility(self, model_id: str, ram_total_gb: float, gpu_vram_gb: float | None) -> dict[str, Any]:
        model = self.get_model(model_id)
        if model is None:
            raise ValueError(f'Unknown model id: {model_id}')

        if model.id == 'sd15':
            min_ram = 8.0
            min_vram = 2.0
        elif model.id == 'sdxl':
            min_ram = 16.0
            min_vram = 6.0
        elif model.id == 'wan21':
            min_ram = 16.0
            min_vram = 6.0
        else:
            min_ram = 8.0
            min_vram = 2.0

        compatible = ram_total_gb >= min_ram and (gpu_vram_gb is None or gpu_vram_gb >= min_vram)
        return {
            'model_id': model_id,
            'compatible': compatible,
            'required_ram_gb': min_ram,
            'required_vram_gb': min_vram,
            'message': 'Model is compatible with this system.' if compatible else 'Model requires more RAM or VRAM than your current hardware provides.',
        }


model_manager = ModelManager()
