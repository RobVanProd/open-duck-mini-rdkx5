# Agent Instructions

This repository controls work around a real biped robot. Preserve safety and evidence quality over speed.

## Core Rules

- Never tune before evidence.
- Frozen preregistration text is the authority boundary: a result may report
  pass/fail but may not broaden what the preregistration says a pass authorizes.
- On the active policy track, do not access the robot by SSH, stage files,
  install files, or run hardware until an explicit repository policy-clearance
  artifact authorizes the hardware phase. User approval does not substitute
  for a missing project clearance gate.
- Do not substitute runtime limiters, command wrappers, gain changes, transport
  changes, or incidental telemetry investigations for the policy architecture
  named by the recorded plan.
- The active ground-up policy search is preregistered in
  `outputs/analysis/GROUND_UP_REFERENCE_POLICY_SEARCH_PREREGISTRATION_20260712.md`.
  `BEST_WALK_ONNX_2` is the frozen comparison baseline, not a teacher or warm
  start. The upstream recipe is a protected control, not an assumed winner.
  Total Colab use is capped at 94 compute units and begins only with a capped
  throughput/control calibration after CPU contracts pass. RDK access and all
  local GPUs remain unauthorized.
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
- The grounded rate165 operator packet is prepared, but no hardware action is
  authorized. The next physical gate is supported home-pose geometry, not
  policy replay. The historical `left_knee=-1.4880` offset was corrected to
  `0.0371` on June 27; do not describe the old value as live. A fresh snapshot
  and full-pose visual confirmation are still required. Approval is stage-specific: snapshot/home pose, paused staging,
  suspended x=0, suspended x=0.08, and grounded replay are separate gates.
- Gate 0 was captured read-only on 2026-07-12 with motors untouched. The live
  config exactly matches the corrected June-27 hash, `start_paused=true`, and
  canonical instrumentation hashes match. The board initially booted at year
  2000, then self-synchronized; use trusted `collector_utc` when remote time is
  implausible and retain the historical clock warning.
- Gate 1 was later explicitly authorized and passed on the stand with Rob's
  visual report that home looked really good. Pitch tracking p95 was
  0.000-0.005 rad with no sustained violations. Retain a warning for 3 recovered
  CRC/read retries (1.46%, zero writes, no control impact). Torque-off cleanup
  completed. The board clock subsequently self-synchronized.
- Gate 2 file staging was authorized on 2026-07-12. The rate165 candidate is on
  the board at `/home/sunrise/phase2_grounded_rate165_20260712_e06643e5.onnx`
  with exact SHA256 `e06643e...ea33`; config and baseline hashes are unchanged,
  no runtime was active, and no motor hardware was initialized. Paused runtime
  start/suspended x=0 still requires separate explicit approval.
- Gate 3 suspended x=0 was authorized and completed for 15 seconds. Numeric
  gates have no holds: pitch p95 0.0053-0.0130 rad, zero saturation/write
  errors/tracking spikes, stable timing. Retain 7 recovered CRC reads (0.94%)
  as a warning. Torque cleanup and no-runtime checks passed. Rob reported small
  equal, opposite-phase bilateral leg motion, closing the visual gate. Gate 3
  passes with warning; x=0.08 is not authorized.
- Gate 4 suspended x=0.08 was authorized and completed for 15 seconds. Rob said
  it looked similar but more aggressive. Target velocity p95 was 0.93-1.69
  rad/s and pitch tracking p95 0.034-0.058 rad, but 25 recovered CRC reads
  (3.35%) exceeded the 2% red threshold and correlated with tracking spikes.
  Gate 4 holds; grounded replay is blocked. Torque cleanup completed.
- While the robot remains on its stand, Rob has given continuing authorization
  for suspended `x=0.00` movement tests of the Rustypot transport work. This
  authorization does not include a nonzero command or grounded movement. Keep
  the existing 15-second contract, automatic torque-off, and abort conditions.
- Rustypot transport-reopen candidate 1 failed its first live `x=0.00` test on
  the first ID-13 CRC event: the Python exception traceback retained the old
  exclusive PyO3 serial handle, reopen returned `Device or resource busy`, and
  `self.io=None` caused cascading read failures. Independent torque-off ran,
  no process/port owner remained, and the exact pre-test runtime hashes were
  restored. Do not redeploy candidate 1. Candidate 2 isolates calls in a
  short-lived frame and has an exclusive-handle CPU regression test.
- Candidate 2 also failed live on the first ID-13 CRC because the caller passed
  a bound PyO3 method into `_retry`, retaining the exclusive handle outside the
  helper frame. Cleanup and exact baseline restoration again passed. A no-bus-
  IO probe proved the adapter can close/reopen immediately, ruling out USB
  release latency. Candidate 3 passes operation names rather than bound methods.
- Candidate 3 recovered all 11 live ID-13 CRC events without a busy-port or
  `NoneType` cascade and preserved tracking below 0.03 rad, but each recovery
  incurred about 98 ms and the gate held on 11 control-budget violations. The
  delay matches explicit `gc.collect()` on the RDK, not serial reopen (measured
  near 0.35 ms). Candidate 4 removes full cyclic GC; operation-name ownership
  allows normal CPython reference counting to close the PyO3 handle.
- Candidate 4 clean suspended `x=0.00` completed 747/747 samples and recovered
  all 14 ID-13 CRC events with 14 transport resets, zero write errors, zero
  control-budget overruns, dt max 0.02015 s, and zero tracking spikes above
  0.05 rad. Numeric gate passes with a 1.87% read-error warning; visual operator
  confirmation is still required. The recovery boundary is solved, but the
  underlying ID-13 checksum corruption remains a separate signal-integrity
  issue. Candidate 4 is currently staged on the RDK; do not infer x=0.08 or
  grounded authorization from the suspended x=0 result.
- Rob visually confirmed the candidate-4 clean `x=0.00` run was symmetric, so
  the suspended gate passes with the retained 1.87% CRC warning. Next checksum
  diagnosis should be torque-disabled read-order A/B evidence: canonical order,
  ID 13 last, and a small 12/13/14/23 control. Do not write the STS3215 EEPROM
  return-delay register unless read-only ordering evidence first supports a
  response-collision mechanism.
- The authorized torque-disabled ordering test completed: canonical 12/13/14,
  ID-13-last 12/14/13, and 12/13/14/23 each completed 1,490 synchronous reads
  with zero CRC errors/resets (4,470 total), max call <=1.34 ms, and clean
  torque-off cleanup. Reject a simple static response-order collision and do
  not write return-delay EEPROM. Remaining discriminators are full 14-servo
  response density versus torque/current/supply-ground noise or powered state.
- The matched load/order matrix resolved the checksum mechanism. Full-14
  canonical reads reproduced ID-13 CRC errors torque-off (13/1490, replicated
  10/1490) and static-home torque-on (8/1490); full-14 with ID 13 last produced
  0/1490. Candidate 5 requests ID 13 last and remaps returned values to the
  unchanged canonical joint order. Suspended x=0 then passed 747/747 with zero
  CRC/reset/write errors, zero control overruns, dt max 0.02066 s, and zero
  tracking spikes >0.05 rad. Visual symmetry confirmation is pending. Keep the
  return-delay EEPROM unchanged.
- Candidate-5 x=0.08 readiness is green but the motor stage is not authorized:
  live rate165/config/HWI/walker/diagnostic/turn-off hashes match, start_paused
  is true, and the RDK is idle with no tty owner. The dedicated runner
  `scripts/collect_grounded_rate165_gate4_x008.sh` is suspended-only, fixed at
  x=0.08 for 15 seconds, requires physical-presence and exact confirmation,
  isolates logs, and performs independent torque-off. Obtain explicit x=0.08
  approval before running it; stop for review afterward with no grounded step.
- Candidate-5 suspended x=0.08 was explicitly authorized and completed once:
  747/747 samples, zero CRC/reset/write errors, zero control overruns, and dt
  max 0.02029 s. Rob said it looked clean. The CRC/bus-control-impact objective
  is resolved, but Gate 4 remains `HOLD_TRACKING`: left hip pitch p95 0.0513 rad
  and left knee p95 0.0572 rad exceed the unchanged 0.05 threshold, with 143
  post-startup tracking events above 0.05 and no bus/timing correlation. Do not
  weaken the gate or proceed grounded. Any tracking intervention is a separate
  evidence task and no additional motor test is authorized by this result.
- The x=0.08 tracking miss is small in angle but dynamic, not physical alignment:
  0.0513 rad=2.939 deg and 0.0572 rad=3.278 deg versus 0.05 rad=2.865 deg;
  signed means are near zero and error rises with target rate. Reject offsets.
  A saved-trace slew cap would distort the knee target by up to about 4.4 deg.
  The preregistered default-off intervention is left hip pitch P 30->31 and
  left knee P 30->34, derived from measured error ratios, with every other
  variable frozen. First run suspended x=0 only after explicit approval, then
  restore body/head P 30/8, D 0 and torque off. x=0.08 remains a separate gate.
- The dedicated runner `scripts/collect_left_pitch_gain_x0.sh` is ready but not
  deployed/run. It is fixed to suspended x=0, 15 seconds, P 31/34, exact hashes,
  physical presence and exact confirmation; it cannot run x=0.08 or grounded.
  Every exit invokes `restore_runtime_gains_and_turn_off.py`. Explicit approval
  of this gain-change x=0 stage is still required despite general x=0 clearance.
- The first authorized gain x=0 attempt produced only 299 samples/5.989 s and is
  invalid: the freshly booted RDK wall clock stepped from year 2000 to 2026,
  tripping a `time.time()` duration guard. Motion, bus, and cleanup were clean.
  Runtime duration/filter guards now use `time.monotonic()`. Repeat the same
  already-authorized x=0 stage with gains and thresholds unchanged.
- The monotonic-clock repeat completed 747/747 at suspended x=0 with P 31/34:
  zero CRC/reset/write/control errors, dt max 0.02015 s, zero tracking spikes
  >0.05 rad, hip/knee p95 0.0086/0.0123 rad. Normal gains were restored and
  torque disabled; no runtime/port owner remains. Numeric x=0 passes, but visual
  symmetry/no-oscillation confirmation is pending. x=0.08 is not authorized.
- Rob confirmed the P31/34 suspended x=0 repeat looked normal. The gain trial
  passes x=0 numerically and visually. A single suspended x=0.08 validation may
  be prepared with identical gains and rollback, but requires separate explicit
  approval; do not infer grounded authorization.
- `scripts/collect_left_pitch_gain_x008.sh` is prepared and refusal-tested for
  the separately gated P31/34 suspended x=0.08 validation. It has exact hashes,
  fixed 15-second x=0.08 only, isolated logs, and restores normal gains/torque
  off on every exit. It has no x=0 or grounded path. Explicit x=0.08 approval is
  still required before running it.
- The authorized P31/34 suspended x=0.08 trial completed and is rejected: hip
  p95 0.0514 versus 0.0513 baseline, knee 0.0569 versus 0.0572 (only 0.0003 rad
  better), and head yaw 0.0558; Gate 4 remains HOLD_TRACKING. Rob said it looked
  clean. Normal gains were restored and torque disabled. Do not tune gains
  upward post hoc. The runs had different IMU/closed-loop states, so the only
  supported next gain question is a separately approved fixed-target A/B replay.
- Fixed-target gain A/B is prepared offline, not authorized: replay the exact
  clean P30 x=0.08 target sequence (747 ticks, artifact SHA 3f5fd9c3...) once at
  P30 and once at P31/34, policy/IMU disabled, with normal-gain/torque-off
  between and after phases. Support gains only if both target joints improve
  p95 >=10% without >10% regression on any-joint p95/max. Do not tune afterward.
- Fixed-target A/B completed: hip p95 improved only 0.66%, knee 7.06%, below
  the frozen 10% rule; knee max worsened 15.00%, neck max 32.89%, head roll max
  26.33%, head yaw max 16.14%, and right hip pitch max 11.73%. Zero bus/write
  errors; normal gains restored and torque off. Reject P31/34 and do not raise
  gains post hoc. Remaining supported class is offline target-trajectory shaping
  with motion preservation, not offsets or gains.
- Offline hardware-fit tail caps (hip 2.5, knee 3.25 rad/s) affect only 0.134%
  of targets and predict no hip p95 change / only 0.00043 rad knee improvement.
  A cap strong enough to approach the knee gate would alter targets by about
  4.4 deg across ~14% of samples. Close alignment, P31/34, and tail-limit local
  fixes. The remaining honest route is a separately preregistered motion-
  preserving policy/trajectory objective; grounded remains blocked.
- Rob reported no visible difference between fixed-target P30 and P31/34. This
  agrees with the insufficient numeric effect and closes the gain visual review.
- Rob confirmed candidate 5's final suspended x=0 run looked symmetric. The
  full gate is closed as `PASS_X0`: zero CRC/reset/write errors, clean timing
  and tracking, symmetric motion, and torque-off cleanup. Candidate 5 remains
  staged on the RDK. This does not authorize x=0.08 or grounded movement.
- CRC localization across home/x0/x008 shows every corrupt response is servo ID
  13 (`right_knee`), usually with checksum high-bit flips. Events are not
  concentrated at high right-knee target speed or one gait phase; battery
  voltage was not captured. Leading branch is localized ID-13 signal integrity.
  Do not repeat policy motion. Next proposed test is torque-disabled read-only
  polling of IDs 12/13/14 plus homologous left-knee ID 23, requiring separate
  approval. No authoritative physical bus topology is documented.
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
- 2026-07-12: The fixed-target gain A/B produced no visible distinction and
  failed its frozen numeric rule. The clean ID13-last `x=0.08` trace instead
  shows phase-localized left pitch-chain tracking error. The only open local
  policy route is the offline-only, motion-preserving phase/joint temporal
  objective preregistered in
  `outputs/analysis/PHASE2_RATE165_PHASE_LOCAL_OBJECTIVE_PREREGISTRATION_20260712.md`.
  It must pass the unchanged x=0/x=0.08 bridge gates and its 95% motion floors;
  no GPU, Colab, deployment, robot motion, or grounded replay is authorized.
- 2026-07-12: The preregistered phase-local temporal objective was implemented
  and screened once on CPU. It terminated after 72 samples, moved backward,
  violated base-height and velocity-envelope gates, and heavily saturated
  several actions. Result:
  `outputs/analysis/PHASE2_RATE165_PHASE_LOCAL_COMPACT_RESULT_20260712.md`.
  Close this objective without tuning or longer training; do not allocate
  Colab. Preserve the promoted rate165 candidate unchanged.
- 2026-07-12: Fixed-target P30/P31-34 system identification is stable across
  phases and finds materially tighter pitch-chain effective velocity limits.
  The exact per-joint 7000-step BC refit reduced rates but failed frozen motion
  floors and retained velocity excess. See
  `outputs/analysis/RATE165_HARDWARE_CALIBRATED_REFIT_RESULT_20260712.md`.
  Close supervised rate-penalty refits. The only supported distinct policy
  class is separately preregistered constrained optimization against the new
  fixed-target bridge; no robot/deployment/grounded action is authorized.
- 2026-07-12: The default-off hardware-vector training bridge now accepts exact
  per-joint delay/tau/velocity vectors plus a per-joint target-rate excess cost.
  CPU state assertions and a PPO update/export smoke passed. The exact
  constrained recipe is preregistered in
  `outputs/analysis/HARDWARE_VECTOR_BRIDGE_CONSTRAINED_PPO_PREREGISTRATION_20260712.md`.
  One self-cleaning Colab T4 job is authorized; local GPUs and robot actions
  remain prohibited.
- 2026-07-12: The one authorized hardware-vector constrained PPO Colab job
  completed 245,760 steps and the T4 session was stopped. All checkpoints
  eliminated velocity excess by collapsing to double-support standing
  (vx <=0.0003 m/s, zero single support). Close penalty-based constrained PPO
  without tuning and do not spend another Colab job on it. Result:
  `outputs/analysis/HARDWARE_VECTOR_BRIDGE_CONSTRAINED_PPO_RESULT_20260712.md`.
- 2026-07-12: Exact hard-vector projection of the unchanged rate165 trajectory
  passes the hardware-calibrated bridge at x=.08 and x=0, both 8/8. x=.08 has
  vx 0.0291, ratio 0.3635, 22.93% single support, and zero velocity excess;
  x=0 remains still with pitch-chain p95 <=0.0642. See
  `outputs/analysis/RATE165_HARD_VECTOR_PROJECTION_RESULT_20260712.md`.
  The frozen preregistration authorizes architecture work only, not a runtime
  limiter or hardware path. A policy must internalize the envelope and pass
  the frozen offline clearance gates before any robot validation.
- 2026-07-12: The runtime-vector approval packet is superseded as off-plan and
  retained only as an audit record:
  `outputs/analysis/RATE165_HARD_VECTOR_RUNTIME_APPROVAL_PACKET_20260712.md`.
  Do not use its stage, install, or motion runners for policy qualification.
  The active track is policy development and offline clearance only.
- 2026-07-12: The side-by-side vector stage was explicitly approved and passed.
  All three staged hashes match; live walker/diagnostic hashes are unchanged,
  the port is unowned, no runtime is active, and HWI/motors were not engaged.
  See `outputs/analysis/RATE165_HARD_VECTOR_STAGE_RESULT_20260712.md`. The next
  gate is separate approval for backup-backed live installation only.
- 2026-07-12: Backup-backed hard-vector live installation was explicitly
  approved and passed at that time. Candidate hashes were made live; baseline
  walker/diagnostic backups matched, all files compiled, the port was unowned,
  no runtime was active, and HWI/motors were not engaged. See
  `outputs/analysis/RATE165_HARD_VECTOR_INSTALL_RESULT_20260712.md`. This was
  later identified as off-plan and rolled back; it is history, not current state.
- 2026-07-12: The hard-vector suspended x=0 gate was explicitly approved and
  completed 747/747. Exact vector telemetry, zero CRC/read/write/reset errors,
  clean timing, zero >0.05 tracking spikes, and torque-off/idle cleanup all
  pass. Numeric status is `PASS_NUMERIC_AWAIT_VISUAL`; neck/head yaw retain a
  warning-only p95 0.0219/0.0280. See
  `outputs/analysis/RATE165_HARD_VECTOR_X0_RESULT_20260712.md`. Do not infer
  x=.08 approval before visual x=0 confirmation and a separate explicit gate.
- 2026-07-12: An operator-requested identical hard-vector x=0 repeat completed
  with zero bus errors and no tracking spikes, but held on two isolated control
  gaps: 0.06212 s at tick 250 and 0.06087 s at tick 540. Torque-off/idle cleanup
  passed. Status is `HOLD_CONTROL_IMPACT_AND_VISUAL_ASYMMETRY`; see
  `outputs/analysis/RATE165_HARD_VECTOR_X0_REPEAT_RESULT_20260712.md`. Rob
  reported noticeably greater left-leg motion; telemetry confirms left/right
  knee actual ranges 0.023/0.003 rad. The asymmetry is equally present in
  pre-vector rate165 x=0 traces and the limiter was inactive, so this is policy
  zero-command dither, not a limiter regression or right-knee fault. Do not run
  x=.08. This run is retained as operational evidence only and provides no
  policy-qualification credit.
- 2026-07-12: The RDK hard-vector installation was rolled back from its exact
  pre-install backup. Live walker/diagnostic hashes are restored to
  `b9732b...`/`f28433...`; the added velocity-limit parser is absent. The ONNX,
  config, and ID13-last HWI remain unchanged. Runtime is idle, serial is free,
  no motor access occurred, and both off-plan side-by-side stage directories
  were removed. The exact pre-install backup remains for audit. See
  `outputs/analysis/RDK_HARD_VECTOR_ROLLBACK_AND_PROCESS_CORRECTION_20260712.md`.
- 2026-07-14: Correct deterministic-home evaluation superseded the earlier
  randomized-reset classification of the ground-up reference-residual A/B. All
  A0/A1 x=.074 runs at 3M/4M pass emergence; A1 4M is strongest at 0.06398 m/s.
  Its x=.08 saturation is explained by fixed-command normalization, not robot
  behavior. See `GROUND_UP_HOME_RESET_REFERENCE_RESIDUAL_AB_RESULT_20260714.md`.
- 2026-07-14: Exact measured hard-vector projection preserves A1 4M gait 2/2
  at x=.074 with 0.05345 m/s, bilateral transitions, no saturation, and zero
  target-rate excess. The broader bridge gate still holds at tracking p95
  0.20246 versus 0.20. This is offline evidence only.
- 2026-07-14: Train-time hard-vector plus uniform x=[.074,.080) support now
  passes its CPU transition/export contract. The returned observation carries
  the realized bounded action, and stateful ONNX uses `obs, previous_action` to
  produce `continuous_actions, previous_action_out`. The preregistered 1,024-
  step CPU continuation smoke restored A1 4M exactly, updated all 10 policy
  leaves with finite metrics, and passed chained ONNX bounds. One exact 2M-step
  Colab continuation is authorized by
  `GROUND_UP_HARD_VECTOR_COMMAND_SUPPORT_CONTINUATION_PREREGISTRATION_20260714.md`.
  No local GPU, RDK-X5, deployment, robot, torque, or motor access is authorized.
- 2026-07-14: The single authorized A1 hard-vector command-support T4
  continuation completed at steps 0/1,003,520/2,007,040. Its 8.16 MB archive
  and manifest were recovered and hash-verified before the session was stopped;
  Colab then reported zero active sessions. This is a training-artifact pass
  only. The two post-update stateful ONNX policies must now run the frozen local
  CPU home-reset x=.074/.077/.080, seeds 100/101 behavior gate. Training reward
  is excluded. No local GPU, RDK-X5, robot, deployment, torque, or motor access.
- 2026-07-14: The A1 hard-vector command-support continuation is evaluated and
  rejected. All 12 x=.074/.077/.080 home-reset runs at 1M/2M complete, walk,
  retain bilateral transitions, and have zero target-rate excess, proving the
  command-normalization and hard-vector mechanisms. Neither checkpoint passes
  fitted tracking: 1M p95 is .212-.222 rad and 2M is .219-.239 versus .20; 2M
  x=.08 also reaches 1.8519% saturation versus 1%. Close this exact continuation
  without LR/reward/vector/range/horizon tuning. The next authorized work is a
  read-only integration audit of the existing measured per-joint delay/tau
  actuator bridge against the ground-up stack. It does not authorize training,
  local GPU, RDK-X5, robot, deployment, torque, or motor access.
- 2026-07-14: The read-only measured-bridge integration audit passes. The JAX
  training transition and independent NumPy evaluator agree within
  1.4305115e-7 rad across five 256-tick deterministic sequences; all source
  ordering and vector-provenance checks pass. The composable order is hard-
  bounded sent target, then fitted delay/tau plus pitch-chain velocity bridge,
  then physics, while observation history retains the sent target and actual
  joint state. Non-pitch 5.24 rad/s values are neutral, not claimed as measured.
  This selects a bridge-only causal arm but does not authorize training. The
  rejected penalty stack must not be restored. See
  `outputs/analysis/GROUND_UP_MEASURED_BRIDGE_INTEGRATION_AUDIT_20260714.md`.
- 2026-07-14: The measured-bridge-only continuation is preregistered before
  implementation. It protects the 1,003,520 hard-vector checkpoint because it
  has better tracking and zero saturation versus the later checkpoint. The
  only causal change is deterministic fitted delay/tau after the existing hard
  target limit; no bridge penalty, behavior prior, restore KL, or other reward
  term is allowed. A passing CPU restore/update/export contract is required
  before one frozen 2M-step hosted job. See
  `outputs/analysis/GROUND_UP_MEASURED_BRIDGE_ONLY_CONTINUATION_PREREGISTRATION_20260714.md`.
- 2026-07-14: The measured-bridge implementation and CPU continuation contract
  pass. The composed patch applies cleanly after the hard-vector stack; compiled
  physics control equals the bridged target exactly, independent-model error is
  <=2.24e-7 rad, sent-target observation history is preserved, and no bridge
  reward/cost exists. The 1,024-step smoke restored the protected 1,003,520
  checkpoint with zero parameter error, changed all 10 policy leaves, kept all
  parameters/metrics finite, and exported valid stateful ONNX with 2.98e-8
  maximum bound excess. This authorizes only the one frozen hosted continuation
  in the preregistration. No local GPU, RDK-X5, robot, deployment, or motor use.
  See `outputs/analysis/GROUND_UP_MEASURED_BRIDGE_CONTINUATION_CPU_SMOKE_20260714.md`.
- 2026-07-14: The single measured-bridge-only T4 continuation completed and
  was recovered/hash-verified before shutdown; Colab has zero active sessions.
  All 12 post-update CPU runs walk with bilateral transitions, zero saturation,
  and zero target-rate excess. The 1M x=.08 cell passes tracking at .18858 rad,
  proving bridge training can clear the actuator gate without penalties or
  gait collapse, but the other 1M cells are .20137/.21099 and all 2M cells are
  .20332-.20832 versus the <=.20 threshold. The persistence rule therefore
  rejects the exact feedforward bridge-only arm without checkpoint selection or
  tuning. Next work is a read-only actor/actuator-state observability audit; no
  training is authorized. See
  `outputs/analysis/GROUND_UP_MEASURED_BRIDGE_ONLY_RESULT_20260714.md`.
- 2026-07-14: The exact 115-D actuator-state observability audit passes and
  selects an applied-target slot, not recurrence. The existing three action
  histories cover the 2-3 tick delay within 5.15e-8 rad. The absolute sent-
  target slot is an affine duplicate of last_act within 5.15e-8 rad, while
  previous bridge-applied target is absent. A controlled identical-observation/
  identical-action fork with only 0.04 rad hidden applied-state difference
  changes next physics control by 0.0299975 rad and next qpos by 0.0028491 rad.
  Replace the redundant sent-target slot with applied target while keeping 115
  inputs; no training is authorized until separate preregistration/CPU proof.
  See `outputs/analysis/GROUND_UP_ACTUATOR_OBSERVABILITY_AUDIT_20260714.md`.
- 2026-07-14: The applied-target-state continuation is preregistered before
  implementation. It protects the bridge-only 1M checkpoint because its mean
  three-command tracking is .20031 versus .20550 at 2M and it already passes
  x=.08. The sole change is replacing redundant sent-target obs indices 83:97
  with bridge-applied target while keeping 115 inputs, sent action histories,
  physics, reward, architecture, and ONNX interface unchanged. A CPU default-
  off/slot/fork/restore/update/export contract must pass before one frozen T4
  job. See
  `outputs/analysis/GROUND_UP_APPLIED_TARGET_STATE_CONTINUATION_PREREGISTRATION_20260714.md`.
- 2026-07-14: The applied-target observation and continuation CPU gates pass.
  The actor remains exactly 115-D; default-off behavior, all non-replacement
  observation fields, and physics match exactly; enabled indices 83:97 equal
  the bridge-applied target with zero measured error; and the prior 0.04 rad
  hidden-state fork is visible only in that slot. The CUDA-sharded protected
  checkpoint was explicitly remapped through a verified CPU target tree with
  zero save/restore error. The final 1,024-step smoke restores the protected
  source exactly, changes all 10 policy leaves, retains finite metrics, and
  exports valid stateful hard-bounded ONNX at step zero and 1,024. This
  authorizes only the single frozen 2M-step T4 continuation in the existing
  preregistration. No local GPU, RDK-X5, robot, deployment, torque, or motor
  access is authorized. See
  `outputs/analysis/GROUND_UP_APPLIED_TARGET_CONTINUATION_CPU_SMOKE_20260714.md`.
- 2026-07-14: The single applied-target-state T4 continuation completed and its
  8,161,319-byte archive reproduced manifest SHA-256 `3b7457fe...52c9e7`
  locally before Colab was stopped; zero sessions remain. The 1M checkpoint is
  the first complete nominal pass in this route: all six x=.074/.077/.080,
  seeds 100/101 cells walk, transition bilaterally, have zero saturation/rate
  excess, and track at .18877/.18502/.17679 rad. The 2M checkpoint retains gait
  and zero saturation/rate excess but regresses tracking to
  .21617/.21694/.20817, failing all six cells versus .20. The frozen two-
  checkpoint persistence rule therefore rejects the exact arm without
  cherry-picking 1M. Next work is a read-only 1M-to-2M drift audit; no further
  training or x=0/robot/RDK/GPU gate is authorized. See
  `outputs/analysis/GROUND_UP_APPLIED_TARGET_STATE_RESULT_20260714.md`.
- 2026-07-14: The CPU-only applied-target 1M-to-2M drift audit passes all
  checkpoint, finite-value, 324-sample trace, and exact ONNX replay checks.
  Swapping only actor parameters produces .09496 raw-action RMS drift versus
  .01407 from swapping only observation normalization, a 6.75x ratio. Hosted
  evaluation reward improves by 16.73 while external joint-target tracking
  regresses by up to .02899 rad; the corresponding bridge-error changes are
  zero or negligible. This isolates actor/objective drift rather than bridge,
  normalization, restore, checksum, or transport corruption. Prior failed
  restore-KL/behavior-prior work is not revived. Next work is a read-only
  reward-contract audit; no training, robot, RDK-X5, deployment, or GPU access
  is authorized. See
  `outputs/analysis/GROUND_UP_APPLIED_TARGET_DRIFT_AUDIT_20260714.md`.
