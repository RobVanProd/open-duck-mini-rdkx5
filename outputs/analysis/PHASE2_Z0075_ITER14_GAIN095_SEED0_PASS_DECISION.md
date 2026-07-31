# Phase 2 z=0.0075 Iter14 Gain-0.95 Seed0 Pass Decision

status: `HOLD_ITER14_GAIN095_SEED0_PASS_NOT_TRANSFERRED`

This is offline sim/data work only. It did not SSH, deploy, run robot tests,
grounded replay, or change runtime behavior.

## Question

Iter13 fixed seeds 2 and 6 but still failed seed 0 under the first intermediate
push. A diagnostic action-gain screen tested whether the seed0 lunge was caused
by a small amount of excess action authority that could be captured as a
deployable student update.

## Diagnostic Gain Screen

Condition:

- task: `rough_terrain_backlash`
- command_x: `0.08`
- bridge: corrected fitted bridge
- terrain z scale: `0.0075`
- reset mode: `home-support`
- push interval: `1.0-1.5s`
- push magnitude: `0.075-0.125`

Seed0 5s screens:

| gain | status | samples | mean vx | track ratio | pitch p95 | base min | note |
|---:|---|---:|---:|---:|---:|---:|---|
| 0.70 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | 0.0031 | 0.0385 | 0.0820 | 0.1533 | stable standstill |
| 0.80 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | 0.0045 | 0.0568 | 0.1041 | 0.1533 | stable standstill |
| 0.90 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | 0.0145 | 0.1815 | 0.1741 | 0.1532 | stable but too slow |
| 0.95 | `PASS_CANDIDATE_SIM_GATE` | 250 | 0.0219 | 0.2741 | 0.1981 | 0.1532 | narrow useful band |
| 0.975 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 118 | 0.1698 | 2.1229 | 0.9367 | 0.0077 | lunge/pitchover |

The gain boundary is sharp. Slightly reducing authority can stop the seed0
first-push lunge, but too much reduction collapses motion.

## Full Fail-Seed Gain Check

The 15s fail-seed check at eval-only gain `0.95` was not promotable:

| seed | status | samples | mean vx | track ratio | pitch p95 | base min | push success |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0210 | 0.2621 | 0.1781 | 0.1532 | 0.9167 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0225 | 0.2818 | 0.1824 | 0.1532 | 0.9231 |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 749 | -0.0042 | -0.0526 | 0.1965 | 0.0556 | 0.9231 |

Seed6 failed late with a backward/base-height collapse. Global output scaling is
therefore not a valid deployable Phase 2 fix.

## Iter14 Student

Iter14 tried to transfer the useful seed0 behavior without global scaling:

1. traced the seed0 gain-0.95 15s pass with full observations
2. built a one-entry BC manifest from that pass trace
3. merged it into the Iter13 87-entry base manifest
4. trained/exported a phase/command-modulated BC student

Candidate:

- path: `policy/candidates/phase2_z0075_iter14_gain095_seed0_pass_rate150_20260704/candidate.onnx`
- sha256: `632d5f96e4fdda6b842e433bb2b26608ab92509e7249947e6a2f40cb94034d2d`
- student npz sha256: `60563c640ae41c97dd995cdd1e30b87c5e803e7bb0590a41e4b6867b6b003ad9`
- merged manifest: `outputs/analysis/phase2_z0075_iter14_gain095_seed0_pass_merged_manifest.json`

Iter14 fail-seed gate:

| seed | status | samples | mean vx | track ratio | pitch p95 | base min | p95 excess | tracking p95 | push success |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 107 | 0.1813 | 2.2667 | 1.0269 | 0.0144 | 0.0000 | 0.1939 | 0.0000 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0305 | 0.3815 | 0.1981 | 0.1533 | 0.0000 | 0.1804 | 0.9231 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0308 | 0.3846 | 0.1623 | 0.1533 | 0.0000 | 0.1796 | 0.9231 |

## Decision

`HOLD_ITER14_GAIN095_SEED0_PASS_NOT_TRANSFERRED`

The gain-0.95 seed0 pass is real but did not transfer into the deployable
student. Iter14 preserves seeds 2 and 6, but seed0 still fails by the same early
first-push lunge/pitchover signature as Iter13.

Do not promote Iter14. Do not package global gain `0.95` as a candidate because
it regresses seed6.

## Next Recommendation

The next recovery branch should be state-conditioned around the first-push lunge
itself, not a global gain screen and not a single pass-trace BC append. Candidate
directions:

- collect live-oracle labels on seed0 first-push drift plus explicit pass-control
  traces for seeds 2 and 6
- add a push-window/lunge classifier from observation history or recurrence so
  attenuation only applies when the body is entering the seed0 lunge state
- keep seeds 2 and 6 as hard controls before any 8-seed promotion gate

The corrected actuator envelope remains fixed; no robot validation is allowed
from this hold.
