"""
FlowCast AI - Universal Cross-Platform Inference Engine.

Runs neural network models seamlessly across:
1. Systems with ONNX Runtime (x86_64, Windows, Cloud)
2. Mainframe architectures (IBM LinuxONE / s390x) via optimized NumPy vectorization.

Provides an identical interface:
    session.run(None, {input_name: x_matrix}) -> [probabilities]
"""

import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
import joblib

try:
    import onnxruntime as ort
    HAS_ONNXRUNTIME = True
except ImportError:
    HAS_ONNXRUNTIME = False
    ort = None


def mish(x: np.ndarray) -> np.ndarray:
    """Mish activation: x * tanh(softplus(x))"""
    return x * np.tanh(np.log1p(np.exp(np.clip(x, -20.0, 20.0))))


def softmax(x: np.ndarray) -> np.ndarray:
    """Numerically stable softmax."""
    e = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e / np.sum(e, axis=-1, keepdims=True)


class UniversalInferenceSession:
    """
    Cross-platform inference session.
    Auto-detects whether ONNX Runtime is available, and transparently falls back
    to high-performance vectorized NumPy execution on platforms like IBM LinuxONE (s390x).
    """

    def __init__(
        self,
        model_name: str,
        onnx_path: Optional[Path] = None,
        weights_dict: Optional[Dict[str, np.ndarray]] = None,
        session_options: Optional[Any] = None
    ):
        self.model_name = model_name
        self.use_ort = False
        self.ort_session = None
        self.input_name = f"{model_name}_features"
        self.weights = weights_dict or {}

        # 1. Attempt to use ONNX Runtime if available
        if HAS_ONNXRUNTIME and onnx_path and Path(onnx_path).exists():
            try:
                opts = session_options or ort.SessionOptions()
                self.ort_session = ort.InferenceSession(
                    str(onnx_path),
                    opts,
                    providers=["CPUExecutionProvider"]
                )
                self.input_name = self.ort_session.get_inputs()[0].name
                self.use_ort = True
            except Exception as e:
                print(f"[UniversalInference] ONNX Runtime init failed for {model_name} ({e}), falling back to NumPy.")
                self.use_ort = False

    def get_inputs(self):
        class DummyInput:
            def __init__(self, name):
                self.name = name
        return [DummyInput(self.input_name)]

    def run(self, output_names: Any, feed_dict: Dict[str, np.ndarray]) -> List[np.ndarray]:
        """
        Execute forward pass and return list matching ONNX Runtime format: [output_tensor].
        """
        x = list(feed_dict.values())[0]
        if not isinstance(x, np.ndarray):
            x = np.asarray(x, dtype=np.float32)

        # Path A: ONNX Runtime
        if self.use_ort and self.ort_session:
            feed = {self.input_name: x}
            return self.ort_session.run(output_names, feed)

        # Path B: Native Vectorized NumPy (s390x / LinuxONE optimized)
        return [self._numpy_forward(x)]

    def _numpy_forward(self, x: np.ndarray) -> np.ndarray:
        w = self.weights

        if self.model_name == "health":
            # Module 1: 3-layer MLP with BatchNorm + Mish
            h = x
            for lin_idx, bn_idx in [(0, 1), (4, 5), (8, 9)]:
                weight = w[f"base_model.network.{lin_idx}.weight"]
                bias = w[f"base_model.network.{lin_idx}.bias"]
                scale = w[f"base_model.network.{bn_idx}.weight"]
                b_bias = w[f"base_model.network.{bn_idx}.bias"]
                mean = w[f"base_model.network.{bn_idx}.running_mean"]
                var = w[f"base_model.network.{bn_idx}.running_var"]

                h = h @ weight.T + bias
                h = (h - mean) / np.sqrt(var + 1e-5) * scale + b_bias
                h = mish(h)

            w_head = w["base_model.network.12.weight"]
            b_head = w["base_model.network.12.bias"]
            logits = h @ w_head.T + b_head
            return softmax(logits)

        elif self.model_name in ("delays", "stock"):
            # Module 2 & 3: 2-layer MLP with BatchNorm + Mish
            h = x
            for lin_idx, bn_idx in [(0, 1), (4, 5)]:
                weight = w[f"model.encoder.{lin_idx}.weight"]
                bias = w[f"model.encoder.{lin_idx}.bias"]
                scale = w[f"model.encoder.{bn_idx}.weight"]
                b_bias = w[f"model.encoder.{bn_idx}.bias"]
                mean = w[f"model.encoder.{bn_idx}.running_mean"]
                var = w[f"model.encoder.{bn_idx}.running_var"]

                h = h @ weight.T + bias
                h = (h - mean) / np.sqrt(var + 1e-5) * scale + b_bias
                h = mish(h)

            w_head = w["model.encoder.8.weight"]
            b_head = w["model.encoder.8.bias"]
            logits = h @ w_head.T + b_head
            return softmax(logits)

        else:
            raise ValueError(f"Unknown model name for NumPy forward: {self.model_name}")
