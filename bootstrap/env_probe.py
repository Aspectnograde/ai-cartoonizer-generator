"""Environment diagnostics: report ORT providers, GPU, and model availability."""
from __future__ import annotations

from pathlib import Path

from config.settings import Settings


def _ort_providers() -> list[str]:
    try:
        import onnxruntime as ort
    except ImportError:
        return ["<onnxruntime not installed>"]
    return list(ort.get_available_providers())


def _gpu_summary() -> str:
    providers = _ort_providers()
    for p in ("CUDAExecutionProvider", "DmlExecutionProvider", "TensorrtExecutionProvider"):
        if p in providers:
            return p
    return "CPUExecutionProvider (no GPU provider detected)"


def probe_environment(settings: Settings) -> None:
    import platform

    print("=== ai-cartoonizer-generator :: doctor ===")
    print(f"python        : {platform.python_version()}")
    print(f"platform      : {platform.system()} {platform.release()}")
    print(f"app version   : {settings.app_version}")
    print(f"ort providers : {', '.join(_ort_providers())}")
    print(f"active accel  : {_gpu_summary()}")
    print(f"models dir    : {Path(settings.models_dir).resolve()}")
    for style in settings.styles_available:
        weight = Path(style.weight)
        flag = "OK " if weight.exists() else "MISSING"
        print(f"  [{flag}] {style.id:<22} -> {weight}")
    print("=== end ===")