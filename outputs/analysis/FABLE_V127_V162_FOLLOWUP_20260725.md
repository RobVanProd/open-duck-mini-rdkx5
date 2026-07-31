# Fable follow-up: V127 through V162

We executed the previously selected mechanism and its preregistered successor
family. This is the evidence-complete follow-up. Select one next mechanism
class only if it is mechanically distinct, preserves the frozen deployment
contract, and has a CPU-only falsifier that can reject it before hosted
training.

## Frozen success rule

- Policy observation ABI: 115-D actor input produced from the frozen 101-D RDK
  observation plus the existing 14-D projected-reference action.
- Stateful ONNX: `obs`, `h_in`, `previous_action` to
  `continuous_actions`, `h_out`, `previous_action_out`.
- Actions: 14, existing home, G3 guard, x=0 deadband, measured per-joint rate
  projection, and final-action feedback.
- Both preregistered checkpoints must each pass all eight 600-tick nominal
  cells: P30/P31-34, x=0/.074/.077/.080, seed 167931544.
- Torque peak `<=1.91229675 N.m`; current peak `<=2.5 A`; all unchanged
  tracking, gait, rate, saturation, duration, and x=0 gates.
- Only after 16/16 may the complete frozen robustness matrix run.
- No checkpoint cherry-pick, threshold change, retry selected from behavior,
  or Gate-5/robot authority.

## What happened to the selected PPO-Lagrangian mechanism

V127 implemented the proposal exactly:

- dense per-tick torque-exceedance cost outside reward clipping;
- separate cost critic and cost GAE;
- derived dual update, no scalar sweep;
- exact V121-half restore;
- one hosted continuation only;
- exports at +1,003,520 and +2,007,040.

The run was valid. V128 nominal behavior was:

- constrained half: `2/8`, worst torque `2.11871719 N.m`;
- constrained final: `8/8`, worst torque `1.84084892 N.m`.

The persistence rule rejected it. PPO-Lagrangian is closed with no eta retry,
resume, or checkpoint selection. The late checkpoint proves a safe nominal
closed loop exists in this actor family; the early-to-late reversal proves the
mechanism did not keep training inside that set.

## What happened to the prescribed oracle-teacher successor

The exact two-fit sim oracle passed all eight V121-final cells, with zero empty
intersections. The teacher therefore existed.

The successor family was then exhausted:

- V129 adapter-head distillation: loss did not persistently improve; closed
  before behavior.
- V133 compact local residual: held-trace event recall `0.1111`; closed.
- V134 full-actor teacher update: corrected error improved, but preservation
  leakage exceeded the frozen 1% limit.
- V137 recurrent sequence teacher: same preservation failure.
- V140 behavior-blind preservation projection of V134 produced the strongest
  near-candidate.
- V141: V140 final missed only P30 x=.074 right-ankle torque,
  `1.92083263 N.m`.
- V144 exact shadow oracle labeled the safe precursor correction.
- V148-V151 finite local residuals displaced the failure; the family was
  capped and closed.
- V152-V157 phase/contact/velocity gates fixed the causal x=.074 cell, then
  failed immediately at P30 x=.077; this family was closed.
- V145-V147 full-actor, global-direction, and head-only on-policy DAgger
  updates failed the same correction-versus-preservation contract.

No teacher/distillation variant earned hosted training.

## Complete V140 failure surface

V158 and V160 completed exact shadow-oracle traces for all six moving
plant/command cells on the unchanged V140 trajectory.

New V160 cells:

- P30 x=.080: already safe, peak `1.89452744 N.m`;
- P31/34 x=.074: five violations, peak `2.00883770 N.m`;
- P31/34 x=.077: two violations, peak `1.99059296 N.m`;
- P31/34 x=.080: two violations, peak `2.06777191 N.m`.

Across V160:

- nine actual violations;
- only left knee and right ankle;
- 26 projected joint events;
- zero empty intersections.

Across the complete six moving traces, after excluding ordinary supreme/rate
clips and keeping only torque-projection action deltas:

- 20 nonzero joint labels total;
- left knee: 16;
- right ankle: 4.

A preservation-first leave-one-(plant,command)-trace-out linear classifier on
the full runtime-observable observation, recurrent state, and previous action
recalled only `3/16` left-knee and `1/4` right-ankle labels, with false
positives. This was diagnostic only, but it collapses the prior for another
sparse learned residual.

## Other frozen-contract falsifiers

V159 tried the only untouched runtime timing knob as a one-point CPU screen:
phase-frequency factor `0.95`, the existing controller's single `-0.05`
quantum. It failed before behavior because the actor's 14-D reference-action
slot and the RDK winner-v2 adapter both require one integer phase step per
tick. Interpolation would change the frozen observation contract. Cadence is
closed as nondeployable under this policy contract.

V161 tested a zero-credit common trust projection:

```text
theta_i(alpha) = theta_V121_half
               + alpha * (theta_V128_i - theta_V121_half)
```

The same alpha was applied to both constrained checkpoints. Alpha was selected
without torque or behavior, using the inherited V140 preservation budget over
all 4,800 green-source states.

- selected alpha: `0.0015716552734375`;
- maximum budget use: `0.9994685084`;
- transformed policies remained distinct.

V162 stopped at the first failure:

- half P30 x=0: pass;
- half P30 x=.074: pass, peak `1.79370499`;
- half P30 x=.077: pass, peak `1.88560677`;
- half P30 x=.080: fail, peak `1.92917061`.

The preregistration forbids an alpha retry. Uniform post-training trust
projection is closed.

## Current causal statement

The exact oracle proves the remaining violations are controllable in sim, but
the required precursor action is sparse, joint-specific, command-dependent,
plant-dependent, and not reliably separable from ordinary gait states by the
tested deployable residual representations. A later constrained PPO policy is
nominally safe, but its training path is not persistently safe. The remaining
problem is therefore not bus timing, observation blindness, an unavailable
safe action, or an error-counter issue. It is persistent policy optimization
inside a very narrow closed-loop feasible set.

## Candidate next class for critique

The only mechanically distinct frozen-contract class we can currently justify
is a **feasibility-preserving constrained continuation**:

1. Start from the green V121-half source.
2. Keep the V127 dense cost critic/GAE only as a proposal generator; do not
   retry or tune its dual.
3. After every PPO proposal, use an exact deterministic nominal feasibility
   acceptance test and backtrack the entire parameter update to the largest
   step that leaves all eight nominal cells green.
4. Reject the proposal if no preregistered nonzero step both preserves
   feasibility and improves a frozen robustness cost.
5. Export at the same two absolute steps; both must be green by construction,
   then face the unchanged complete robustness matrix.

This differs from V161: V161 projected two already-trained endpoints using an
action-MSE proxy. The proposed optimizer keeps every training iterate inside
the actual closed-loop feasible set and uses the gate as a constraint, never
as checkpoint selection.

The concern is compute and stagnation: the green source has only
`0.00265930 N.m` nominal torque margin, and V161 showed that even a 0.157%
long-horizon parameter displacement can leave the feasible set.

## Questions

1. Is feasibility-preserving parameter-space continuation the correct next
   class, or is there a cheaper mechanically distinct class?
2. What CPU-only falsifier should reject it before hosted training?
3. How should a nontrivial accepted-step requirement be derived without
   coefficient hunting?
4. Can the exact eight-cell feasibility test be reduced safely for
   per-update use without turning the gate into a proxy again?
5. If this class is not earned, state the exact reviewed contract expansion
   required next (reference geometry, phase/reference interpolation, command
   support, or architecture) and the cheapest falsifier for that expansion.

Do not propose another reward scalar, eta change, dual retry, checkpoint
selection, post-hoc alpha sweep, finite local residual, sparse distillation,
runtime torque projection, phase-only trigger, or long-range transport model.
Those families are closed by the evidence above.
