# Movement Bootstrap V15B A100 No-Sentinel Summary

status: `HOLD_REMOTE_NO_SENTINEL_POST_STEP0`

## Context

V15 phase 1 was relaunched on A100 after the export-handoff fix:

```text
recipe: movement_bootstrap_v15
phase: phase1_no_bridge_high_entropy_gait_discovery
session: open-duck-a100-v15b
export_min_step: 1
robot_touched: false
```

The run again disappeared without writing the workflow `.exit` sentinel or
artifact bundle. The Colab session reported idle and the remote log stopped
growing.

## Recovered Artifacts

Recovered files:

```text
outputs/analysis/movement_bootstrap_v15b_a100_phase1_no_sentinel/stdout.txt
outputs/analysis/movement_bootstrap_v15b_a100_phase1_no_sentinel/stderr.txt
outputs/analysis/movement_bootstrap_v15b_a100_phase1_no_sentinel/smoke_manifest.start.json
```

No ONNX, checkpoint, final manifest, or artifact bundle was produced.

## Log Finding

The run reached step 0 and the new export guard was active:

```text
STEP: 0 reward: -191.49404907226562 reward_std: 169.26931762695312
Skipping checkpoint/export at step 0; export_min_step=1
```

There is no Python traceback. Stderr only contains the menagerie clone progress
and a JAX overflow warning during startup:

```text
RuntimeWarning: overflow encountered in cast
```

## Interpretation

The first V15 A100 failure happened immediately after step-0 ONNX export. V15B
proves skipping step-0 export works, but the Colab A100 process still dies
after step 0, before any later PPO progress callback.

This is an offline training infrastructure hold, not a policy-quality result.
The next low-risk debugging step is to run a smaller A100 smoke/phase-1
configuration with fewer envs/batch size, or to run the same V15 phase on a
different CUDA backend, before spending more full A100 time.

Robot validation remains blocked.
