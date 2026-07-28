import numpy as np
import pytest

from distributed_mimo.config import StudyConfig
from distributed_mimo.metrics import spectral_efficiency
from distributed_mimo.precoding import precoder
from distributed_mimo.topology import wrapped_distances


def test_wrapped_distance_uses_nearest_image():
    users = np.array([[1.0, 50.0]])
    antennas = np.array([[99.0, 50.0]])
    assert wrapped_distances(users, antennas, 100.0)[0, 0] == pytest.approx(2.0)


def test_zf_removes_interference_for_full_rank_channel():
    rng = np.random.default_rng(3)
    channel = rng.normal(size=(3, 6)) + 1j * rng.normal(size=(3, 6))
    weights = precoder(channel, "zf")
    effective = channel @ weights
    off_diagonal = effective - np.diag(np.diag(effective))
    assert np.max(np.abs(off_diagonal)) < 1e-10


def test_phase_error_can_reduce_zf_performance():
    rng = np.random.default_rng(7)
    channel = rng.normal(size=(4, 12)) + 1j * rng.normal(size=(4, 12))
    weights = precoder(channel, "zf")
    ideal = spectral_efficiency(channel, weights, 10.0)
    impaired = spectral_efficiency(
        channel, weights, 10.0, np.linspace(-1.0, 1.0, channel.shape[1])
    )
    assert impaired.mean() < ideal.mean()


def test_invalid_zf_dimensions_rejected_by_config():
    with pytest.raises(ValueError):
        StudyConfig(num_antennas=4, num_users=5)

