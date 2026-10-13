"""Logging configuration loader (YAML) + get_logger helper."""
from __future__ import annotations

import logging
import logging.config
from pathlib import Path

import yaml

_CONFIGURED = False


def configure_logging(config_path: Path | str = "config/logging.yaml") -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    path = Path(config_path)
    if path.exists():
        Path("logs").mkdir(exist_ok=True)
        with path.open("r", encoding="utf-8") as fh:
            logging.config.dictConfig(yaml.safe_load(fh))
    else:
        logging.basicConfig(level=logging.INFO)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)