# Winner-v12 calibrator CPU-smoke contract

- Status: `PASS_WINNER_V12_CALIBRATOR_CPU_SMOKE_CONTRACT`
- Decision: `AUTHORIZE_ONE_WINNER_V12_CPU_SMOKE_ONLY`
- Superseded attempt: run `29801884782` was invalid before simulation (0 optimizer updates, 0 smoke physics steps)
- Execution: one CPU-only 16-environment × 250-tick smoke
- Optimizer: exactly one Stage-1 update and one Stage-2 update
- Formal support cells: `0`
- Robot clearance: `false`

The smoke validates training plumbing, stage isolation, automatic response
routing, save/restore, and the deployable ONNX boundary. It does not select
a policy or measure supported-configuration behavior.

The observation observer is always the runtime P30 observer. Alternating
P30/P31-34 selections are hidden physical plants only; they cannot alter
obs[83:97] directly or enter the actor, critic, or auxiliary target as labels.

A pass stops for review and permits only a separate prospective full-training
preregistration. It grants no hosted compute, X5, Gate 5, or robot authority.
