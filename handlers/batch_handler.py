"""Batch handler — walk a directory and cartoonize every image/video."""
from __future__ import annotations

from pathlib import Path

from config.settings import Settings
from cartoonizer_core.engine import CartoonizerEngine, RenderResult
from utils.logging_setup import get_logger

log = get_logger(__name__)

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".avi", ".webm"}


def process_directory(
    engine: CartoonizerEngine,
    settings: Settings,
    root: Path,
    style_id: str | None,
    output_dir: Path,
) -> list[RenderResult]:
    results: list[RenderResult] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in IMAGE_EXT:
            results.append(engine.render(path, style_id, output_dir, False, 1.0, "auto"))
        elif suffix in VIDEO_EXT:
            results.append(engine.render(path, style_id, output_dir, True, 1.0, "auto"))
        else:
            log.debug("skip unsupported: %s", path)
    return results