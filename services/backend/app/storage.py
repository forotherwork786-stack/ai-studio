from __future__ import annotations

from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    model_name: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=1)
    negative_prompt: str | None = None
    width: int = Field(default=1024, ge=256, le=4096)
    height: int = Field(default=1024, ge=256, le=4096)
    steps: int = Field(default=28, ge=1, le=100)
    guidance_scale: float = Field(default=7.5, ge=1.0, le=30.0)
    seed: int | None = None
    task_type: str = Field(default='image')


class JobStatus(BaseModel):
    task_id: str
    status: str
    progress: float | None = None
    output_path: str | None = None
    error: str | None = None
