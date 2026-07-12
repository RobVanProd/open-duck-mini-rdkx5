# Agent Instructions

This repository controls work around a real biped robot. Preserve safety and evidence quality over speed.

## Core Rules

- Never tune before evidence.
- Do not start unregistered or ad hoc policy training. The authorized offline
  joint-weighted, 2.0 rad/s temporally bounded behavior-teacher causal smoke
  completed on 2026-07-11. None of its 40,960, 81,920, or 122,880 checkpoints
  passed the compact corrected-bridge x=0.08 gate, so the branch is closed:
  do not promote it, run extended seed evaluation, or train it further. No
  additional policy training is authorized.
- The authorized offline phase-action-delta causal screen completed and failed
  its consistency rule: seeds 1 and 3 improved, seed 6 regressed sharply, all
  three high-progress cohort seeds regressed, and overall mean progress fell.
  The route is closed. Do not tune its scale, export it, promote it, deploy it,
  or use it for training. No additional eval intervention or policy training is
  authorized without a new evidence-backed, pre-registered task.
- One non-interventional CPU-only baseline data expansion is authorized: run
  the original rate175 step-163,840 policy for 1 second at x=0.08 on new seeds
  8-23, using the same corrected fitted bridge and 2.0 rad/s pitch-chain limiter
  as the matched control, with full-observation traces. Its only purpose is to
  measure whether the isolated seed-6 reset state recurs and whether nearby
  states have consistent outcomes. No policy/action modifier, training,
  promotion, deployment, robot access, Colab, or GPU use is authorized.
- One held-out continuation of that same non-interventional baseline collection
  is authorized on seeds 24-39. Freeze the discovery metrics before running:
  primary = first-10-tick teacher-disagreement p95 ROC AUC for fall versus
  duration-complete; secondary = first-20-tick disagreement mean ROC AUC. Use
  the same policy, x=0.08, 1-second duration, bridge, limiter, tracing, and CPU
  platform. Do not fit a threshold, alter actions, train, promote, deploy, use
  the robot, allocate Colab, or use any GPU.
- The held-out baseline block completed. Teacher disagreement replicated as a
  fall-ranking diagnostic, but no threshold is authorized; the two held-out
  positives are insufficient for calibration. Baseline seeds 8-39 produced
  7/32 one-second falls and only 3/32 passes. Do not collect more seeds, tune a
  monitor threshold, change reset behavior, or run another intervention without
  a new reviewed evidence task. Training, promotion, deployment, robot access,
  Colab, and GPU use remain unauthorized.
- One reset-only CPU causal screen is authorized on the seven observed one-
  second fall seeds `9,12,14,19,20,36,37`: preserve the original rate175 step-
  163,840 policy, canonical playground reset, x=0.08 command, corrected fitted
  bridge, and 2.0 rad/s pitch limiter, changing only `reset_settle_ticks` from
  0 to 10. Run 1 second with full traces. No alternative settle count, home-
  support reset, action change, training, promotion, deployment, robot, Colab,
  or GPU use is authorized.
- The settle-10 failure-seed screen completed with 7/7 falls, all earlier than
  the matched settle-0 controls. The route is closed. Do not tune settle ticks,
  substitute home-support reset, fit a disagreement threshold, or attempt an
  active recovery without a separately reviewed task. No training, promotion,
  deployment, robot access, Colab, or GPU use is authorized.
- A subsequent offline, saved-JSON threshold-transfer audit did not alter any
  runtime behavior. A discovery-fitted first-10-tick p95 cutoff transferred to
  held-out seeds, but the reverse held-out-fitted cutoff detected only 1/5
  discovery failures (sensitivity 0.20). Threshold transfer is asymmetric, so
  no start-paused cutoff is calibrated or authorized. Do not implement or tune
  a runtime gate from these 32 traces. More independent failure positives or a
  separately reviewed multivariate reset-health study are required first.
- The preregistered saved-trace multivariate reset-health study also failed.
  Nearest failure-versus-completion reset risk had transfer AUC 0.750/0.764;
  equal-weight combination tied disagreement at 1.000 discovery-to-held-out but
  reduced reverse-transfer AUC from 0.909 to 0.818. Close this exact normalized
  101-observation nearest-neighbor/equal-weight route. Do not tune its distance,
  weights, features, or threshold post hoc. The remaining supported diagnostic
  hypothesis is the simpler temporal disagreement ranking, which requires new
  independent failure positives before calibration.
- That independent validation is complete on seeds 40-71: 11/32 fell and only
  4/32 passed. First-10-tick p95 disagreement retained ranking information
  (AUC 0.823), but the frozen 0.08247255 cutoff produced TP/FN/TN/FP
  9/2/16/5 (sensitivity 0.818, specificity 0.762). Reject this cutoff as a
  simulator or robot safety gate. Do not collect more threshold-only seeds,
  refit the cutoff, or add post-hoc reset features. The next evidence problem
  is an outcome-aligned active-recovery target or a separately preregistered
  policy-objective experiment; neither is currently authorized for deployment.
- A preregistered first-0.20-second physical-signature analysis across seed
  blocks 8-23, 24-39, and 40-71 found two replicated fall correlates: absolute
  pitch growth (AUC 0.855/0.750/0.753) and actuator tracking error
  (0.945/0.821/0.827). Joint localization identified only the right knee as
  consistent across all blocks (AUC 0.727/0.929/0.753; failure mean tracking
  error about 0.36-0.44 rad versus 0.22-0.24 rad completed). This is a candidate
  causal-screen variable, not permission to change a gain, limiter, target, or
  policy. Establish whether target demand/rate drives the error before
  preregistering any matched CPU intervention.
- The saved-trace mechanism audit rejected right-knee target demand and rate
  saturation: no demand feature met the frozen cross-block rule, saturation was
  absent, and demand/error correlations were near zero or negative. Error-
  origin analysis instead found tick-0 absolute mismatch replicated
  (AUC 0.709/0.893/0.753) while later growth did not. Do not lower the limiter.
  The only preregistered next causal screen is a default-off eval-only bridge
  initialization that starts actuator index 12 from measured reset position on
  seeds 40-71 under the frozen pass rule. No other joint or parameter change is
  authorized by this evidence.
- The preregistered right-knee bridge reset-alignment causal screen failed and
  was stopped after seeds 40-50. It reached 6 falls (limit 5), created a new
  fall on baseline-complete seed 50, and recovered only seed 49. Early tracking
  error decreased on 4/6 tested baseline-fall seeds without reliable outcome
  recovery. Close this exact route: do not tune alignment duration, scale,
  offsets, other joints, gains, or limiters. Treat right-knee mismatch as a
  diagnostic symptom/partial mediator, not a recovery target. The remaining
  evidence-supported learning question is direct canonical-reset outcome
  robustness under a separately preregistered objective, not another local
  action correction.
- The preregistered no-behavior-prior Stage A Colab branch completed. All three
  checkpoints passed x=0 but failed x=0.08: step 81,920 held for low progress;
  steps 163,840 and 245,760 held for tracking (p95 about 0.216 rad). No expanded
  seed sweep is authorized or needed; close the branch without tuning KL,
  timesteps, or reintroducing a modified prior. Higher training reward did not
  align with the compact gate. The next objective audit should consider the
  default-off command-progress failure termination, which directly matches the
  measured positive-command no-progress outcome, as a separate one-factor
  hypothesis from the original baseline recipe.
- The preregistered command-progress failure branch is complete and rejected.
  No checkpoint passed both compact commands: step 81,920 failed x=0.08
  progress; step 163,840 reached ratio 0.287 but failed tracking at x=0 and
  x=0.08; step 245,760 failed x=0 tracking and x=0.08 progress. Do not run the
  seeds 40-71 expansion or tune the 0.25 ratio / 30-tick warmup. The Colab
  runtime disappeared during its CPU sweep, but all checkpoints were recovered
  from a valid artifact snapshot and the exact sweep was completed with local
  CPU-only JAX. This exact direct-termination route is closed.
- A source-and-data audit confirms the next objective mismatch: the existing
  actuator-tracking reward measures mean sent-vs-bridge-applied error, while
  the compact gate measures worst pitch-chain sent-vs-actual-joint error. In
  8/12 completed compact evaluations the surrogate passed while the joint gate
  failed. A default-off six-pitch-joint direct cost now passes its CPU-only
  contract. Its preregistered scale is -0.007914891239136222, calibrated from
  frozen x=0/x=0.08 traces to equal the existing bridge penalty's mean reward
  contribution. Do not tune scale, delta, indices, aggregation, KL, or length.
- The preregistered direct joint-target tracking experiment is complete and
  rejected. All checkpoints preserved x=0, but step 81,920 failed x=0.08
  progress and steps 163,840/245,760 failed x=0.08 tracking at 0.21784/0.21703
  rad. No seeds 40-71 expansion is authorized. Close the exact pitch-chain
  mean-cost formulation at scale -0.007914891239136222; do not increase its
  scale or tune delta, indices, aggregation, KL, or training length post hoc.
- Compact-gate feasibility was audited with the frozen rate-bounded teacher.
  Discovery seeds 0-7 produced 1/8 passes; independent seeds 8-23 produced
  only 1/16 passes and 5/16 falls. Those five fall seeds exactly match the
  baseline fall set, so the teacher does not recover the unsupported-start
  states. Do not weaken the compact gate or resume broad-reset scalar training.
  Keep normal grounded `home-support` walking and unsupported `playground`
  reset recovery as separate contracts, as established in prior project docs.
- The normal-start track is re-anchored to
  `phase2_corrected_live_oracle_iter1_rate165_20260703`. Candidate hashes match,
  its authoritative home-support result is 8/8 pass at x=0 and x=0.08, and
  current-tool seed-0 regressions reproduce the recorded 15-second metrics
  exactly. Treat it as offline-ready for grounded-start review only. Do not
  infer unsupported-start recovery, deploy it, or move the robot without an
  explicit reviewed hardware-validation request.
- Do not change gains, offsets, IMU remaps, action scale, or phase timing without a reviewed evidence-backed task.
- Do not deploy behavior changes to the robot unless explicitly requested.
- Do not run moving hardware tests unless Rob is physically present and explicitly approves that exact test.
- Default to docs, tools, analysis, and tests first.
- Keep PRs small and single-purpose.
- Treat documentation as part of the robot state. Update README, roadmap, audit, evidence manifest, and runbooks when project facts change.
- Do not leave important state only in chat, board-local files, or untracked scratch outputs.

## Hardware Safety

- Read-only SSH checks are acceptable.
- Moving scripts require explicit user confirmation and physical support unless grounded by design.
- Start paused wherever possible.
- Stop on unexpected motion, bus-error bursts, large lean, wrong joint, wrong side, or wrong sign.

## Repository Hygiene

- Do not commit `.duck_access/`.
- Do not commit private SSH keys, known_hosts, tokens, or secrets.
- Do not commit huge raw JSONL logs or videos by default.
- Commit summaries and selected evidence only when they support a decision.
- Keep evidence filenames, manifests, and docs synchronized.
- When adding a tool or workflow, document how to run it and what output is expected.

## RHO-Inspired Operating Model

- Keep agent reasoning and experimentation outside the live robot control loop.
- Ship frozen, readable code that can be inspected before it runs on hardware.
- Treat each PR as a candidate mutation with evidence gates.
- Accept changes only when they improve or clarify a measured gate.
- Preserve rejected or inconclusive findings as notes so the project does not repeat the same investigation.
- Prefer whole-repository understanding over isolated one-file edits when a change touches sensor, policy, and hardware contracts.

## Validation

Before finalizing changes, run applicable checks:

```bash
python3 -m py_compile tools/*.py instrumentation/mini_bdx_runtime/telemetry.py instrumentation/scripts/sim2real_diagnostics.py
python3 -m json.tool docs/telemetry_schema.json >/tmp/telemetry_schema.validated.json
```

For docs-only changes, still check repo status and confirm no runtime behavior files changed unintentionally.

## Current Next Gate

Collect first evidence:

1. Config snapshot.
2. Home pose log.
3. Home pose analysis.
4. IMU tilt log.
5. IMU tilt analysis.
6. Foot contact test.

Do not proceed to grounded walking until low-risk gates pass.
