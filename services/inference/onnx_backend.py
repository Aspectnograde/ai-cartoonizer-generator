"""ONNX Runtime style-transfer session wrapper.

Wraps an ORT InferenceSession with preprocessing (normalize to [-1,1], NCHW),
inference, and postprocessing (denormalize, clip). Input/output tensor names
are resolved from the model metadata at load time.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from utils.errors import InferenceError
from utils.logging_setup import get_logger

log = get_logger(__name__)


class OnnxStyleSession:
    def __init__(self, weight_path: Path, device: str = "auto", fp16: bool = True) -> None:
        import onnxruntime as ort

        providers = self._pick_providers(ort, device)
        opts = ort.SessionOptions()
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        opts.intra_op_num_threads = 0

        self.session = ort.InferenceSession(str(weight_path), sess_options=opts, providers=providers)
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.fp16 = fp16 and any("CUDA" in p or "Dml" in p for p in providers)
        log.info("loaded style session %s on %s", weight_path.name, providers[0])

    @staticmethod
    def _pick_providers(ort, device: str) -> list[str]:  # noqa: ANN001
        available = ort.get_available_providers()
        order = {
            "cuda": ["CUDAExecutionProvider", "CPUExecutionProvider"],
            "dml": ["DmlExecutionProvider", "CPUExecutionProvider"],
            "cpu": ["CPUExecutionProvider"],
            "auto": ["CUDAExecutionProvider", "DmlExecutionProvider", "CPUExecutionProvider"],
        }.get(device, ["CPUExecutionProvider"])
        return [p for p in order if p in available]

    def run_single(self, rgb: np.ndarray) -> np.ndarray:
        if rgb.ndim != 3 or rgb.shape[2] != 3:
            raise InferenceError(f"expected HxWx3 RGB, got {rgb.shape}")

        x = rgb.astype(np.float32) / 127.5 - 1.0
        x = np.transpose(x, (2, 0, 1))[None, ...]
        if self.fp16:
            x = x.astype(np.float16)

        try:
            y = self.session.run([self.output_name], {self.input_name: x})[0]
        except Exception as exc:  # noqa: BLE001
            raise InferenceError(f"ORT run failed: {exc}") from exc

        y = np.asarray(y, dtype=np.float32)[0]
        y = np.transpose(y, (1, 2, 0))
        y = (y + 1.0) * 127.5
        return np.clip(y, 0, 255).astype(np.uint8)