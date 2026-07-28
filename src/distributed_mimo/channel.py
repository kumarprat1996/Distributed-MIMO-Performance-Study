from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .config import ChannelConfig
from .topology import wrapped_distances


def large_scale_gain(
    rng: np.random.Generator,
    users: NDArray[np.float64],
    antennas: NDArray[np.float64],
    area_side_m: float,
    config: ChannelConfig,
) -> NDArray[np.float64]:
    distance = wrapped_distances(users, antennas, area_side_m)
    distance = np.maximum(distance, config.reference_distance_m)
    gain = (config.reference_distance_m / distance) ** config.path_loss_exponent
    shadowing_db = rng.normal(0.0, config.shadowing_std_db, size=gain.shape)
    return gain * 10.0 ** (shadowing_db / 10.0)


def rayleigh_channel(
    rng: np.random.Generator, gain: NDArray[np.float64]
) -> NDArray[np.complex128]:
    fading = (
        rng.standard_normal(gain.shape) + 1j * rng.standard_normal(gain.shape)
    ) / np.sqrt(2.0)
    return np.sqrt(gain) * fading

