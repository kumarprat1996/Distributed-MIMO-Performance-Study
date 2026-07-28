from __future__ import annotations

from dataclasses import dataclass
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .channel import large_scale_gain, rayleigh_channel
from .config import StudyConfig
from .metrics import energy_efficiency, spectral_efficiency
from .precoding import precoder
from .topology import antenna_positions, user_positions

DEPLOYMENTS = ("collocated", "distributed")
PRECODERS = ("mrt", "zf")


@dataclass(frozen=True)
class Result:
    deployment: str
    precoder: str
    x: float
    mean_se: float
    edge_se: float
    energy_efficiency_bit_per_joule: float


def _channels_for_realization(
    rng: np.random.Generator, config: StudyConfig
) -> dict[str, np.ndarray]:
    users = user_positions(rng, config.num_users, config.area_side_m)
    channels: dict[str, np.ndarray] = {}
    for deployment in DEPLOYMENTS:
        antennas = antenna_positions(
            rng, deployment, config.num_antennas, config.area_side_m
        )
        gain = large_scale_gain(
            rng, users, antennas, config.area_side_m, config.channel
        )
        channels[deployment] = rayleigh_channel(rng, gain)
    return channels


def _summarize(
    values: list[np.ndarray],
    ee_values: list[float],
    deployment: str,
    method: str,
    x: float,
) -> Result:
    flattened = np.concatenate(values)
    return Result(
        deployment=deployment,
        precoder=method,
        x=x,
        mean_se=float(flattened.mean()),
        edge_se=float(np.percentile(flattened, 5)),
        energy_efficiency_bit_per_joule=float(np.mean(ee_values)),
    )


def run_baseline(config: StudyConfig) -> list[Result]:
    rng = np.random.default_rng(config.seed)
    accum: dict[tuple[str, str, float], tuple[list[np.ndarray], list[float]]] = {}
    for _ in range(config.realizations):
        channels = _channels_for_realization(rng, config)
        for deployment, channel in channels.items():
            for method in PRECODERS:
                weights = precoder(channel, method)
                for snr_db in config.snr_db:
                    snr = 10.0 ** (snr_db / 10.0)
                    se = spectral_efficiency(channel, weights, snr)
                    key = (deployment, method, snr_db)
                    values, energies = accum.setdefault(key, ([], []))
                    values.append(se)
                    energies.append(
                        energy_efficiency(
                            se,
                            snr,
                            config.num_antennas,
                            deployment,
                            config.energy,
                        )
                    )
    return [
        _summarize(*accum[(deployment, method, snr_db)], deployment, method, snr_db)
        for deployment in DEPLOYMENTS
        for method in PRECODERS
        for snr_db in config.snr_db
    ]


def run_phase_sensitivity(config: StudyConfig) -> list[Result]:
    rng = np.random.default_rng(config.seed + 1)
    snr = 10.0 ** (config.phase_study_snr_db / 10.0)
    accum: dict[tuple[str, str, float], tuple[list[np.ndarray], list[float]]] = {}
    for _ in range(config.realizations):
        channels = _channels_for_realization(rng, config)
        unit_phase_noise = rng.standard_normal(config.num_antennas)
        for deployment, channel in channels.items():
            for method in PRECODERS:
                weights = precoder(channel, method)
                for phase_std_deg in config.phase_std_deg:
                    phase = np.deg2rad(phase_std_deg) * unit_phase_noise
                    se = spectral_efficiency(channel, weights, snr, phase)
                    key = (deployment, method, phase_std_deg)
                    values, energies = accum.setdefault(key, ([], []))
                    values.append(se)
                    energies.append(
                        energy_efficiency(
                            se,
                            snr,
                            config.num_antennas,
                            deployment,
                            config.energy,
                        )
                    )
    return [
        _summarize(
            *accum[(deployment, method, phase_std_deg)],
            deployment,
            method,
            phase_std_deg,
        )
        for deployment in DEPLOYMENTS
        for method in PRECODERS
        for phase_std_deg in config.phase_std_deg
    ]


def save_results(
    results: list[Result], output_dir: str | Path, stem: str, xlabel: str
) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    csv_path = output / f"{stem}_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=Result.__dataclass_fields__)
        writer.writeheader()
        writer.writerows(result.__dict__ for result in results)

    figure_path = output / f"{stem}.png"
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    styles = {
        ("collocated", "mrt"): ("o-", "Co-located MRT"),
        ("collocated", "zf"): ("s-", "Co-located ZF"),
        ("distributed", "mrt"): ("o--", "Distributed MRT"),
        ("distributed", "zf"): ("s--", "Distributed ZF"),
    }
    for key, (style, label) in styles.items():
        subset = [result for result in results if (result.deployment, result.precoder) == key]
        axes[0].plot([r.x for r in subset], [r.mean_se for r in subset], style, label=label)
        axes[1].plot([r.x for r in subset], [r.edge_se for r in subset], style, label=label)
    axes[0].set_ylabel("Mean spectral efficiency (bit/s/Hz/user)")
    axes[1].set_ylabel("5th-percentile spectral efficiency (bit/s/Hz/user)")
    for axis in axes:
        axis.set_xlabel(xlabel)
        axis.grid(True, alpha=0.3)
    axes[0].legend(fontsize=8)
    figure.tight_layout()
    figure.savefig(figure_path, dpi=180)
    plt.close(figure)
    return csv_path, figure_path

