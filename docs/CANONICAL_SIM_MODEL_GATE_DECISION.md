# Canonical Sim Model Gate Decision

status: `RECOMMEND_CANONICAL_FLAT_TERRAIN_BACKLASH`

Purpose: stop silently mixing `flat_terrain` and `flat_terrain_backlash` gate
results when judging deployable Open Duck Mini policies.

## Finding

The command-conditioned pitch-rate-limited warm start has a sharp x=0.0
hard-seed split by model variant:

```text
flat_terrain, x=0.0, 10 s, seeds 1 and 7:
  both seeds fall

flat_terrain_backlash, x=0.0, 15 s, seeds 1 and 7:
  both seeds pass
```

Decision artifact:

```text
outputs/analysis/CMD_PITCH_RL_2P25_MODEL_VARIANT_X0_HARD_SEED_DECISION.md
```

This makes task/model selection a first-class gate condition.

## Recommendation

Use `flat_terrain_backlash` as the canonical offline promotion model for the
current sim-to-real branch.

Rationale:

```text
- upstream Open Duck Mini v2 training/audit commands reference flat_terrain_backlash
- the published-policy/reference propulsion audits were run on flat_terrain_backlash
- the real robot has servo/linkage compliance, so the backlash model is the more
  plausible sim-to-real substrate than the no-backlash flat model
- the current deployable warm-start lineage was mainly evaluated on fitted
  bridge + flat_terrain_backlash gates
```

Use `flat_terrain` as a stress/ablation gate, not as a silent replacement for
the canonical promotion model.

## Required Reporting

Every candidate gate must report:

```text
task: flat_terrain or flat_terrain_backlash
xml/model: scene_flat_terrain.xml or scene_flat_terrain_backlash.xml
duration
seeds
bridge mode
```

A candidate that passes `flat_terrain_backlash` has not passed `flat_terrain`
unless that exact gate was run.

## Promotion Rule

Before robot-side suspended validation, a candidate should pass:

```text
x=0.0, flat_terrain_backlash, fitted bridge, full seed set
x=0.08, flat_terrain_backlash, fitted bridge, full seed set
```

Optional but valuable stress checks:

```text
x=0.0, flat_terrain, fitted bridge, hard seeds 1 and 7
x=0.08, flat_terrain, fitted bridge, hard seeds selected from the canonical gate
```

Failing the stress checks should be reported, but it should not be mixed into
the canonical pass/fail statement unless the team explicitly changes the
canonical model.

## Support-Transition Smoke Check

The first tiny support-transition recovery smoke confirms why the model name
must be part of every gate:

```text
candidate: /tmp/open_duck_support_transition_recovery_finetune/smoke_20260627T021502Z_cpu/2026_06_26_221541_1040.onnx

flat_terrain, x=0.0, fitted bridge, 15 s, seeds 0-7:
  falls: seeds 1 and 7

flat_terrain_backlash, x=0.0, fitted bridge, 15 s, hard seeds 1 and 7:
  duration complete: 2 / 2

flat_terrain_backlash, x=0.08, fitted bridge, 15 s, seeds 0-7:
  duration complete: 7 / 8
  fall/termination: seed 3 at 78 samples
  mean vx: -0.0284 m/s
  mean track ratio: -0.3549

matched warm-start baseline, same gate:
  duration complete: 8 / 8
  falls: 0
  mean vx: 0.0348 m/s
  mean track ratio: 0.4344
  hold reason: tracking
```

Interpretation: the smoke is not a deployable candidate. It passes the
canonical hard-seed x=0 standing check, but it fails the canonical x=0.08
forward-motion gate and regresses against the matched warm-start baseline. The
earlier `flat_terrain` x=0 failure should be retained as stress evidence, not
used as the canonical promotion result.

## Robot Boundary

This decision does not authorize robot validation, deployment, runtime changes,
or `duck_config.json` edits. It only defines how offline sim gates should be
named and interpreted.
