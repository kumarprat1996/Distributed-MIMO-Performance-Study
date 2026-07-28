from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .config import EnergyConfig


def spectral_efficiency(
    channel: NDArray[np.complex128],
    weights: NDArray[np.complex128],
    snr_linear: float,
    phase_rad: NDArray[np.float64] | None = None,
) -> NDArray[np.float64]:
    if phase_rad is None:
        phase_rad = np.zeros(channel.shape[1])
    effective = channel @ (np.exp(1j * phase_rad)[:, None] * weights)
    per_user_power = snr_linear / channel.shape[0]
    received = per_user_power * np.abs(effective) ** 2
    desired = np.diag(received)
    interference = received.sum(axis=1) - desired
    sinr = desired / (1.0 + interference)
    return np.log2(1.0 + sinr)


def total_power_w(
    snr_linear: float,
    num_antennas: int,
    deployment: str,
    config: EnergyConfig,
) -> float:
    fronthaul = (
        config.fronthaul_power_per_antenna_w * num_antennas
        if deployment == "distributed"
        else 0.0
    )
    return (
        snr_linear / config.power_amplifier_efficiency
        + config.fixed_power_w
        + num_antennas * config.rf_chain_power_w
        + fronthaul
    )


def energy_efficiency(
    spectral_efficiency_values: NDArray[np.float64],
    snr_linear: float,
    num_antennas: int,
    deployment: str,
    config: EnergyConfig,
) -> float:
    throughput = config.bandwidth_hz * spectral_efficiency_values.sum()
    return throughput / total_power_w(
        snr_linear, num_antennas, deployment, config
    )

