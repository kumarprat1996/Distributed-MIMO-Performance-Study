from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def user_positions(
    rng: np.random.Generator, num_users: int, area_side_m: float
) -> NDArray[np.float64]:
    return rng.uniform(0.0, area_side_m, size=(num_users, 2))


def antenna_positions(
    rng: np.random.Generator,
    deployment: str,
    num_antennas: int,
    area_side_m: float,
) -> NDArray[np.float64]:
    if deployment == "collocated":
        return np.full((num_antennas, 2), area_side_m / 2.0)
    if deployment == "distributed":
        return rng.uniform(0.0, area_side_m, size=(num_antennas, 2))
    raise ValueError(f"unknown deployment: {deployment}")


def wrapped_distances(
    users: NDArray[np.float64],
    antennas: NDArray[np.float64],
    area_side_m: float,
) -> NDArray[np.float64]:
    delta = np.abs(users[:, None, :] - antennas[None, :, :])
    delta = np.minimum(delta, area_side_m - delta)
    return np.linalg.norm(delta, axis=-1)

