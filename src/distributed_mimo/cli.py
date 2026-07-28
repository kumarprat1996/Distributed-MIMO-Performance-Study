from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config
from .simulation import run_baseline, run_phase_sensitivity, save_results


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "study", choices=("baseline", "phase", "all"), nargs="?", default="all"
    )
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=Path("results"))
    return parser


def main() -> None:
    args = _parser().parse_args()
    config = load_config(args.config)
    if args.study in ("baseline", "all"):
        paths = save_results(
            run_baseline(config),
            args.output,
            "baseline_spectral_efficiency",
            "Transmit SNR (dB)",
        )
        print(f"Baseline results: {paths[0]} and {paths[1]}")
    if args.study in ("phase", "all"):
        paths = save_results(
            run_phase_sensitivity(config),
            args.output,
            "phase_sensitivity",
            "Phase-error standard deviation (degrees)",
        )
        print(f"Phase results: {paths[0]} and {paths[1]}")


if __name__ == "__main__":
    main()

