"""Distributed MIMO simulation package."""

from .config import StudyConfig, load_config
from .simulation import run_baseline, run_phase_sensitivity

__all__ = ["StudyConfig", "load_config", "run_baseline", "run_phase_sensitivity"]

