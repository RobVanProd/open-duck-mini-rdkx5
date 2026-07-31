# Ground-Up Torso-COM Crossed Phase-Localization Preregistration

status: `PREREGISTERED_READ_ONLY_CPU_CROSSED_PHASE_LOCALIZATION`

## Evidence question

The completed signed causal-response matrix is mixed: 67/144 cells are
corrective, 55 are amplifying, 22 are intermediate, and none is physically
negligible. The mixture localizes most strongly by fork tick, but that table
does not distinguish two causes:

1. the actor's accelerometer-caused action response changes with policy state
   or gait phase; or
2. the same action response changes physical pitch sign when applied at a
   different plant state or gait phase.

The existing artifact narrows the question without answering it. The physical
`COM_POS - COM_NEG` pitch endpoint is positive in all 144 cells, and its vector
norm spans only .141763-.193862 rad. The actor-effect vector is always
non-negligible but changes signed alignment with fork time. The saved action
response vectors also rotate across ticks. These are deterministic
descriptions, not a family-selection result.

This study crosses the target physical-state tick with the donor tick of the
actor's measured response. It asks whether signed pitch alignment follows the
donor actor response, the target plant state, or their interaction.

## Frozen sources

- signed result JSON SHA-256:
  `8c09ada8ce392c09fcee3cd9e7f449be5b1c50ca28b1640a4a3103755cc3b814`;
- signed evaluator SHA-256:
  `6e25285e9b12b8763aac0723e16c6d5ca63cac9e1956205fd44bdff714179b4d`;
- signed contract JSON and its recorded source hashes remain authoritative;
- exact replay manifest SHA-256:
  `ac42abc8a940d97f0c0373ce624eaf2d2f803ac574e0de52c82303c7a759da07`;
- six contracted ONNX manifest SHA-256:
  `d50bfc57e29dea9479d16506d175175e6a94f69c5d62700168d5bf9df3cadac4`;
- P30 and P31/34 actuator-fit hashes, playground commit, composed environment,
  scene, reference table, and bridge source remain exactly those frozen by the
  signed study.

No training reward is a source or selector.

## Frozen matrix

Use the same 36 nominal moving traces:

- six policies;
- both measured fits;
- commands x=.074/.077/.080;
- deterministic seed 167931544.

For each trace, cross target-state ticks `[0,24,32,40]` with donor actor-response
ticks `[0,24,32,40]`. This is exactly 36 x 4 x 4 = 576 matrix cells: 144
diagonal cells and 432 off-diagonal cells.

The 144 diagonal cells must reproduce the prior signed result. They are a
validity check, not new evidence and are counted once. Every off-diagonal cell
is executed once. No outcome retry, extra tick, command, fit, checkpoint,
horizon, or midpoint is permitted.

## Frozen crossed intervention

For each trace, sequentially reconstruct the contracted ONNX baseline and the
`obs[3:6] +/- d` fork outputs at all four ticks, using the same measured
direction `d` as the signed study. At donor tick `t_d`, define the two actor
offsets relative to that tick's baseline output:

- `delta_neg(t_d) = action_neg(t_d) - action_baseline(t_d)`;
- `delta_pos(t_d) = action_pos(t_d) - action_baseline(t_d)`.

At target tick `t_s`, reconstruct the exact physical state, baseline action,
recurrent state, fitted actuator queue, prior sent target, and applied control
from the target trace. The actor pair is:

- `CROSS_NEG`: target baseline action + `delta_neg(t_d)`;
- `CROSS_POS`: target baseline action + `delta_pos(t_d)`.

Only that first raw action differs. Both branches then receive the identical
saved target-trace baseline actions for the next seven ticks. Both use nominal
dynamics, the target fit, target bridge state, existing target-rate stage,
20 ms control tick, and unchanged native MuJoCo substeps.

The offset construction is frozen because it preserves both magnitude and
asymmetry of the actor's actual donor-tick response while removing the donor's
unrelated baseline action. On the diagonal, it algebraically restores the
original `action_neg/action_pos` pair exactly. Contract failure is required if
any planned crossed raw action is outside [-1,1], if either donor intervention
is zero, or if target/donor indexing is not a complete Cartesian product. No
post-outcome scaling or clipping repair is allowed.

For each target state, reuse the exact prior physical disturbance vector
`D(t_s) = pitch_COM_POS - pitch_COM_NEG` from the hash-locked signed result.
It is independent of donor tick by construction. Simulate the crossed actor
pair and define `A(t_s,t_d) = pitch_CROSS_POS - pitch_CROSS_NEG` over the same
eight ticks.

## Frozen cell metric

Use the prior signed metric and thresholds unchanged:

`c(t_s,t_d) = dot(D(t_s), A(t_s,t_d)) / (norm(D) * norm(A))`.

- `CORRECTIVE`: both norms >=1e-6 rad and c<=-.25;
- `AMPLIFYING`: both norms >=1e-6 rad and c>=+.25;
- `ORTHOGONAL_OR_MIXED`: both norms >=1e-6 rad and -.25<c<+.25;
- `PHYSICALLY_NEGLIGIBLE`: either norm <1e-6 rad.

Pitch-rate, height, local-vx, raw action, sent-target, and applied-target
differences are secondary diagnostics only. No p-value or confidence claim is
made.

## Frozen deterministic effect decomposition

For each of the 36 policy/fit/command trace groups, form the 4x4 matrix of
continuous alignment cosines `y[s,d]`. If any cell is negligible, its cosine is
undefined and the study decision is `INVALID_NEGLIGIBLE_CROSS_CELL`; no
imputation is allowed.

Within each group, remove its grand mean and compute the standard balanced
two-way sums of squares:

- `SS_TARGET = 4 * sum_s(mean_d(y[s,d]) - grand_mean)^2`;
- `SS_DONOR = 4 * sum_d(mean_s(y[s,d]) - grand_mean)^2`;
- `SS_INTERACTION = sum_s,d(y[s,d] - row_mean[s] - col_mean[d] + grand_mean)^2`.

Aggregate these sums across the six fit/command groups belonging to each
policy, then divide by their sum to obtain target, donor, and interaction
fractions. This decomposition is deterministic and descriptive; it is not an
independent-sample ANOVA and reports no inferential statistic.

A policy is:

- `DONOR_ACTOR_RESPONSE_DOMINANT` if donor fraction >=.60 and is at least 2x
  both other fractions;
- `TARGET_PLANT_STATE_DOMINANT` under the exact symmetric target rule;
- `CROSSED_INTERACTION_DOMINANT` under the exact symmetric interaction rule;
- otherwise `DISTRIBUTED_OR_UNRESOLVED`.

The .60 and 2x boundaries are frozen before crossed outcomes. Report the full
4x4 categorical counts for every policy and the aggregate; these do not alter
the decision.

## Frozen decision

Both checkpoints of every arm must agree, and all three arms must agree, before
a mechanism-level next study is selected.

1. If all six policies are `DONOR_ACTOR_RESPONSE_DOMINANT`, decision
   `SUPPORT_PREREGISTERED_ACTOR_ACTION_ATTRIBUTION_STUDY`. This supports only a
   read-only joint/action-component attribution study.
2. If all six are `TARGET_PLANT_STATE_DOMINANT`, decision
   `SUPPORT_PREREGISTERED_PHASED_PLANT_AUTHORITY_STUDY`. This supports only a
   read-only phase-conditioned actuator-effect study.
3. If all six are `CROSSED_INTERACTION_DOMINANT`, decision
   `SUPPORT_PREREGISTERED_JOINT_PHASE_INTERACTION_STUDY`. This supports only a
   read-only joint-by-phase attribution study.
4. Otherwise decision `CROSSED_LOCALIZATION_UNRESOLVED_NO_FAMILY_SELECTED`.

No closest policy, checkpoint, arm, fraction, tick, or cell is promoted.
These outcomes select at most the named next preregistration, never an
architecture, reward, policy, checkpoint, or training run.

## Validity and authority boundary

Before formal crossed cells, a committed CPU-only contract must verify every
frozen source hash, all six graph hashes and CPU providers, all 36 trace hashes,
complete target/donor indexing, exact recurrent and bridge reconstruction,
baseline/sent/applied target reproduction, nonzero donor offsets, and that all
1,152 planned first-branch raw actions remain inside [-1,1]. It must execute
zero formal cells.

During the formal run, all 144 diagonal actor pitch trajectories and alignment
values must reproduce the signed-result artifact within 1e-12. Any failure
invalidates the complete crossed study; it cannot be repaired or partially
selected.

This preregistration authorizes one contract and one exact CPU-only crossed
study. It authorizes no training, Colab, GPU/iGPU, R2/R3, policy or reward
change, explicit COM input, memory or estimator implementation, runtime design,
RDK-X5, robot access, deployment, torque, or motors.
