from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class ChannelConfig:
    path_loss_exponent: float = 3.7
    reference_distance_m: float = 10.0
    shadowing_std_db: float = 8.0


@dataclass(frozen=True)
class EnergyConfig:
    bandwidth_hz: float = 20e6
    power_amplifier_efficiency: float = 0.4
    fixed_power_w: float = 10.0
    rf_chain_power_w: float = 0.2
    fronthaul_power_per_antenna_w: float = 0.1


@dataclass(frozen=True)
class StudyConfig:
    seed: int = 42
    realizations: int = 200
    area_side_m: float = 500.0
    num_antennas: int = 32
    num_users: int = 8
    snr_db: tuple[float, ...] = (-10, -5, 0, 5, 10, 15, 20)
    phase_std_deg: tuple[float, ...] = (0, 2, 5, 10, 20, 30, 45, 60)
    phase_study_snr_db: float = 10.0
    channel: ChannelConfig = field(default_factory=ChannelConfig)
    energy: EnergyConfig = field(default_factory=EnergyConfig)

    def __post_init__(self) -> None:
        if self.num_antennas < self.num_users:
            raise ValueError("num_antennas must be at least num_users for ZF")
        if self.realizations < 1:
            raise ValueError("realizations must be positive")
        if self.area_side_m <= 0:
            raise ValueError("area_side_m must be positive")


def load_config(path: str | Path | None = None) -> StudyConfig:
    if path is None:
        return StudyConfig()

    with Path(path).open("rb") as handle:
        raw = tomllib.load(handle)

    simulation = raw.get("simulation", {})
    channel = ChannelConfig(**raw.get("channel", {}))
    energy = EnergyConfig(**raw.get("energy", {}))
    return StudyConfig(
        **{
            **simulation,
            "snr_db": tuple(simulation.get("snr_db", StudyConfig.snr_db)),
            "phase_std_deg": tuple(
                simulation.get("phase_std_deg", StudyConfig.phase_std_deg)
            ),
            "channel": channel,
            "energy": energy,
        }
    )

