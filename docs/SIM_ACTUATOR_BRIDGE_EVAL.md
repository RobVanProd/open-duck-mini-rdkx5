# Sim Actuator Bridge Eval

Last updated: 2026-06-21

## Purpose

Evaluate whether the measured real actuator bridge can reproduce the suspended
`x=0.08` failure before training a new policy.

This is an offline-only gate:

- no robot motion
- no SSH
- no deployment
- no runtime behavior changes
- no training

## Current Real Evidence

The current evidence chain is:

| evidence | result |
|---|---|
| home pose | mostly cleared |
| IMU tilt | +Z dominant, no gross axis flip |
| foot contacts | electrical responsiveness cleared |
| joint identity | no software order/sign failure found |
| suspended `x=0.0` | mostly healthy, warnings only |
| suspended `x=0.08` | coherent air-walking visually, but dynamic pitch-chain lag |
| actuator sine sweep `0.25-0.5 Hz`, `0.03 rad` | clean low-speed single-joint tracking |

The key mismatch is target speed:

```text
0.5 Hz / 0.03 rad sine max target velocity ~= 0.094 rad/s
suspended x=0.08 pitch-chain p95 target velocity ~= 3.09-5.22 rad/s
```

PR #13 fit a delayed / lagged / velocity-limited actuator model from existing
telemetry:

```text
best pitch-chain delay fit: 3 ticks
effective velocity limits: about 2.25-3.75 rad/s
combined model p95 fit error: about 0.019-0.035 rad
raw x=0.08 pitch tracking p95: about 0.13-0.21 rad
```

## Why Sim Reproduction Comes Before Training

Training should not start until the current policy fails in sim for the same
reason it fails on the real suspended Duck.

The intended proof is:

```text
BEST_WALK_ONNX_2 in vanilla sim
  -> action / target waveform appears trackable

BEST_WALK_ONNX_2 with fitted actuator bridge
  -> x=0.08-like pitch-chain lag appears
```

If that happens, the actuator bridge captures an important part of the
sim-to-real gap. If it does not happen, the bridge model is incomplete and
training against it would be premature.

## Current Sim Contract Status

The local sibling `../Open_Duck_Playground` has a constant named
`JOINTS_ORDER_NO_HEAD` with `10` joints, but that is not the full instantiated
environment contract.

The policy/sim contract audit instantiates `Joystick(flat_terrain)` with:

```text
../envs/open-duck-playground/bin/python
```

and confirms:

```text
observation: [1, 101]
action:      [1, 14]
MJCF nu:     14
home ctrl:   14
JAX backend: gpu / rocm:0
```

So the previous `HOLD_POLICY_SIM_CONTRACT_MISMATCH` is resolved.

The closed-loop eval tool now implements a target-stage bridge insertion by
mirroring `Joystick.step()` through:

```text
action delay
target = home + delayed_action * action_scale
max_motor_velocity rate limit
```

and then inserting the actuator bridge before `mjx_env.step(...)`.
`state.info["motor_targets"]` remains the sent target, so obs `83:97` continues
to represent commanded motor targets rather than bridged physical response.
This avoids silent action padding/truncation and avoids double-rate-limiting.

The current eval gate is:

```text
HOLD_SIM_RUNTIME_ERROR
```

Meaning: the correct sim contract exists and the bridge insertion point is
implemented, but the local ROCm/JAX/MJX execution failed during the closed-loop
GPU step with `ROCM_ERROR_ILLEGAL_ADDRESS`.

## Expected Behavior

Vanilla sim expectation:

- `BEST_WALK_ONNX_2` runs through the same observation/action contract.
- target velocity and action saturation are logged.
- pitch-chain simulated tracking stays close to targets if the sim actuator is
  still optimistic.

Fitted actuator bridge expectation:

- delay, lag, and effective velocity limits are inserted after policy target
  generation.
- pitch-chain tracking error rises toward the real suspended `x=0.08` range.
- estimated lag moves toward the measured `3-4` tick range.

Stress actuator bridge expectation:

- delay and lag are sampled from the broader bridge ranges:

```text
delay_ticks: 3-8
tau_s: 0.06-0.14
effective_velocity_limit_rad_s: about 2.25-4.7
```

- the policy should remain stable before it is considered a robot candidate.

## Success / Hold Criteria

`PASS_SIM_REPRODUCTION`:

- exact `101` observation / `14` action sim contract is available
- vanilla and fitted bridge modes run offline
- fitted bridge creates pitch-chain lag resembling real suspended `x=0.08`
- output metrics are written to `outputs/analysis/`

`HOLD_POLICY_SIM_CONTRACT_MISMATCH`:

- available sim environment action/observation contract does not match
  `BEST_WALK_ONNX_2`

`HOLD_SIM_INTEGRATION_PENDING`:

- sim contract matches, but fitted actuator bridge is not yet inserted into the
  closed-loop policy eval path

`HOLD_SIM_RUNTIME_ERROR`:

- the sim contract and insertion point exist, but the closed-loop JAX/MJX eval
  fails at runtime
- current observed failure: ROCm stream synchronization failure with
  `ROCM_ERROR_ILLEGAL_ADDRESS`

`HOLD_MODEL_INCOMPLETE`:

- fitted actuator bridge does not reproduce the real degradation

`HOLD_ENV_NOT_READY`:

- local JAX/ROCm/MuJoCo environment is not ready

`PROCEED_TO_TRAINING_WRAPPER`:

- sim reproduction is plausible
- next PR should implement the JAX/MJX training actuator wrapper

## Commands

Check local training/eval environment without training:

```bash
../envs/open-duck-playground/bin/python tools/check_training_env.py
```

Optional MuJoCo offscreen context check:

```bash
../envs/open-duck-playground/bin/python tools/check_training_env.py --render-check
```

Audit policy/sim contract:

```bash
python3 tools/audit_policy_sim_contract.py \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --output-md outputs/analysis/POLICY_SIM_CONTRACT_AUDIT.md \
  --output-json outputs/analysis/policy_sim_contract_audit.json
```

Run sim/contract preflight only:

```bash
python3 tools/eval_policy_with_actuator_bridge.py \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --env-python ../envs/open-duck-playground/bin/python \
  --command-x 0.08 \
  --duration 15 \
  --output-dir outputs/analysis
```

Run closed-loop sim eval:

```bash
../envs/open-duck-playground/bin/python tools/eval_policy_with_actuator_bridge.py \
  --mode closed-loop-sim \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --command-x 0.08 \
  --duration 15 \
  --bridge-mode all \
  --output-dir outputs/analysis
```

The closed-loop worker is contained in a subprocess so GPU runtime faults are
captured as evidence instead of aborting the parent tool.

Run telemetry replay bridge check using existing suspended `x=0.08` evidence:

```bash
python3 tools/eval_policy_with_actuator_bridge.py \
  --mode telemetry-replay \
  --telemetry-jsonl outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_thresholds.jsonl \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --env-python ../envs/open-duck-playground/bin/python \
  --output-dir outputs/analysis
```

By default the evaluator uses the audited policy IO contract to avoid noisy
local ONNX metadata imports:

```text
obs:    [1, 101]
action: [1, 14]
```

To ask ONNX Runtime for metadata explicitly:

```bash
python3 tools/eval_policy_with_actuator_bridge.py --inspect-policy-io
```

## Outputs

The eval harness writes:

```text
outputs/analysis/SIM_ACTUATOR_BRIDGE_EVAL.md
outputs/analysis/sim_actuator_bridge_eval.json
outputs/analysis/CLOSED_LOOP_ACTUATOR_BRIDGE_EVAL.md
outputs/analysis/closed_loop_actuator_bridge_eval.json
```

Current committed closed-loop output shows:

```text
overall_status: HOLD_SIM_RUNTIME_ERROR
contract preflight: PASS_ENV_INSTANTIATED, obs=101, actions=14
insertion point: target-stage bridge before mjx_env.step
worker error: ROCM_ERROR_ILLEGAL_ADDRESS
```

Current telemetry replay output still shows:

```text
telemetry_replay: PASS_TELEMETRY_REPLAY_REPRODUCTION
median fitted sim/real p95 tracking ratio: about 0.981
max p95 fitted model error: about 0.035 rad
```

Interpretation:

- the actuator bridge reproduces the recorded target-to-actual relationship
  from real telemetry
- the local Playground contract matches `BEST_WALK_ONNX_2`
- closed-loop MuJoCo policy reproduction is blocked by the local ROCm/JAX/MJX
  runtime fault, not by robot evidence or policy/sim contract mismatch
- training remains blocked until the closed-loop runtime fault is fixed and the
  sim reproduction result is reviewed
