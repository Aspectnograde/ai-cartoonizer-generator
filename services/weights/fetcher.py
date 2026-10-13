"""Fetch style weights from a manifest URL with sha256 verification."""
from __future__ import annotations

import hashlib
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from utils.errors import WeightMissingError
from utils.logging_setup import get_logger

log = get_logger(__name__)


@dataclass(slots=True)
class WeightEntry:
    style_id: str
    url: str
    sha256: str
    filename: str


def _digest(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def fetch_weight(entry: WeightEntry, dest_dir: Path, force: bool = False) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / entry.filename

    if target.exists() and not force:
        if _digest(target) == entry.sha256:
            log.info("weight already present: %s", target.name)
            return target
        log.warning("hash mismatch, re-downloading: %s", target.name)

    log.info("downloading %s -> %s", entry.url, target)
    with urllib.request.urlopen(entry.url, timeout=30) as resp, target.open("wb") as fh:
        while chunk := resp.read(1 << 20):
            fh.write(chunk)

    actual = _digest(target)
    if actual != entry.sha256:
        target.unlink(missing_ok=True)
        raise WeightMissingError(f"sha256 mismatch for {entry.filename}: {actual}")
    return target