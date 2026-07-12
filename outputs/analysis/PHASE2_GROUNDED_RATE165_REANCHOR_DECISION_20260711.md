# Phase 2 Grounded Rate165 Re-Anchor Decision

Date: 2026-07-11

Status: **PASS_OFFLINE_GROUNDED_CANDIDATE_CURRENT**

## Decision

Re-anchor the normal-start walking track to the preserved candidate:

`policy/candidates/phase2_corrected_live_oracle_iter1_rate165_20260703`

Its recorded hashes verify exactly:

- ONNX: `e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33`;
- NPZ: `2a896d32b9e40565008073970cacc9d31c8543e5ee8f3ee44162c5ddcd73ed36`.

The authoritative existing gate remains 8/8 passes at both `x=0.08` and
`x=0` for 15 seconds under `rough_terrain_backlash`, `z=0.0026`, explicit
`home-support` reset, and the corrected fitted bridge.

Current-tool seed-0 regressions reproduced the recorded metrics exactly:

| command | status | duration | vx | ratio | tracking p95 | velocity excess |
|---:|---|---:|---:|---:|---:|---:|
| 0.08 | pass | 15 s | 0.0272 | 0.3400 | 0.1827 | 0.0000 |
| 0.00 | pass | 15 s | -0.0000 | NA | 0.0317 | 0.0000 |

No compatibility regression exists, so the prior 8/8 evidence remains
authoritative without rerunning identical deterministic home-support seeds.

## Contract Separation

The later broad-reset Stage A work addressed a different problem: recovery
from randomized `playground` starts, including unsupported postures. Its frozen
teacher and baseline share the exact hard-reset fall set on seeds 8-23, and the
teacher failed the independent distributional criteria. Those failures do not
invalidate normal grounded walking, and the grounded candidate does not claim
unsupported-start recovery.

Canonical interpretation:

1. `home-support`: normal grounded walking contract; candidate is current and
   offline-ready for review;
2. `playground`: unsupported-start recovery research contract; unresolved and
   not a deployment prerequisite unless the real start protocol requires it.

## Safety Boundary

This is an offline evidence handoff, not robot approval. No SSH, deploy,
grounded replay, hardware command, or moving test was performed. Any robot-side
validation requires an explicit reviewed request and physical support.

Primary current artifacts:

- `outputs/analysis/PHASE2_GROUNDED_RATE165_CURRENT_TOOL_X008_SEED0.md`;
- `outputs/analysis/phase2_grounded_rate165_current_tool_x008_seed0.json`;
- `outputs/analysis/PHASE2_GROUNDED_RATE165_CURRENT_TOOL_X0_SEED0.md`;
- `outputs/analysis/phase2_grounded_rate165_current_tool_x0_seed0.json`.
