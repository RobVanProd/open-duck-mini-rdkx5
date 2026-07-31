# Phase 2 z0.0075 Iter21 History-Context Rate150 Decision

status: `HOLD_HISTORY_CONTEXT_STILL_REGRESSES_SEED7`

## Context

The previous low-weight snippet loop recovered the latest failed seed but then
moved another sensitive seed into reverse/low-progress collapse. The last
memoryless patch-loop candidate recovered seeds 0, 1, 2, and 6, but failed seed7.

This experiment keeps the deployable policy contract:

`obs[1,101] -> continuous_actions[1,14]`

It changes the phase-modulated feed-forward student by giving the modulation path
richer context that is already present in the observation vector:

- command channels: `6:13`
- action history: `41:83`
- previous motor targets: `83:97`
- foot contacts: `97:99`
- phase: `99:101`

No robot tests, SSH, deploy, runtime behavior changes, grounded replay, or PPO
training were performed.

## Candidate

- path: `policy/candidates/phase2_z0075_iter21_history_context_rate150_20260704/candidate.onnx`
- ONNX sha256: `84fa4aac2830514cd8671f88201fec731f7f7d26c300abc3eff68c8a971bb086`
- NPZ sha256: `946f24f1dee2daa7804c6f9bbb6e938db9ff8985380df5cf4a98ad8fce94feb1`
- source manifest: `outputs/analysis/phase2_z0075_iter21_seed67_w2_seed1_plus_seed2_merged_manifest.json`
- source manifest sha256: `3398b064c7454faae25d046c630450b4060e3dca58251d0e9c709adfb99029fa`
- screen JSON sha256: `c99c2999370957a209c2ba381db3087dfad7f3b0d9b64827b207d7afb4b7bec2`
- training status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`
- ONNX max abs fidelity error: `0.00000036`

## Fit Metrics

- samples: `53834`
- MAE: `0.010001`
- p95 abs error: `0.031843`
- target-rate p95: `1.361174 rad/s`
- target-rate max: `9.392404 rad/s`

The pairwise target-rate p95 is inside the intended rate-cleaning band, but the
max pairwise target-rate remains high. The closed-loop corrected-bridge screen is
therefore the decision source.

## Compact Screen

Corrected-bridge screen:

- command: `x=0.08`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.0075`
- bridge: `fitted`
- reset: `home-support`, settle `10` ticks
- pushes: enabled, `0.075-0.125`, interval `1.0-1.5 s`
- seeds: `0,1,2,6,7`

| seed | status | samples | termination | track_ratio | mean_local_vx | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 | max_vel_excess |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3483 | 0.0279 | 0.1735 | 0.1590 | 1.5596 | 0.1793 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3144 | 0.0252 | 0.1825 | 0.1573 | 1.5518 | 0.1849 | 0.0000 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3787 | 0.0303 | 0.1780 | 0.1590 | 1.5423 | 0.1842 | 0.0000 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.2961 | 0.0237 | 0.1765 | 0.1584 | 1.5505 | 0.1801 | 0.0000 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 274 | `fall_or_nan` | -0.5217 | -0.0417 | 0.1734 | 0.0690 | 1.5707 | 0.1767 | 0.0000 |

## Interpretation

The deployable history-context modulation did not solve the sensitive-seed
cycling problem. It preserved seeds 0, 1, 2, and 6, but seed7 still moved into
reverse/low-progress collapse and fell. The failure again has zero corrected
velocity-envelope excess and acceptable tracking p95, so this is not an
actuator-limit regression.

Compared with the prior patch-loop candidate, seed7 remains the active failure:

- previous seed7 failure: 288 samples, track_ratio `-0.5495`
- history-context seed7 failure: 274 samples, track_ratio `-0.5217`

The richer deployable context is therefore not enough by itself. Appending
another memoryless snippet patch remains disallowed as the primary strategy.

## Decision

Do not promote this candidate and do not run x=0.0 or robot validation.

Recommended next step:

- run the live-oracle DAgger loop rather than static relabel-and-freeze patches;
- use the compact sensitive-seed screen `0,1,2,6,7` as the anti-regression gate;
- if a recurrent/stateful student is tested next, label it explicitly as
  diagnostic-only unless the runtime export contract is later changed.
