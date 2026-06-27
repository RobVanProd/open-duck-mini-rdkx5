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

## Robot Boundary

This decision does not authorize robot validation, deployment, runtime changes,
or `duck_config.json` edits. It only defines how offline sim gates should be
named and interpreted.
