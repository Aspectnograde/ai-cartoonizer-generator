"""Single-image cartoonization handler."""
from __future__ import annotations

import time
from pathlib import Path

import cv2
import numpy as np

from config.settings import Settings, StyleSpec
from cartoonizer_core.engine import RenderResult
from cartoonizer_core.tiler import stitch, tile_coords
from services.inference.session_pool import SessionPool
from utils.image_io import imread_rgb, imwrite_rgb
from utils.logging_setup import get_logger

log = get_logger(__name__)


class ImageHandler:
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
        rgb = imread_rgb(source)
        log.debug("loaded image shape=%s", rgb.shape)

        session = self._pool.get(style.weight, device=device)
        tile = self.settings.tile_size
        overlap = self.settings.tile_overlap

        if max(rgb.shape[:2]) <= tile:
            out = session.run_single(rgb)
        else:
            coords = tile_coords(rgb.shape[0], rgb.shape[1], tile, overlap)
            tiles = []
            for (y0, x0, y1, x1) in coords:
                crop = rgb[y0:y1, x0:x1]
                tiles.append(((y0, x0, y1, x1), session.run_single(crop).astype(np.float32)))
            out = stitch(tiles, rgb.shape[:2], overlap)

        if upscale > 1.0:
            out = cv2.resize(
                out,
                None,
                fx=upscale,
                fy=upscale,
                interpolation=cv2.INTER_LANCZOS4,
            )

        output_dir.mkdir(parents=True, exist_ok=True)
        dest = output_dir / f"{source.stem}.{style.id}.cartoon.png"
        imwrite_rgb(dest, out)
        elapsed = time.perf_counter() - t0
        log.info("image render done -> %s (%.2fs)", dest, elapsed)
        return RenderResult(output_path=dest, style_id=style.id, frames=1, elapsed_s=elapsed)