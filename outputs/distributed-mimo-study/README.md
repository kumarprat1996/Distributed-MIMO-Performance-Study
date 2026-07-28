# Distributed MIMO Performance and Synchronization Study

A reproducible Monte Carlo study comparing co-located and distributed
multi-user MIMO downlinks with maximum-ratio transmission (MRT) and
zero-forcing (ZF).

The initial model includes:

- equal total antenna counts for both deployments;
- distance-dependent path loss and log-normal shadowing;
- Rayleigh small-scale fading;
- MRT and ZF precoding with equal user power allocation;
- independent antenna phase errors;
- mean and 5th-percentile spectral efficiency; and
- a simple circuit/transmit/fronthaul energy model.

## Quick start

Python 3.10 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

# Run the baseline SNR sweep
mimo-study baseline --config configs/baseline.toml

# Run the phase-error sensitivity study
mimo-study phase --config configs/baseline.toml

# Run both studies
mimo-study all --config configs/baseline.toml

# Run tests
pytest
```

Figures and tidy CSV data are written to `results/`. To run without installing
the command-line entry point, use:

```bash
PYTHONPATH=src python -m distributed_mimo baseline
```

## System model

For user channel matrix `H` and precoder `W`, the received effective channel is

```text
G = H D_phi W
```

where `D_phi` is diagonal and contains the antenna phase offsets. Total
transmit power is shared equally across users. For user `k`,

```text
SINR_k = (P/K)|G_kk|² /
         (noise + (P/K) sum_{j != k}|G_kj|²).
```

The spectral efficiency is `log2(1 + SINR)`. The energy-efficiency metric is
the sum throughput divided by a configurable model containing transmit,
fixed-site, RF-chain, and distributed-fronthaul power.

The simulation uses wrapped edge distances. This suppresses artificial border
advantages while retaining a finite square deployment area. Distributed
antenna positions and user positions are shared between MRT and ZF comparisons
within a realization.

## Interpretation

The most useful outputs are:

- `baseline_spectral_efficiency.png`: performance versus SNR;
- `phase_sensitivity.png`: degradation versus phase-error standard deviation;
- `*_summary.csv`: data suitable for independent analysis.

The 5th percentile approximates cell-edge/reliability behavior. Mean spectral
efficiency captures overall performance. Energy efficiency depends on the
assumed hardware power model, so its parameters should be reported alongside
results rather than treated as universal constants.

## Assumptions and next extensions

This is a narrowband, perfect-CSI baseline. Phase offsets are applied after
precoder construction, representing synchronization drift between channel
estimation and downlink transmission. Natural follow-on experiments are:

1. grouped oscillators (one phase process per access point);
2. imperfect/delayed CSI;
3. OFDM timing and carrier-frequency offset;
4. spatially correlated fading and shadowing;
5. access-point selection and user-centric clustering; and
6. MATLAB implementations checked against the Python outputs.

