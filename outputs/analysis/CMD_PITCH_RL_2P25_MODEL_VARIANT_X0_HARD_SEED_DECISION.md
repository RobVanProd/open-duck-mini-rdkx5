# Commanded Pitch-Rate Warm Start Model-Variant X0 Hard-Seed Decision

status: `HOLD_MODEL_VARIANT_GATE_MISMATCH`

This decision isolates why the command-conditioned pitch-rate-limited warm start
appeared to pass x=0.0 in earlier artifacts but failed the stricter support
transition smoke control.

## Question

Was the x=0.0 hard-seed failure caused by:

```text
1. the support-transition PPO smoke,
2. extending the gate from 10 s to 15 s,
3. switching task/model from flat_terrain_backlash to flat_terrain?
```

## Evidence

Earlier baseline:

```text
artifact: outputs/analysis/CMD_PITCH_RL_2P25_STEP0_X0_GATE.md
task: flat_terrain_backlash
duration: 10 s
seeds: 0-7
result: 8 / 8 duration-complete
```

Same-task strict baseline:

```text
artifact: outputs/analysis/CMD_PITCH_RL_2P25_STEP0_FLAT_X0_FITTED_15S.md
task: flat_terrain
duration: 15 s
seeds: 0-7
result: falls on seeds 1 and 7
```

Task-only hard-seed control:

```text
artifact: outputs/analysis/CMD_PITCH_RL_2P25_STEP0_FLAT_X0_FITTED_10S_HARD_SEEDS.md
task: flat_terrain
duration: 10 s
seeds: 1, 7
result: both seeds fall
```

Duration-only hard-seed control:

```text
artifact: outputs/analysis/CMD_PITCH_RL_2P25_STEP0_BACKLASH_X0_FITTED_15S_HARD_SEEDS.md
task: flat_terrain_backlash
duration: 15 s
seeds: 1, 7
result: both seeds pass
```

## Result

The hard-seed x=0.0 failure is task/model-variant driven, not primarily
duration-driven and not newly introduced by the support-transition PPO smoke.

| task | duration | seeds | result |
|---|---:|---|---|
| `flat_terrain_backlash` | 10 s | 0-7 | pass, 8 / 8 duration-complete |
| `flat_terrain_backlash` | 15 s | 1,7 | pass, 2 / 2 duration-complete |
| `flat_terrain` | 10 s | 1,7 | hold, 2 / 2 fall |
| `flat_terrain` | 15 s | 0-7 | hold, seeds 1 and 7 fall |

## XML Difference

`scene_flat_terrain.xml` includes:

```text
open_duck_mini_v2.xml
```

`scene_flat_terrain_backlash.xml` includes:

```text
open_duck_mini_v2_backlash.xml
```

The backlash model adds dummy backlash joints to the actuated leg chain and uses
different actuator/joint defaults. The key differences include:

```text
flat model:
  generic open_duck_mini_v2 joint frictionloss/armature active
  STS3215 position kp: 13.37
  no per-actuator backlash joints in the kinematic chain

backlash model:
  generic open_duck_mini_v2 joint frictionloss/armature commented out
  STS3215 position kp: 17.11
  +/-0.5 degree backlash joints added for leg actuators
  home keyframe qpos includes the added backlash coordinates
```

## Interpretation

The current best deployable warm start is model-variant sensitive. It is stable
at x=0.0 on the backlash model but not on the non-backlash flat model.

That does not automatically invalidate the candidate, because the real robot
does have servo/linkage compliance and the backlash model may be the intended
training/eval substrate. It does mean future reports must name the task/model
variant explicitly. A candidate that passes `flat_terrain_backlash` should not
be described as passing `flat_terrain`.

## Decision

Before the next PPO or robot discussion, choose the canonical offline promotion
model intentionally:

```text
Option A:
  canonical gate = flat_terrain_backlash
  rationale: closer to known servo/linkage compliance path
  requirement: every status table names backlash explicitly

Option B:
  canonical gate = flat_terrain
  rationale: stricter model without backlash joints
  consequence: current warm start fails x=0.0 hard seeds and cannot be promoted
```

Do not run more x=0.08 tuning until this gate choice is explicit.

No robot test, SSH, deploy, runtime behavior change, or policy overwrite was
performed.
