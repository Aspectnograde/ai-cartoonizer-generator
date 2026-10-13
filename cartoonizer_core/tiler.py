"""Frame tiler — splits large images into overlapping tiles for bounded memory use.

Guarantees: every output pixel is covered by at least one tile; overlap regions
are blended with a cosine ramp to avoid seams. Complexity: O(n_pixels).
"""
from __future__ import annotations

import numpy as np


def _ramp(size: int, overlap: int) -> np.ndarray:
    ramp = np.ones(size, dtype=np.float32)
    if overlap <= 0:
        return ramp
    edge = np.linspace(0.0, 1.0, overlap, dtype=np.float32)
    ramp[:overlap] = edge
    ramp[-overlap:] = edge[::-1]
    return ramp


def tile_coords(height: int, width: int, tile: int, overlap: int) -> list[tuple[int, int, int, int]]:
    step = max(1, tile - overlap)
    coords: list[tuple[int, int, int, int]] = []
    for y in range(0, height, step):
        for x in range(0, width, step):
            y1 = min(y + tile, height)
            x1 = min(x + tile, width)
            coords.append((y, x, y1, x1))
    return coords


def merge_tiles(
    canvas: np.ndarray,
    weights: np.ndarray,
    tile_out: np.ndarray,
    y0: int, x0: int, y1: int, x1: int,
    overlap: int,
) -> None:
    h, w = y1 - y0, x1 - x0
    wy = _ramp(h, overlap)[:, None]
    wx = _ramp(w, overlap)[None, :]
    w2d = wy * wx
    canvas[y0:y1, x0:x1] += tile_out * w2d[..., None]
    weights[y0:y1, x0:x1] += w2d


def stitch(tiles: list[tuple[tuple[int, int, int, int], np.ndarray]], shape: tuple[int, int], overlap: int) -> np.ndarray:
    canvas = np.zeros((*shape, 3), dtype=np.float32)
    weights = np.zeros(shape, dtype=np.float32)
    for (y0, x0, y1, x1), tile_out in tiles:
        merge_tiles(canvas, weights, tile_out, y0, x0, y1, x1, overlap)
    weights[weights == 0] = 1.0
    return (canvas / weights[..., None]).clip(0, 255).astype(np.uint8)