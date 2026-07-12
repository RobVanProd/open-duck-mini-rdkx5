# Compact Tracking Gate Feasibility Seeds 8-23 Result

Date: 2026-07-11

Status: **FAILS PASS-COUNT AND STABILITY CRITERIA**

The frozen rate-bounded teacher completed the preregistered independent
one-second `x=0.08` block on seeds 8-23.

- passes: `1/16` (seed 10), below the required `2/16`;
- falls: `5/16` (seeds 9, 12, 14, 19, 20), above the allowed `2/16`;
- tracking holds: `3/16` (seeds 8, 18, 22);
- low-progress holds: `7/16` (seeds 11, 13, 15, 16, 17, 21, 23);
- mean velocity: `-0.0540 m/s`;
- mean command ratio: `-0.6744`.

The five fall seeds exactly match the frozen Stage A baseline's fall seeds in
the same independent block. The rate-bounded teacher therefore does not change
survival membership on these hard resets. It is not a distributionally stable
feasibility oracle and cannot justify weakening or removing the compact gate.

Combined with discovery seeds 0-7, the teacher passes only `2/24` compact
resets. The evidence supports separating two contracts already documented in
the repository:

1. normal grounded walking from explicit `home-support` reset;
2. unsupported-start recovery under broad `playground` reset.

Further scalar Stage A training on the broad reset is suspended. The existing
grounded-start branch must not be blocked by failure to recover unsupported
random starts, and unsupported recovery must remain a separate research gate.
No threshold, reset, or policy was changed by this audit.

Primary evidence:

- `outputs/analysis/phase2_compact_tracking_gate_feasibility_seed8_23.json`
- `outputs/analysis/phase2_stage_a_reset_neighborhood_expansion_seed8_23.json`

CPU-only. No GPU, robot, SSH, deployment, grounded replay, or moving hardware
test was used.
