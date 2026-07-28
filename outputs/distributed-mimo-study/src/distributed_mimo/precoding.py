from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def _normalize_columns(matrix: NDArray[np.complex128]) -> NDArray[np.complex128]:
    norms = np.linalg.norm(matrix, axis=0, keepdims=True)
    return matrix / np.maximum(norms, np.finfo(float).eps)


def precoder(
    channel: NDArray[np.complex128], method: str
) -> NDArray[np.complex128]:
    if method == "mrt":
        raw = channel.conj().T
    elif method == "zf":
        gram = channel @ channel.conj().T
        raw = channel.conj().T @ np.linalg.pinv(gram, rcond=1e-10)
    else:
        raise ValueError(f"unknown precoder: {method}")
    return _normalize_columns(raw)

