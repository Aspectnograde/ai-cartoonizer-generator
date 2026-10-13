"""Image IO helpers — RGB read/write with explicit channel ordering."""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def imread_rgb(path: Path) -> np.ndarray:
    bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if bgr is None:
        raise FileNotFoundError(f"cannot read image: {path}")
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def imwrite_rgb(path: Path, rgb: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist