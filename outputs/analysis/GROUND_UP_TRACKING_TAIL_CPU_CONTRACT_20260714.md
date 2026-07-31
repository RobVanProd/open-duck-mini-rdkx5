# Ground-Up Tracking-Tail CPU Contract

status: `PASS_TRACKING_TAIL_CPU_CONTRACT`

- frozen threshold: `0.2 rad`
- pitch-chain indices: `[2, 3, 4, 11, 12, 13]`
- default scale: `0.0`
- frozen trace rows: `3600`
- nonzero trace fraction: `0.15861111`
- mean raw tail cost: `0.000017306060`
- JAX/NumPy maximum error: `9.95374684369e-11`
- transition state/observation error: `0`
- transition reward-contract error: `3.08314338326e-08`
- transition nonzero-cost steps: `18/64`

Every contract check passes only if the diagnostic is exactly zero below
and at .20 rad, monotonic above it, uses the same six gate joints, remains
default-off, and reproduces an independent NumPy implementation.

This is a diagnostic wiring pass only. It does not select a scale or
authorize PPO, Colab, deployment, RDK-X5, or robot use.
