# Instrumented Low-Command Hardware Eval Handoff

status: `PREPARED_OPERATOR_HANDOFF_ONLY`

This is an operator handoff packet. The tool did not SSH, deploy, command motors, or run a policy.

## Scope

- fixed command x: `0.0`
- duration: `15.0` seconds
- corrected knee required: `True`
- duck_config hash: `131a7b8fce1107b14f4727562f44f9e17324caf7fc22512ad7115911f050991b`

## Checklist

- operator physically present
- robot supported on stand/catch rig
- corrected knee offset/hash recorded
- motors off before and after procedure unless the operator explicitly enables torque
- fixed low command only
- JSONL telemetry captured
- no grounded replay unless separately approved
- no tuning, remap, gain, action-scale, phase, policy, or duck_config change

## Telemetry Fields

- timestamp or dt_s
- action.motor_targets_sent_rad or equivalent 14-vector
- joints.actual_position_rad or equivalent 14-vector
- action.onnx_action if policy is used
- bus/read/write/CRC counters if available
- contacts/base pose if available

## Command Template

The command below is a placeholder for the operator-approved runtime harness. This tool does not execute it.

```bash
OPERATOR_ONLY_PLACEHOLDER --fixed-command-x 0.000 --duration 15.0 --jsonl outputs/first_evidence/<timestamp>/instrumented_lowcmd_hw_eval.jsonl
```

## Post-Run Analysis

After telemetry exists, run:

```bash
python3 tools/instrumented_lowcmd_hw_eval.py analyze \
  outputs/first_evidence/<timestamp>/instrumented_lowcmd_hw_eval.jsonl \
  --output-md outputs/analysis/INSTRUMENTED_LOWCMD_HW_EVAL.md \
  --output-json outputs/analysis/instrumented_lowcmd_hw_eval.json
```
