# Corrected Dynamic Replay Approval Packet

status: `AWAITING_EXPLICIT_OPERATOR_APPROVAL`

Purpose: collect corrected-knee dynamic policy-waveform telemetry after the
left-knee offset correction, without grounding the robot and without tuning.

This packet is not an approval. It records the exact scoped robot action that
would be run only after explicit operator approval.

## Current Evidence

- corrected left_knee offset: `0.0371 rad`
- duck_config sha256: `131a7b8fce1107b14f4727562f44f9e17324caf7fc22512ad7115911f050991b`
- corrected low-speed sine sweeps: `PASS`
- max sine-only pitch-chain p95 tracking:
  - `0.25 Hz`: `0.0103 rad`
  - `0.5 Hz`: `0.0076 rad`
  - `1.0 Hz`: `0.0103 rad`
- no write errors in corrected sine sweeps
- no grounded replay has been run
- no walking policy replay has been run after the knee correction

## Why This Test Exists

The corrected sine sweeps only reached about `0.17 rad/s` p95 target velocity
at `1.0 Hz`. The previous `x=0.08` policy waveform reached about `3-5 rad/s`.

Therefore the sine-only fit verifies low-speed corrected-knee tracking, but it
does not refresh the dynamic actuator bridge used for walking-policy decisions.
The next useful robot-side evidence is suspended/free-air policy-waveform
tracking.

## Hard Scope

```text
robot supported/on stand or suspended
operator physically present
policy replay suspended/free-air only
fixed command_x = 0.08
short duration
telemetry JSONL
terminal log
no grounded replay
no tuning
no gain/offset/remap/action-scale/phase changes
stop on unexpected motion, twitch, bus bursts, tracking spike, or operator concern
```

## Exact Command Template

The local wrapper should create a local output directory and copy telemetry
back after the run. The remote command itself is:

```bash
cd /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts
/home/sunrise/duck_env/bin/python sim2real_diagnostics.py suspended_policy_replay \
  --telemetry-path /home/sunrise/duck_logs/<timestamp>_corrected_dynamic_replay/suspended_policy_replay_x008_corrected_knee.jsonl \
  --onnx_model_path /home/sunrise/BEST_WALK_ONNX_2.onnx \
  --duration 15 \
  --command-x 0.08 \
  --action_scale 0.25 \
  --max_motor_velocity 5.24 \
  --telemetry-every-n 1 \
  --i-understand-this-moves-the-robot
```

`sim2real_diagnostics.py` initializes paused and requires Enter before replay
starts. The operator should visually confirm the robot is supported and safe
before allowing unpause.

## After Run

If approved and collected, analyze with:

```bash
python3 tools/analyze_policy_target_velocity.py \
  outputs/first_evidence/<timestamp>_corrected_dynamic_replay/suspended_policy_replay_x008_corrected_knee.jsonl \
  --output outputs/analysis/CORRECTED_DYNAMIC_REPLAY_TARGET_VELOCITY.md

python3 tools/fit_actuator_response_model.py \
  outputs/first_evidence/<timestamp>_corrected_dynamic_replay/suspended_policy_replay_x008_corrected_knee.jsonl \
  --selection-metric trimmed_rmse_95 \
  --output-md outputs/analysis/ACTUATOR_RESPONSE_FIT_CORRECTED_KNEE.md \
  --output-json outputs/analysis/actuator_response_fit_corrected_knee.json

python3 tools/compare_actuator_response_fits.py \
  --old outputs/analysis/actuator_response_fit.json \
  --new outputs/analysis/actuator_response_fit_corrected_knee.json \
  --output-md outputs/analysis/CORRECTED_KNEE_ACTUATOR_FIT_COMPARE.md \
  --output-json outputs/analysis/corrected_knee_actuator_fit_compare.json
```

No grounded replay should follow automatically.
