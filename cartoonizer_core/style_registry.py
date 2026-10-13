"""Style registry — resolves style ids to weight specs and validates artifacts."""
from __future__ import annotations

from pathlib import Path

from config.settings import StyleSpec
from utils.errors import StyleNotFoundError, WeightMissingError


class StyleRegistry:
    def __init__(self, styles: list[StyleSpec]) -> None:
        self._styles: dict[str, StyleSpec] = {s.id: s for s in styles}

    def list(self) -> list[StyleSpec]:
        return list(self._styles.values())

    def resolve(self, style_id: str | None) -> StyleSpec:
        if style_id is None:
            if not self._styles:
                raise StyleNotFoundError("<empty registry>")
            return next(iter(self._styles.values()))

        spec = self._styles.get(style_id)
        if spec is None:
            raise StyleNotFoundError(style_id)

        weight = Path(spec.weight)
        if not weight.exists():
            raise WeightMissingError(f"{style_id} -> {weight} (run tools/fetch_weights.py)")
        return spec