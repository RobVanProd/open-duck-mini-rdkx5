# Compact Tracking Gate Feasibility Seed 0-7 Result

Date: 2026-07-11

Status: **MIXED RESULT; COMPACT GATE IS RESET-SENSITIVE**

The frozen rate-bounded teacher was evaluated for one second at `x=0.08` on
seeds 0-7 using the unchanged fitted bridge and candidate gate.

- passes: `1/8` (seed 4);
- tracking holds: `5/8` (seeds 0, 1, 2, 5, 7);
- low-progress holds: `2/8` (seeds 3, 6);
- falls: `0/8`;
- mean velocity: `0.0275 m/s`;
- mean command ratio: `0.3436`.

The strongest known stable teacher can pass the compact contract, so the gate
is not universally infeasible. It fails on seven of eight reset seeds despite
completing all eight 15-second runs without falls, so seed-0 compact failure is
not evidence of general instability or lack of forward capability. The gate is
reset-sensitive under the preregistered rule.

Do not change the threshold, discard the gate, resume policy training, or
reinterpret prior branches from this discovery block. Run the separately
preregistered independent reset block first.

Primary evidence:

- `outputs/analysis/phase2_compact_tracking_gate_feasibility_seed0_7.json`

CPU-only. No GPU, robot, SSH, deployment, grounded replay, or moving hardware
test was used.
