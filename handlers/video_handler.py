"""Video cartoonization handler — frame-by-frame with streaming writer."""
from __future__ import annotations

import time
from pathlib import Path

import cv2
import numpy as np

from config.settings import Settings, StyleSpec
from cartoonizer_core.engine import RenderResult
from services.inference.session_pool import SessionPool
from utils.errors import VideoCodecError
from utils.logging_setup import get_logger
from utils.progress import ProgressReporter

log = get_logger(__name__)


class VideoHandler:
    def __init__(self, settings: Settings, registry) -> None:  # noqa: ANN001
        self.settings = settings
        self.registry = registry
        self._pool = SessionPool(settings)

    def process(
        self,
        source: Path,
        style: StyleSpec,
        output_dir: Path,
        upscale: float,
        device: str,
    ) -> RenderResult:
        t0 = time.perf_counter()
        cap = cv2.VideoCapture(str(source))
        if not cap.isOpened():
            raise VideoCodecError(f"cannot open video: {source}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        out_w, out_h = int(width * upscale), int(height * upscale)

        output_dir.mkdir(parents=True, exist_ok=True)
        dest = output_dir / f"{source.stem}.{style.id}.cartoon.mp4"
        fourcc = cv2.VideoWriter_fourcc(*self.settings.video_codec)
        writer = cv2.VideoWriter(str(dest), fourcc, fps, (out_w, out_h))
        if not writer.isOpened():
            raise VideoCodecError(f"cannot open writer for {dest}")

        session = self._pool.get(style.weight, device=device)
        progress = ProgressReporter(total, desc=f"cartoonize {source.name}")
        frames = 0

        try:
            while True:
                ok, frame_bgr = cap.read()
                if not ok:
                    break
                rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                out = session.run_single(rgb)
                if upscale > 1.0:
                    out = cv2.resize(out, (out_w, out_h), interpolation=cv2.INTER_LANCZOS4)
                writer.write(cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
                frames += 1
                progress.tick()
        finally:
            cap.release()
            writer.release()
            progress.close()

        elapsed = time.perf_counter() - t0
        log.info("video render done -> %s (%d frames, %.1fs)", dest, frames, elapsed)
        return RenderResult(output_path=dest, style_id=style.id, frames=frames, elapsed_s=elapsed)