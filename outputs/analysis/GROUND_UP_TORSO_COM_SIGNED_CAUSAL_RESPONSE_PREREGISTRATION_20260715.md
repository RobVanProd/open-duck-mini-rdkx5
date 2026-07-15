# Ground-Up Torso-COM Signed Causal-Response Preregistration

status: `PREREGISTERED_READ_ONLY_CPU_SIGNED_CAUSAL_RESPONSE`

## Evidence question

The completed full-observation study produces two facts that cannot yet select
a policy family. Under the frozen linear probes, COM class is recovered only
at the deterministic reset transient. Independently, all six actors materially
change output when only `obs[3:6]` is moved along the measured NEG-to-POS COM
direction. The output response is real, but its physical sign is unknown.

This study asks one question: from the same nominal physical state, does the
actor action caused by a more POS-like accelerometer input create a pitch
trajectory that opposes or reinforces the pitch trajectory caused by moving
the physical torso COM from NEG to POS?

This is a deterministic causal sign audit, not a statistical population test.
It reports no p-value, confidence interval, or independent-sample claim.

## Frozen sources

- full-observation result JSON SHA-256:
  `e55462259ab5c850f7226e0a9e107a985ee6007a1ceaf1b8fa5eec025f83ede7`;
- exact replay manifest SHA-256:
  `ac42abc8a940d97f0c0373ce624eaf2d2f803ac574e0de52c82303c7a759da07`;
- replay trace-manifest SHA-256:
  `7d7ccbe3b06e3a58546be5da02bdb138a218c08c11a0f10dea74a29d891c9f01`;
- six contracted ONNX manifest SHA-256:
  `d50bfc57e29dea9479d16506d175175e6a94f69c5d62700168d5bf9df3cadac4`;
- P30 actuator fit SHA-256:
  `908ddb01e5d82e661d77b8f3cb186a84665695660b86b304c6d1ae89c79cdb0b`;
- P31/34 actuator fit SHA-256:
  `a39776c06c5e26425e24b50e7dab3f441823e23904cad4977b8c921d9c9ca276`;
- playground control commit: `b9be205ac64488c23504ca42e5ec790337adeec3`;
- composed `joystick.py` SHA-256:
  `3f7c63918ec811259eaa1c0020abd504e25336d1a7d9fbfefe2cc08baaa5521b`;
- flat-backlash scene SHA-256:
  `33af97247d6a876cf47c9e37185cb71bd09f6793bc0f62d90cbe2a91caa3ba63`;
- actuator bridge source SHA-256:
  `3c9f2714f394d6f9f0c7e7baa693311eb7cf562617cabc4cd03d063db09dadce`.

The measured observation direction remains exactly:

`d = [1.1654748916625977, 0.11948448419570923, 1.0919904708862305] m/s^2`.

## Frozen cells and states

Use only the 36 nominal moving-command traces:

- six policies;
- P30 and P31/34 measured actuator fits;
- commands x=.074/.077/.080;
- deterministic seed 167931544;
- fork ticks `[0,24,32,40]`.

This produces exactly 144 signed cells, 24 per policy. The x=0 deadband cells
are excluded prospectively because both observation forks are required to
remain zero there and cannot measure action-response sign. Endpoint-condition
states are excluded because their physical trajectories have already diverged;
the causal comparison must begin from a common nominal state.

At tick zero, physical state is the exact deterministic home-support reset. At
tick `t>0`, the pre-policy physical state is the preceding trace row's saved
`qpos`, `qvel`, and applied control. The ONNX recurrent input is reconstructed
sequentially from zero through tick `t`. The fitted actuator bridge is
reconstructed from home through the saved sent-target sequence before tick
`t`. Every reconstruction must reproduce the saved baseline ONNX action, sent
target, and applied target at the fork boundary within the contract tolerance;
otherwise the cell is invalid rather than repaired.

## Frozen matched interventions

Each cell creates two separate matched pairs from the identical source state.
Both use the native CPU MuJoCo model, the measured fit for that cell, 20 ms
control ticks, the model's unchanged substep count, the existing environment
target-rate stage, and the reconstructed delay/tau/velocity bridge.

### Physical disturbance pair

- `COM_NEG`: change only `body_ipos[2,0]` on name-resolved
  `trunk_assembly` by -0.05 m;
- `COM_POS`: change only the same field by +0.05 m;
- apply the exact saved baseline action sequence from fork tick through fork
  tick + 7 in both branches.

No observation or policy output enters the difference between these branches.

### Actor-response pair

- keep the physical model nominal in both branches;
- reconstruct the exact ONNX recurrent input at the fork;
- `ACTION_NEG`: subtract `d` only from observation indices `[3:6]` for the
  fork-tick ONNX call;
- `ACTION_POS`: add `d` only to those same indices;
- use the resulting contracted graph output only at the fork tick;
- use the identical saved baseline actions for the next seven ticks in both
  branches.

The recurrent output from the counterfactual call is not fed forward because
the purpose is the isolated physical effect of the one measured actor response,
not an unregistered recurrent intervention. No other observation, physical
state, model field, bridge state, command, action, or future control changes
within either matched pair.

## Frozen response and sign metric

Record signed base pitch after each of eight control ticks. Define:

- disturbance vector `D[h] = pitch_COM_POS[h] - pitch_COM_NEG[h]`;
- actor vector `A[h] = pitch_ACTION_POS[h] - pitch_ACTION_NEG[h]`;
- signed alignment `c = dot(D,A) / (norm(D) * norm(A))`.

Also report the corresponding pitch-rate, base-height, local-vx, sent-target,
and applied-target branch differences as secondary diagnostics. They do not
select the result.

A cell is:

- `CORRECTIVE` if both vector norms are at least 1e-6 rad and `c <= -0.25`;
- `AMPLIFYING` if both norms are at least 1e-6 rad and `c >= +0.25`;
- `ORTHOGONAL_OR_MIXED` if both norms are at least 1e-6 rad and
  `-0.25 < c < +0.25`;
- `PHYSICALLY_NEGLIGIBLE` if either norm is below 1e-6 rad.

The +/-0.25 boundaries and 1e-6-rad magnitude floor are frozen before any
cell outcome. Pitch quaternion conversion and subtraction order must be the
same in all branches. No absolute-value sign erasure is allowed.

## Frozen policy-level persistence

Each policy has 24 cells. It is `SYSTEMATIC_CORRECTIVE` only if all are true:

- at least 18/24 cells are `CORRECTIVE`;
- no more than 2/24 are `AMPLIFYING`;
- each actuator fit has at least 8/12 corrective cells; and
- each fork tick has at least 4/6 corrective fit/command cells.

`SYSTEMATIC_AMPLIFYING` uses the exact symmetric rule with corrective and
amplifying exchanged. `PHYSICALLY_NEGLIGIBLE_POLICY` requires at least 18/24
negligible cells. Every other pattern is `MIXED_POLICY_RESPONSE`.

Both temporally distinct checkpoints of an arm must receive the same systematic
classification before that arm can support a family-level interpretation. No
closest checkpoint or arm is promoted.

## Frozen decision

1. If all six policies are `SYSTEMATIC_CORRECTIVE`, decision
   `SUPPORT_MEMORY_OR_ESTIMATOR_PREREGISTRATION`: the actor's local physical
   sign is already corrective, while the prior probe found no persistent class
   decode; separately preregister a mechanism that carries or supplies the
   latent estimate.
2. If all six are `SYSTEMATIC_AMPLIFYING`, decision
   `SUPPORT_OBJECTIVE_SIGN_PREREGISTRATION`: the current learned local response
   reinforces the disturbance; separately preregister an objective/formulation
   study before any training.
3. If all six are `PHYSICALLY_NEGLIGIBLE_POLICY`, decision
   `SUPPORT_ACTUATOR_EFFECT_FORMULATION_PREREGISTRATION`: the substantial ONNX
   response does not create material pitch authority through the measured
   transport.
4. Otherwise decision `MIXED_SIGN_NO_POLICY_FAMILY_SELECTED`. Record the exact
   policy/fit/command/tick localization; a new study may be preregistered, but
   no architecture or objective family follows automatically.

These decisions authorize only the named next preregistration. They do not
authorize implementation, training, checkpoint selection, or policy promotion.

## Contract and authority boundary

Before formal cells, a committed CPU contract must prove exact source hashes,
CPU-only JAX/MuJoCo/ONNX execution, graph identity, name-resolved body-2 X-only
COM mutation, trace-state indexing, ONNX recurrent reconstruction, bridge
queue reconstruction, saved baseline target reproduction, branch cloning, and
matched-pair isolation. It must show identical branches are numerically exact
and each intended intervention is nonzero. No formal cell may run before that
contract passes.

This preregistration authorizes one contract and one exact 144-cell read-only
CPU study. It authorizes no outcome retry, threshold/horizon/tick/state/command
change, policy or reward modification, training, Colab, GPU/iGPU, R2/R3,
explicit COM input, memory implementation, runtime design, RDK-X5, robot
access, deployment, torque, or motors.
