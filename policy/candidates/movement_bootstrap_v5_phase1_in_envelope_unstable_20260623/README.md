# Movement Bootstrap V5 Phase-1 Candidate

This package preserves the first candidate that showed nonzero forward motion
inside the measured actuator envelope. It is an evidence artifact, not a robot
deployment candidate.

- source run: `open-duck-a100-v5-staged-curriculum-20260623T181611Z`
- source phase: `01_phase1_feasible_low_command_mild_bridge`
- source checkpoint: `2026_06_23_182604_368640.onnx`
- sha256: `dcaa47993f65f4eedf980a78255d723409873b9b65e6a7d3d1002beeea7a3b48`
- policy contract: `obs[1,101] -> continuous_actions[1,14]`

Key sim evidence at `command_x=0.08` under the fitted bridge:

- local-frame forward velocity mean: about `0.189 m/s`
- command tracking ratio: about `2.37`
- max pitch-chain target velocity p95: about `1.95 rad/s`
- target velocity stayed below the measured `2.25-3.75 rad/s` envelope
- rollout terminated after about `80` samples

Interpretation:

The candidate is the current existence proof that in-envelope forward motion is
reachable on the stock ST3215 actuator budget. It is not stable enough for robot
validation. Later v5 phases destroyed this behavior, either by drifting
above-envelope or collapsing to standstill, so future work should stabilize this
behavior without leaving the measured actuator envelope or freezing.
