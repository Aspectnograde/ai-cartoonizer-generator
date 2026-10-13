"""Pydantic request/response schemas for the cartoonizer API surface."""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class RenderRequest(BaseModel):
    input_path: Path
    style_id: str | None = None
    output_dir: Path = Field(default=Path("output"))
    is_video: bool = False
    upscale: float = Field(default=1.0, ge=1.0, le=4.0)
    device: str = "auto"

    @field_validator("device")
    @classmethod
    def _device_ok(cls, v: str) -> str:
        allowed = {"auto", "cpu", "cuda", "dml"}
        if v not in allowed:
            raise ValueError(f"device must be one of {sorted(allowed)}")
        return v


class RenderResponse(BaseModel):
    output_path: Path
    style_id: str
    frames: int
    elapsed_s: float