# Ground-Up Torso-COM Full-Observation Replay and Sensitivity Preregistration

status: `PREREGISTERED_CPU_ONLY_READ_ONLY_REPLAY_AND_ACTOR_FORK`

## Evidence question

The saved-trace decode establishes one deterministic fact: under the frozen
home-support reset, tick-zero `obs[3:6]` is one exact accelerometer vector per
torso-COM class. It does not establish statistical significance, persistence
through gait, or actor use of that signal. The old N>1 ridge table is
non-monotone because adding later nuisance features can reduce held-out
accuracy even while its tick-zero separator remains unchanged.

This study asks two narrower questions before selecting another policy family:

1. Is COM class descriptively decodable from the full 115-D actor observation
   at individual mid-gait ticks or from fixed local mid-gait windows?
2. Do the six contracted actors change their output when only the local
   accelerometer input `obs[3:6]` is changed along the measured COM-class
   direction, with every other observation value and recurrent input fixed?

Neither answer is treated as a statistical population claim. No p-value is
reported.

## Frozen sources

- source behavior directory:
  `outputs/analysis/ground_up_torso_com_behavior_eval`;
- 36 source matrix JSON files, 8,647,527 bytes total;
- canonical matrix manifest SHA-256 (sorted relative path, tab, file SHA-256,
  newline): `0128c39a9322beecb9f94f4200819093afd2ca50ea2944a8d6add5db852b9839`;
- six contracted transformed ONNX files, 5,441,706 bytes total;
- canonical policy manifest SHA-256 by the same algorithm:
  `d50bfc57e29dea9479d16506d175175e6a94f69c5d62700168d5bf9df3cadac4`;
- policy hashes:
  - `A05_DIRECT_1003520`: `e50a121bf0c2d9a2715d65b8356e4e1af68a16c1ecb264975c1c1d33acea32a7`;
  - `A05_DIRECT_2007040`: `eaa01f1d1c29f7bb6e7c9cf77093229e708ad317bb8d2a175617f4e9955b11c5`;
  - `U05_DIRECT_1003520`: `6aa4364ec3291d5f42b5adf725a79c3c18f0062f0f4741e09f814ea1af7db9af`;
  - `U05_DIRECT_2007040`: `c16be9b15549343073a24e3844da54d648415dbd5979e321db10e45fc6167a11`;
  - `U_CURRICULUM_512000`: `1653f55429867c63248175c7f3be2b8b550f57dd29f03321da312495ba6528b5`;
  - `U_CURRICULUM_1024000`: `2665ac124d59ddeb93777cf1d82ca1bc0d0506bb26bd1c06645356c66fce3001`;
- transform-contract JSON SHA-256:
  `d724a7d0ac96ab18aaa1ea29e5872436d09977cb47af58db46f916423bf14a86`;
- correction JSON SHA-256:
  `ef62ea7e479c1734dd8b416ce4bcb4636de9d4b5bf40c55cf729c8a536af1f37`;
- raw tick-zero audit JSON SHA-256:
  `c391599d3aabde3a7ea5f5e4eb889290abaa17d90730a7cbac8e4b9a73cc9931`;
- P30 fit SHA-256:
  `908ddb01e5d82e661d77b8f3cb186a84665695660b86b304c6d1ae89c79cdb0b`;
- P31/34 fit SHA-256:
  `a39776c06c5e26425e24b50e7dab3f441823e23904cad4977b8c921d9c9ca276`;
- reference table SHA-256:
  `8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212`;
- evaluator SHA-256:
  `b05f49e0692237aa6aff924d9fa41fe9ce06b46d806187597022ac52eb2a4d3a`;
- closed-loop evaluator SHA-256:
  `e6182ad45c0409820ad8086694a5d12b9c7154ed70a47a836895dc61ab55fd90`.

The matrix remains exactly three conditions x six policies x two actuator
fits x four commands = 144 deterministic cells. Conditions are `NOMINAL`,
corrected `TORSO_COM_X_NEG=-0.05 m`, and symmetric
`TORSO_COM_X_POS=+0.05 m`; commands are x=0/.074/.077/.080; seed is 167931544;
reset is deterministic `home-support`; horizon is 600 ticks. Training reward
is neither read nor used.

## Stage 0: contract before replay

A committed CPU contract must pass before any replay. It must verify all source
hashes and counts, exact ONNX graph identity against the six contracted files,
stateful interface `obs,previous_action -> continuous_actions,previous_action_out`,
115-D observations, 14-D actions/state, all frozen source matrix inputs and
per-run torso readbacks, the body-2 `trunk_assembly` one-axis mutation for both
COM endpoints, default-off nominal identity, and accelerator exclusion through
`CUDA_VISIBLE_DEVICES=""`, `JAX_PLATFORMS=cpu`, and CPU-only JAX and ONNX
providers. It must refusal-test any hash, readback, graph, condition, or device
mismatch.

The contract also freezes the comparison normalizer used below and unit-tests
it on copied source JSON. A static evaluator-source check must show that
`trace_full_obs` only appends the declared trace fields; the contract may not
run a behavior cell to establish this.

## Stage 1: reporting-only full-observation replay

Replay all 144 cells exactly once. The only evaluator changes are a new trace
destination and `trace_full_obs=true`. Every row must contain finite
`obs_state[115]`, contiguous ticks from zero, and the existing telemetry. Each
matrix must retain exact policy/fit/reference hashes, command, seed, reset,
600-tick request, dynamics override, and per-run readback.

For each new matrix, compare to its frozen source after removing only:

- wall-clock duration fields;
- trace path fields;
- `inputs.trace_dir`;
- `inputs.trace_full_obs`;
- trace-mode reporting fields whose value changes solely because full tracing
  is enabled.

All remaining JSON values must match exactly. Any mismatch invalidates the
replay and stops the study before decode or sensitivity. Raw full traces are a
reproducible local corpus and are not committed because of their size; commit
their sorted path/hash/size/row manifest and all analysis summaries.

## Stage 2A: frozen descriptive decode

Every trace contributes class-labelled observations only through tick 40,
which precedes the earliest source termination. The class label comes only
from the frozen condition. No action, reward, velocity, pose, contact,
termination, post-step telemetry, or training metric is a probe feature.

Evaluate two predeclared feature families independently:

- `ACCEL3`: observation indices `[3:6]`;
- `FULL115`: all actor observation indices `[0:115]`.

For each family, fit the same deterministic three-class ridge rule used by the
earlier audit: training-fold standardization, zero standard deviation replaced
by one, bias column, one-hot least squares, L2 coefficient 1.0 with unpenalized
bias, and class order `NEG,NOMINAL,POS`.

Evaluate:

- instantaneous ticks 0 through 40 inclusive;
- local windows ending at ticks `[8,16,24,32,40]`, with suffix widths
  `[1,2,4,8,16]` wherever the width is at most `end_tick+1`.

A window is the row-major flattening of the selected consecutive observations.
Every exact width is reported separately. In addition, report a descriptive
existence envelope over the frozen widths at each endpoint: whether at least
one individual width passes. This envelope is monotone by definition and may
not be presented as the accuracy of a newly fit or test-selected model.

Use the same nine group-held-out folds: leave out each of three arms, four
commands, and two fits. Report every fold confusion matrix, accuracy, pooled
family macro-F1, and class recall. There are no permutations, p-values,
confidence intervals, or independent-sample claims.

An individual tick or exact window passes the descriptive probe only if:

- minimum accuracy over all nine folds is at least 0.75;
- pooled macro-F1 is at least 0.80 for each fold family; and
- minimum pooled class recall is at least 0.70.

Interpretation labels are frozen:

1. `PERSISTENT_CURRENT_STATE_DECODE_UNDER_FROZEN_PROBES` only if the same
   feature family passes every instantaneous tick 24 through 40.
2. Otherwise, `LOCAL_HISTORY_DECODE_UNDER_FROZEN_PROBES` only if the same
   feature family and the same exact width greater than one pass at every
   endpoint 24, 32, and 40.
3. Otherwise, if tick zero passes,
   `RESET_TRANSIENT_ONLY_UNDER_FROZEN_PROBES`.
4. Otherwise, `NO_DECODE_UNDER_FROZEN_PROBES`.

Labels 2-4 are probe-limited negative statements; they do not prove information
absence or authorize narrowing the COM range. The ACCEL3 and FULL115 results
remain separate; a worse FULL115 result may not erase a passing subset result.

## Stage 2B: frozen identical-state actor sensitivity

Reconstruct each actor's `previous_action` input by replaying its ONNX graph
sequentially over the saved observations from an all-zero initial state. At
every row, the baseline output and next recurrent output must reproduce the
recorded policy output within 1e-6 maximum absolute error. A failure invalidates
that trace rather than permitting state substitution.

The measured COM direction is frozen from the pre-replay raw audit as half the
POS-minus-NEG tick-zero accelerometer difference:

`d = [1.1654748916625977, 0.11948448419570923, 1.0919904708862305] m/s^2`.

At ticks `[0,24,32,40]`, evaluate two counterfactual forks for every available
trace state:

- `obs_minus`: subtract `d` only from indices `[3:6]`;
- `obs_plus`: add `d` only to indices `[3:6]`.

The policy graph, recurrent input, all other 112 observation values, state,
condition, command, fit, and actor identity remain bit-identical within a pair.
Record the 14-D output difference, RMS, maximum absolute difference, and the
central directional slope. Report per policy and tick plus aggregate medians,
p95, and maxima. This is local input sensitivity, not a simulator intervention
and not a claim about corrective sign.

The output response is classified as:

- `NEAR_ZERO_ACCEL_RESPONSE` only if every policy at both reset (tick 0) and
  the pooled mid-gait ticks (24/32/40) has p95 action-difference RMS <=0.001
  normalized action and p95 maximum absolute action difference <=0.004. With
  the frozen 0.25-rad action scale, the latter is <=0.001 rad target effect.
- `SUBSTANTIAL_ACCEL_RESPONSE` if any policy at reset or mid-gait has median
  action-difference RMS >=0.004 or median maximum absolute difference >=0.016.
- otherwise `INTERMEDIATE_ACCEL_RESPONSE`.

These thresholds are frozen before fork outcomes. A substantial response does
not establish that its sign is stabilizing; it selects only a separately
preregistered signed causal-response study.

## Joint decision and authority

The result must report both decode and sensitivity labels. It may support only
the following next preregistration:

- persistent current-state decode plus near-zero response: an
  objective/optimization exploitation study;
- reset-transient-only or local-history decode plus near-zero response: a
  memory or estimator-input study;
- substantial response: a signed causal-response study;
- any intermediate, invalid, or conflicting result: no arm family selected.

This mapping does not authorize implementation or training. It explicitly does
not distinguish objective design from optimizer failure, and it does not call
a substantial response correct or wrong-signed.

This preregistration authorizes only: one contract, one exact 144-cell CPU
reporting replay, the frozen decode, and the frozen read-only ONNX forks. It
authorizes no retries after outcomes, policy or simulator behavior changes,
training, Colab, GPU/iGPU, R2 resumption, R3+, explicit COM input, architecture
change, range narrowing, runtime design, RDK-X5, robot access, deployment,
torque, or motors.
