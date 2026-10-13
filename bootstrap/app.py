"""CLI entry point for ai-cartoonizer-generator.

Usage:
    cartoonizer render path/to/photo.jpg --style anime_shonen_v3 --out output/
    cartoonizer render path/to/clip.mp4  --style ghibli_soft_v2 --video
    cartoonizer list-styles
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bootstrap.env_probe import probe_environment
from cartoonizer_core.engine import CartoonizerEngine
from config.settings import load_settings
from utils.logging_setup import configure_logging


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cartoonizer",
        description="AI cartoonizer generator — stylize images and video into cartoon art.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    render = sub.add_parser("render", help="Cartoonize an image or video file.")
    render.add_argument("input", type=Path, help="Input image or video path.")
    render.add_argument("--style", default=None, help="Style id (see list-styles).")
    render.add_argument("--out", type=Path, default=Path("output"), help="Output directory.")
    render.add_argument("--video", action="store_true", help="Treat input as video.")
    render.add_argument("--upscale", type=float, default=1.0, help="Upscale factor (1/2/4).")
    render.add_argument("--device", default="auto", help="auto|cpu|cuda|dml")

    sub.add_parser("list-styles", help="List installed cartoon styles.")
    sub.add_parser("doctor", help="Print environment diagnostics.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    settings = load_settings()
    configure_logging(settings.logging_config)

    if args.command == "doctor":
        probe_environment(settings)
        return 0

    engine = CartoonizerEngine(settings)

    if args.command == "list-styles":
        for style in engine.list_styles():
            print(f"{style.id:<24} {style.label}")
        return 0

    if args.command == "render":
        if not args.input.exists():
            print(f"input not found: {args.input}", file=sys.stderr)
            return 2
        result = engine.render(
            source=args.input,
            style_id=args.style,
            output_dir=args.out,
            is_video=args.video,
            upscale=args.upscale,
            device=args.device,
        )
        print(str(result))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())