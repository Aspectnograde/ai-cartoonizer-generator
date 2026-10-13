"""LRU cache of loaded ONNX style sessions keyed by (weight path, device)."""
from __future__ import annotations

from pathlib import Path

from config.settings import Settings
from services.inference.onnx_backend import OnnxStyleSession
from utils.logging_setup import get_logger

log = get_logger(__name__)


class SessionPool:
    def __init__(self, settings: Settings, max_loaded: int = 3) -> None:
        self.settings = settings
        self.max_loaded = max_loaded
        self._cache: dict[tuple[str, str], OnnxStyleSession] = {}

    def get(self, weight: str, device: str = "auto") -> OnnxStyleSession:
        key = (weight, device)
        session = self._cache.get(key)
        if session is not None:
            return session

        if len(self._cache) >= self.max_loaded:
            evicted, _ = next(iter(self._cache.items()))
            log.info("evicting session %s", evicted[0])
            self._cache.pop(evicted)

        session = OnnxStyleSession(Path(weight), device=device, fp16=self.settings.fp16)
        self._cache[key] = session
        return session

    def clear(self) -> None:
        self._cache.clear()