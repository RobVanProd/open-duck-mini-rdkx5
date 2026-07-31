# Compact Tracking Gate Feasibility Seeds 8-23 Preregistration

Date: 2026-07-11

Status: **COMPLETED; FAILS PASS-COUNT AND STABILITY CRITERIA**

Repeat the frozen seed 0-7 feasibility audit on independent seeds 8-23 with no
changes: rate-bounded teacher, `x=0.08`, `flat_terrain_backlash`, fitted bridge,
2.0 rad/s pitch-chain policy-action bound on indices `2,3,4,11,12,13`, one
second, no push, no settle, and the unchanged candidate gate.

The decision rates are inherited from the project's expanded 32-seed rule and
scaled exactly to 16 seeds:

- stability-compatible: falls <=2/16 (from <=5/32, conservatively rounded
  down);
- pass-count-compatible: passes >=2/16 (from >=4/32).

Interpretation:

- passes >=2 and falls <=2: independent evidence that the controller/gate pair
  can satisfy the project's existing distributional rates, while remaining
  reset-sensitive unless 16/16 pass;
- passes <2: compact feasibility does not replicate at the existing pass-rate
  requirement;
- falls >2: the teacher is not stability-compatible on this independent block.

Do not alter thresholds or train a policy from this audit. Its purpose is to
decide whether single-seed compact rejection is a valid prerequisite for the
existing distributional gate. CPU only with JAX and both GPU visibility
variables forced off. No robot, deployment, SSH, or grounded replay.
