# Live-Oracle Command-Gated X0-Safe Diagnostic

status: `HOLD_X008_TRACKING_PLATEAU_X0_SOLVED_BY_COMMAND_GATE`

This diagnostic composes two existing deployable ONNX students without changing
the deployed observation/action contract:

- low-command branch: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate/candidate.onnx`
- high-command branch: `outputs/analysis/live_oracle_dagger_phase_student_iter0_candidate/candidate.onnx`
- command gate: `abs(obs[6]) <= 0.02`
- output: `outputs/analysis/live_oracle_command_gated_x0safe_iter0_candidate/candidate.onnx`

The wrapper is an offline analysis artifact. It did not train, deploy, SSH, run
robot tests, or change robot runtime behavior.

## ONNX Gate Verification

`outputs/analysis/live_oracle_command_gated_x0safe_iter0_onnx_gate_verify.json`

- status: `PASS_ONNX_GATE_VERIFY`
- max absolute action error versus selected source branch: `0.0`
- x=0.0 and x=0.01 selected the low-command branch
- x=0.03, x=0.08, and x=-0.08 selected the high-command branch

## Canonical X0 Gate

`outputs/analysis/LIVE_ORACLE_COMMAND_GATED_X0SAFE_ITER0_X0_GATE.md`

- task: `flat_terrain_backlash`
- bridge: `fitted`
- duration: `15s`
- seeds: `0-7`
- duration complete: `8 / 8`
- falls: `0 / 8`
- mean local vx: `0.0003 m/s`
- max pitch-chain sent velocity p95: `0.4067 rad/s`
- max pitch-chain tracking p95: `0.0718 rad`

Result: `PASS_X0_COMMAND_SEMANTICS`

The command-gated structure fixes the zero-command drift/collapse failure that
scalar zero-action relabeling could not fix. In particular, seed 5 completes
the full 15s x=0.0 gate.

## Canonical X008 Gate

`outputs/analysis/LIVE_ORACLE_COMMAND_GATED_X0SAFE_ITER0_X008_GATE.md`

- task: `flat_terrain_backlash`
- bridge: `fitted`
- duration: `15s`
- seeds: `0-7`
- duration complete: `8 / 8`
- falls: `0 / 8`
- mean track ratio: `0.5613`
- max pitch-chain sent velocity p95: `3.6791 rad/s`
- max pitch-chain tracking p95: `0.2665 rad`

Result: `HOLD_X008_TRACKING_PLATEAU`

The high-command branch is intentionally the iteration-0 movement student, so
the x=0.08 result reproduces the known stable moving plateau: good forward
motion and no falls, but strict pitch-chain tracking remains above the
pre-registered `0.20 rad` threshold.

## Interpretation

This diagnostic cleanly separates two failure modes:

- x=0.0 command semantics are a command-conditioning/branching problem, not an
  unavoidable property of the source-VX movement behavior.
- x=0.08 strict tracking is still a representation/training-signal problem. A
  hard command gate alone cannot break the `~0.26 rad` plateau.

Do not promote this wrapper as a robot candidate. It is useful evidence for the
next representation rung: the student likely needs explicit command-conditioned
structure, and the x=0.08 branch still needs a memory/phase or live-oracle
representation change that reduces tracking without destroying forward motion.
