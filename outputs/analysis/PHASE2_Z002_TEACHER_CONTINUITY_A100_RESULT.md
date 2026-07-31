# Phase 2 z=0.002 Teacher-Continuity A100 Result

status: `HOLD_Z002_TEACHER_CONTINUITY_A100_MISCONFIGURED_NOT_PROMOTED`

This was an offline Colab A100 run. It did not SSH, deploy, touch the robot, run grounded replay, or change runtime behavior.

## Run

- workflow: `phase2-z002-teacher-continuity`
- Colab session: `open-duck-l4`
- hardware: `A100`
- remote run: `open_duck_colab_cli_phase2-z002-teacher-continuity_20260630T031748Z`
- training return code: `0`
- elapsed_s: `737.4981`
- exported checkpoints: `40960`, `81920`, `122880`
- remote exit sentinel: `missing`
- remote artifact bundle: `downloaded`

## Configuration Finding

The run was not a clean test of the intended teacher-continuity recipe. The recipe specified a light actuator-tracking term:

```text
actuator_tracking_scale = -0.005
```

The generated remote training command actually used:

```text
actuator_tracking_scale = -0.04
```

That mismatch came from the Colab workflow generator and has been fixed for the next launch.

## ONNX Exports

| step | sha256 | size bytes |
|---:|---|---:|
| 40960 | `bb1f9181d839c5971ae587a30decf3606354661c86f5eb409259cfec32c81b20` | 883946 |
| 81920 | `e781d3242bd289c91405404f9e6bc30bdab4a15eadbc1da65cc42ed1e2cfd159` | 884094 |
| 122880 | `b621a1f00ca1d92f6e002bbbd5fefec13601e1b44775020bbc9fa2e6b572c3b8` | 884094 |

## Compact Corrected-Bridge Sweep

Local CPU sweep:

```text
commands: 0.0,0.08
duration: 1.0 s
bridge: corrected fitted actuator bridge
platform: CPU closed-loop eval
```

| checkpoint | x=0.0 | x=0.08 | x=0.08 track ratio | x=0.08 mean vx | max pitch vel p95 | max tracking p95 |
|---|---|---|---:|---:|---:|---:|
| `40960` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.2026 | 0.0162 | 1.5504 | 0.2177 |
| `81920` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.2377 | 0.0190 | 1.5486 | 0.2175 |
| `122880` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_TRACKING` | 0.3016 | 0.0241 | 1.4881 | 0.2161 |

No checkpoint promoted. The latest checkpoint preserved meaningful in-envelope motion and improved tracking slightly versus the scalar A100 run, but it still held above the `0.20 rad` tracking threshold.

## Decision

Do not promote this run. Because the run used the wrong actuator-tracking scale, do not treat it as a falsifier of the teacher-continuity recipe.

The next aligned action is to rerun `phase2-z002-teacher-continuity` after the workflow-generator fix, confirming the remote training summary reports `actuator_tracking_scale = -0.005`.

Robot validation remains blocked.
