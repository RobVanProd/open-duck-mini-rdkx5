# Command-Conditioned Pitch-Rate-Limited BC Decision

status: `HOLD_FITTED_TRACKING_AFTER_TARGET_RATE_FIX`

This was an offline-only deployable-shape behavior-cloning experiment. It did
not train PPO, SSH, deploy, run robot tests, or change robot runtime behavior.

## Inputs

- standstill source: `outputs/analysis/scale0p75_x0_full_obs_traces/scale0p75/seed_*/trace.jsonl`
- walking source: `outputs/analysis/source_vx_pitch_chain_rate_limited_2p25_traces/*.jsonl`
- manifest: `outputs/analysis/ppo_swish_cmd_conditioned_pitch_ratelimit_2p25_manifest.json`
- BC fit: `outputs/analysis/PPO_LOC_SWISH_CMD_PITCH_RL_2P25_BC_STUDENT.md`
- candidate ONNX: `outputs/analysis/ppo_loc_swish_cmd_pitch_rl_2p25_candidate/candidate.onnx`
- PPO step-0 checkpoint: `outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint`
- PPO step-0 ONNX: `outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0.onnx`

Raw JSONL traces remain ignored local training inputs.

## What Changed

The old command-conditioned manifest used zero-action x=0.0 standstill traces,
but zero action falls on hard seeds 3 and 5. This run replaced those with
full-observation x=0 traces from the existing scale-0.75 stabilizing policy:

```text
scale0p75 x=0.0 trace source:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0003 m/s
  mean max tracking p95: 0.0710 rad
```

The x=0.08 walking labels were also rate-limited across the pitch chain:

```text
pitch-chain joints:
  left_hip_pitch, left_knee, left_ankle,
  right_hip_pitch, right_knee, right_ankle
cap:
  2.25 rad/s
changed ticks:
  3577
```

The resulting swish PPO-loc BC fit had lower supervised error and low predicted
target rate:

```text
samples: 8000
p95 action error: 0.024947
target-rate p95: 1.784699 rad/s
target-rate max: 2.497077 rad/s
```

## Fitted-Bridge Gates

At `x=0.0`, the candidate fixed the prior hard-seed fall pattern:

```text
x=0.0 fitted bridge:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0004 m/s
  mean body pitch p95: 0.0249 rad
  mean max pitch target velocity p95: 0.4448 rad/s
  mean max tracking p95: 0.0730 rad
  worst max tracking p95: 0.0837 rad
```

This is a near-pass at zero command. The only formal hold is seed 1 tracking
at `0.0837 rad`, slightly above the preferred `0.08 rad` threshold.

At `x=0.08`, the candidate remained stable and in-envelope, but still held on
tracking:

```text
x=0.08 fitted bridge:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0341 m/s
  mean track ratio: 0.4267
  mean body pitch p95: 0.1182 rad
  mean max pitch target velocity p95: 2.1371 rad/s
  max pitch target velocity p95 range: 2.1112-2.1734 rad/s
  mean max tracking p95: 0.1963 rad
  worst max tracking p95: 0.2008 rad
```

## Interpretation

This run separates the current blockers cleanly:

- command-conditioned x=0.0 stability is mostly solved in a deployable ONNX
  shape.
- x=0.08 target-rate margin is solved; the candidate stays well under the
  fitted actuator envelope.
- x=0.08 fitted actuator tracking is not solved; tracking remains around
  `0.19-0.20 rad` despite target-rate p95 near `2.14 rad/s`.

So the next issue is not scalar action amplitude, target-rate clipping, or
zero-command behavior. The remaining gap is the closed-loop action timing /
state feedback needed to make the fitted bridge actually follow the walking
targets. More one-step BC label smoothing is unlikely to be sufficient by
itself.

## Decision

Do not promote this candidate to robot validation.

Next useful direction:

```text
PPO fine-tuning or another closed-loop training pass from this warm start,
with the fitted actuator bridge active and tracking/target-rate feedback in
the training objective.
```

This candidate is a good warm-start artifact because it is stable at `x=0.0`,
stable at `x=0.08`, command-conditioned, and in-envelope. It is not a finished
policy because fitted tracking at `x=0.08` remains far above the gate.

## PPO Step-0 Promotion

The BC fit was promoted into an actual Brax/PPO step-0 checkpoint:

```text
artifact: outputs/analysis/PPO_BC_SWISH_CMD_PITCH_RL_2P25_STEP0_EXPORT_FIDELITY.md
status: PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY
```

The step-0 ONNX was then gated directly.

```text
x=0.0 fitted bridge:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0005 m/s
  mean body pitch p95: 0.0245 rad
  mean max pitch target velocity p95: 0.4825 rad/s
  mean max tracking p95: 0.0740 rad
  worst max tracking p95: 0.0861 rad

x=0.08 fitted bridge:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0347 m/s
  mean track ratio: 0.4343
  mean body pitch p95: 0.1174 rad
  mean max pitch target velocity p95: 2.1196 rad/s
  max pitch target velocity p95 range: 2.0803-2.1527 rad/s
  mean max tracking p95: 0.1958 rad
  worst max tracking p95: 0.2013 rad
```

This confirms the exact PPO warm-start artifact is stable, command-conditioned,
and in-envelope, but not a deployment candidate. The next branch should start
PPO fine-tuning from this checkpoint with the fitted bridge active and should
grade success by reducing fitted tracking without losing x=0 stability or
x=0.08 forward progress.
