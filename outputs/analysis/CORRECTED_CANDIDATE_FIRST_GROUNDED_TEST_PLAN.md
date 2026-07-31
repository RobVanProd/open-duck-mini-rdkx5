# Corrected Candidate First Grounded Test Plan

status: `PREPARED_NOT_RUN`

This document defines the first grounded test that may be considered after the
corrected candidate cleared stand/suspended transfer at `x=0.0` and `x=0.08`.
It does not authorize the run by itself.

## Candidate

```text
policy: policy/candidates/corrected_bridge_cmd_conditioned_rate175_20260627/candidate.onnx
policy_sha256: 63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e
robot_policy_copy: /home/sunrise/corrected_bridge_cmd_conditioned_rate175_20260627.onnx
robot_policy_copy_sha256: 63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e
duck_config_sha256: 131a7b8fce1107b14f4727562f44f9e17324caf7fc22512ad7115911f050991b
```

The baseline `/home/sunrise/BEST_WALK_ONNX_2.onnx` must not be overwritten.

## Preconditions

All of these must be true immediately before the test:

- operator is physically present
- robot is on the ground only for this explicitly grounded test
- operator has immediate power cutoff access
- side-view observation or video is available
- feet have clear floor contact and no cable snag
- no people, fingers, or tools are inside the leg/foot work area
- candidate hash and `duck_config.json` hash match the values above
- no other walking/runtime process is running
- no tuning, gain, offset, IMU remap, action scale, phase timing, or policy file
  change is made before the run

## First Run

Use the smallest bounded useful test:

```text
command_x: 0.08
duration: 5 seconds maximum
telemetry: enabled, every tick
policy: corrected candidate copy, not BEST_WALK_ONNX_2
```

The candidate is intentionally slow. Sim gate tracking was about 42% of the
command, so the expected result is cautious forward motion or very slow stepping,
not full-speed walking.

## Stop Conditions

Cut power or stop the run immediately if any of these occur:

- body pitches forward hard
- feet scuff, cross, or snag
- robot yaws or rolls sharply
- one leg visibly drags or collapses
- any joint chatters, twitches, or sounds strained
- telemetry terminal reports write errors or repeated runtime exceptions
- operator is uncomfortable with the motion for any reason

Do not continue into another grounded run after a stop condition. Analyze the
telemetry first.

## Operator Approval Phrase

Before this test is run, the operator should explicitly approve this exact scope:

```text
Approved: run first grounded corrected-candidate x=0.08 telemetry test.
Robot is on the floor with immediate cutoff.
Duration max 5 seconds.
No tuning.
No BEST_WALK.
Stop after telemetry.
```

## Remote Command Template

Fill in a fresh timestamp before running. This command is intentionally bounded
with both runtime and shell timeouts.

```bash
set -euo pipefail
TS="$(date -u +%Y%m%dT%H%M%SZ)_corrected_candidate_x008_grounded_first"
LOG_DIR="/home/sunrise/duck_logs/${TS}"
mkdir -p "${LOG_DIR}"
cd /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts
PYTHONPATH=/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/mini_bdx_runtime \
timeout 20s /home/sunrise/duck_env/bin/python v2_rl_walk_mujoco.py \
  --onnx_model_path /home/sunrise/corrected_bridge_cmd_conditioned_rate175_20260627.onnx \
  --fixed_command_x 0.08 \
  --max_runtime_seconds 5 \
  --force_unpaused \
  --log-telemetry \
  --telemetry-path "${LOG_DIR}/corrected_candidate_x008_grounded_first.jsonl" \
  --telemetry-every-n 1
```

## Post-Run Analysis

Copy the telemetry back under `outputs/first_evidence/<timestamp>/`, then run:

```bash
python3 tools/instrumented_lowcmd_hw_eval.py analyze \
  outputs/first_evidence/<timestamp>/corrected_candidate_x008_grounded_first.jsonl \
  --output-md outputs/analysis/CORRECTED_CANDIDATE_HW_X008_GROUNDED_FIRST_ANALYSIS.md \
  --output-json outputs/analysis/corrected_candidate_hw_x008_grounded_first_analysis.json
```

Also preserve terminal output. If video exists, reference it in the decision
artifact without committing large video files by default.

## Pass / Hold

Pass requires all of:

- no fall
- no cutoff needed
- no write errors
- no action saturation burst
- no visible wrong-side/wrong-sign joint behavior
- no sustained pitch-chain tracking error above the stand-transfer envelope
- read checksum warnings, if present, do not correlate with control damage

Any stop condition, fall, write error, or obvious unstable body motion is a hold.
Do not tune around a hold before analyzing telemetry.
