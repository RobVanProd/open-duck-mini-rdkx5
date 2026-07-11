# Phase 2 Stage A Reset Settle-10 Failure-Seed Result

Date: 2026-07-11

Status: **HOLD — passive settle rejected**

This was an offline CPU-only reset diagnostic. No training, policy/action
change, robot access, deployment, GPU, or Colab allocation was performed.

## Paired result

The exact seven canonical one-second fall seeds were rerun with the only change
`reset_settle_ticks: 0 -> 10` under the same original rate175 step-163,840
policy, x=0.08 command, fitted corrected bridge, playground reset, and 2.0 rad/s
pitch-chain limiter.

| seed | settle-0 samples | settle-10 samples | change | settle-10 outcome |
|---:|---:|---:|---:|---|
| 9 | 34 | 22 | -12 | fall |
| 12 | 37 | 25 | -12 | fall |
| 14 | 41 | 33 | -8 | fall |
| 19 | 32 | 24 | -8 | fall |
| 20 | 27 | 19 | -8 | fall |
| 36 | 28 | 16 | -12 | fall |
| 37 | 27 | 20 | -7 | fall |

Aggregate:

- settle-0: 7/7 falls, mean 32.29 samples before termination
- settle-10: 7/7 falls, mean 22.71 samples before termination
- mean termination moved 9.57 ticks earlier (0.191 s)
- settle-10 mean velocity: -0.2307 m/s
- settle-10 mean base-height minimum: 0.0808 m

## Decision

Ten passive settle ticks do not stabilize the failure distribution; they make
every observed failure occur earlier. Therefore:

1. reject passive settle-10;
2. do not sweep settle duration;
3. do not infer that a deterministic home-support reset preserves walking—the
   existing project evidence shows stable double-support/low-progress basins;
4. retain teacher disagreement only as an offline early-warning feature;
5. require either a calibrated start-paused/reset-health decision or a separately
   sourced active-recovery target before another intervention.

No threshold, recovery action, training, deployment, or robot-side test is
authorized.

Primary artifacts:

- `outputs/analysis/PHASE2_STAGE_A_RESET_SETTLE10_FAILURE_SEEDS.md`
- `outputs/analysis/phase2_stage_a_reset_settle10_failure_seeds.json`
