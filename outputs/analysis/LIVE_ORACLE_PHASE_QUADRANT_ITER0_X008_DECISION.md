# Live-Oracle Phase-Quadrant Iter0 X008 Decision

status: `HOLD_HARD_PHASE_QUADRANT_REGRESSION`

This is the first explicit phase-indexed student rung. It preserves the deployed
contract as one ONNX graph:

`obs[1,101] -> continuous_actions[1,14]`

It does not train PPO, deploy, SSH, run robot tests, or change robot runtime
behavior.

## Setup

Inputs:

- source manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_000/live_oracle_dagger_x008_manifest.json`
- split tool: `tools/split_bc_manifest_by_phase.py`
- wrapper tool: `tools/wrap_policy_phase_quadrant_gate.py`
- output policy: `outputs/analysis/live_oracle_phase_quadrant_iter0_x008_candidate/candidate.onnx`

Phase split rule:

- bin 0: `obs[99] >= 0 and obs[100] >= 0`
- bin 1: `obs[99] < 0 and obs[100] >= 0`
- bin 2: `obs[99] < 0 and obs[100] < 0`
- bin 3: `obs[99] >= 0 and obs[100] < 0`

Split samples:

- bin 0: `1568`
- bin 1: `1568`
- bin 2: `1568`
- bin 3: `1296`
- total: `6000`

ONNX phase-gate verification:

- artifact: `outputs/analysis/live_oracle_phase_quadrant_iter0_x008_onnx_gate_verify.json`
- status: `PASS_ONNX_PHASE_GATE_VERIFY`
- max action error versus selected phase head: `0.0`

## Supervised Fit

Each phase head fit the local labels better than the shared iter0 MLP:

| phase | MAE | p95 abs error | target-rate p95 |
|---:|---:|---:|---:|
| 0 | 0.007918 | 0.023037 | 4.059961 |
| 1 | 0.007380 | 0.021736 | 4.078670 |
| 2 | 0.007501 | 0.022169 | 3.969443 |
| 3 | 0.006822 | 0.018928 | 4.173622 |

The supervised loss improvement did not translate to closed-loop improvement.

## Canonical X008 Gate

Artifact:

`outputs/analysis/LIVE_ORACLE_PHASE_QUADRANT_ITER0_X008_GATE.md`

Canonical gate:

- task: `flat_terrain_backlash`
- bridge: `fitted`
- duration: `15s`
- seeds: `0-7`

Result:

- duration complete: `7 / 8`
- falls/terminations: `1 / 8`
- mean track ratio: `0.4168`
- mean local vx: `0.0333 m/s`
- max pitch-chain sent velocity p95: `5.2400 rad/s`
- max pitch-chain tracking p95: `0.2711 rad`

Compared with live-oracle iter0:

- iter0 duration complete: `8 / 8`
- iter0 falls: `0 / 8`
- iter0 mean track ratio: `0.5613`
- iter0 max pitch-chain sent velocity p95: `3.6791 rad/s`
- iter0 max pitch-chain tracking p95: `0.2665 rad`

## Interpretation

The hard phase-quadrant split is rejected.

It improved supervised per-phase imitation error, but it made the closed-loop
policy worse:

- introduced one fall/termination
- reduced forward tracking ratio
- increased pitch-chain sent velocity above the measured envelope
- did not reduce the strict tracking plateau

This points to phase-boundary discontinuity or off-manifold recovery as the
failure mode. The next rung should not be another hard quadrant split. The next
reasonable options are:

- smooth phase-conditioned mixing between heads
- a single shared trunk with phase-conditioned modulation
- recurrence/hidden state with live-oracle DAgger labels

Do not promote this policy to robot validation.
