"""CartoonizerEngine — top-level orchestrator for image and video rendering.

Owns: settings, style registry, loaded inference sessions (lazy), and the
image/video handlers. Concurrency: single-threaded per engine instance;
video frames are pipelined through a bounded queue sized by settings.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config.settings import Settings, StyleSpec
from cartoonizer_core.style_registry import StyleRegistry
from handlers.image_handler import ImageHandler
from handlers.video_handler import VideoHandler
from utils.logging_setup import get_logger

log = get_logger(__name__)


@dataclass(slots=True)
class RenderResult:
    output_path: Path
    style_id: str
    frames: int
    elapsed_s: float

    def __str__(self) -> str:  # noqa: D105
        return f"{self.style_id} :: {self.frames} frame(s) -> {self.output_path} ({self.elapsed_s:.2f}s)"


class CartoonizerEngine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.registry = StyleRegistry(settings.styles_available)
        self._image_handler = ImageHandler(settings, self.registry)
        self._video_handler = VideoHandler(settings, self.registry)

    def list_styles(self) -> list[StyleSpec]:
        return self.registry.list()

    def render(
        self,
        source: Path,
        style_id: str | None,
        output_dir: Path,
        is_video: bool,
        upscale: float,
        device: str,
    ) -> RenderResult:
        resolved_style = self.registry.resolve(style_id)
        log.info("render start source=%s style=%s video=%s", source, resolved_style.id, is_video)

        if is_video:
            return self._video_handler.process(
                source=source,
                style=resolved_style,
                output_dir=output_dir,
                upscale=upscale,
                device=device,
            )
        return self._image_handler.process(
            source=source,
            style=resolved_style,
            output_dir=output_dir,
            upscale=upscale,
            device=device,
        )