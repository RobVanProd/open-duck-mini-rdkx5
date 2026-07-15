# Ground-Up Torso-COM Observability Decode Preregistration

status: `PREREGISTERED_READ_ONLY_CPU_LINEAR_DECODE`

## Question

The completed remediation falsifies the narrow exposure-gap hypothesis. Before
targeted torso-X training, corrected `TORSO_COM_X_NEG` moving cells fell at
41-42 ticks with mean vx down to -0.410971 m/s. After 512K-2M stage-relative
steps of full-range exposure, X_NEG still falls at 42-55 ticks with mean vx
down to -0.410235 m/s. All nominal cells remain full-duration passes. X_POS is
signed oppositely: x=0 remains stable, while all moving cells accelerate to
0.254248-0.424365 m/s and fall at 50-101 ticks. Endpoint tracking p95 remains
below 0.184 rad.

This probe asks the smallest question the saved corpus can answer exactly:
is torso-COM class linearly decodable from a pre-fall window of the exact six
actor inputs saved in every trace (`obs0_6`, gyro plus accelerometer)?

## Frozen source corpus

- trace root:
  `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/ground_up_torso_com_behavior_eval/traces`
- 144 JSONL traces, 48 each for `TORSO_COM_X_NEG`, `NOMINAL`, and
  `TORSO_COM_X_POS`;
- 133,772,055 total bytes;
- canonical sorted relative-path/SHA-256 manifest hash:
  `2b69f79d118c77c6dcd4f714c7ba6f45ea526b747f09de164d6cdebbcb1709f1`;
- source decision SHA-256:
  `855d1c160de979a609691204647f872f2343095579f873f6cf9eb0eefc777f1`;
- exact arms/checkpoints: `A05_DIRECT` and `U05_DIRECT` at
  1,003,520/2,007,040; `U_CURRICULUM` at 512,000/1,024,000;
- exact fits: P30 and P31/34;
- exact commands: x=0/.074/.077/.080;
- seed: 167931544.

Every trace must contain finite six-value `obs0_6` rows with contiguous ticks
from zero and at least 42 rows. Every saved matrix JSON must reference exactly
one of the 144 trace paths. Any corpus, schema, hash, count, label, grouping, or
tick failure invalidates the evidence rather than being repaired.

## Recorded-observation boundary

The behavior run used `trace_full_obs=false`. No trace contains `obs_state`.
Therefore this probe must not claim to test the full 115-D observation, and it
must not use post-step telemetry (`body_pitch_rad`, velocity, position, target,
contact, reward, termination, or policy action) as classifier input. Only the
exact pre-policy `obs0_6` sequence is admissible.

## Frozen samples and windows

Each trace contributes one prefix sample for each N in
`[1, 2, 4, 8, 16, 24, 32, 40]`. A sample is the row-major flattening of
`obs0_6` at ticks `[0, N)`. Forty ticks is below the earliest observed fall at
tick 42, so no window contains post-termination evidence. Labels are fixed as
`NEG`, `NOMINAL`, and `POS` from the condition directory.

## Frozen probe

Use only a deterministic three-class linear ridge probe:

1. Standardize every flattened feature with training-fold mean and standard
   deviation; replace a zero standard deviation with one.
2. Append a bias column.
3. Fit one-hot least squares with L2 coefficient `1.0`; do not penalize bias.
4. Predict by largest class score with class order `NEG`, `NOMINAL`, `POS`.

No small MLP, PCA, derivative feature, telemetry feature, hyperparameter
search, class reweighting, window shifting, midpoint, or post-outcome retry is
authorized.

## Frozen generalization folds

Evaluate all eight windows under nine group-held-out folds:

- leave each of three arms out;
- leave each of four command values out;
- leave each of two actuator fits out.

The training standardizer and probe are fit independently inside each fold.
Report every fold accuracy, pooled macro-F1 for each fold family, every pooled
class recall, and confusion matrices. Classes are exactly balanced in every
fold. Checkpoints are never separated from their arm identity for an arm-held
out test.

## Frozen statistical control

Run 1,000 deterministic label permutations with seed 167931544. Within every
matched `(arm, checkpoint, fit, command)` triplet, independently permute the
three condition labels. For each permutation evaluate all N and retain the
maximum across N of the minimum accuracy over all nine held-out folds. The
family-wise p-value is `(1 + null >= observed) / 1001`.

## Frozen pass and interpretation

The earliest N passes only if all are true:

- minimum accuracy over all nine folds is at least 0.75;
- pooled macro-F1 is at least 0.80 in each of the arm, command, and fit fold
  families;
- minimum pooled class recall across all fold families is at least 0.70;
- max-stat permutation p-value is at most 0.01.

Decision order:

1. If N=1 passes: `PASS_INSTANTANEOUS_IMU_COM_DECODE`. The saved instantaneous
   actor input contains COM information; separately preregister an
   objective/exploitation study. Memory is not selected by this outcome.
2. If the earliest passing N is greater than one:
   `PASS_TEMPORAL_IMU_COM_DECODE`. History adds necessary decodability under
   the frozen probe; separately preregister a memory or estimator-input arm.
3. If no N passes: `NO_STORED_IMU_PREFIX_DECODE_UNDER_FROZEN_LINEAR_PROBE`.
   This is not evidence that the full 115-D observation is insufficient. It
   authorizes no policy or formulation change; a separate contract would be
   required to capture/reconstruct full observations before making that claim.

Training reward is not an input or selector. The probe may not train or modify
a policy.

## Authority boundary

This preregistration authorizes one read-only CPU execution of the exact probe
and its reporting contract. It authorizes no simulator replay, policy training,
Colab, GPU/iGPU, R2 resumption, R3+, runtime design, RDK-X5, robot access,
deployment, torque, or motors. A decode pass authorizes only the separately
preregistered study named by its decision branch.

