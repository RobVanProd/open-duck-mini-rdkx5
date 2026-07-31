import datetime as _dt
import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np


SCHEMA_VERSION = "sim2real.telemetry.v1"


def utc_timestamp():
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def timestamp_slug():
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def default_telemetry_path(name="telemetry"):
    return str(Path("outputs") / "telemetry" / f"{timestamp_slug()}_{name}.jsonl")


def sha256_file(path):
    path = os.path.expanduser(str(path))
    if not path or not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def to_builtin(value):
    if value is None:
        return None
    if isinstance(value, np.ndarray):
        return to_builtin(value.tolist())
    if isinstance(value, np.generic):
        return to_builtin(value.item())
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if isinstance(value, (list, tuple)):
        return [to_builtin(v) for v in value]
    if isinstance(value, dict):
        return {str(k): to_builtin(v) for k, v in value.items()}
    return value


def _initializer_arrays(model):
    from onnx import numpy_helper

    return {
        initializer.name: numpy_helper.to_array(initializer)
        for initializer in model.graph.initializer
    }


def extract_onnx_obs_normalization(onnx_path, input_name="obs", obs_size=101):
    """Return embedded observation normalization constants if ONNX is available.

    The exported Open Duck policies normalize with a graph pattern equivalent to:
    normalized = (obs - mean) * reciprocal_std.
    """

    onnx_path = os.path.expanduser(str(onnx_path))
    result = {
        "mean": None,
        "std_recip": None,
        "std": None,
        "source": None,
        "error": None,
    }
    if not os.path.exists(onnx_path):
        result["error"] = f"ONNX path not found: {onnx_path}"
        return result

    try:
        import onnx

        model = onnx.load(onnx_path)
        arrays = _initializer_arrays(model)
        nodes = list(model.graph.node)

        mean = None
        std_recip = None
        source = None

        for node in nodes:
            if node.op_type != "Sub" or input_name not in node.input:
                continue
            sub_output = node.output[0] if node.output else None
            mean_names = [name for name in node.input if name != input_name]
            for name in mean_names:
                if name in arrays and arrays[name].shape == (obs_size,):
                    mean = arrays[name].astype(float)
                    source = f"Sub:{node.name or '<unnamed>'}:{name}"
                    break
            if mean is None or sub_output is None:
                continue
            for consumer in nodes:
                if sub_output not in consumer.input:
                    continue
                if consumer.op_type not in ("Mul", "Div"):
                    continue
                constant_names = [name for name in consumer.input if name != sub_output]
                for name in constant_names:
                    if name in arrays and arrays[name].shape == (obs_size,):
                        constant = arrays[name].astype(float)
                        if consumer.op_type == "Mul":
                            std_recip = constant
                        else:
                            std_recip = 1.0 / constant
                        source += f" -> {consumer.op_type}:{consumer.name or '<unnamed>'}:{name}"
                        break
                if std_recip is not None:
                    break
            if mean is not None and std_recip is not None:
                break

        if mean is None or std_recip is None:
            candidates = [
                arr.astype(float)
                for arr in arrays.values()
                if getattr(arr, "shape", None) == (obs_size,)
            ]
            if len(candidates) >= 2:
                mean = candidates[0]
                std_recip = candidates[1]
                source = "fallback:first_two_vector_initializers"

        if mean is None or std_recip is None:
            result["error"] = "Could not locate obs normalization constants"
            return result

        with np.errstate(divide="ignore", invalid="ignore"):
            std = np.where(std_recip != 0, 1.0 / std_recip, np.nan)
        result.update(
            {
                "mean": mean.tolist(),
                "std_recip": std_recip.tolist(),
                "std": std.tolist(),
                "source": source,
            }
        )
    except Exception as exc:
        result["error"] = repr(exc)
    return result


def require_onnx_obs_normalization(info, onnx_path="<unknown>"):
    """Reject missing or malformed policy normalization metadata.

    Telemetry that silently omits normalized observations defeats the purpose of
    the observation-contract diagnostic.  Keep extraction read-only, but make
    callers explicitly require a complete result before starting a capture.
    """

    if info is None:
        raise RuntimeError(
            f"ONNX observation normalization unavailable for {onnx_path}: "
            "extractor returned no result"
        )
    error = info.get("error")
    if error:
        raise RuntimeError(
            f"ONNX observation normalization unavailable for {onnx_path}: "
            f"{error}"
        )
    for name in ("mean", "std_recip"):
        values = info.get(name)
        if values is None:
            raise RuntimeError(
                f"ONNX observation normalization unavailable for {onnx_path}: "
                f"missing {name}"
            )
        array = np.asarray(values, dtype=float)
        if array.shape != (101,):
            raise RuntimeError(
                f"ONNX observation normalization unavailable for {onnx_path}: "
                f"{name} shape {array.shape}, expected (101,)"
            )
        if not np.all(np.isfinite(array)):
            raise RuntimeError(
                f"ONNX observation normalization unavailable for {onnx_path}: "
                f"{name} contains a non-finite value"
            )
    if np.any(np.asarray(info["std_recip"], dtype=float) <= 0):
        raise RuntimeError(
            f"ONNX observation normalization unavailable for {onnx_path}: "
            "std_recip must be strictly positive"
        )
    return info


def normalize_observation(obs, mean, std_recip):
    if obs is None or mean is None or std_recip is None:
        return None
    obs = np.asarray(obs, dtype=float)
    mean = np.asarray(mean, dtype=float)
    std_recip = np.asarray(std_recip, dtype=float)
    if obs.shape != mean.shape or obs.shape != std_recip.shape:
        return None
    return ((obs - mean) * std_recip).tolist()


class JsonlTelemetryLogger:
    def __init__(self, path):
        self.path = os.path.expanduser(str(path))
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._f = open(self.path, "a", buffering=1)

    def log(self, record):
        self._f.write(json.dumps(to_builtin(record), separators=(",", ":")) + "\n")

    def close(self):
        if not self._f.closed:
            self._f.flush()
            self._f.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
