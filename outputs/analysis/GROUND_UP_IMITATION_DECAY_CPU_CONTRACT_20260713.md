# Ground-Up Imitation-Decay CPU Contract

status: `PASS_GATE_AND_RESUME_PLANNER_CPU_ONLY`

## Mechanism

`tools/plan_ground_up_imitation_decay.py` reduces the current imitation scale
by exactly one half only when two distinct consecutive checkpoint evaluations
both pass the frozen ground-up gait-emergence gate. It also requires:

- both evaluations to use `ground_up_policy_eval.v1`;
- moving-command emergence and finite recorded x=0 behavior in both;
- two distinct policy hashes;
- an existing restore checkpoint;
- positive current imitation scale and additional timestep count.

When any condition fails, the planner emits no training argv.

## Negative-path evidence

The real 1,024-step reference-conditioned CPU smoke was evaluated twice as an
input deliberately incapable of satisfying the gate. The planner returned
`HOLD_IMITATION_DECAY_STAGE` for both missing gait emergence and duplicate
checkpoint identity. Its recorded resume argv is `null`:

`outputs/analysis/ground_up_imitation_decay_hold_contract.json`

## Positive-path contract evidence

Two minimal schema-valid fixtures with distinct policy hashes exercised the
positive path. With an existing Orbax checkpoint, current scale `1.0`, and
1,000,000 additional timesteps, the planner returned
`READY_IMITATION_DECAY_STAGE`, set the next scale to exactly `0.5`, preserved
the checkpoint and PPO geometry, and included the absolute hashed-reference
feature-table path in its argv.

The fixtures prove control flow only; they are explicitly not behavioral
evidence and are never inputs to candidate promotion.

## Boundary

All checks were local CPU/file operations. No Colab unit, GPU, RDK, robot,
deployment, torque, or motor activity occurred. Actual imitation decay remains
blocked until real consecutive checkpoint evaluations pass.
