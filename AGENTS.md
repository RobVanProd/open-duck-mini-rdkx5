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
- 2026-07-14: The nominal horizon audit rejects the apparent 1M pass as a
  startup-window artifact. The old 54-tick screen covers only 9% of the
  600-tick training episode. Applied-target 1M crosses the .20 rad tracking
  limit by cumulative tick 108 at x=.074/.080 and tick 162 at x=.077; its
  600-tick p95 is .21334-.22317. Both checkpoints still walk for all 600 ticks
  with zero rate excess. `BEST_WALK_ONNX_2` is slower (.01443-.01749 m/s),
  has 3.61-3.87 rad/s rate excess, and also fails full-horizon tracking. Future
  nominal advancement now prospectively requires the complete 600-tick gate.
  Mean error can improve while p95/exceedance frequency worsens, selecting a
  default-off tail-exceedance diagnostic for CPU contract only; the earlier
  failed mean pseudo-Huber, restore-KL, and behavior-prior recipes remain
  closed. No training or hardware access is authorized. See
  `outputs/analysis/GROUND_UP_NOMINAL_HORIZON_PERSISTENCE_AUDIT_20260714.md`,
  `outputs/analysis/GROUND_UP_NOMINAL_HORIZON_GATE_AMENDMENT_20260714.md`, and
  `outputs/analysis/GROUND_UP_TEMPORAL_TAIL_OBJECTIVE_DECISION_20260714.md`.
- 2026-07-14: The tracking-tail implementation and continuation CPU gates pass.
  The default-off pitch-chain diagnostic exactly implements squared exceedance
  above the unchanged .20 rad tracking gate, leaves transition state and
  observation unchanged, and matches NumPy over all 3,600 frozen trace rows
  within 9.95e-11. The 1,024-step CPU continuation restores the protected 1M
  source exactly, changes all 10 actor leaves, keeps every checkpoint and
  metric finite, records the nonzero tail metric at steps 0 and 1,024, and
  exports two valid hard-bounded stateful ONNX graphs. This authorizes only the
  three fixed, sequential hosted arms in the preregistered <=6-compute-unit
  search. It does not authorize local GPU/iGPU, RDK-X5, robot, deployment,
  torque, or motor access. See
  `outputs/analysis/GROUND_UP_TRACKING_TAIL_CPU_CONTRACT_20260714.md`,
  `outputs/analysis/GROUND_UP_TRACKING_TAIL_SEARCH_PREREGISTRATION_20260714.md`,
  and
  `outputs/analysis/GROUND_UP_TRACKING_TAIL_CONTINUATION_CPU_SMOKE_20260714.md`.
- 2026-07-14: The fixed tracking-tail hosted package passes its local contract.
  T1/T2/T3 exactly match the preregistered scales, each independently restores
  the protected applied-target 1M checkpoint, each requests 1M additional steps
  with three quantized exports, and every uploaded asset hash and composed
  patch applies cleanly at control commit `b9be205`. The single-session four-
  hour wall cutoff is 4.28 compute units at the user-reported 1.07 CU/hour,
  below the frozen 6-CU ceiling. Training reward cannot select an arm. This
  authorizes the fixed hosted package only; behavior is unevaluated and no
  local GPU, RDK-X5, robot, deployment, torque, or motor access follows. See
  `outputs/analysis/GROUND_UP_TRACKING_TAIL_COLAB_PACKAGE_CHECK_20260714.md`.
- 2026-07-14: The fixed tracking-tail search launched at
  2026-07-14T18:36:34Z in the named Colab T4 session
  `ground-up-tracking-tail-20260714`. All 15 assets uploaded successfully and
  remote asset validation passed before background PID 845 started. The order
  is fixed T1 -> T2 -> T3, with independent restore from the same protected 1M
  source for every arm. The session is limited by the preregistered package's
  four-hour wall cutoff. Behavior remains unevaluated; no local GPU, RDK-X5,
  robot, deployment, torque, or motor access is authorized.
- 2026-07-14: Before any behavior result was read, the running T1 arm exposed a
  mechanical checkpoint-schedule error in the package expectation: Brax uses
  `ceil(1,000,000 / (2 * 20,480)) = 25` updates per evaluation epoch, so the
  exact half/final steps are 512,000 and 1,024,000, not 501,760 and 1,003,520.
  The training command, scale, source, gate, and selection rule are unchanged.
  T1 is retained only if both corrected exports exist; the recovery path then
  rebuilds the exact package and runs T2/T3 from the same protected source.
  No reward or behavior outcome was inspected to make this correction.
- 2026-07-14: The hosted tracking-tail screen completed and the 24,480,277-byte
  archive reproduced SHA-256 `ae4c631a...d8ca60f` locally before Colab was
  stopped; zero sessions remain. All 36 preregistered CPU behavior cells walk
  for 600 ticks with bilateral transitions, zero saturation, and zero measured
  rate excess. T1 half/final worst tracking p95 is .22883/.23242, T2 is
  .21505/.20972, and T3 is .22048/.20410 versus the unchanged <=.20 limit.
  No arm passes both checkpoints, so the exact squared tail-exceedance
  formulation is closed without selecting T3 final or tuning another scale.
  No x=0, local GPU, RDK-X5, robot, deployment, torque, or motor gate is
  authorized. Next work is a read-only joint/phase trace audit. See
  `outputs/analysis/GROUND_UP_TRACKING_TAIL_SEARCH_RESULT_20260714.md`.
- 2026-07-14: Read-only joint and temporal audits reject two tempting follow-
  ups. Across all 36 traces, only left knee/ankle exceed .20 rad and the gate-
  setting joint shifts with scale, but per-tick max joint cost is exactly 6x
  the closed six-joint mean on every trace; it is only an untested stronger
  scale. T3 final misses the 30-tick five-percent boundary by 1/7/3 ticks with
  <.014 rad conditional RMS excess, but linear hinge has 21 gate-ranking
  disagreements versus 17 for squared hinge and is not selected. Temporal
  occupancy is the unresolved quantity; no trainable surrogate or hosted run
  is authorized. Next is a read-only phase/rate-boundary audit. See
  `outputs/analysis/GROUND_UP_TRACKING_TAIL_JOINT_PHASE_AUDIT_20260714.md` and
  `outputs/analysis/GROUND_UP_TRACKING_TAIL_TEMPORAL_OCCUPANCY_AUDIT_20260714.md`.
- 2026-07-14: The phase/rate-boundary audit selects a CPU-only stateful ONNX
  A/B. Across all 36 traces, 97.6268% of gate-setting exceedance ticks occur at
  or within two ticks after the measured target-rate boundary versus 79.7326%
  elsewhere (odds ratio 10.4565), and at least 88.31% of each trace's events
  lie in four reference-period bins. Three pitch-rate multipliers are frozen
  from 1x/2x/4x the exact T3-final .2041005-to-.20 gap before outcomes. All 12
  transformed T2/T3 half/final ONNX policies pass graph/interface, non-target
  initializer identity, exact pitch-delta, eight-tick bound, and state-output
  checks. This authorizes only the preregistered 72-cell local CPU screen; it
  does not authorize training, local GPU, x=0, RDK-X5, robot, deployment,
  torque, or motor use. See
  `outputs/analysis/GROUND_UP_TRACKING_TAIL_RATE_BOUNDARY_AUDIT_20260714.md`,
  `outputs/analysis/GROUND_UP_STATEFUL_PITCH_RATE_BOUNDARY_SCREEN_PREREGISTRATION_20260714.md`,
  and `outputs/analysis/GROUND_UP_STATEFUL_PITCH_RATE_TRANSFORM_CONTRACT_20260714.md`.
- 2026-07-14: The preregistered stateful pitch-rate boundary screen completed
  all 72 CPU-only behavior cells. Every cell ran the full 600 ticks, walked
  with bilateral transitions, and had zero action saturation and zero measured
  pitch-chain rate excess. R1 T2 half/final worst tracking p95 is
  .21493/.20887 and R1 T3 is .21985/.20074; R2 T2 is .21214/.20430 and R2 T3
  is .21317/.19931; R3 T2 is .20789/.21070 and R3 T3 is .21298/.19852 versus
  the unchanged <=.20 rad limit. No rate/tail combination passes both half and
  final checkpoints, so the screen is closed without promoting the closest
  result. No training, x=0 gate, local GPU, RDK-X5, robot, deployment, torque,
  or motor access is authorized. See
  `outputs/analysis/GROUND_UP_STATEFUL_PITCH_RATE_BOUNDARY_SCREEN_RESULT_20260714.md`.
- 2026-07-14: The preregistered smooth temporal-occupancy diagnostic closed
  without a winner. All 36 frozen 600-tick traces and three input hashes pass,
  and seed-100/101 diagnostics reproduce exactly. The best smooth candidate
  reduces exact-occupancy rank discordance from 20 to 14 pairs, but its p95
  discordance is 20 versus 17 for the closed squared hinge. No candidate beats
  both hinge baselines on both frozen rankings, so no occupancy surrogate,
  implementation, or training run advances. No Colab, local GPU, RDK-X5,
  robot, deployment, torque, or motor access is authorized. See
  `outputs/analysis/GROUND_UP_TEMPORAL_OCCUPANCY_SURROGATE_SCREEN_RESULT_20260714.md`.
- 2026-07-14: Actor-only cumulative checkpoint averaging is preregistered as
  the next CPU stabilization screen, based on measured 6.749x actor-dominant
  drift and repeated half/final gate instability. Transfer of the published
  SWA mechanism to this PPO trajectory is treated as an inference to test, not
  an assumed result. All eight T2/T3 cumulative-half/final ONNX policies pass
  exact archive/member hash, identical graph, actor arithmetic, current-
  checkpoint normalizer, nonactor initializer, pitch-rate delta, finite CPU
  inference, state-feedback, and chained-bound checks; maximum bound excess is
  2.98e-8 rad. This authorizes only the frozen 48-cell CPU behavior screen. No
  training, Colab, local GPU, RDK-X5, robot, deployment, torque, or motor access
  is authorized. See `outputs/analysis/GROUND_UP_ACTOR_SWA_SCREEN_PREREGISTRATION_20260714.md`
  and `outputs/analysis/GROUND_UP_ACTOR_SWA_TRANSFORM_CONTRACT_20260714.md`.
- 2026-07-14: The preregistered actor-SWA screen completed all 48 CPU-only
  behavior cells. Every cell ran 600 ticks with bilateral gait, zero action
  saturation, and zero measured rate excess, but no cumulative-average
  checkpoint clears .20 rad tracking. Unchanged T2 half/final is
  .21767/.21530, unchanged T3 is .22404/.21492, R3 T2 is .22102/.21761, and R3
  T3 is .22189/.21141. Actor averaging therefore preserves gait but worsens or
  fails to repair the gate; the formulation is closed without selecting the
  closest result. No training, x=0 gate, Colab, local GPU, RDK-X5, robot,
  deployment, torque, or motor access is authorized. Next work is read-only
  sent/applied/actual error decomposition. See
  `outputs/analysis/GROUND_UP_ACTOR_SWA_SCREEN_RESULT_20260714.md`.
- 2026-07-14: The preregistered sent/applied/actual decomposition passes on all
  156 committed traces (78 unique seed-100 traces) with exact seed-101
  reproduction and <=1e-12 identity error. Across 68 failing unique traces,
  all 3,329 above-.20-rad gate-joint events are compound: neither sent-to-
  applied bridge error nor applied-to-actual servo error exceeds .20 alone,
  and the two components align in sign in 100% of events. TAIL, RATE, and SWA
  independently classify `COMPOUND_SUBTHRESHOLD`. This rejects another bridge-
  only or servo-only retune and selects preregistration of an actual-position-
  centered absolute target guard CPU contract. It authorizes no implementation,
  training, Colab, local GPU, RDK-X5, robot, deployment, torque, or motor use.
  See `outputs/analysis/GROUND_UP_TRACKING_ERROR_DECOMPOSITION_RESULT_20260714.md`.
- 2026-07-14: The actual-position-centered target guard is preregistered at
  .20/.1825/.165 rad, derived from the .20 tracking boundary and zero/half/full
  one-tick buffer at the 1.75 rad/s maximum pitch rate. All 12 T2/T3 half/final
  stateful ONNX variants pass exact archive, interface, source initializer and
  operator-prefix, 13-node append, reachable chained CPU inference, realized-
  state feedback, nonpitch identity, absolute-guard, and existing velocity-
  boundary checks. Maximum guard excess and nonpitch error are zero; velocity
  numerical excess is 1.04e-7 normalized action units. This authorizes only
  the preregistered 72-cell CPU behavior screen. No training, Colab, local GPU,
  RDK-X5, robot, deployment, torque, or motor access is authorized. See
  `outputs/analysis/GROUND_UP_ACTUAL_CENTERED_GUARD_TRANSFORM_CONTRACT_20260714.md`.
- 2026-07-14: The 72-cell actual-centered guard screen produces the first
  persistent full-horizon nominal winner in the ground-up route. G1 (.20 rad)
  passes all six cells at both half/final for T2 (.18082/.18167 worst p95) and
  T3 (.18299/.17929); the frozen largest-margin, lower-worst-tracking tie-break
  selects `G1_EXACT_BOUNDARY/T2_EQUAL`, with minimum vx .08338 m/s. G2/T3 and
  both G3 combinations also pass, while G2/T2 is rejected for a 579-tick
  termination. This evidence supports the missing absolute sent-to-measured
  invariant, not a narrower buffer. It authorizes only preregistration of the
  x=0 preservation gate for both selected half/final policies. No x=0 run is
  authorized before that preregistration, and no training, Colab, local GPU,
  RDK-X5, robot, deployment, torque, or motor access is authorized. See
  `outputs/analysis/GROUND_UP_ACTUAL_CENTERED_GUARD_SCREEN_RESULT_20260714.md`.
- 2026-07-14: The preregistered four-cell x=0 preservation gate rejects direct
  promotion of the nominal G1/T2 winner. Both seeds reproduce exactly: half
  terminates at tick 73 with 87.67% action saturation and final at tick 211
  with 95.73% saturation. Rate excess remains zero and pre-termination
  tracking is inside .20, isolating the actor's unsupported x=0 output rather
  than the absolute guard. The command normalizer was trained only on
  x=.074-.080, so x=0 is far out of support. This authorizes only
  preregistration of a command-deadband zero-action repair that must preserve
  positive-command outputs exactly. The nominal winner remains held; no
  robustness ladder, training, Colab, local GPU, RDK-X5, robot, deployment,
  torque, or motor access is authorized. See
  `outputs/analysis/GROUND_UP_GUARD_WINNER_X0_RESULT_20260714.md`.
- 2026-07-14: The preregistered command-deadband repair transform passes every
  frozen structural and CPU-inference check for both selected half/final G1/T2
  policies. At x=0, action and recurrent state outputs are exactly zero; at
  x=.074/.077/.080, both outputs are bit-exact to their guarded sources. The
  original external interface, every source initializer, and the complete
  source operator prefix are preserved, with exactly five wrapper nodes
  appended. This authorizes only the frozen 16-cell local CPU behavior matrix.
  No robustness ladder, training, Colab, local GPU, RDK-X5, robot, deployment,
  torque, or motor access is authorized. See
  `outputs/analysis/GROUND_UP_COMMAND_DEADBAND_REPAIR_TRANSFORM_CONTRACT_20260714.md`.
- 2026-07-14: The frozen 16-cell command-deadband behavior matrix passes at
  both half/final checkpoints. All four x=0 cells complete 600 ticks at home
  with zero saturation and rate excess, |mean vx| .000658 m/s, and .030323 rad
  worst pitch-chain tracking p95. The unchanged moving-command gates also pass:
  half/final worst tracking is .180822/.181667 rad and minimum vx is
  .083376/.095190 m/s. This repairs the isolated out-of-support zero-command
  failure without changing the trained-command behavior. It authorizes only
  preregistration of an offline robustness ladder. No robustness run before
  preregistration, training, Colab, local GPU, RDK-X5, robot, deployment,
  torque, or motor access is authorized. See
  `outputs/analysis/GROUND_UP_COMMAND_DEADBAND_REPAIR_RESULT_20260714.md`.
- 2026-07-14: The offline robustness ladder is preregistered in the order
  already frozen by the original ground-up plan. R1 tests both independently
  measured P30 and P31/34 actuator fits; R2 isolates each pinned dynamics axis;
  R3 isolates declared sensor noise from additional 0/1/2-tick delays; R4 uses
  only the declared minimum .1 m/s push; R5 uses the established first rough
  rung z=.002; R6 combines only independently passed z=.002 and .1 m/s push.
  Seeds are mechanically derived from the committed repair-result hash. Both
  half/final checkpoints must retain all prior gates, with a tooling contract
  before every stage and an immediate stop at the first failure. Only R1 may be
  contracted and run next. No later stage, training, Colab, local GPU, RDK-X5,
  robot, deployment, torque, or motor access is authorized. See
  `outputs/analysis/GROUND_UP_OFFLINE_ROBUSTNESS_LADDER_PREREGISTRATION_20260714.md`.
- 2026-07-14: The R1 measured-actuator-fit contract passes every frozen check:
  both policy and P30/P31-34 fit hashes are exact, both fit schemas contain
  finite combined models for the six pitch joints, both stateful policy
  interfaces and shapes are exact, CPU inference is finite at all four
  commands, and accelerators are disabled. This authorizes only the 16-cell R1
  CPU behavior matrix: two checkpoints x two measured fits x four commands x
  one mechanically derived seed. No R2+, training, Colab, local GPU, RDK-X5,
  robot, deployment, torque, or motor access is authorized. See
  `outputs/analysis/GROUND_UP_ROBUSTNESS_R1_CONTRACT_20260714.md`.
- 2026-07-14: R1 closes the frozen guarded/deadband policy as a robustness
  winner at the first isolated stage. P30 still passes both checkpoints. Under
  the independently measured P31/34 fit, all six moving cells remain upright,
  bilateral, unsaturated, and below .20 rad tracking (.180555/.183142 worst),
  while x=0 also passes. The sole hard failure is exact and persistent: the
  policy reaches 1.750001 rad/s at the left ankle against P31/34's 1.50 rad/s
  fitted limit, a .250001 rad/s excess in every moving cell at both checkpoints.
  R2 and every later robustness stage are blocked. The next permitted work is
  preregistration of a future formulation that trains against both measured
  fits and their componentwise conservative velocity envelope; it is not yet
  authorized to implement or train. No Colab, local GPU, RDK-X5, robot,
  deployment, torque, or motor access is authorized. See
  `outputs/analysis/GROUND_UP_ROBUSTNESS_R1_RESULT_20260714.md`.
- 2026-07-14: Before spending Colab credit, a one-variable dual-fit
  conservative-envelope repair is preregistered. It changes only the existing
  ONNX `max_action_delta[0,4]` left-ankle constant from .14 to .12 normalized
  action/tick, exactly 1.50 rad/s x .02 s / .25 rad. Every node, interface,
  other initializer, zero-command deadband, and actual-position guard must be
  exact. After a transform contract, the repaired half/final policies must
  repeat all 16 R1 cells under both P30 and P31/34 fits. Passing only re-enters
  R1 and permits an R2 contract; failing closes the inference-only repair and
  permits preregistration of dual-fit training. No transform or behavior is
  authorized before its contract, and no training, Colab, local GPU, RDK-X5,
  robot, deployment, torque, or motor access is authorized. See
  `outputs/analysis/GROUND_UP_DUAL_FIT_CONSERVATIVE_ENVELOPE_REPAIR_PREREGISTRATION_20260714.md`.
- 2026-07-14: The dual-fit conservative-envelope transform passes after one
  pre-behavior contract correction: randomized measured joint offsets were
  made physically consistent with the chained previous target so the existing
  downstream actual-position guard would not correctly override the upstream
  rate clamp for impossible states. Both policies change only
  `max_action_delta[0,4]` from the stored float32 .14 to .12; every node,
  interface, and other initializer is exact. x=0 action/state remain exactly
  zero, CPU outputs are finite, maximum chained left-ankle delta is .120000124
  with 1.24e-7 numerical excess inside the frozen 5e-7 tolerance. This
  authorizes only the preregistered 16-cell dual-fit CPU behavior repeat. No
  R2+, training, Colab, local GPU, RDK-X5, robot, deployment, torque, or motor
  access is authorized. See
  `outputs/analysis/GROUND_UP_DUAL_FIT_CONSERVATIVE_ENVELOPE_TRANSFORM_CONTRACT_20260714.md`.
- 2026-07-14: The preregistered 16-cell dual-fit repeat passes completely after
  the single conservative left-ankle bound change. P30 half/final worst
  tracking is .180856/.183170 rad with minimum vx .086462/.097620 m/s;
  P31/34 is .178733/.181057 rad with minimum vx .084912/.096041 m/s. Both
  checkpoints preserve x=0, bilateral gait, zero saturation, and zero measured
  envelope excess under both hardware fits. This repairs and re-enters R1; it
  authorizes only construction of the R2 isolated-dynamics evaluator contract.
  R2 behavior, R3+, training, Colab, local GPU, RDK-X5, robot, deployment,
  torque, and motor access remain unauthorized. See
  `outputs/analysis/GROUND_UP_DUAL_FIT_CONSERVATIVE_ENVELOPE_REPAIR_RESULT_20260714.md`.
- 2026-07-14: The exact R2 isolated-dynamics matrix is preregistered before its
  evaluator contract or behavior. It contains 20 conditions in pinned source
  order: friction, friction-loss, armature, six one-axis torso-COM endpoints,
  link/torso mass, two deterministic home joint-offset corners, and KP. Every
  condition must pass both repaired checkpoints, both measured actuator fits,
  all four commands, the hash-derived seed, and 600 ticks: 16 cells each, 320
  maximum. Conditions are strictly sequential and stop at the first failure.
  The evaluator must first prove one-axis-only field/index mutation, endpoint
  readback, home-reset propagation, default-off reproduction, and CPU-only
  execution. No R2 behavior before that contract, R3+, training, Colab, local
  GPU, RDK-X5, robot, deployment, torque, or motor access is authorized. See
  `outputs/analysis/GROUND_UP_ROBUSTNESS_R2_MATRIX_PREREGISTRATION_20260714.md`.
- 2026-07-14: The R2 evaluator contract passes all frozen checks. All 20
  conditions contain exactly one supported axis, direct MJX readback shows no
  model fields outside the intended axis change, all readbacks are finite,
  default-off model arrays are exact, and the complete default-off 600-tick
  final/P30/x=.08 behavior reproduces the committed repaired-R1 result exactly
  after excluding wall-clock time. The .03-rad initialization smoke proves all
  14 offsets reach deterministic home-support reset. JAX and ONNX remain CPU
  only. This authorizes sequential R2 behavior beginning only with
  `FLOOR_FRICTION_LO`, stopping at its first failed condition. No R3+,
  training, Colab, local GPU, RDK-X5, robot, deployment, torque, or motor
  access is authorized. See
  `outputs/analysis/GROUND_UP_ROBUSTNESS_R2_EVALUATOR_CONTRACT_20260714.md`.
- 2026-07-14: The first condition-1 outputs are invalid evidence and were not
  aggregated because the campaign wrapper retained the requested override but
  discarded the simulator's per-run model readback. A serialization-only fix
  now copies that readback into every run. Its CPU smoke records floor friction
  1.0 -> .5 and changed index [0,0] exactly. The identical 16 condition-1 cells
  must be rerun and overwrite the invalid outputs; no behavior parameter may
  change. Condition 2+, R3+, training, Colab, local GPU, RDK-X5, robot,
  deployment, torque, and motor access remain unauthorized. See
  `outputs/analysis/GROUND_UP_ROBUSTNESS_R2_REPORTING_CONTRACT_20260714.md`.
- 2026-07-14: The evidence-complete `FLOOR_FRICTION_LO` rerun passes all 16
  cells with exact per-run 1.0 -> .5 floor-friction readback. Both actuator
  fits and both checkpoints preserve x=0, bilateral gait, zero saturation and
  measured-envelope excess. Worst tracking remains .183170 rad and minimum vx
  remains .084912 m/s across the matrix; no measurable behavior regression is
  present in this flat-contact suite. Only `FLOOR_FRICTION_HI` is authorized
  next. Condition 3+, R3+, training, Colab, local GPU, RDK-X5, robot,
  deployment, torque, and motor access remain unauthorized. See
  `outputs/analysis/GROUND_UP_ROBUSTNESS_R2_FLOOR_FRICTION_LO_RESULT_20260714.md`.
- 2026-07-14: `FLOOR_FRICTION_HI` also passes all 16 cells with exact per-run
  1.0 readback. It is the model's default boundary and reproduces the repaired
  R1 metrics exactly. Only `JOINT_FRICTIONLOSS_LO` is authorized next;
  condition 4+, R3+, training, Colab, local GPU, RDK-X5, robot, deployment,
  torque, and motor access remain unauthorized. See
  `outputs/analysis/GROUND_UP_ROBUSTNESS_R2_FLOOR_FRICTION_HI_RESULT_20260714.md`.
- 2026-07-14: `JOINT_FRICTIONLOSS_LO` passes all 16 cells with exact 0.9x
  before/after vector readback. Worst tracking is .182504 rad and minimum vx is
  .084560 m/s; all x=0, gait, saturation, and envelope gates pass. Only
  `JOINT_FRICTIONLOSS_HI` is authorized next. Condition 5+, R3+, training,
  Colab, local GPU, RDK-X5, robot, deployment, torque, and motor access remain
  unauthorized. See
  `outputs/analysis/GROUND_UP_ROBUSTNESS_R2_JOINT_FRICTIONLOSS_LO_RESULT_20260714.md`.
- 2026-07-14: `JOINT_FRICTIONLOSS_HI` passes all 16 cells with exact 1.1x
  readback. Worst tracking is .182750 rad and minimum vx is .082996 m/s; every
  earlier hard gate remains green. Only `ARMATURE_LO` is authorized next.
  Condition 6+, R3+, training, Colab, local GPU, RDK-X5, robot, deployment,
  torque, and motor access remain unauthorized. See
  `outputs/analysis/GROUND_UP_ROBUSTNESS_R2_JOINT_FRICTIONLOSS_HI_RESULT_20260714.md`.
- 2026-07-14: `ARMATURE_LO` passes all 16 cells with exact 1.0x readback and
  reproduces the repaired-R1 default metrics. Only `ARMATURE_HI` is authorized
  next. Condition 7+, R3+, training, Colab, local GPU, RDK-X5, robot,
  deployment, torque, and motor access remain unauthorized. See
  `outputs/analysis/GROUND_UP_ROBUSTNESS_R2_ARMATURE_LO_RESULT_20260714.md`.
- 2026-07-14: `ARMATURE_HI` passes all 16 cells with exact 1.05x readback.
  Worst tracking is .183966 rad and minimum vx is .083785 m/s; all hard gates
  pass. Only `TORSO_COM_X_NEG` is authorized next. Condition 8+, R3+,
  training, Colab, local GPU, RDK-X5, robot, deployment, torque, and motor
  access remain unauthorized. See
  `outputs/analysis/GROUND_UP_ROBUSTNESS_R2_ARMATURE_HI_RESULT_20260714.md`.
- 2026-07-14: The first `TORSO_COM_X_NEG` formal pass is invalid evidence and
  does not authorize condition 8. A post-aggregation causal audit found all 16
  traces byte-identical to the default-armature traces. The evaluator had
  mutated `body_ipos[1]`, but compiled body 1 is the massless `base`; the
  intended inertial torso is body 2, `trunk_assembly`, at .698526 kg. The
  evaluator now resolves `trunk_assembly` by name, rejects massless targets,
  and records name/ID/mass. Its corrected contract passes exact identity,
  default-off reproduction, CPU-only execution, and a new paired sensitivity
  smoke proving the -.05 m COM shift changes dynamics. Only an identical
  condition-7 rerun is authorized. Condition 8+, R3+, training, Colab, local
  GPU, RDK-X5, robot, deployment, torque, and motor access remain unauthorized.
  See
  `outputs/analysis/GROUND_UP_ROBUSTNESS_R2_TORSO_BODY_INDEX_CORRECTION_20260714.md`.
- 2026-07-14: The corrected `TORSO_COM_X_NEG` condition fails all four frozen
  checkpoint/fit matrices and stops R2. All 16 requested cells and exact
  `trunk_assembly` body-2 readbacks are present on CPU. Every x=0 cell falls
  after 47 samples (.94 s), with base height reaching .05631 m and mean vx
  reversing to -.37185 m/s. Every moving cell falls after 41-42 samples;
  minimum matrix mean vx ranges from -.39295 to -.41097 m/s. Both half/final
  checkpoints fail under both P30 and P31/34 fits, so this is a persistent
  torso-COM robustness failure rather than fit or checkpoint selection noise.
  The frozen stop rule authorizes no `TORSO_COM_X_POS`, later R2 condition,
  R3+, training, Colab, local GPU, RDK-X5, robot, deployment, torque, or motor
  access. See
  `outputs/analysis/GROUND_UP_ROBUSTNESS_R2_TORSO_COM_X_NEG_RESULT_20260714.md`.
- 2026-07-14: The condition-7 failure exposes the same torso-index defect in
  the training pipeline: upstream `playground/common/randomize.py` declares
  `TORSO_BODY_ID = 1`, so its advertised COM jitter and added torso mass target
  the massless outer `base`, not .698526 kg `trunk_assembly` body 2. The new
  ground-up patch corrects the default index and adds a targeted X-COM
  randomizer that the runner enables independently of nominal deterministic
  reset/command/noise/push controls after resolving the torso by name. Its CPU
  contract passes: 4,096 uniform samples cover -.04999 to +.04999 m, exact
  anchors have counts 1378/1372/1346, only `body_ipos[2,0]` changes, and the
  default randomizer now changes body 2 while body 1 stays massless and exact.
  See `outputs/analysis/GROUND_UP_TORSO_COM_RANDOMIZER_CONTRACT_20260714.md`.
- 2026-07-14: A three-arm torso-COM remediation search is preregistered before
  package work or compute: direct uniform +/-.05 m, direct categorical
  -.05/0/+.05 m anchors, and a uniform .01 -> .03 -> .05 m curriculum. Every
  arm restores the same raw T2 final checkpoint, preserves the proven nominal
  recipe, uses the conservative 1.50 rad/s left-ankle limit, and changes only
  the COM sampling schedule/distribution. A CPU restore/1,024-step/package
  contract is required before a maximum 8-Colab-unit sequential search. Every
  evaluated export receives the same guard/deadband/envelope transforms and
  must persist at two checkpoints across nominal R1 plus both X COM endpoints
  under both actuator fits. No closest arm can advance. Colab is not yet
  authorized; local GPU, condition 8+, R3+, RDK-X5, robot, deployment, torque,
  and motor access remain unauthorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_REMEDIATION_SEARCH_PREREGISTRATION_20260714.md`.
- 2026-07-14: The torso-COM hosted package and 1,024-step CPU smoke pass with
  zero failed checks. The protected source restores exactly at step zero, all
  actor leaves change after the finite update, both stateful ONNX exports pass
  interface and conservative rate-bound checks, the tail metric is finite and
  nonzero, every uploaded asset hash matches, and a fresh composition matches
  the randomizer contract. This authorizes only the frozen sequential
  `U05_DIRECT`, `A05_DIRECT`, and `U_CURRICULUM` Colab search under its maximum
  8-compute-unit ceiling. It does not authorize a closest-result promotion,
  condition 8+, R3+, local GPU, RDK-X5, robot, deployment, torque, or motor
  access. See
  `outputs/analysis/GROUND_UP_TORSO_COM_PACKAGE_CPU_SMOKE_20260714.md`.
- 2026-07-14: The first hosted invocation exited before asset validation,
  environment installation, or training because Colab injected its kernel
  `-f` argument and the job used strict argument parsing. No checkpoint or
  policy update occurred. The transport-only correction uses
  `parse_known_args`, leaving every frozen asset, arm, command, seed, schedule,
  and compute ceiling unchanged; repeat the CPU package checker before retry.
- 2026-07-14: The retry completed the entire `U05_DIRECT` training command,
  then stopped only at an incorrect predicted-export assertion. The remotely
  observed checkpoint and ONNX steps are exactly `0/1003520/2007040`, matching
  the established 256-environment hosted rounding from prior 2M jobs, rather
  than CPU-smoke-derived `0/1024000/2048000`. Preserve this completed arm; do
  not retrain it. Correct only the deterministic export-name contract (and the
  analogous curriculum names `501760/1003520`), rerun the CPU package checker,
  and resume sequentially. No behavior result or selection changed.
- 2026-07-14: Curriculum stage 1 completed at exact exports `0/512000` and
  stopped at the remaining inferred `501760` assertion. The distinction is
  `512000` for the two-evaluation 500k shape versus `501760/1003520` for the
  three-evaluation 1M shape. Preserve stage 1 without retraining, correct both
  500k-stage name assertions to `512000`, rerun the package checker, and resume.
  No training or selection variable changed.
- 2026-07-14: Curriculum stages 2 and 3 completed. Stage 2 exported
  `0/512000`; stage 3 exported `0/512000/1024000`, proving the original
  curriculum naming was correct. Only the direct 2M arms use
  `1003520/2007040`. Preserve all five completed stage outputs, restore the
  preregistered curriculum names, rerun the package checker, then use one
  reporting-only resume to validate and archive without retraining.
- 2026-07-14: Before the final reporting-only resume, Colab marked the session
  lost (404/401) and the file API no longer exposed the completed outputs. No
  checkpoint or ONNX from that session is recoverable evidence. The exact
  search remains within its 8-unit ceiling and may be rerun unchanged, but the
  transport must first atomically rebuild a downloadable partial archive after
  every completed stage. CPU-check and commit that recovery-only change before
  allocating a replacement session; download each partial snapshot while the
  session remains live.
- 2026-07-15: The exact replacement search completed all three arms/five stages
  in 3272.1054 hosted seconds. Atomic snapshots were downloaded after every
  stage; the final 35,367,830-byte archive matches SHA-256
  `364d889bee76a0dee0e2635f3847a5b63d8d92e37af8aa80070f325a8ecfe592`,
  and Colab has zero active sessions. The local CPU artifact contract passes
  all checks: every source hash, command, export step, curriculum restore link,
  training log, event file, checkpoint, and all 13 ONNX hashes/interfaces/rate
  bounds are exact. Behavior remains unevaluated. This authorizes only the
  preregistered local CPU behavior evaluation; it does not make any arm a
  winner or authorize later robustness, local GPU, RDK-X5, or robot access.
  See `outputs/analysis/GROUND_UP_TORSO_COM_COLAB_ARTIFACT_CHECK_20260715.md`.
- 2026-07-15: The six frozen full-range evaluation exports pass their transform
  contract. Each source hash matches the recovered manifest; the 0.20-rad
  actual-position guard and x=0 deadband CPU contracts pass; all source
  initializers remain exact; and every source already contains the conservative
  0.12 normalized left-ankle delta (1.50 rad/s), so no envelope mutation is
  needed. This authorizes only the preregistered CPU behavior matrices. No arm
  is selected, and local GPU, RDK-X5, and robot access remain unauthorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_EVAL_POLICY_TRANSFORM_CONTRACT_20260715.md`.
- 2026-07-15: The frozen torso-COM remediation behavior evaluation is complete.
  All 144 requested cells are present on CPU with exact evaluator configuration,
  contracted policy path/hash, and per-run dynamics readback. All 12 nominal
  matrices pass. All 12 corrected `TORSO_COM_X_NEG` matrices and all 12
  symmetric `TORSO_COM_X_POS` matrices fail; every arm therefore passes only
  4/12 matrices and 20/48 cells. No arm advances and no closest arm is promoted.
  Decision: `CLOSE_EXACT_TARGETED_COM_FORMULATION_NO_WINNER`. This exact
  formulation is closed. R2 resumption, R3+, training, Colab, runtime design,
  local GPU/iGPU, RDK-X5, and robot access remain unauthorized; any next
  hypothesis requires a separate preregistration. See
  `outputs/analysis/GROUND_UP_TORSO_COM_REMEDIATION_BEHAVIOR_DECISION_20260715.md`.
- 2026-07-15: A direct pre/post audit rejects missing corrected-axis exposure
  as a sufficient causal explanation. Pre-remediation X_NEG fell at 41-47
  ticks with mean vx down to -.410971 m/s; after 512K-2M steps of corrected
  full-range training exposure, XNEG still falls at 42-55 ticks with mean vx
  down to -.410235 m/s. XPOS has the opposite signed failure: all moving cells
  reach .254248-.424365 m/s and fall, while every x=0 cell and the complete
  nominal matrix remain stable. Tracking stays below .184 rad. See
  `outputs/analysis/GROUND_UP_TORSO_COM_EXPOSURE_HYPOTHESIS_AUDIT_20260715.md`.
- 2026-07-15: The preregistered read-only CPU observability probe passes its
  evidence contract and selects `PASS_INSTANTANEOUS_IMU_COM_DECODE`. The exact
  tick-zero six-input gyro/accelerometer vector classifies NEG/NOMINAL/POS at
  100% in every held-out arm, command, and actuator-fit fold; family-wise
  permutation p is 1/1001. Raw audit shows gyro is zero and each COM class has
  one distinct accelerometer vector repeated across all 48 traces. History is
  not selected. Only a separately preregistered objective/exploitation study
  is supported; no training, simulator replay, explicit COM input, range
  narrowing, architecture change, Colab, GPU/iGPU, RDK-X5, or robot work is
  authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_OBSERVABILITY_DECODE_RESULT_20260715.md`
  and
  `outputs/analysis/GROUND_UP_TORSO_COM_INSTANTANEOUS_DECODE_RAW_AUDIT_20260715.md`.
- 2026-07-15: The decode selection above is superseded after a nested-feature
  audit. Tick-zero remains one exact accelerometer vector per COM class, but
  the 144 rows are only three deterministic prototypes, so p=1/1001 is not an
  inferential significance result. Prefix construction and training-fold
  standardization preserve tick zero exactly at every N; a tick-zero-only
  probe stays perfect. The all-feature ridge regresses at N=2/8/16 because it
  reallocates weight onto later command-dependent nuisance dimensions. Thus
  the N>1 table is not a monotone information test and selects neither memory
  nor an objective/exploitation route. Only a separately preregistered
  CPU-only full-115-D replay plus actor obs[3:6] sensitivity contract is
  supported. No replay, training, architecture change, Colab, GPU/iGPU,
  RDK-X5, or robot work is yet authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_DECODE_INTERPRETATION_CORRECTION_20260715.md`.
- 2026-07-15: The next read-only evidence study is preregistered before replay.
  It freezes one exact 144-cell CPU reporting replay with full 115-D traces,
  separate ACCEL3/FULL115 instantaneous and local-window probes with no
  inferential p-value, and identical-state forks of all six contracted actors
  changing only `obs[3:6]` along the measured COM direction. A source/device/
  graph/reproduction contract must pass first. No replay or sensitivity is
  authorized before that contract, and no outcome directly authorizes
  training, Colab, GPU/iGPU, RDK-X5, robot, deployment, torque, or motors. See
  `outputs/analysis/GROUND_UP_TORSO_COM_FULL_OBSERVATION_REPLAY_SENSITIVITY_PREREGISTRATION_20260715.md`.
- 2026-07-15: The full-observation study contract passes all 15 source, graph,
  CPU-provider, matrix/readback, append-only trace, comparison-normalizer, and
  refusal checks without executing a simulator behavior cell. Exact hashes of
  the replay and analysis tools are frozen in the JSON contract. This
  authorizes only the one exact 144-cell CPU reporting replay; decode and actor
  forks may follow only if all behavior fields reproduce. No training, Colab,
  GPU/iGPU, RDK-X5, robot, deployment, torque, or motors are authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_FULL_OBSERVATION_REPLAY_SENSITIVITY_CONTRACT_20260715.md`.
- 2026-07-15: The exact reporting replay passes all 36 matrices/144 cells on
  CPU. All 40,520 full-observation rows are finite and contiguous; every
  non-reporting behavior and dynamics-readback field reproduces exactly. Raw
  traces total 282,562,344 bytes and have canonical manifest SHA-256
  `7d7ccbe3...9c9f01`. Before any analysis outcome, the oversized primal ridge
  solve was mechanically replaced by its algebraically identical dual form
  when features exceed samples; fixed scores agree within 2.14e-14 and a new
  zero-behavior-cell contract freezes the corrected analysis hash. Only the
  preregistered decode and actor forks are authorized next. See
  `outputs/analysis/GROUND_UP_TORSO_COM_FULL_OBSERVATION_REPLAY_RESULT_20260715.md`
  and
  `outputs/analysis/GROUND_UP_TORSO_COM_FULL_OBSERVATION_ANALYSIS_IMPLEMENTATION_CORRECTION_20260715.md`.
- 2026-07-15: The full-observation study completes with
  `RESET_TRANSIENT_ONLY_UNDER_FROZEN_PROBES` plus
  `SUBSTANTIAL_ACCEL_RESPONSE`. ACCEL3 and FULL115 both pass only at tick zero;
  neither instantaneous ticks 24-40 nor any one fixed local-window width passes
  the frozen persistence rule. This is probe-limited, not an information-
  absence claim. Separately, all 576 identical-state ONNX forks reproduce
  baseline action exactly and all six actors materially respond when only
  `obs[3:6]` is changed: mid-gait p95 maximum differences are .07206-.12575
  normalized action. Near-zero actor sensitivity is rejected, but corrective
  sign is unknown. Only a separately preregistered read-only CPU signed causal-
  response study is supported; no objective, memory, estimator, training,
  Colab, GPU/iGPU, RDK-X5, or robot action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_FULL_OBSERVATION_REPLAY_SENSITIVITY_RESULT_20260715.md`.
- 2026-07-15: The signed causal-response study is preregistered before any
  physical fork. It freezes 144 nominal moving-state cells across all six
  policies, both measured fits, three commands, and ticks 0/24/32/40. Each cell
  compares the eight-tick pitch trajectory from physical COM +/- .05 m under
  identical saved actions against the pitch trajectory from actor obs[3:6]
  +/- the measured COM direction under nominal dynamics. Cosine <=-.25 is
  corrective and >=+.25 amplifying, with policy/checkpoint persistence frozen
  before outcomes. A CPU reconstruction/isolation contract must pass first.
  No formal fork, training, Colab, GPU/iGPU, RDK-X5, or robot action is yet
  authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_SIGNED_CAUSAL_RESPONSE_PREREGISTRATION_20260715.md`.
- 2026-07-15: The signed causal-response pre-outcome contract passes every
  check with zero formal cells executed. It locks 36 exact nominal moving
  traces, all six CPU ONNX graphs, recurrent reconstruction, the fitted
  actuator queue, saved sent/applied targets, exact matched-branch identity,
  and a `trunk_assembly` body-2 X-COM-only mutation. Maximum baseline error is
  zero, matched-branch error is zero, and the maximum bridge/target error is
  5.15e-08 rad. The exact contracted tool may now run the frozen 144 cells;
  no other study, training, Colab, GPU/iGPU, RDK-X5, runtime, or robot action
  is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_SIGNED_CAUSAL_RESPONSE_CONTRACT_20260715.md`.
- 2026-07-15: The exact 144-cell signed causal-response study completes on
  CPU. Every physical and actor pitch effect is non-negligible, but all six
  checkpoints are `MIXED_POLICY_RESPONSE`: aggregate counts are 67 corrective,
  55 amplifying, 22 mixed, and zero negligible. No checkpoint meets either
  systematic-sign rule, so neither sibling pair supports a family and the
  frozen decision is `MIXED_SIGN_NO_POLICY_FAMILY_SELECTED`. The strongest
  descriptive localization is temporal (tick 0: 19/7 corrective/amplifying;
  tick 24: 21/9; tick 32: 16/15; tick 40: 11/24), but it cannot promote a
  closest checkpoint or select memory, objective, estimator, actuator-effect,
  policy, or training work. Only a separately preregistered localization study
  may follow. No training, Colab, GPU/iGPU, RDK-X5, runtime, or robot action is
  authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_SIGNED_CAUSAL_RESPONSE_RESULT_20260715.md`.
- 2026-07-15: The next read-only localization study is preregistered before any
  new simulator branch. Existing vectors show that physical COM pitch response
  remains positive in every cell while actor-effect sign changes with time,
  but cannot tell whether actor response or plant phase causes the mixture.
  The crossed study freezes 36 traces x four target-state ticks x four donor
  actor-response ticks = 576 cells. Donor ONNX offsets are transplanted around
  each target baseline, preserving actual magnitude/asymmetry and exactly
  reproducing the prior pair on the diagonal. A deterministic two-way effect
  decomposition and all-six-policy persistence rule are frozen before outcomes.
  A zero-formal-cell CPU contract must pass first. No training, Colab,
  GPU/iGPU, RDK-X5, runtime, or robot action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_CROSSED_PHASE_LOCALIZATION_PREREGISTRATION_20260715.md`.
- 2026-07-15: The crossed phase-localization pre-outcome contract passes all
  checks with zero formal cells. It verifies the exact 36-trace, 576-cell
  Cartesian index (144 diagonal and 432 off-diagonal), all six CPU ONNX graphs,
  recurrent/bridge/target reconstruction, and nonzero donor offsets. All 1,152
  planned first actions remain naturally inside [-1,1], spanning
  -.969705-.972630, so no clipping or outcome repair is needed. Maximum
  bridge/target error is 5.15e-08 rad. The hash-locked tool may now run the
  exact matrix, subject to its 1e-12 diagonal-reproduction validity gate. No
  training, Colab, GPU/iGPU, RDK-X5, runtime, or robot action is authorized.
  See
  `outputs/analysis/GROUND_UP_TORSO_COM_CROSSED_PHASE_LOCALIZATION_CONTRACT_20260715.md`.
- 2026-07-15: The exact 576-cell crossed phase-localization study completes on
  CPU and passes its validity gate: all 144 diagonal pitch/alignment outcomes
  reproduce with zero error, and no cell is negligible. Aggregate counts are
  303 corrective, 207 amplifying, and 66 intermediate. All six checkpoints are
  `DISTRIBUTED_OR_UNRESOLVED`. Interaction is the largest descriptive effect
  for every checkpoint (.453109-.572954), but none reaches the frozen .60 and
  2x dominance rule, so it cannot be promoted. The target/donor grid confirms
  coupling—for donor tick 40 the response is mostly corrective at target ticks
  0/24/32 but amplifying at target tick 40—without selecting an actor-action,
  plant-phase, joint-phase, architecture, objective, estimator, policy, or
  training family. Any further evidence step requires separate
  preregistration. No training, Colab, GPU/iGPU, RDK-X5, runtime, or robot
  action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_CROSSED_PHASE_LOCALIZATION_RESULT_20260715.md`.
- 2026-07-15: A matched-state physical accelerometer map is preregistered
  before any sensor outcome. The prior signed/crossed studies reused a reset-
  derived COM direction at every phase even though prior probes found it clean
  only at reset. The new 144-cell CPU study uses identical nominal/COM-NEG/
  COM-POS states at ticks 0/24/32/40, calls `mj_forward` without advancing time
  or applying an action, and reads the name-resolved accelerometer. It freezes
  magnitude, centering, direction, native-vs-saved readback, tick-zero anchor,
  persistence, and next-study rules. A zero-formal-cell contract must pass
  before physical COM sensor readback. No actor fork, dynamic step, training,
  Colab, GPU/iGPU, RDK-X5, runtime, or robot action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_MATCHED_ACCELEROMETER_MAP_PREREGISTRATION_20260715.md`.
- 2026-07-15: The matched accelerometer-map pre-outcome contract passes every
  check with zero formal sensor cells, zero dynamic steps, and zero actor calls.
  It locks the exact 36 traces/144 states, CPU-only device, name-resolved
  three-axis `accelerometer` at address 6 on `imu`, finite state schemas, and
  body-2 X-only COM mutations. The exact tool may now read the frozen static
  sensor map, subject to preregistered 1e-3 m/s^2 nominal-readback and tick-zero
  direction validity gates. No actor fork, dynamic step, training, Colab,
  GPU/iGPU, RDK-X5, runtime, or robot action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_MATCHED_ACCELEROMETER_MAP_CONTRACT_20260715.md`.
- 2026-07-15: The formal matched accelerometer map is
  `INVALID_MATCHED_ACCELEROMETER_READBACK`. Native `mj_forward` reconstructed
  from saved reporting `qpos/qvel/ctrl` misses the saved MJX actor
  accelerometer by up to 7.427465 m/s^2 (frozen tolerance 1e-3), and the native
  tick-zero COM half-direction misses frozen `d` by .173359 m/s^2. Therefore
  none of the 144 apparent direction classes is interpretable or selectable;
  do not relax tolerance or use the closest table. This is a method failure,
  not evidence for fixed, weak, rotated, or nonlinear COM sensing. A valid
  successor must be separately preregistered and branch exact replayed MJX
  environment state including observation/solver state, rather than rebuilding
  native state from reporting fields. No actor fork, training, Colab,
  GPU/iGPU, RDK-X5, runtime, or robot action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_MATCHED_ACCELEROMETER_MAP_RESULT_20260715.md`.
- 2026-07-15: The exact MJX correction is preregistered before instrumentation
  or COM branch outcomes. It freezes default-off append-only evaluator fields,
  the same 12 nominal matrices/36 moving runs/144 ticks, exact baseline trace
  reproduction, live pre-policy MJX state cloning, body-2 X-only model forks,
  `mjx.forward` without branch time advancement, and the same physical-map
  thresholds as the invalid native attempt. A committed contract must prove
  default-off behavior/schema identity and lock post-instrumentation hashes
  before formal map readback. No actor fork, training, Colab, GPU/iGPU,
  RDK-X5, runtime, or robot action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_EXACT_MJX_ACCELEROMETER_REPLAY_PREREGISTRATION_20260715.md`.
- 2026-07-15: The exact-MJX pre-outcome contract passes all checks with zero
  formal COM cells. The default-off append-only instrumentation is hash locked,
  and a 600-tick CPU regression reproduces the prior full-observation trace
  field-for-field and byte-for-byte (`e4a245...`) with zero map fields. Static
  inspection verifies guarded default-off configuration and `mjx.forward`-only
  COM branches with no time advancement. The exact tool may now replay the
  frozen 12 matrices/36 moving runs/144 cells. No actor counterfactual,
  training, Colab, GPU/iGPU, RDK-X5, runtime, or robot action is authorized.
  See
  `outputs/analysis/GROUND_UP_TORSO_COM_EXACT_MJX_ACCELEROMETER_REPLAY_CONTRACT_20260715.md`.
- 2026-07-15: The exact 36-run MJX replay completes but is
  `INVALID_EXACT_MJX_ACCELEROMETER_REPLAY`. Its baseline instrumentation is
  proven exact: all 21,600 trace rows reproduce with zero mismatches after
  stripping the append-only field, and nominal actor accelerometer error is
  zero. However, all 36 tick-zero COM half-directions miss frozen `d` by
  .0133886 m/s^2, above the frozen 1e-3 tolerance. Therefore none of the 144
  apparent classes is interpretable or selectable. Do not relax tolerance or
  use the closest table. The discrepancy is now localized to live nominal
  `state.data` forwarded under a replaced COM model versus data initialized
  under that COM model; the responsible initialization field is unproven. Only
  a separately preregistered read-only initialization-order audit may follow.
  No actor fork, training, Colab, GPU/iGPU, RDK-X5, runtime, or robot action is
  authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_EXACT_MJX_ACCELEROMETER_REPLAY_RESULT_20260715.md`.
- 2026-07-15: A deterministic seven-variant MJX initialization-order audit is
  preregistered before any new endpoint sensor read. It freezes the exact
  nominal/NEG/POS tick-zero trace oracle and compares fresh COM-model init,
  unchanged live forward, isolated qacc-warmstart reset, isolated fresh
  `_impl`, their combination, and two fresh-primary-copy variants. The 1e-3
  endpoint tolerance and first-match causal decision are frozen. This is a
  single-state methods audit only; a zero-outcome contract must pass first. No
  dynamic step, actor/policy call, training, Colab, GPU/iGPU, RDK-X5, runtime,
  or robot action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_MJX_INITIALIZATION_ORDER_AUDIT_PREREGISTRATION_20260715.md`.
- 2026-07-15: The initialization-order pre-outcome contract passes all source,
  trace, body/sensor, home-state, MJX-field, variant-source, and CPU checks.
  It executed zero formal endpoint reads, dynamic steps, or actor calls. The
  committed contract authorizes only the frozen seven-variant tick-zero audit.
  See
  `outputs/analysis/GROUND_UP_TORSO_COM_MJX_INITIALIZATION_ORDER_AUDIT_CONTRACT_20260715.md`.
- 2026-07-15: The seven-variant initialization-order audit is invalid by its
  frozen validity rule. Fresh nominal and fresh endpoint initialization match
  the oracle exactly, but the reconstructed `LIVE_FORWARD_REPRODUCTION` also
  matches exactly and therefore does not reproduce the prior .0133886337
  m/s^2 half-direction error. All seven variants match and none is selectable.
  This localizes the unmodeled factor to the difference between standalone
  live-data reconstruction and the evaluator's actual tick-zero MJX data
  propagation. No 144-cell retry, actor, training, or hardware action is
  authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_MJX_INITIALIZATION_ORDER_AUDIT_RESULT_20260715.md`.
- 2026-07-15: A four-variant MJX JIT-boundary audit is preregistered before any
  new endpoint read. It compares the exact eager branch closure, the exact
  evaluator JIT closure, externally constructed model arguments, and paired
  endpoint JIT evaluation at the same single tick-zero reset. Exact oracle,
  prior-invalid reproduction, endpoint order, tolerances, and decision rules
  are frozen. A zero-outcome contract must pass first. No dynamic step, actor,
  training, or hardware action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_MJX_JIT_BOUNDARY_AUDIT_PREREGISTRATION_20260715.md`.
- 2026-07-15: The JIT-boundary zero-outcome contract passes exact source,
  prior-result, model/body/sensor/reset, frozen-variant/order, and CPU checks.
  It executed zero formal endpoint reads, dynamic steps, or actor calls. Only
  the frozen four-variant tick-zero audit is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_MJX_JIT_BOUNDARY_AUDIT_CONTRACT_20260715.md`.
- 2026-07-15: The four-variant JIT-boundary audit is valid. The exact eager
  closure matches the endpoint oracle with zero error. The exact evaluator JIT
  closure misses by up to .0268936157 m/s^2 and reproduces the preceding
  invalid half-direction exactly. External model arguments remain within
  7.24196e-6 m/s^2 of that invalid direction; paired JIT reproduces it exactly.
  Decision: `GENERAL_JIT_FORWARD_DISCREPANCY_OR_UNRESOLVED`. This selects only
  an eager diagnostic-branch correction candidate for separate
  preregistration; no map retry, actor, training, or hardware action is yet
  authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_MJX_JIT_BOUNDARY_AUDIT_RESULT_20260715.md`.
- 2026-07-15: A corrected exact 36-run/144-cell accelerometer replay is
  preregistered before changing the evaluator. The only allowed executable
  correction is replacing the default-off diagnostic runner's `jax.jit`
  wrapper with the exact eager closure validated at zero oracle error. The
  original corpus, ticks, anchor, classes, and decision thresholds are frozen.
  A zero-formal-cell, byte-identical default-off contract must pass first. No
  actor counterfactual, training, or hardware action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_EAGER_MJX_ACCELEROMETER_REPLAY_PREREGISTRATION_20260715.md`.
- 2026-07-15: The eager-MJX replay zero-formal-cell contract passes all frozen
  source, one-line correction, guard, branch, corpus, and CPU checks. Its
  complete 600-tick default-off trace is field-for-field and byte-for-byte
  identical to the frozen prior trace, contains zero map fields, and executes
  zero formal COM cells. Only the corrected 36-run/144-cell reporting replay
  is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_EAGER_MJX_ACCELEROMETER_REPLAY_CONTRACT_20260715.md`.
- 2026-07-15: The corrected eager-MJX 36-run/144-cell replay is valid. All
  21,600 baseline rows match after stripping the append-only map field,
  nominal observation error is zero, and all 36 tick-zero directions match the
  frozen anchor exactly. Tick 0 is 36/36 compatible; ticks 24/32/40 are
  dominated by weak and nonlinear-center signatures. Frozen decision:
  `SUPPORT_PREREGISTERED_MATCHED_SENSOR_ACTOR_RESPONSE_STUDY`. That named study
  is already complete: all six actors are materially responsive, signed
  response is mixed, and crossed localization is distributed/unresolved. No
  policy family, training, or hardware action is selected. See
  `outputs/analysis/GROUND_UP_TORSO_COM_EAGER_MJX_ACCELEROMETER_REPLAY_RESULT_20260715.md`.
- 2026-07-15: An 11-point deterministic reset-COM estimator feasibility curve
  is preregistered before any interior-offset sensor read. It calibrates only
  at the existing -.05/0/+.05 anchors and evaluates a frozen piecewise-linear
  estimator at eight held-out 1 cm interior offsets. Correct sign, strict
  ordering, adjacent separation above 1e-3 m/s^2, and a 5 mm held-out error
  ceiling select only a reset-latched estimator arm for separate
  preregistration. A zero-outcome contract must pass first. No dynamic step,
  actor, training, or hardware action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_FEASIBILITY_PREREGISTRATION_20260715.md`.
- 2026-07-15: The reset-COM estimator zero-outcome contract passes exact
  upstream-source, body/sensor/reset, 11-offset split, model mutation, frozen
  estimator source, one-read cardinality, no-JIT/no-step, and CPU checks. It
  executed zero formal sensor reads, dynamic steps, or actor calls. Only the
  frozen 11-point eager reset curve is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_FEASIBILITY_CONTRACT_20260715.md`.
- 2026-07-15: The 11-point reset-COM estimator feasibility curve is valid and
  selects `SUPPORT_RESET_LATCHED_PIECEWISE_LINEAR_COM_ESTIMATOR_ARM`. All
  anchors are exact; all eight held-out estimates have correct sign and strict
  order; maximum error is .0012139763 m versus the frozen .005 m ceiling; and
  minimum adjacent sensor separation is .279735532 m/s^2 versus the .001
  floor. This is one deterministic simulator reset only. It does not establish
  noise, reset-pose, floor, hardware, or deployment robustness and authorizes
  only a separate estimator-arm preregistration, not training. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_FEASIBILITY_RESULT_20260715.md`.
- 2026-07-15: The selected reset-estimator input arm is preregistered as
  `RESET_EST_LATCH_U05`. It adds one default-off normalized coordinate at
  policy/privileged index 101, before the unchanged final 14-D reference
  action, and expands the protected T2 checkpoint with coherent identity
  normalizer state and zero actor/critic rows. The CPU package contract passes:
  all other checkpoint values and save/restore are bit-exact; actor and critic
  step-zero errors are zero at z=-1/0/+1; three torso-COM anchor resets match
  the independent frozen estimator; and default-off remains 115/226-D. The
  work used zero dynamic steps and zero training. A separate hosted-training
  preregistration/package is required before any Colab session or PPO step.
  No behavior evaluation, GPU/iGPU, RDK-X5, runtime, or robot action is
  authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_INPUT_PACKAGE_CONTRACT_20260715.md`.
- 2026-07-15: The one-arm hosted package for `RESET_EST_LATCH_U05` is now
  preregistered and passes all 17 CPU contract checks. It freezes one
  uninterrupted 2M continuation, exports at 0/1,003,520/2,007,040, one
  session/process, no resume/retry, a 2,400-second wall ceiling, and a 2.0-CU
  ceiling. The hosted-topology expansion function reproduces the local
  expansion contract on CPU with bit-exact noninserted values/save-restore and
  zero actor/critic error at z=-1/0/+1. Asset/archive validation and the exact
  training command pass. This contract opened zero Colab sessions and ran zero
  training steps. A separate explicit hosted-run authorization is still
  required; do not launch Colab or PPO from this artifact. Behavior evaluation,
  GPU/iGPU, RDK-X5, runtime, and robot work remain unauthorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_HOSTED_PACKAGE_CONTRACT_20260715.md`.
- 2026-07-15: The hosted launch boundary is now frozen and passes all 20
  zero-session checks. It fixes Colab CLI 0.6.0, a fresh named T4 session,
  exactly 19 hash-locked uploads, total session wall time <=2,400 seconds,
  projected compute <=2.0 units, remaining-time exec timeout, no resume/retry,
  named-session-only `finally` cleanup, and atomic hash-verified recovery. A
  pre-run correction makes cleanup mandatory before `colab new`, reserves 120
  seconds from every work timeout for stop, and prevents pass unless stop
  succeeds within the total wall ceiling. The
  1.07/hour control projects to .713333 units; a 3.10/hour control fails at
  2.066667. Dry-run staging/plan passes, and session inventory remains no
  active sessions before/after. The helper cannot allocate without explicit
  `--allow-colab-allocation`. Do not supply it until the user unmistakably
  approves the single hosted `RESET_EST_LATCH_U05` run. No training, behavior
  evaluation, GPU/iGPU, RDK-X5, runtime, or robot action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_LAUNCH_CLEANUP_CORRECTION_PREREGISTRATION_20260715.md`
  and
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_COLAB_LAUNCH_CONTRACT_20260715.md`.
- 2026-07-15: The single explicitly approved `RESET_EST_LATCH_U05` hosted
  launch was attempted once and failed closed before upload or training. A
  fresh T4 session reached READY, but session-specific `colab status` omitted
  the compute-unit rate required by the frozen projection gate. The launcher
  stopped the named session successfully after 14.394865 seconds; independent
  inventory confirms no active sessions. Zero uploads, training processes, and
  PPO steps occurred. Compute consumption is unknown and is not inferred from
  the missing rate. Decision: `STOP_NO_RETRY_STATUS_RATE_UNAVAILABLE`. This is
  a launch-method failure, not a policy result. Do not retry or resume this
  launch. Any further allocation requires a separately preregistered method
  correction and new explicit authorization. No behavior evaluation,
  GPU/iGPU, RDK-X5, runtime, or robot action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_HOSTED_LAUNCH_RESULT_20260715.md`.
- 2026-07-15: The only supported successor to the failed hosted launch is now
  preregistered as a rate-attestation launch-method correction. Colab CLI 0.6.0
  source proves `status` and `sessions` expose no compute rate or balance; the
  prior contract's synthetic rate fixture did not prove a real CLI field. The
  correction freezes fresh operator-transcribed Colab Resources-UI rate,
  balance, and timestamp inputs, validates the projected 2.0-CU ceiling and
  freshness before allocation, and retains named T4 status only for identity.
  A zero-session CPU contract must pass before any new approval is requested.
  This preregistration does not authorize allocation, training, behavior
  evaluation, GPU/iGPU, RDK-X5, runtime, or robot action. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_RATE_ATTESTATION_CORRECTION_PREREGISTRATION_20260715.md`.
- 2026-07-15: The rate-attestation launch correction contract passes all 20
  frozen checks with zero sessions, remote bytes, training processes, or PPO
  steps. It proves mandatory rate/balance/timestamp validation occurs before
  allocation; 1.07/hour projects to .713333 units, 3.0/hour passes exactly at
  2.0, and 3.000001 fails. Freshness boundaries are 600 seconds old and 60
  seconds future; all invalid/nonfinite/missing controls fail. Captured real
  status passes idle named-T4 identity without a rate, and all wrong-identity
  controls fail. All 19 assets and prior lifecycle invariants remain exact.
  Allocation remains unauthorized until the operator supplies a fresh Colab
  Resources-UI rate, balance, timezone-aware timestamp, and new explicit
  approval. No behavior evaluation, GPU/iGPU, RDK-X5, runtime, or robot action
  is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_RATE_ATTESTATION_CORRECTION_CONTRACT_20260715.md`.
- 2026-07-15: A fresh idle Resources-UI reading is 79.36 available units,
  approximately 0/hour, and zero sessions; CLI independently confirms zero
  sessions. This falsifies positive-rate acquisition before allocation, so do
  not launch with zero or reuse 1.07. A same-session pretraining handshake is
  preregistered: after exact idle-T4 identity, wait at most 120 seconds for the
  operator's two live UI values, validate the unchanged 2.0-CU projection,
  then upload/train or fail closed. The operator explicitly approved one such
  corrected launch after its zero-allocation contract passes. No upload,
  training, behavior evaluation, local GPU/iGPU, RDK-X5, runtime, or robot
  action is authorized before that contract. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_SAME_SESSION_RATE_HANDSHAKE_PREREGISTRATION_20260715.md`.
- 2026-07-15: The same-session rate-handshake contract passes all 20 frozen
  checks with zero sessions, remote bytes, or PPO steps. Exact order is idle-T4
  identity, <=120-second local rate request, live attestation validation, then
  upload/training. Timeout and every invalid rate/balance/time/source/session
  control fail before upload. All 19 assets and lifecycle limits remain exact.
  The operator approved one interactive corrected launch; after its request
  marker only the live UI rate and available units are needed. No behavior
  evaluation, local GPU/iGPU, RDK-X5, runtime, or robot action is authorized.
  See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_SAME_SESSION_RATE_HANDSHAKE_CONTRACT_20260715.md`.
- 2026-07-15: The approved interactive launch used a valid live 1.07/hour,
  79.36-unit attestation and uploaded all 19 assets, but stopped before PPO at
  the hosted checkpoint-expansion gate. The sole reported failure is
  `step_zero_outputs_exact` against the frozen 1e-7 ceiling. The detailed
  remote report was not in the failed-job recovery set, so the error magnitude
  is unknown and must not be inferred or used to relax tolerance. Training
  processes/steps are zero. Named cleanup passed after 184.648470 seconds and
  no session remains; elapsed wall projects to .0548816 units at the attested
  rate, not an exact billing claim. Decision:
  `STOP_NO_RETRY_HOSTED_GPU_EXPANSION_EQUIVALENCE_FAILED`. Only a separately
  preregistered report-before-raise GPU expansion diagnostic may follow. No
  further Colab allocation, behavior evaluation, local GPU/iGPU, RDK-X5,
  runtime, or robot action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_SAME_SESSION_HOSTED_LAUNCH_RESULT_20260715.md`.
- 2026-07-15: The only supported successor is preregistered as a short T4
  report-before-raise expansion diagnostic. It freezes the same restore and
  expansion path, captures all per-z actor/critic errors, and terminates before
  training. Wall/CU ceilings are 300 seconds/.25 units with a <=60-second live
  rate handshake. The original 1e-7 threshold cannot be relaxed. A zero-session
  package contract must pass first, then a new explicit approval is required;
  the prior approval is consumed. No diagnostic allocation, PPO, behavior
  evaluation, local GPU/iGPU, RDK-X5, runtime, or robot action is authorized
  now. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_GPU_EXPANSION_DIAGNOSTIC_PREREGISTRATION_20260715.md`.
- 2026-07-15: The short GPU expansion diagnostic package contract passes all
  frozen checks with zero sessions/remote bytes/PPO. Exact pass/fail fixtures
  prove the wrapper captures the original report and stops before training.
  The launcher freezes 21 uploads, 300 seconds, .25 units, 60-second handshake
  and stop reserve, atomic recovery, and named cleanup. A new explicit approval
  is required before one diagnostic allocation; after its marker only the live
  UI rate and available units are needed. No training, behavior evaluation,
  local GPU/iGPU, RDK-X5, runtime, or robot action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_GPU_EXPANSION_DIAGNOSTIC_PACKAGE_CONTRACT_20260715.md`.
- 2026-07-15: The first diagnostic allocation timed out after 60 seconds while
  Resources UI still showed idle 0/hour. It performed zero uploads/diagnostic/
  PPO work, stopped successfully after 74.175680 seconds, and left no session.
  The operator then explicitly authorized completing the goal without further
  billing-number input. A wall-only correction is preregistered: one fresh T4,
  hard 300-second wall and 60-second stop reserve, exact 21 files, same no-PPO
  wrapper, compute usage recorded `UNMEASURED`, and no rate/CU claim. A zero-
  session contract must pass before allocation. No training, behavior
  evaluation, local GPU/iGPU, RDK-X5, runtime, or robot action is authorized.
  See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_GPU_DIAGNOSTIC_RATE_TIMEOUT_RESULT_20260715.md`
  and
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_GPU_DIAGNOSTIC_WALL_ONLY_CORRECTION_PREREGISTRATION_20260715.md`.
- 2026-07-15: The wall-only GPU diagnostic contract passes all frozen checks
  with zero sessions/remote bytes/PPO. Billing-input/rate/CU-cap surfaces are
  absent and usage is recorded `UNMEASURED`; exact fresh T4, 21 files,
  300-second wall, 60-second stop reserve, no-PPO wrapper, classification,
  atomic recovery, and cleanup remain enforced. The operator's continuing
  authorization permits one diagnostic allocation without further billing
  input. No training, behavior evaluation, local GPU/iGPU, RDK-X5, runtime, or
  robot action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_GPU_DIAGNOSTIC_WALL_ONLY_CONTRACT_20260715.md`.
- 2026-07-15: The wall-only T4 diagnostic recovered the exact report and
  stopped before PPO. Actor error is exactly 1.1920928955078125e-07 at all
  three z values; critic error is zero; every other expansion check passes.
  Raw classification is invalid because its implementation expected the wrong
  CPU-directory hash and literal `CudaDevice`. Direct extraction of the exact
  archive yields 05c0...920e, matching the report, and named status proves T4
  while the report says `cuda:0`. A CPU-only validity correction is
  preregistered to verify these facts and apply the original 1e-7 classes
  without altering the raw result. No new Colab, PPO, behavior evaluation,
  local GPU/iGPU, RDK-X5, runtime, or robot action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_GPU_EXPANSION_DIAGNOSTIC_RESULT_20260715.md`
  and
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_GPU_DIAGNOSTIC_VALIDITY_CORRECTION_PREREGISTRATION_20260715.md`.
- 2026-07-15: The CPU-only diagnostic validity correction passes every frozen
  check. Exact archive extraction reproduces hosted source hash `05c0...920e`,
  the launch proves the named T4/GPU session, the report device is `cuda:0`,
  and cleanup/report/training-zero evidence is exact. The corrected frozen-
  threshold outcome is `FINITE_GPU_EQUIVALENCE_EXCEEDS_ORIGINAL_1E7`: actor
  error is exactly one float32 epsilon (`1.1920928955078125e-07`) for all three
  z values, critic error is zero, and every other expansion check passes. The
  original 1e-7 threshold is not relaxed. Only a separately preregistered
  CPU-only action-distribution/ULP sensitivity audit is selected; no training,
  Colab, behavior evaluation, local GPU/iGPU, RDK-X5, runtime, or robot action
  is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_GPU_DIAGNOSTIC_VALIDITY_CORRECTION_RESULT_20260715.md`.
- 2026-07-15: The selected action-distribution ULP audit is preregistered before
  outcome computation. It treats the measured one-float32-epsilon actor error
  as an arbitrary coordinatewise box over all 28 NormalTanh parameters,
  enumerates every signed coordinate plus the two full corners, and checks
  deterministic mode, scale, physical target, and a rigorous diagonal-Gaussian
  W2/tanh upper bound against the existing 1e-6 action-identity boundary. Only
  a passing CPU audit may select a separate epsilon-aware expansion-method
  correction. No tolerance changes, training, Colab, behavior evaluation,
  local GPU/iGPU, RDK-X5, runtime, or robot action are authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_ACTION_DISTRIBUTION_ULP_SENSITIVITY_PREREGISTRATION_20260715.md`.
- 2026-07-15: The first ULP audit invocation stopped before actor restore or
  outcome computation because raw Orbax restore tried to resolve protected
  `cuda:0` sharding on the CPU host. A pre-outcome implementation correction
  freezes the already-verified CPU template and standard target-tree restore
  arguments, with exact source hash/shape/finite/CPU checks. No perturbation or
  decision rule changes. Only the same CPU audit may be rerun; no training,
  Colab, local GPU/iGPU, RDK-X5, runtime, or robot action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_ACTION_DISTRIBUTION_ULP_RESTORE_CORRECTION_20260715.md`.
- 2026-07-15: The corrected CPU-only action-distribution ULP audit passes every
  frozen check. Across all signed single-coordinate perturbations and both full
  28-parameter corners at the measured float32-epsilon envelope, maximum
  deterministic action difference is 1.18213e-7, scale difference 5.50010e-8,
  physical target difference 2.95531e-8 rad, and rigorous Gaussian-W2/tanh
  upper bound 4.79740e-7. All remain below the established 1e-6 action-
  identity boundary and its 2.5e-7-rad physical image. The original 1e-7
  expansion result remains failed. This selects only preregistration of an
  epsilon-aware hosted expansion correction; no training, Colab, behavior,
  local GPU/iGPU, RDK-X5, runtime, or robot action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_ACTION_DISTRIBUTION_ULP_SENSITIVITY_RESULT_20260715.md`.
- 2026-07-15: The epsilon-aware hosted expansion correction is preregistered.
  It preserves the original hosted source and raw failed report, and permits a
  wrapper to continue only for the exact sole failure with all actor errors at
  most float32 epsilon, zero critic error, exact GPU/source/ULP evidence, and
  every other expansion check passing. A zero-session CPU contract is required
  before one fresh no-retry T4 job under the original 2M recipe, 2,400-second
  wall/120-second stop reserve, and `UNMEASURED` compute recording. Continuing
  user authorization removes further billing/approval prompts but does not
  broaden the frozen job. No local GPU/iGPU, RDK-X5, runtime, or robot action
  is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_EPSILON_AWARE_HOSTED_EXPANSION_CORRECTION_PREREGISTRATION_20260715.md`.
- 2026-07-15: The epsilon-aware expansion wrapper passes its CPU-only contract
  with zero sessions/remote bytes/PPO. It preserves the original source and raw
  failure, accepts only the exact sole failure at <=float32 epsilon with zero
  critic error and exact source/GPU/ULP evidence, and rejects over-epsilon,
  nonzero-critic, wrong-source, extra-failure, original-pass, and missing-GPU
  controls. The complete original 2M recipe and exports remain exact. Only the
  wall-only launcher contract may follow; no allocation, training, local GPU/
  iGPU, RDK-X5, runtime, or robot action is authorized yet. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_EPSILON_AWARE_HOSTED_EXPANSION_CONTRACT_20260715.md`.
- 2026-07-15: The epsilon-aware wall-only launcher passes every zero-session
  contract check. It freezes one fresh named T4, 24 exact assets, the original
  job plus correction wrapper, 2,400-second total wall, 120-second stop
  reserve, atomic recovery, and mandatory named cleanup. Compute is recorded
  `UNMEASURED`; no billing/attestation input exists. Invalid execution fails
  closed and cleanup runs. Continuing user authorization permits this one no-
  retry launch without another numbers/approval prompt. Recovered artifacts
  remain behavior-unevaluated; no local GPU/iGPU, RDK-X5, runtime, or robot
  action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_EPSILON_AWARE_WALL_LAUNCHER_CONTRACT_20260715.md`.
- 2026-07-15: The single epsilon-aware T4 launch failed before checkpoint
  restore, expansion report, or PPO because the wrapper imported preinstalled
  JAX before the original job upgraded JAX/JAXLIB in the same process. Orbax
  then mixed the retained Python module with newly installed plugin binaries
  and raised in the CUDA Triton dialect. All 24 uploads completed, no training
  command/result artifact exists, cleanup passed after 89.500354 seconds, and
  zero sessions remain; compute is `UNMEASURED`. Decision:
  `STOP_NO_RETRY_PREINSTALL_JAX_IMPORT_CONTAMINATION`. A separately
  preregistered correction moves only that import into the post-install
  expansion callback and requires both wrapper and new wall-launch contracts
  before one fresh authorized session. No local GPU/iGPU, RDK-X5, runtime, or
  robot action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_EPSILON_AWARE_HOSTED_LAUNCH_RESULT_20260715.md`
  and
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_POSTINSTALL_JAX_IMPORT_CORRECTION_PREREGISTRATION_20260715.md`.
- 2026-07-15: The post-install JAX import correction passes both required CPU
  contracts. Only `import jax` moved into the post-install expansion callback;
  a simulated module proves `module.main()` begins before JAX import, and every
  epsilon-aware pass/fail fixture remains unchanged. The rebuilt wall launcher
  retains 24 assets, wall/cleanup/recovery rules, and `UNMEASURED` compute with
  fresh session `open-duck-reset-estimator-epsilon2-t4`. Continuing user
  authorization permits one fresh no-retry T4 launch without another billing/
  approval prompt. No local GPU/iGPU, RDK-X5, runtime, or robot action is
  authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_POSTINSTALL_JAX_IMPORT_CORRECTION_CONTRACT_20260715.md`.
- 2026-07-15: The fresh epsilon2 T4 job completed and the reset-estimator hosted
  artifact contract passes. All three 0/1,003,520/2,007,040 checkpoints and
  ONNX exports, archive/manifest/directory/file hashes, exact 116-D CPU ONNX
  interfaces, logs, command, corrected expansion plus preserved raw failure,
  wall limits, recovery, and cleanup are exact. Hosted execution took 958.802
  seconds; total session wall was 1,068.778 seconds, compute is `UNMEASURED`,
  and zero sessions remain. Behavior and reward are unevaluated. Only a local
  CPU contract applying the frozen guard/deadband/conservative-envelope
  transforms to the two post-update exports may follow; no training, Colab,
  local GPU/iGPU, RDK-X5, runtime, or robot action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_HOSTED_ARTIFACT_CONTRACT_20260715.md`.
- 2026-07-15: The reset-estimator behavior evaluator plumbing is preregistered
  before implementation. It adds one default-false evaluator/CLI switch that
  enables only the environment's existing reset-latched estimator input before
  construction, preserving body-2 override-before-reset ordering. A CPU reset-
  only contract must prove default-off 115-D identity and enabled 116-D latch
  propagation at nominal/-.05/+.05 before the exact 12-matrix/48-cell frozen
  behavior evaluation. Both checkpoints must pass every cell; no closest
  promotion or reward selection is allowed. No training, Colab, local GPU/
  iGPU, RDK-X5, runtime, or robot action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_BEHAVIOR_EVALUATOR_PREREGISTRATION_20260715.md`.
- 2026-07-15: The first reset-only evaluator contract stopped before behavior:
  the stochastic pre-reset saturated all three COM latches at +1 even though
  the later home-support state was deterministic. The failed result is
  preserved. A correction is preregistered to enable the existing nominal
  reset together with the estimator input, matching hosted training and the
  prior estimator package; the same zero-step CPU contract must pass before
  behavior. No training, Colab, GPU/iGPU, RDK-X5, runtime, or robot action is
  authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_EVALUATOR_NOMINAL_RESET_CORRECTION_PREREGISTRATION_20260715.md`.
- 2026-07-15: The corrected reset-only CPU evaluator contract passes with zero
  policy steps and zero behavior cells. Default-off remains 115-D/no latch;
  enabled -.05/0/+.05 resets are 116-D and latch -1.0/-0.0000445/+0.999989
  at index 101, matching the independent estimator within 1e-6. Body-2 X-only
  readback, exact transformed graph identity, and CPU-only execution pass. The
  exact frozen 12-matrix/48-cell behavior evaluation may proceed without a new
  approval prompt. No training, Colab, GPU/iGPU, RDK-X5, runtime, or robot
  action is authorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_BEHAVIOR_EVALUATOR_CORRECTED_CONTRACT_20260715.md`.
- 2026-07-15: The frozen RESET_EST_LATCH_U05 behavior evaluation is complete
  and valid: 12 matrices/48 cells, exact CPU/config/policy/fit/readback
  contracts, and no training-reward selection. Both checkpoints pass all four
  nominal matrices. X_NEG fails x=0 and moving cells; X_POS passes x=0 but
  fails every moving cell. The arm passes 4/12 matrices and 20/48 cells, so
  decision `CLOSE_RESET_EST_LATCH_U05_NO_PASS` closes it without retry,
  midpoint, or closest-checkpoint promotion. No new family is selected. Any
  new evidence question requires a separate preregistration; training, Colab,
  GPU/iGPU, RDK-X5, runtime, and robot work remain unauthorized. See
  `outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_BEHAVIOR_DECISION_20260715.md`.
- 2026-07-16: The preregistered oracle COM viability-funnel study completes
  through its frozen Stage-B hard stop. Stage A localizes all 24 failing moving
  endpoint cells and commits 298 exact four-tick states; 49 P30/x=.077 states
  form the fixed two-sign/two-checkpoint design subset. The deterministic
  six-pitch-joint screen finds valid sequences from 5/49 states at 8 ticks,
  4/49 at 16 ticks, and 0/49 at 32 ticks. X_NEG first has no valid sequence at
  tick 4 and X_POS at tick 12. Decision:
  `HOLD_LOCAL_AUTHORITY_NOT_COMPOSABLE`. The frozen hard stop prohibits the
  online planner and 48-cell Stage-C matrix, so neither ran. Do not promote a
  closest sequence or tune horizons, basis, amplitudes, beam, margins, or
  thresholds. Any gait-retraining or broader-controller branch requires a
  separate preregistration. Training, hosted compute, GPU/iGPU, RDK-X5,
  runtime, deployment, and robot work remain unauthorized; clearance is NO.
  See `outputs/analysis/ORACLE_COM_RECEDING_HORIZON_RESULT.md`.
- 2026-07-16: Review corrects the project headline. The protected
  G1_EXACT_BOUNDARY/T2_EQUAL pair composed with the exact x=0 deadband and
  conservative left-ankle envelope repair is the first persistent full-horizon
  nominal winner. Both checkpoints pass the complete P30/P31-34 R1 matrix;
  worst tracking is 0.183170038 rad and minimum vx is 0.084911748 m/s with zero
  saturation, rate excess and envelope excess. `Remediation winner: NONE`
  applies only to the closed torso-COM remediation arms. Robot clearance is
  still NO; generic COM training must not reopen. See
  `outputs/analysis/DEPLOYMENT_REVIEW_DECISION_20260716.md`.
- 2026-07-16: C1 is resolved at the offline contract boundary. The winner ONNX
  does not internalize fitted-bridge delay queues or lag state; its 14-D
  previous-action state is the bounded-action chain. The host must supply the
  bridge-realized target at obs[83:97]. The existing fitted forward observer
  reconstructs all 9,600 frozen composite trace targets under both fits with
  zero error. Runtime integration and hardware-fit selection remain blocked
  behind a separate v2 implementation contract; no Gate 5 or robot clearance
  follows. See `outputs/analysis/WINNER_V2_BRIDGE_OBSERVER_CONTRACT_20260716.md`.
- 2026-07-16: The deployment-specific signed torso-COM break-radius curve
  completes 15 points, 60 matrices and 240 CPU cells with exact per-run body-2
  X-only readback and monotone sampled outcomes. Certified inner offsets are
  -0.02265625 m and +0.00546875 m; nearest observed failures are -0.02343750 m
  and +0.00625000 m. Only comparison with the separately contracted real-build
  COM estimate is authorized. That estimate currently holds because no
  as-built RDK-X5/battery mass ledger, trunk datum or X placements exist in the
  workspace; do not substitute stock geometry or nominal web weights. No model
  correction, training, Gate 5, RDK-X5 or robot action is authorized. See
  `outputs/analysis/COMPOSITE_WINNER_TORSO_COM_BREAK_RADIUS_RESULT_20260716.md`
  and `outputs/analysis/REAL_BUILD_TORSO_COM_INPUT_AUDIT_20260716.md`.
- 2026-07-17: The winner-v2 native-runtime offline contract passes after one
  preserved invalid checker invocation was corrected from the unrelated
  21,600-row eager/JIT corpus to the frozen 144-trace/40,520-row full-
  observation manifest. The default legacy 101-D CLI path and C3 golden vector
  remain exact. The explicit v2 path validates either protected checkpoint,
  requires an explicit contracted actuator fit and reference table, composes
  the applied-target slot plus projected-reference suffix, carries exact 14-D
  ONNX state, and fails closed on uncontracted commands, timing, phase, filter,
  home, shapes, nonfinite values or hashes. All 40,520 observation rows, 9,600
  bridge rows and both 256-step stateful sequences pass; runtime-to-recorded
  bridge error is zero. Decision:
  `PASS_WINNER_V2_RUNTIME_OFFLINE_CONTRACT_HOLD_HARDWARE_FIT_SELECTION`.
  This selects no hardware fit and authorizes no deployment, Gate 5, robot or
  RDK-X5 access. The next deployment evidence remains the as-built torso-COM
  ledger and a separately contracted hardware-fit measurement/selection. See
  `outputs/analysis/WINNER_V2_RUNTIME_CONTRACT_20260717.md`.
- 2026-07-17: Measured actuator-fit provenance selects P30 semantics for the
  deployment observer: the body runtime used P30, the valid fixed-target P30
  phase contains 747 samples with zero read/write/reset errors, and the frozen
  P31/34 gain route was rejected. The preregistered CPU observer-by-plant
  cross-fit then passed all 32 cells spanning both persistent checkpoints,
  both measured plant fits, both observer fits and x=0/.074/.077/.080. The P30
  observer passes both plant fits at worst tracking 0.183170038 rad and minimum
  vx 0.084084972 m/s with zero rate/envelope excess. Decision
  `PASS_P30_OBSERVER_MEASURED_CROSS_FIT_BRACKET` pins only the P30 fit hash in
  winner-v2; P31/34 and gain overrides are rejected before hardware
  initialization. This removes the need for a new capture solely to choose
  between the two existing fits, but claims no current hardware health and
  authorizes no Gate 5, deployment, RDK-X5 or robot use. See
  `outputs/analysis/WINNER_V2_OBSERVER_CROSS_FIT_RESULT_20260717.md` and
  `outputs/analysis/WINNER_V2_P30_OBSERVER_PIN_20260717.md`.
- 2026-07-17: The real-build torso-COM input re-audit found no new RDK-X5
  assembly CAD, installed-component mass ledger, common trunk datum, X
  placements or uncertainty bounds. Decision remains
  `HOLD_REAL_BUILD_COM_INPUTS_INCOMPLETE`; do not derive a numerical estimate
  from stock geometry, nominal product weights or inference. Populate the
  committed measurement template before comparing with the asymmetric break
  radius. See
  `outputs/analysis/REAL_BUILD_TORSO_COM_INPUT_REAUDIT_20260717.md`.
- 2026-07-17: Before any real-build values were entered, the torso-COM
  measurement template's unauditable free-text frame transform was corrected
  to a numeric v2 datum origin, datum uncertainty and +/- axis mapping. The
  deterministic CPU calculator implements the frozen weighted-COM box-extrema
  method and hashed asymmetric break-radius comparison. Five synthetic contract
  cases pass. The untouched template fails closed on 46 missing/invalid fields,
  sets `numerical_estimate_reported=false`, and emits no estimate. The physical
  measurement packet is ready, but status remains
  `HOLD_REAL_BUILD_COM_INPUTS_INCOMPLETE` until source-backed as-built values
  are supplied. No threshold or authority changed; Gate 5, deployment, model
  correction, RDK-X5 and robot use remain unauthorized. See
  `outputs/analysis/REAL_BUILD_TORSO_COM_MEASUREMENT_SCHEMA_CORRECTION_20260717.md`,
  `outputs/analysis/REAL_BUILD_TORSO_COM_CALCULATOR_CONTRACT_20260717.md`, and
  `outputs/analysis/REAL_BUILD_TORSO_COM_MEASUREMENT_PACKET_20260717.md`.
- 2026-07-17: The referenced Frank Fu RDK-X5 source trail was audited before
  using it for real-build COM. The authored article adapts the OS, Python
  dependencies and runtime, but sends physical construction back to upstream
  stock Open Duck. The pinned upstream v2 tree at
  `b23317a485b3cec7d8417f352478778b3475173c` has 436 paths, zero RDK/X5 paths,
  and retains Pi Zero plus stock battery assets. The article and tree provide
  no RDK mount, installed component masses, X placements, common datum or
  uncertainties, so 0/46 measurement fields are promotable. Decision
  `HOLD_SOURCE_DOCUMENTS_NOT_MEASUREMENT_EVIDENCE` closes the hypothesis that
  this public material is already sufficient mechanical evidence. Do not use
  stock geometry, nominal board weights or image scale inference. See
  `outputs/analysis/FRANK_FU_RDK_X5_BUILD_SOURCE_AUDIT_20260717.md`.
- 2026-07-19: The policy robot-readiness re-audit leaves the evidence boundary
  unchanged. The G1/T2 composite and P30 observer remain a passing offline
  hardware candidate, but the fail-closed real-build COM calculator still
  finds exactly 46 missing physical fields and emits no numerical estimate.
  Decision remains `HOLD_REAL_BUILD_COM_INPUTS_INCOMPLETE`; robot clearance is
  NO. The next valid policy datum is the powered-off build-specific torso mass,
  X-placement, datum and uncertainty record, not another simulator tune or a
  nominal web specification. See
  `outputs/analysis/POLICY_ROBOT_READINESS_REAUDIT_20260719.md`.
- 2026-07-19: The native-runtime `Comms.md` request is answered by a hash-bound
  policy package at `artifacts/runtime_handoff/rdkx5_native_20260719/`.
  Its initial disposition was `REQUIRES_REVIEWED_115_RUNTIME_V2`: both protected persistent
  graphs require `obs[1,115]` plus `previous_action[1,14]`, and return final
  action plus next state. Four fresh 600-tick CPU full-observation traces
  reproduce the frozen P30 traces exactly; the package smoke verifies every
  hash, both graph ABIs, five adjacent chained ticks per command/checkpoint,
  bit-exact x=0 action/state, NaN rejection, and zero golden error. Legacy
  commanded-target substitution first diverges at moving tick 1; an erroneous
  advanced-first phase/reference diverges at tick 0. No single deployment
  checkpoint is selected post hoc, so `SELECTED_ONNX_SHA256=NOT_READY`.
  At that stage runtime v2 review and the real-build COM audit remained blockers;
  Gate 5 and robot clearance remain NO. See
  `outputs/analysis/POLICY_RUNTIME_HANDOFF_20260719.md`.
- 2026-07-19: A prospective single-checkpoint selection is preregistered from
  native RDK-X5 representation evidence rather than the already-read behavior
  tables. Eval-only wrappers quantize only BNO055 gyro/acceleration and STS3215
  position/velocity input slices at their exact native register resolutions.
  Their zero-behavior-cell contract passes every frozen source, ABI, graph,
  initializer, slice-isolation, NumPy-equivalence, CPU-provider, x=0, and
  256-tick state-chain check; maximum quantizer error is zero. Wrapper hashes
  are `a24b74ff...3273` at 512K and `11c8d56...361a` at 1024K. Only the frozen
  16-cell CPU matrix is authorized next. Both checkpoints must pass before the
  lower-worst-tracking/higher-minimum-vx rule may select one original graph;
  no sibling promotion is allowed. `SELECTED_ONNX_SHA256` remains `NOT_READY`
  until that result. This screen covers finite representation only, not sensor
  bias/noise/age, real COM, runtime review, Gate 5, RDK-X5, or robot clearance.
  See
  `outputs/analysis/WINNER_V2_NATIVE_QUANTIZED_CHECKPOINT_SELECTION_PREREGISTRATION_20260719.md`
  and `outputs/analysis/WINNER_V2_NATIVE_QUANTIZED_EVAL_CONTRACT_20260719.md`.
- 2026-07-19: The frozen native-representation selection completes once with
  all 16/16 cells and 9,600/9,600 trace rows passing. Both persistent
  checkpoints pass all eight sibling cells. The preregistered first criterion
  selects the original 512000-step graph because worst tracking p95 is
  .1809259653 rad versus .1818299592 rad at 1024000; reward has no selection
  weight. `SELECTED_ONNX_SHA256` is now
  `99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de`.
  The eval quantizer is not deployed. This removes only the checkpoint-choice
  blocker: reviewed stateful 115-D runtime-v2 acceptance, all 46 real-build COM
  inputs, and Gate 5 remain incomplete. Robot clearance remains NO; no robot,
  RDK-X5, motor, torque, GPU or iGPU access is authorized. See
  `outputs/analysis/WINNER_V2_NATIVE_QUANTIZED_CHECKPOINT_SELECTION_RESULT_20260719.md`
  and `outputs/analysis/WINNER_V2_RUNTIME_SELECTED_BINARY_RELAY_20260719.md`.
- 2026-07-19: A direct powered-off torso-COM evidence route is preregistered
  before any physical value is read. It measures the complete isolated
  `trunk_assembly` counterpart from two support reactions over exactly three
  reload trials, rather than reconstructing it from the 46-field component
  ledger. The clean upstream URDF and simulator XML independently locate the
  bilateral hip-yaw-axis datum at X=-.019 m. The specimen boundary excludes
  both leg chains and the head/neck child at their modeled joints, requires all
  deployment-fixed RDK/battery/thermal/wiring contents present, and permits no
  powered or software action. Exact support/load uncertainties, total-mass
  consistency, trial overlap, the frozen asymmetric COM bounds, and decision
  tokens are fixed. Only the blank-template CPU calculator/contract is
  authorized next; robot clearance remains NO. See
  `outputs/analysis/REAL_BUILD_TORSO_COM_DIRECT_REACTION_PREREGISTRATION_20260719.md`.
- 2026-07-19: The direct-reaction blank-template CPU contract passes all 14
  checks with zero formal physical readings and no numerical estimate. Source
  URDF/XML and break-radius hashes are exact; the datum remains X=-.019 m;
  eight direct-route unit cases plus the five original ledger cases pass. The
  direct template requires 15 numeric readings/uncertainties rather than 40
  per-component numbers, while retaining exact specimen isolation, three
  reload trials, total-mass consistency and evidence requirements. Status is
  `HOLD_REAL_BUILD_DIRECT_COM_INPUTS_INCOMPLETE` until the powered-off operator
  packet is populated. No physical action by the agent or robot/RDK-X5/Gate 5
  authority follows. See
  `outputs/analysis/REAL_BUILD_TORSO_COM_DIRECT_REACTION_CONTRACT_20260719.md`
  and
  `outputs/analysis/REAL_BUILD_TORSO_COM_DIRECT_REACTION_MEASUREMENT_PACKET_20260719.md`.
- 2026-07-19: The runtime-v2 action-history metadata correction passes its
  preregistered contract. Golden traces plus evaluator source establish
  `obs[41:55]`, `obs[55:69]`, and `obs[69:83]` as final actions `t-2`, `t-3`,
  and `t-4`; the separate recurrent `previous_action[t]` remains final action
  `t-1`. All 2,400 packaged rows pass both exact checks. Package schema is now
  `winner_v2_rdkx5_native_handoff.v1.1`, replacement manifest SHA-256 is
  `d771d188...c6827c5`, and the selected original 512000-step ONNX remains
  byte-identical at `99d3afce...304de`. This is metadata/hash-chain repair,
  not recursive cross-CPU acceptance, runtime deployment, Gate 5, or robot
  clearance. The recursive closure rule requires a separate preregistration.
- 2026-07-19: The selected winner-v2 recursive cross-CPU closure is now
  preregistered before a formal rerun. Identical-input ONNX checks retain the
  unchanged `1e-6` boundary. Fully recursive drift is judged separately at the
  physical actuator boundary: maximum logical-target and P30-state difference
  must be at most half one native STS3215 position count
  (`pi/4096=.0007669903939428206 rad`), and the exact deployed conversion may
  differ by at most one raw count. All history, exogenous-field, limiter,
  saturation, measured-rate, envelope and x=0 gates remain unchanged. Only
  the selected 512000 x=0/.080 cells decide; 1024000 is audit-only and cannot
  advance. The pre-outcome contract passes with zero formal result reads and
  zero recursive ticks. Any formal result must be generated after this commit
  by a committed deterministic runtime verifier. No robot, RDK-X5, Gate 5,
  deployment, GPU or iGPU authority follows.
- 2026-07-19: A post-preregistration policy-side Linux CPU corroboration ran
  the committed runtime-v2 transaction across all four 600-tick package cells
  under the frozen native-resolution rule. Both selected 512000 cells pass
  `PASS_RECURSIVE_BIT_EXACT_WIRE_CLOSURE`: action, recurrent state, logical
  target and all 16,800 selected STS raw goal words are exact; selected P30
  error is at most `5.9576471e-8 rad`. Both audit-only 1024000 cells also pass.
  This does not replace the required post-preregistration formal result from
  the runtime agent's CPU and does not grant runtime acceptance, X5/AArch64
  equivalence, COM clearance, Gate 5 or robot authority.
- 2026-07-19: The formal post-preregistration runtime-CPU result is accepted as
  `PASS_RECURSIVE_BIT_EXACT_WIRE_CLOSURE`. The formal Windows replay and an
  independent policy-side Linux replay each complete all four 600-tick cells;
  both selected 512000 cells preserve x=0 exactly and produce zero mismatches
  across all 16,800 selected raw STS goal words. Formal selected moving-cell
  target/P30 maxima are `5.9604645e-7`/`5.6025073e-7 rad`, far below the frozen
  half-count boundary. The 1024000 sibling remains audit-only. Runtime tests
  pass 254/254 and its artifact manifest is clean. Runtime commit
  `264ac40074992c72b295a7cbeb141df59ce3d613` corrects the dedicated reduced
  result to the frozen `teacher_forced_observation_exact_zero` gate. Policy
  independently reproduces corrected reduced SHA-256
  `1292772e54f3734f2e48b5b0d75fb0c931949d3b7820598c4a9040a8b765dc5e`;
  every one of its four observation values is exactly zero, the superseded
  `teacher_forced_observation_at_most_1e_6` key is absent, and the formal full
  result/hash is unchanged. This closes only the
  reviewed CPU recursive-numeric blocker. Powered-off direct COM, a reviewed
  frozen asset set, X5 CPU-only replay, Gate 5, deployment and robot clearance
  remain incomplete and unauthorized. See
  `outputs/analysis/WINNER_V2_RECURSIVE_CROSS_CPU_CLOSURE_RESULT_20260719.md`.
- 2026-07-19: Policy review holds runtime offline asset-lock SHA-256
  `4da893b3...de940` as `HOLD_STALE_OFFLINE_ASSET_LOCK`. It was created
  concurrently and pins superseded policy result commit `fab1fea` / hash
  `17ddae42...babf06a`, while the dedicated-artifact acceptance then at
  `bc4132b` hashed to `852b7108...8f667`. The reduced-report defect is now
  corrected and independently revalidated; the old lock nevertheless remains
  explicitly stale/revoked because it predates the corrected runtime artifact,
  current verifier/test/manifest identities, and this final policy acceptance
  identity. Regenerate the asset lock against those current identities. Do not
  deploy or plan X5 preflight from the stale lock. See
  `outputs/analysis/WINNER_V2_OFFLINE_ASSET_LOCK_REVIEW_20260719.md`.
- 2026-07-19: Policy independently accepts replacement offline asset-lock
  SHA-256 `48fd6d81...4ef31` as
  `PASS_FROZEN_OFFLINE_ASSET_LOCK_POLICY_REVIEW`. It binds final policy
  acceptance commit `4c99b5e` / result SHA-256 `5380897c...b7ddc`, corrected
  reduced SHA-256 `1292772e...dc5e`, unchanged formal SHA-256
  `e1842ca6...9b14`, selected ONNX `99d3afce...304de`, corrected handoff
  manifest `d771d188...c6827c5`, and runtime identity `7189559`. Policy and
  runtime verifiers pass; runtime tests pass 254/254 and its manifest is clean.
  The superseded lock `4da893b3...de940` remains revoked. This freezes offline
  identities only. Powered-off direct COM evidence, policy robot clearance,
  X5 no-servo CPU replay and separately reviewed Gate 5 remain pending and
  unauthorized. See
  `outputs/analysis/WINNER_V2_OFFLINE_ASSET_LOCK_REVIEW_20260719.md`.
- 2026-07-19: The no-per-unit-measurement product direction supersedes the
  powered-off COM packet as an advancement gate. The existing selected graph
  is held because its verified X-COM failure bracket lies well inside the
  required `[-.05,+.05] m` domain. A CPU-only compiled-model audit now derives
  the prospective replacement domain from the already-frozen R2 endpoints:
  X/Y/Z COM each `+/-.05 m`, resulting torso mass
  `.5286734-.8683786 kg`, and positive, triangle-valid inertia ranges coupled
  to the frozen mass/placement bounds. Optional non-locomotion parts are
  represented by aggregate dynamics rather than manual inventory. Decision:
  `PASS_VARIABLE_CONFIGURATION_DOMAIN_BASIS_CURRENT_CANDIDATE_HELD`. It
  authorizes only replacement-study preregistration. No passing runtime
  envelope exists; training, hosted compute, GPU/iGPU, RDK-X5, automatic
  calibration, X5 preflight, Gate 5, deployment and robot use remain
  unauthorized. See
  `outputs/analysis/WINNER_V3_SUPPORTED_CONFIGURATION_BASIS_20260719.md`.
- 2026-07-19: The replacement study is prospectively frozen before any new
  candidate outcome as `R64_ZERO_INIT_RECURRENT_ADAPTER`. It restores the
  protected T2_EQUAL 512K checkpoint, adds one deployable 64-state recurrent
  adapter whose action head is exactly zero at initialization, preserves the
  PPO reward/critic and baked hard-vector/actual-centered/envelope/deadband
  stack, and permits no oracle or true configuration input. One CPU-only,
  seed-100, no-retry curriculum scales the evidence-derived configuration
  domain through 25%, 50%, then full range. Both checkpoints at 1,003,520 and
  2,007,040 full-domain steps must pass the exact 1,024-cell matrix: nominal,
  24 fixed aggregate anchors, 16 discovery coupled samples, 16 independently
  seeded heldout samples, and six native sensor/transport conditions, crossed
  with both actuator plants and x=0/.074/.077/.080. Every prior 600-tick gate
  stays unchanged; all-joint current p95 must also remain <=.65 A. No closest
  result can advance. Only a complete pass can begin the separate selected
  policy -> clearance -> envelope Git sequence. The CPU implementation
  contract is next. Colab/hosted compute, GPU/iGPU, RDK-X5, robot, serial,
  torque, motion, Gate 5 and deployment remain unauthorized. See
  `outputs/analysis/WINNER_V3_VARIABLE_CONFIGURATION_REPLACEMENT_PREREGISTRATION_20260719.md`.
- 2026-07-19: The preregistered recurrent-adapter CPU contract passes on one
  formal 1,024-step CPU smoke. Two pre-update implementation stops are logged:
  archived CUDA sharding required the established CPU-template remap, then the
  recurrent normalizer required a neutral `policy_hidden[64]` leaf. Neither
  produced an optimizer update. The completed run initially held on a stale
  literal copied from the sibling checkpoint (`8,048,640`); a committed
  read-only audit, with no smoke rerun, proves both the protected T2_EQUAL 512K
  source and expanded checkpoint use count `7,536,640` and corrects the result.
  All 64 fixed/pseudorandom step-zero logits are bit-exact to the protected
  actor; initial ONNX action/hidden errors are zero; base, adapter-state and
  adapter-head parameters all update finitely; the trained CPU ONNX has exact
  `obs + previous_action + h_in -> action + previous_action_out + h_out` ABI;
  and a 256-tick state chain is finite. Decision:
  `PASS_WINNER_V3_RECURRENT_ADAPTER_CPU_CONTRACT`. This is plumbing only and
  authorizes implementation and execution of the single preregistered CPU
  curriculum, not hosted/Colab, GPU/iGPU, RDK-X5, robot, runtime, motion,
  Gate 5, deployment or clearance. See
  `outputs/analysis/WINNER_V3_RECURRENT_ADAPTER_CPU_CONTRACT_20260719.md` and
  `outputs/analysis/WINNER_V3_RECURRENT_ADAPTER_NORMALIZER_COUNT_CORRECTION_20260719.md`.
- 2026-07-19: The coupled winner-v3 configuration/actuator/sensor curriculum
  implementation and its pre-outcome contract are frozen before candidate
  training or behavior outcomes. It targets named inertial body 2, reconstructs
  a positive-definite, triangle-valid full torso inertia tensor, uses one
  all-link mass scale, samples the measured actuator interval plus fixed
  episode delays/noise/native quantization, records exact readback, and gives
  the actor no true configuration input. A development-only checker passes
  bit-exact residual-off traces and 4,096 model plus episode samples at each of
  0/25/50/100% scale; formal curriculum PPO steps and formal behavior cells are
  both zero. Decision:
  `PASS_WINNER_V3_CURRICULUM_PREOUTCOME_CONTRACT`. The next and only authorized
  action is a fresh, independently composed, hash-locked formal CPU
  implementation contract. Training remains prohibited until that formal
  contract passes; hosted/Colab, GPU/iGPU, RDK-X5, robot, runtime, Gate 5,
  deployment and clearance remain unauthorized. See
  `outputs/analysis/WINNER_V3_VARIABLE_CONFIGURATION_CURRICULUM_PREOUTCOME_CONTRACT_20260719.md`.
- 2026-07-19: The fresh formal winner-v3 coupled-curriculum CPU contract passes
  as `PASS_WINNER_V3_VARIABLE_CONFIGURATION_CURRICULUM_CONTRACT`. Independent
  baseline and winner-v3 simulator compositions produce bit-exact default-off
  traces across qpos/qvel/control/115-D observation/reward/done/targets/action/
  phase/command. All 4,096 model and episode samples pass at each curriculum
  fraction; the full inertia tensors remain positive-definite and
  triangle-valid; exact readback, fixed delay support, native float32
  quantization and the home-relative measured bridge equation pass. The run
  used CPU JAX only and executed zero PPO steps and zero formal behavior cells.
  This authorizes only the one frozen seed-100 no-retry CPU curriculum. It is
  not behavior evidence or a passing supported-configuration envelope;
  hosted/Colab, GPU/iGPU, RDK-X5, robot, runtime, Gate 5, deployment and
  clearance remain unauthorized. See
  `outputs/analysis/WINNER_V3_VARIABLE_CONFIGURATION_CURRICULUM_CONTRACT_20260719.md`.
- 2026-07-19: The exact winner-v3 CPU curriculum launch is hash-frozen as
  `PASS_WINNER_V3_CPU_CURRICULUM_LAUNCH_CONTRACT` and its read-only driver
  validation passes on `TFRT_CPU_0`. One process restores and expands the
  protected T2_EQUAL 512K checkpoint, then executes only 245,760 steps at 25%,
  245,760 at 50%, and 2,007,040 at full domain with persistent full-domain
  exports at 1,003,520 and 2,007,040. The driver has no subprocess or retry
  surface, rejects any existing work/result path, checks finite metrics and
  parameters, proves exact stage restore continuity, and fixes a 43,200-second
  wall ceiling before outcome. Formal training steps and behavior cells remain
  zero. This authorizes only that one CPU process; training reward has no
  selection weight. No hosted/Colab, GPU/iGPU, RDK-X5, robot, runtime, Gate 5,
  deployment or clearance is authorized. See
  `outputs/analysis/WINNER_V3_CPU_CURRICULUM_LAUNCH_CONTRACT_20260719.md`.
- 2026-07-19: The only authorized winner-v3 CPU curriculum completed without
  retry as `PASS_WINNER_V3_RECURRENT_ADAPTER_TRAINING_ARTIFACT`. PID 723798
  executed all three frozen stages in 2,627.284 seconds, emitted exact stage
  steps, preserved both restore boundaries at zero tree error, and produced
  finite stateful ONNX graphs at full-domain steps 1,003,520
  (`3d5e6dd4...ab77b04d`) and 2,007,040 (`fb725c5e...195544f0`). An independent
  extraction audit passes archive SHA-256 `bee604f0...ce48d91`, 23,521,941
  bytes / 171 safe members, every checkpoint and graph hash, finite leaves and
  initializers, exact three-input/three-output ABI, one logged PID, and both
  stage continuities. Decision:
  `PASS_WINNER_V3_RECURRENT_ADAPTER_TRAINING_ARTIFACT_CHECK`. Training reward
  has no selection weight and formal behavior cells remain zero. This
  authorizes only the frozen 1,024-cell CPU behavior evaluation. It is not a
  supported-configuration pass; hosted/Colab, GPU/iGPU, RDK-X5, robot, runtime,
  Gate 5, deployment and clearance remain unauthorized. See
  `outputs/analysis/WINNER_V3_RECURRENT_ADAPTER_TRAINING_RESULT_20260719.md` and
  `outputs/analysis/WINNER_V3_RECURRENT_ADAPTER_TRAINING_ARTIFACT_CHECK_20260719.md`.
- 2026-07-19/20: The only winner-v3 formal behavior run completed all 64
  conditions / 1,024 cells in one CPU process with no retry in 26,772.001
  seconds. The raw result SHA-256 `8fa33f86...bca44` is deliberately preserved
  as `INVALID_WINNER_V3_VARIABLE_CONFIGURATION_RESULT`: its aggregate reporter
  rejected JAX display name `TFRT_CPU_0` because it searched for the literal
  `CpuDevice`, and it treated each expected early-termination trace as missing
  evidence. A read-only correction reran zero behavior cells and changed no
  graph, model, trace, threshold, seed, gate or physics value. It verifies all
  1,024 trace hashes, exact trace-row/recorded-sample counts, finite/schema/reset
  audits, condition-to-cell hashes, policy hashes and every per-run model
  readback; process-wide CPU evidence is SHA-256 `ae1c51c...dec2f`.
- 2026-07-19/20: The corrected result SHA-256 `bf072daf...cd0d9` is
  `HOLD_WINNER_V3_VARIABLE_CONFIGURATION_RESULT_REPORTING_CORRECTED` with
  frozen decision `HOLD_WINNER_V3_VARIABLE_CONFIGURATION_REPLACEMENT`.
  Exactly 48/1,024 cells pass physical gates; each persistent checkpoint passes
  24/512 and fails the all-cells rule. Physical failures are: all-joint current
  p95 944, candidate gate 251, duration/trace 239, positive commanded motion
  107, zero-command velocity/base-height 36 each, saturation 38, guard envelope
  34, rate 12, tracking 4 and bilateral transitions 1. Negative X still
  reverses/falls and positive X still runs away/falls. Correction JSON SHA-256
  is `c1385765...420c`; the verified 1,024-entry trace manifest SHA-256 is
  `0f31debf...2f4f4` and binds 8,147,644,105 local trace bytes. No replacement
  graph, policy-clearance artifact or supported-configuration envelope exists;
  runtime sentinels remain pending and robot clearance is false. This exact
  replacement branch is closed. Any new formulation or training route requires
  a separate preregistration. No hosted/Colab, GPU/iGPU, RDK-X5, robot, serial,
  torque, motion, X5 preflight, Gate 5 or deployment action is authorized. See
  `outputs/analysis/WINNER_V3_VARIABLE_CONFIGURATION_RESULT_CORRECTED_20260720.md`
  and
  `outputs/analysis/WINNER_V3_VARIABLE_CONFIGURATION_REPORTING_CORRECTION_20260720.md`.
- 2026-07-20: The runtime-requested read-only failure attribution rehashes and
  replays all 1,024 committed cells/traces without changing the completed
  result. Exactly 705 cells fail only the frozen current-p95 check; current
  exceedance follows direction loss in all 107 wrong-direction/current cases,
  so current does not explain the signed-X mechanism. Negative X reverses/falls
  and positive X overspeeds/falls with exact model, command, and reset readback.
  The first corrected source review found Feetech's 2024 catalog support for
  the 0.65 A rated point. See
  `outputs/analysis/WINNER_V3_FAILURE_ATTRIBUTION_20260720.md`.
- 2026-07-20: A second prospective source correction finds Feetech's detailed
  STS3215 A/0 specification dated 2020-04-10. It explicitly reports the exact
  `8 kg.cm/A = 0.784532 N.m/A` motor constant, 0.65 A rated current, 2.5 A
  stall current, 19.5 kg.cm stall torque, and over-current protection above
  2 A for 2 s. The completed winner-v3 gate remains unchanged. Prospective
  candidates report 0.65 A p95 diagnostically, reject torque/current beyond
  the stall envelope, and reject 100 consecutive 50 Hz ticks strictly above
  2 A. Decision `PASS_PROSPECTIVE_CURRENT_GATE_APPLICATION_CONTRACT` authorizes
  only response-interface preregistration. No training, hosted compute,
  runtime implementation, hardware, or robot action is authorized. See
  `outputs/analysis/WINNER_V3_CURRENT_GATE_APPLICATION_CONTRACT_20260720.md`.
- 2026-07-20: The proposed automatic-response policy ABI is preregistered for
  runtime schema review only as `winner-v4-response73-r64`. It preserves the
  115-D observation, 14-D final action, phase, previous-action, and 64-state
  meanings while adding a separate immutable `response_context[1,73]` input.
  Its exact order is the runtime profile-v4 five response metrics for each of
  14 frozen joints followed by the three body-response metrics. It contains no
  true mass, COM, inertia, component identity, or manual measurement. Before
  PPO, runtime/policy flattening, profile reproduction, zero-init actor
  identity, rejection behavior, repeat determinism, and signed-X context
  non-collapse must pass on CPU. Status is
  `PREREGISTERED_PENDING_RUNTIME_REVIEW`; no training, Colab, GPU/iGPU,
  runtime implementation, X5, robot, torque, motion, Gate 5, deployment, or
  clearance is authorized. See
  `outputs/analysis/WINNER_V4_RESPONSE_INTERFACE_PREREGISTRATION_20260720.md`.
- 2026-07-20: Native-runtime review accepts the exact response73 field map and
  73-value flattening order, but correctly holds implementation pending a
  signed-X non-collapse test and an exact simulator realization of the physical
  support mode. The review result is
  `PASS_RESPONSE73_FIELD_MAP_HOLD_POLICY_CONDITIONING_READINESS`, SHA-256
  `e860ac7c...f55f8`, at native-runtime commit
  `fc4eb265...cca51`. This review does not authorize runtime implementation,
  policy training, hosted compute, hardware, or deployment.
- 2026-07-20: The single preregistered zero-PPO response73 CPU falsification
  completed without a classified retry. All eight contexts are finite 73-value
  float32 arrays, exact repeats are bit-identical, and both P30 and P31/34
  distinguish signed X in 60/73 fields. It nevertheless fails the frozen
  support boundary: the -0.05 m endpoint loses double-foot contact during
  settle and finishes at base Z `-0.156836729809` m with roll
  `-3.139646185483` rad, only `0.001946468107` rad from pi. Its later two-foot
  excitation is therefore an inverted, invalid calibration state, not evidence
  for policy conditioning. Formal result SHA-256 is
  `b7eb0a5d...66730`; explanatory diagnostic SHA-256 is
  `acf5af92...82e40`. Decision:
  `HOLD_RESPONSE73_PRETRAINING_FALSIFICATION_FAILED` /
  `DO_NOT_IMPLEMENT_OR_TRAIN_RESPONSE73`. No Colab session was opened. Any
  replacement support or sign-preserving response mechanism requires a new
  prospective contract and runtime review. See
  `outputs/analysis/WINNER_V4_RESPONSE_IDENTIFIABILITY_RESULT_20260720.md` and
  `outputs/analysis/WINNER_V4_SUPPORT_FAILURE_DIAGNOSTIC_20260720.md`.
- 2026-07-21: The ground-up Winner-v12 full-calibrator trainer is frozen with
  exact 80-environment Stage-1/Stage-2 populations, seed `120120`, 100 updates
  per stage, atomic per-update recovery, strict Stage-2 realized-action and
  terminal-mask checks, a 115-D nonzero recurrent ONNX chain, and a one-root
  logical-run claim. The first formal zero-update CPU contract completed its
  simulation work but failed only while serializing `numpy.bool_` check values;
  run `29806564376` is permanently attributed with optimizer updates `0`.
  The narrowly corrected, newly hash-frozen run `29806824132` then passed every
  check in the exact Python 3.12.13 / JAX 0.7.2 / MuJoCo 3.9.0 / NumPy 2.0.2
  CPU environment. Raw result SHA-256 is `faf520cc...a15c3`; optimizer updates,
  formal support cells, locomotion steps, and robot access all remain `0`.
  Decision `AUTHORIZE_ONE_WINNER_V12_FULL_CALIBRATOR_TRAINING_RUN_ONLY` permits
  only one separately hash-bound seed-120120 calibrator run. It does not yet
  authorize the 124-cell support gate, response-conditioned locomotion,
  deployment selection, Gate 5, or robot access. See
  `outputs/analysis/WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT_RESULT_20260721.md`.
- 2026-07-21: Winner-v22 completed the single normalized-predictor training run
  and corrected-coordinate support gate. The learned predictor beats the
  constant baseline at both checkpoints and both actuator plants, but physical
  support still fails in 15/124 half and 14/124 final cells; every physical
  failure is a negative-X roll/pitch boundary. The gate is therefore
  `HOLD_WINNER_V22_NORMALIZED_PREDICTOR_SUPPORT_GATE` and response-conditioned
  locomotion training remains prohibited. See
  `outputs/analysis/WINNER_V22_NORMALIZED_PREDICTOR_SUPPORT_GATE_RESULT_20260721.md`
  and `outputs/analysis/WINNER_V22_SUPPORT_HOLD_ATTRIBUTION_20260721.md`.
- 2026-07-21: The preregistered read-only Winner-v23 negative-X response-use
  diagnostic passed on GitHub run `29878611867`, attempt 1. Its exact original
  artifact ZIP SHA-256 is `be3278db...2e83e87`. All 20 paired cells encode the
  signed response by tick 0, beat the constant predictor on both signs, and
  change action under the same-input hidden-state fork by tick 1. Positive-X
  support passes 20/20 while negative-X support fails 17/20. Classification is
  `RESPONSE_STATE_PRESENT_AND_USED_SUPPORT_CONTROL_INADEQUATE`; this authorizes
  only a separately frozen negative-X support-control-objective CPU contract.
  It does not authorize training, checkpoint selection, runtime work, RDK-X5,
  robot access, Gate 5, deployment, or clearance. See
  `outputs/analysis/WINNER_V23_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC_RESULT_20260721.md`.
- 2026-07-21/22: The first Winner-v24 symmetric support-failure zero-update
  proof is preserved as `HOLD_WINNER_V24_SYMMETRIC_FAILURE_CPU_CONTRACT` from
  GitHub run `29879542867`, attempt 1, artifact ZIP SHA-256
  `0fe26cbd...4bc64a9a`. It applied no optimizer update. Twelve roll/pitch
  failures and 22 settled successes were present; default-off was bit-exact;
  enabled mode changed only reward/return/advantage; predictor loss and
  gradients stayed bit-exact; and PPO action-head/recurrent gradients changed.
  The sole failed check is baseline GAE replay: return max error
  `1.52587890625e-5`, exactly one float32 ULP at the existing 250-point terminal
  scale, while advantage error `9.536743e-7` passed. Do not relax or rerun this
  contract and do not run an optimizer update from it. A prospective,
  read-only attribution is required before any baseline-anchored correction.
  See `outputs/analysis/WINNER_V24_SYMMETRIC_FAILURE_CPU_RESULT_20260721.md`.
- 2026-07-22: The read-only Winner-v24 GAE attribution passed. The prior return
  discrepancy equals exactly one float32 ULP at 250, its advantage replay
  already passed the original threshold, and all 20 other causal/locality
  checks passed. The old result is not rewritten, its threshold is not
  relaxed, and it must not be rerun. The separately versioned baseline-anchored
  zero-update contract is now frozen: recorded baseline returns plus rederived
  values are authoritative, and only the analytically propagated `-250`
  terminal delta is added before advantage renormalization. One first-attempt
  CPU proof is authorized with 80 rollout slots and zero optimizer updates,
  formal support cells, locomotion steps, and robot access. A pass may authorize
  only a separately preregistered one-update CPU proof; it does not authorize
  training, checkpoint selection, deployment, Gate 5, or robot access. See
  `outputs/analysis/WINNER_V24_GAE_ONE_ULP_ATTRIBUTION_20260722.md` and
  `outputs/analysis/WINNER_V24_BASELINE_ANCHORED_CPU_CONTRACT_20260722.md`.
- 2026-07-22: First-attempt baseline-anchored run `29880437377` completed and
  its original ZIP matches GitHub SHA-256 `54d0079b...58a732b`. The raw result
  reports a full pass, but the frozen importer stopped before writing because
  it carried an obsolete six-leaf gradient inventory while the frozen runner
  emitted the exact twelve-leaf Winner-v21 trainable tree. Do not rerun or
  alter the artifact. A separately versioned importer correction may change
  only that expected key inventory and must reuse every other frozen strict
  check. It authorizes no optimizer update, training, robot access, or result
  classification until the unchanged ZIP passes the corrected importer. See
  `outputs/analysis/WINNER_V24_BASELINE_IMPORTER_CORRECTION_20260722.md`.
- 2026-07-22: The separately versioned corrected importer accepted the exact
  unchanged run-`29880437377` ZIP and recorded
  `PASS_WINNER_V24_BASELINE_ANCHORED_CPU_CONTRACT`. All checks pass: 12
  roll/pitch failures and 22 settled successes are present; the analytic delta
  spans 447 sampled cells; default-off and non-objective arrays remain exact;
  the normalized predictor is bit-exact; PPO action-head and recurrent
  gradients change; and composition error is `3.948807716369629e-7` versus the
  frozen `2e-6` bound. Optimizer updates, formal support cells, locomotion
  steps, and robot access remain zero. This authorizes only a separately
  frozen one-update baseline-anchored CPU proof. It does not authorize a full
  training run, support gate, checkpoint selection, deployment, Gate 5, or
  robot access. See
  `outputs/analysis/WINNER_V24_BASELINE_ANCHORED_CPU_RESULT_V2_20260722.md`.
- 2026-07-22: The separate Winner-v24 baseline-anchored one-update CPU proof is
  frozen. It restores the exact final Winner-v22 snapshot and optimizer at
  count 100, reconstructs only rollout index 100, applies the already-passed
  analytic terminal delta, and may execute exactly one Adam update to count
  101. It must prove all twelve leaves change, snapshot/optimizer/normalizer
  readback is exact, and the stateful ONNX contract remains exact. Formal
  support, locomotion, RDK-X5, robot, torque, and hardware access remain zero.
  A pass may authorize only a separately frozen baseline-anchored training
  preregistration; it does not itself authorize training or evaluation. See
  `outputs/analysis/WINNER_V24_BASELINE_ANCHORED_ONE_UPDATE_CPU_CONTRACT_20260722.md`.
- 2026-07-22: First-attempt one-update run `29881265608` completed and its
  original ZIP matches GitHub SHA-256 `f3966403...0e7510fd`. The frozen importer
  stopped before reading the result because GitHub preserved the work-directory
  prefix for the snapshot and ONNX while the importer expected those two names
  flattened. Do not rerun or alter the artifact. A separately versioned path
  correction may accept only the two observed prefixed names while preserving
  the exact four-member inventory and every safety, size, digest, result, and
  authority check. No additional optimizer update or training is authorized
  until that unchanged ZIP passes strict corrected import. See
  `outputs/analysis/WINNER_V24_ONE_UPDATE_IMPORTER_PATH_CORRECTION_20260722.md`.
- 2026-07-22: The path-corrected strict importer accepted the exact unchanged
  run-`29881265608` ZIP and recorded
  `PASS_WINNER_V24_BASELINE_ANCHORED_ONE_UPDATE_CPU_PROOF`. Optimizer count is
  exactly `100 -> 101`; all twelve combined gradients are nonzero; all twelve
  trainable leaves change; snapshot, optimizer, target-normalizer, and stateful
  ONNX readback checks pass. The artifact ZIP SHA-256 is
  `f3966403...0e7510fd`, snapshot SHA-256 is `ab3bbdfb...a3e94a3`, and ONNX
  SHA-256 is `52a1d942...bebb48c`. Formal support, locomotion, and robot access
  remain zero. This authorizes only a separately frozen baseline-anchored
  training preregistration; it does not yet authorize the training run,
  support gate, checkpoint selection, deployment, Gate 5, or robot access. See
  `outputs/analysis/WINNER_V24_BASELINE_ANCHORED_ONE_UPDATE_CPU_RESULT_V2_20260722.md`.
- 2026-07-22: One Winner-v24 baseline-anchored 100-update CPU continuation is
  preregistered. It independently restores the exact Winner-v22 final snapshot
  and optimizer at count 100, runs rollout indices 100-199 with the frozen
  `-250` observed roll/pitch terminal objective, and ends at optimizer count
  200. A rollout with no roll/pitch failures is a required bit-exact objective
  no-op; successful elimination of failures must not abort training. There is
  no coefficient, length, predictor-scale, or checkpoint search.
  Atomic snapshots 101-200 and only count-150/count-200 half/final ONNX graphs
  are retained. The workflow must stop on any transition, mask, hidden replay,
  gradient, snapshot, or graph mismatch. Exactly one first-attempt run is
  authorized. Formal support, checkpoint selection, locomotion, RDK-X5, robot,
  torque, and hardware remain unauthorized. A training pass may authorize only
  a separately frozen support gate. See
  `outputs/analysis/WINNER_V24_BASELINE_ANCHORED_TRAINING_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole first-attempt Winner-v24 baseline-anchored continuation
  completed on GitHub run `29882025982` and passed the frozen strict importer.
  The original 19,174,111-byte ZIP exactly matches GitHub SHA-256
  `0e819dab...b2f0a4a1`; optimizer count is exactly `100 -> 200`, all 100
  atomic snapshots and all twelve trainable-leaf gradients/deltas pass, and
  the count-150/count-200 stateful ONNX hashes are
  `a36d7634...e0846fd3` / `6f3bde15...b1dc425`. Every rollout retained
  observed roll/pitch failure evidence (1,487 total), so the objective never
  used its zero-failure no-op branch. Decision:
  `PASS_WINNER_V24_BASELINE_ANCHORED_TRAINING_ARTIFACT`. This authorizes only a
  separately frozen 248-cell half/final support gate; it does not authorize
  checkpoint selection, locomotion training, runtime work, RDK-X5, robot,
  Gate 5, deployment, or clearance. See
  `outputs/analysis/WINNER_V24_BASELINE_ANCHORED_TRAINING_RESULT_20260722.md`.
- 2026-07-22: The Winner-v24 half/final support gate is separately
  preregistered as
  `PREREGISTERED_WINNER_V24_BASELINE_ANCHORED_SUPPORT_GATE`. It binds the exact
  count-150/count-200 snapshot and ONNX hashes to the unchanged reviewed
  124-cell-per-checkpoint evaluator, 32 heldout repeats per checkpoint, 16
  heldout context checks per checkpoint, normalized-predictor-versus-constant
  rule, and all-or-nothing two-checkpoint decision. The checkpoint-boundary
  adapter explicitly changes only the evaluator labels from the inherited
  `50/100` to `150/200`; it does not alter cells, physics, seeds, thresholds,
  predictor coordinates, or policy bytes. No closest-checkpoint selection is
  permitted. Exactly one first-attempt CPU gate is authorized. Locomotion,
  checkpoint selection, runtime implementation, RDK-X5, robot, torque, motion,
  Gate 5, deployment, and clearance remain unauthorized. See
  `outputs/analysis/WINNER_V24_BASELINE_ANCHORED_SUPPORT_GATE_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v24 baseline-anchored support gate completed on
  GitHub run `29883954243`; the original 251,272-byte ZIP exactly matches
  GitHub SHA-256 `3e0e503a...6e1da1d6` and passes the strict importer. Both
  count-150 and count-200 checkpoints fail exactly 20/124 physical support
  cells. Every failure is roll/pitch-only, occurs at ticks 26-47, and covers
  the same ten negative-X configurations under both P30 and P31/34 plants.
  All sensor/transport cells pass; predictor-versus-constant, context
  separation, repeatability, previous-action chaining, and JAX/ONNX checks all
  pass. This regresses from Winner-v22's 15/124 and 14/124 support failures.
  Decision: `HOLD_WINNER_V24_BASELINE_ANCHORED_SUPPORT_GATE` /
  `DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION`. Close this exact symmetric
  terminal-penalty route; do not select a checkpoint, tune its coefficient or
  length, rerun the gate, or proceed to locomotion, runtime, RDK-X5, robot,
  Gate 5, deployment, or clearance. A new policy mechanism requires separate
  prospective evidence. See
  `outputs/analysis/WINNER_V24_BASELINE_ANCHORED_SUPPORT_GATE_RESULT_20260722.md`.
- 2026-07-22: A saved-result-only Winner-v22-to-v24 support-regression
  attribution executed zero new simulation cells and passed. Winner-v24
  recovered `0/15` half and `0/14` final Winner-v22 failures, added `5` and `6`
  failures respectively, and made every shared failure occur strictly earlier
  (median `-3` ticks at both checkpoints; maxima `-2/-1`). All failures remain
  negative-X roll/pitch-only while response encoding/use and every nonphysical
  support check remain green. Classification:
  `PASS_WINNER_V24_SUPPORT_REGRESSION_ATTRIBUTION`. The scalar symmetric
  terminal-penalty route is causally closed; observability is not the remaining
  blocker. This authorizes only a separately preregistered zero-update
  same-state directional support-control diagnostic that tests actor-action
  changes against short-horizon cloned-state pitch response. It does not
  authorize another loss, training, checkpoint selection, runtime, RDK-X5,
  robot, Gate 5, deployment, or clearance. See
  `outputs/analysis/WINNER_V24_SUPPORT_REGRESSION_ATTRIBUTION_20260722.md`.
- 2026-07-22: One zero-update Winner-v25 same-state directional support-control
  diagnostic is preregistered. It follows the exact 20-tick Winner-v22 final
  recurrent trajectory through the ten negative-X failure configurations and
  both actuator plants, then sends identical observation, previous-action, and
  hidden-state inputs to Winner-v22 final and Winner-v24 half/final. At each of
  800 candidate fork points it clones the exact MuJoCo integration state and
  holds the source or candidate tick action for five ticks, with 1,600 total
  short-horizon rollouts. A local-destabilization classification requires both
  candidate checkpoints to increase absolute pitch on at least 75% of forks
  and have median pitch delta above 1e-6 rad. Exactly one first-attempt CPU run
  is authorized. Optimizer updates, locomotion, checkpoint selection, runtime,
  RDK-X5, robot, Gate 5, deployment, and clearance remain unauthorized. See
  `outputs/analysis/WINNER_V25_DIRECTIONAL_SUPPORT_CONTROL_DIAGNOSTIC_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole first-attempt Winner-v25 directional diagnostic passed
  on GitHub run `29885694381`; its original 430,165-byte ZIP exactly matches
  GitHub SHA-256 `131cc002...db33e9`. All 800 candidate fork points and 1,600
  five-tick rollouts completed, every source clone repeat was bit-exact, and
  both candidates changed the action on 400/400 forks. Winner-v24 half was
  locally destabilizing on 70% of forks with median absolute-pitch delta
  `+0.00017136947` rad, below the frozen 75% rule; final was destabilizing on
  9% with median delta `-0.00063347965` rad. Classification:
  `NO_DOMINANT_SAME_STATE_LOCAL_DESTABILIZATION`. This rejects a five-tick
  direct-action explanation and authorizes only a separately preregistered
  longer-horizon recurrent-credit diagnostic. It does not authorize an
  objective change, training, checkpoint selection, runtime, RDK-X5, robot,
  Gate 5, deployment, or clearance. See
  `outputs/analysis/WINNER_V25_DIRECTIONAL_SUPPORT_CONTROL_DIAGNOSTIC_RESULT_20260722.md`.
- 2026-07-22: One zero-update Winner-v26 recurrent-credit diagnostic is
  preregistered. It runs the exact Winner-v22 final policy for 20 valid ticks
  through the same ten negative-X configurations and both actuator plants,
  then clones the full MuJoCo integration state and supplies the captured
  observation, previous action, and recurrent hidden state identically to the
  Winner-v22 source and Winner-v24 half/final branches. Each branch then evolves
  its own closed-loop observation/action/hidden chain for at most 32 ticks,
  covering the complete recorded Winner-v24 failure window. Post-prefix
  regression requires both candidates to terminate earlier on at least 75% of
  branches with median lead at least one tick. Exactly one first-attempt CPU
  run is authorized. Optimizer updates, locomotion, checkpoint selection,
  runtime, RDK-X5, robot, Gate 5, deployment, and clearance remain
  unauthorized. See
  `outputs/analysis/WINNER_V26_RECURRENT_CREDIT_DIAGNOSTIC_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole first-attempt Winner-v26 recurrent-credit diagnostic
  passed on GitHub run `29886426953`; its original 1,963,488-byte ZIP exactly
  matches GitHub SHA-256 `4bceda8e...d7c7ac3`. All 20 source prefixes, 40
  candidate branches, and 80 recurrent rollouts passed, with bit-exact source
  clone repeats and changed initial candidate actions in all 40 branches.
  Starting from the exact Winner-v22 tick-20 physical/observation/action/hidden
  state, neither Winner-v24 half nor final terminated before the source in any
  branch (`0/20` each; median lead `0`). Classification:
  `NO_DOMINANT_POST_PREFIX_RECURRENT_REGRESSION`. The support regression is
  therefore already embedded before tick 20 rather than caused by later
  recurrent closed-loop accumulation. This authorizes only a separately
  preregistered early-prefix divergence diagnostic. It does not authorize an
  objective change, training, checkpoint selection, runtime, RDK-X5, robot,
  Gate 5, deployment, or clearance. See
  `outputs/analysis/WINNER_V26_RECURRENT_CREDIT_DIAGNOSTIC_RESULT_20260722.md`.
- 2026-07-22: One zero-update Winner-v27 early-prefix source-recovery scan is
  preregistered. For Winner-v24 half/final, the exact candidate trajectory is
  captured at ticks `0/4/8/12/16/20` in the ten negative-X configurations and
  both actuator plants. Candidate continuation and Winner-v22 source recovery
  start from the same candidate physical/bridge/observer/history snapshot and
  captured observation; the source hidden state is advanced prospectively on
  the candidate observation/action history. All branches are right-censored at
  absolute tick 52. Early physical-state lock-in requires source recovery in
  all tick-0 cells for both checkpoints and at most 25% of tick-20 cells.
  Exactly one first-attempt CPU run is authorized: 40 candidate prefixes, 240
  forks, and 720 branch rollouts. Optimizer updates, locomotion, checkpoint
  selection, runtime, RDK-X5, robot, Gate 5, deployment, and clearance remain
  unauthorized. See
  `outputs/analysis/WINNER_V27_EARLY_PREFIX_RECOVERY_SCAN_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole first-attempt Winner-v27 early-prefix recovery scan
  passed on GitHub run `29887070007`; its original 408,492-byte ZIP exactly
  matches GitHub SHA-256 `c567ae46...f1a524e`. All 40 candidate prefixes, 240
  forks, and 720 branch rollouts passed, including exact candidate continuation
  replay, fork-zero Winner-v22 replay with tick-52 right censoring, and bit-
  exact source repeats. Source recovery fractions for half at ticks
  `0/4/8/12/16/20` are `1.00/.85/.40/.10/.05/0`; final is
  `1.00/.95/.15/.15/.15/.15`. Classification:
  `EARLY_PREFIX_PHYSICAL_STATE_LOCK_IN`. The harmful state is accumulated
  largely between ticks 4 and 8, before later recurrence can repair it. This
  authorizes only a separately preregistered prefix joint-group action causal
  screen. It does not authorize an action wrapper, objective change, training,
  checkpoint selection, runtime, RDK-X5, robot, Gate 5, deployment, or
  clearance. See
  `outputs/analysis/WINNER_V27_EARLY_PREFIX_RECOVERY_SCAN_RESULT_20260722.md`.
- 2026-07-22: One zero-update Winner-v28 prefix joint-group causal screen is
  preregistered. For ticks 0-7 it replaces exactly one anatomical group of the
  Winner-v24 action with the Winner-v22 action computed on the same branch
  observation and realized previous action: left lateral, left pitch chain,
  head, right lateral, or right pitch chain; CONTROL changes nothing. At tick 8
  Winner-v22 source recovery runs to the unchanged tick-52 boundary. A group is
  selected only if recovery gain is at least 0.25 for both checkpoints and its
  minimum checkpoint gain is strictly greater than every other group. The
  screen is 240 prefix arms and 480 source-recovery/repeat rollouts, with zero
  optimizer, locomotion, or robot work. Exactly one first-attempt CPU run is
  authorized. No action wrapper, objective, training, checkpoint selection,
  runtime, RDK-X5, robot, Gate 5, deployment, or clearance is authorized. See
  `outputs/analysis/WINNER_V28_PREFIX_JOINT_GROUP_CAUSAL_SCREEN_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole first-attempt Winner-v28 prefix joint-group screen
  passed on GitHub run `29887831090`; its original 272,475-byte ZIP exactly
  matches GitHub SHA-256 `7d2f5719...479de7d`. All 240 prefix arms and 480
  source-recovery/repeat rollouts passed. The unique frozen selection is
  `RIGHT_PITCH_CHAIN` (right hip pitch, knee, ankle; action indices 11-13):
  recovery rises from `.40 -> 1.00` at half and `.15 -> .95` at final, gains
  `.60/.80`. Left pitch chain also helps (`.40/.70`) but is strictly weaker;
  lateral and head groups fail the two-checkpoint selection rule.
  Classification: `SINGLE_PREFIX_JOINT_GROUP_CAUSAL_LOCALIZATION`. This
  authorizes only a separately preregistered CPU contract for an objective
  targeting the selected early right-pitch-chain mechanism. It does not
  authorize a runtime wrapper, training, checkpoint selection, RDK-X5, robot,
  Gate 5, deployment, or clearance. See
  `outputs/analysis/WINNER_V28_PREFIX_JOINT_GROUP_CAUSAL_SCREEN_RESULT_20260722.md`.
- 2026-07-22: One zero-update Winner-v29 prefix right-pitch-chain anchor CPU
  contract is preregistered. It starts from the exact Winner-v24 final snapshot
  at update 200 and compares only deterministic bounded action indices
  `11/12/13` during ticks `0-7` of the eight V28-selected negative-X training
  configurations (16 two-plant episode slots, 384 action elements) with the
  Winner-v22 source evaluated on the same candidate observations and realized
  previous-action history. The source is stop-gradient and keeps its own
  shadow recurrent state. One analytic scale is calibrated by matching raw
  anchor-gradient RMS to the unchanged Winner-v24 combined-gradient RMS over
  the same recurrent/action leaves; no scale search is permitted. Exactly one
  first-attempt CPU proof is authorized with 80 rollout slots and zero optimizer
  updates, formal support cells, locomotion steps, or robot access. A pass may
  authorize only a separately preregistered one-update CPU proof using the exact
  recorded scale; it does not authorize training, checkpoint selection,
  runtime work, RDK-X5, Gate 5, deployment, or clearance. See
  `outputs/analysis/WINNER_V29_PREFIX_RIGHT_PITCH_ANCHOR_CPU_CONTRACT_20260722.md`.
- 2026-07-22: The sole first-attempt Winner-v29 prefix right-pitch anchor CPU
  proof passed on GitHub run `29888962404`; the original 6,404-byte ZIP exactly
  matches GitHub SHA-256 `3ef70a19...3b5c9`. The exact update-200 batch contains
  17 roll/pitch failures and all 384 selected prefix-action elements. Raw anchor
  loss is `0.00035727047`, maximum selected source/candidate action difference
  is `0.02864599`, and the frozen gradient-RMS scale is
  `197.3112030029297`. All six intended recurrent/action leaves have nonzero
  anchor gradients; value, log-std, and predictor leaves are exactly zero.
  Source/candidate JAX-to-ONNX replay error is at most `8.74e-11`; default-off
  gradients and all transition arrays are bit-exact; optimizer, formal support,
  locomotion, and robot counts remain zero. Decision:
  `PASS_WINNER_V29_PREFIX_RIGHT_PITCH_ANCHOR_CPU_CONTRACT`. This authorizes only
  a separately preregistered one-update CPU proof using the exact recorded
  scale. It does not authorize training, checkpoint selection, runtime work,
  RDK-X5, Gate 5, deployment, or clearance. See
  `outputs/analysis/WINNER_V29_PREFIX_RIGHT_PITCH_ANCHOR_CPU_RESULT_20260722.md`.
- 2026-07-22: One Winner-v30 prefix right-pitch anchor one-update CPU proof is
  preregistered. It restores the exact Winner-v24 final snapshot and Adam state
  at count 200, reproduces the Winner-v29 update-200 batch, and adds the frozen
  anchor gradient at exact scale `197.3112030029297` to the unchanged
  Winner-v24 PPO/predictor gradient. It may execute exactly one Adam update to
  count 201, then must strictly reduce selected same-batch anchor MSE, change
  all twelve trainable leaves, save/read back the full snapshot, and export the
  unchanged stateful hard-bounded ONNX ABI. Exactly one first-attempt CPU run is
  authorized. Formal support, locomotion, RDK-X5, robot, torque, and hardware
  remain zero. A pass may authorize only a separately frozen bounded training
  preregistration; it does not itself authorize training, checkpoint selection,
  runtime work, Gate 5, deployment, or clearance. See
  `outputs/analysis/WINNER_V30_PREFIX_RIGHT_PITCH_ANCHOR_ONE_UPDATE_CPU_CONTRACT_20260722.md`.
- 2026-07-22: The sole first-attempt Winner-v30 run `29889578085` completed
  one optimizer update and uploaded its result, count-201 snapshot, and ONNX,
  but the frozen runner classified it HOLD because two cross-run byte-exact
  replay checks failed. Every other check passed, including count `200 -> 201`,
  all twelve nonzero gradients and leaf changes, same-batch anchor-loss
  reduction, snapshot readback, and stateful ONNX validation. Do not rerun or
  alter the artifact. A strict import-only correction is frozen for the exact
  246,907-byte artifact ZIP SHA-256 `50533add...0fb86`; it changes no threshold
  or result and authorizes no additional optimizer update. After unchanged
  import, only a separately preregistered saved-result attribution may examine
  whether cross-worker floating replay—not the update contract—caused the two
  mismatches. Training, support evaluation, runtime work, RDK-X5, robot, Gate 5,
  deployment, and clearance remain unauthorized. See
  `outputs/analysis/WINNER_V30_ONE_UPDATE_HOLD_IMPORT_CORRECTION_20260722.md`.
- 2026-07-22: One saved-result-only Winner-v31 cross-worker replay attribution
  is preregistered. It reads only the committed Winner-v29 result and preserved
  Winner-v30 HOLD result; it executes zero simulation cells, optimizer updates,
  support cells, locomotion steps, or robot work. The exact two failed replay
  checks must remain the only failures, every non-replay update/snapshot/ONNX
  check must pass, each of the three recorded loss pairs must differ by at most
  eight float32 ULPs, and the measured anchor improvement must exceed the
  largest cross-worker anchor delta by at least 10,000x. No V30 rerun, result
  rewrite, or threshold change is authorized. A pass may authorize only a
  separately frozen bounded training preregistration using the preserved
  count-201 artifact; training, checkpoint selection, support evaluation,
  runtime work, RDK-X5, robot, Gate 5, deployment, and clearance remain
  unauthorized. See
  `outputs/analysis/WINNER_V31_CROSS_WORKER_REPLAY_ATTRIBUTION_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v31 saved-result-only attribution passed on
  GitHub run `29890211264`; its original 2,417-byte ZIP exactly matches GitHub
  SHA-256 `da49ac7f...d0eeb29`. The three V29/V30 replay differences are only
  `7/1/4` float32 ULPs for anchor/PPO/predictor loss. The actual one-update
  anchor improvement is `0.0001267446642`, `622,130.5x` larger than the
  cross-worker anchor delta. The exact two replay checks remain the only V30
  holds, while every non-replay update, snapshot, graph, and state-chain check
  passes; execution remains zero simulation/update/support/locomotion/robot.
  Classification: `CROSS_WORKER_FLOAT_REPLAY_ONLY`. This authorizes only a
  separately frozen bounded prefix-anchor training preregistration using the
  preserved count-201 artifact. It does not yet authorize that training,
  support evaluation, checkpoint selection, runtime work, RDK-X5, robot,
  Gate 5, deployment, or clearance. See
  `outputs/analysis/WINNER_V31_CROSS_WORKER_REPLAY_ATTRIBUTION_RESULT_20260722.md`.
- 2026-07-22: One bounded Winner-v32 prefix right-pitch anchor continuation is
  preregistered from the preserved Winner-v30 snapshot and Adam state at count
  201. It performs exactly 100 CPU-only updates (`201 -> 301`) over the
  unchanged 80-environment, 250-tick population, with snapshots after every
  update and fixed half/final checkpoints at counts `251/301`. The unchanged
  Winner-v24 PPO/roll-pitch transition objective and Winner-v22 predictor scale
  `380.9135437011719` are combined with the exact Winner-v29 eight-tick,
  right-pitch-chain anchor at scale `197.3112030029297`; the Winner-v22 teacher
  remains frozen and no action replacement or coefficient search is permitted.
  Training performs zero formal support cells, locomotion, RDK-X5, or robot
  work and cannot select a checkpoint. A passing artifact may authorize only a
  separately preregistered support/context gate over both checkpoints. See
  `outputs/analysis/WINNER_V32_PREFIX_RIGHT_PITCH_ANCHOR_TRAINING_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v32 training run `29890876702` passed and its
  original 19,252,514-byte ZIP exactly matches GitHub SHA-256
  `7c967955...af4d8ac`. All 100 updates (`201 -> 301`), episode receipts,
  action boundaries, V24 transition contracts, 384-element prefix-anchor
  contracts, hidden replays, successor masks, gradients/deltas, atomic
  snapshots, and both stateful ONNX exports pass; the frozen teacher remains
  unchanged and formal support/locomotion/robot counts remain zero. The raw
  anchor loss changes from `0.00023033652` on the first continuation batch to
  `0.00000984033` at count 251 and `0.00001020137` at count 301; this is
  diagnostic only. The exact count-251/count-301 ONNX SHA-256 values are
  `445d9111...dc401c84` and `d9e073e8...9f0874c2`. Neither checkpoint is
  selected. This authorizes only a separately preregistered unchanged support
  gate over both checkpoints, not runtime, RDK-X5, robot, Gate 5, deployment,
  or clearance. See
  `outputs/analysis/WINNER_V32_PREFIX_RIGHT_PITCH_ANCHOR_TRAINING_RESULT_20260722.md`.
- 2026-07-22: One Winner-v33 read-only support gate is preregistered for the
  exact Winner-v32 count-251/count-301 snapshots and ONNX graphs. It reuses the
  reviewed physical evaluator, populations, seeds, thresholds, normalized-head
  affine scoring projection, and all-or-nothing rule that previously exposed
  Winner-v24's negative-X failures: 124 main cells and 32 heldout repeats per
  checkpoint, with all 16 heldout contexts separate and learned prediction
  required to beat the constant baseline per plant. Both checkpoints must pass;
  closest-result selection is forbidden. The gate executes 248 main cells and
  64 repeats, but zero optimizer updates, locomotion training, RDK-X5, or robot
  work. A pass may authorize only a separately preregistered response-
  conditioned locomotion-training design; it is not checkpoint selection or
  robot clearance. See
  `outputs/analysis/WINNER_V33_PREFIX_RIGHT_PITCH_ANCHOR_SUPPORT_GATE_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v33 gate run `29894528597` completed HOLD; its
  original 254,300-byte ZIP exactly matches GitHub SHA-256
  `9189e78d...9a6a9e0`. Both checkpoints, all 248 main cells, and all 64
  heldout repeats were evaluated with exact graph/state chains and prediction
  checks. Count 251 has 25 roll/pitch support failures and count 301 has 30.
  The original V24 negative-X failure set remains, while count 251 additionally
  fails `DISCOVERY_06`, `HELDOUT_07`, and one `HELDOUT_15` plant; count 301
  additionally fails both plants for `OPTIONAL_AGGREGATE_HEAVY_AFT`,
  `DISCOVERY_02/06`, `HELDOUT_07/15`. Thus the soft prefix anchor sharply
  reduced its training MSE but did not repair closed-loop support and worsened
  the unchanged gate. Decision: `DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION`.
  No checkpoint is selected and robot clearance remains false. See
  `outputs/analysis/WINNER_V33_PREFIX_RIGHT_PITCH_ANCHOR_SUPPORT_GATE_RESULT_20260722.md`.
- 2026-07-22: One zero-update Winner-v34 direct right-pitch prefix
  intervention is preregistered over the exact union of 15 Winner-v33 failing
  configurations, both actuator plants, and both Winner-v32 checkpoints. It
  runs 60 CONTROL and 60 `RIGHT_PITCH_REPLACED` cells for 250 ticks. At ticks
  0-7 only, indices `11/12/13` are replaced by Winner-v22 final actions computed
  on the candidate observation and realized previous-action history; Winner-v32
  resumes unchanged at tick 8. CONTROL must reproduce the exact action/hidden
  chains and support outcome from Winner-v33, with only `1e-12` tolerance for
  redundant MuJoCo scalar summaries across CPU executions. A pass requires all
  60 replacement cells to pass, including recovery of every original failure
  and preservation of every original pass. Exactly one formal CPU run is
  authorized. Optimizer updates, locomotion training, runtime wrappers,
  checkpoint selection, RDK-X5, robot, Gate 5, deployment, and clearance remain
  unauthorized. See
  `outputs/analysis/WINNER_V34_PREFIX_RIGHT_PITCH_HARD_INTERVENTION_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v34 formal run `29895731264` completed HOLD; its
  original 138,977-byte ZIP exactly matches GitHub SHA-256
  `5553ab06...0207f3`. All 60 CONTROL cells reproduce the Winner-v33
  action/hidden chains and support outcomes, with maximum redundant scalar
  difference `3.25e-13`; all graph boundaries, state chains, and intervention
  changes are valid. Exact Winner-v22 replacement of right hip pitch, knee,
  and ankle at ticks 0-7 preserves all 5 cells that already passed but recovers
  `0/55` failing cells; replacement support is therefore only `5/60`.
  Classification: `NO_FULL_DIRECT_PREFIX_SUPPORT_RECOVERY`; decision:
  `CLOSE_RIGHT_PITCH_PREFIX_REPLACEMENT_MECHANISM`. Do not extend, retune, or
  train the failed soft-anchor or eight-tick replacement route. No checkpoint
  is selected and robot clearance remains false. See
  `outputs/analysis/WINNER_V34_PREFIX_RIGHT_PITCH_HARD_INTERVENTION_RESULT_20260722.md`.
- 2026-07-22: One zero-update Winner-v35 full-horizon source-continuation
  feasibility test is preregistered. It reuses the exact 60-cell Winner-v34
  matrix. Ticks 0-7 preserve the V28 hybrid prefix (Winner-v32 candidate with
  Winner-v22 right-pitch actions); at tick 8 Winner-v22 final takes all 14
  actions from its shadow recurrent state through tick 249. The committed
  Winner-v34 replacement cells are the comparator and are not rerun. A pass
  requires all 60 hybrid cells, all 55 prior failures recovered, all 5 prior
  passes preserved, graph-bound actions, and a nonzero handoff in every cell.
  Exactly one formal CPU run is authorized. This resolves whether V28's
  short-horizon survival lead is a complete support-valid teacher; it does not
  authorize a runtime hybrid, action wrapper, optimizer update, locomotion
  training, checkpoint selection, RDK-X5, robot, Gate 5, deployment, or
  clearance. See
  `outputs/analysis/WINNER_V35_FULL_HORIZON_SOURCE_CONTINUATION_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v35 formal run `29896417197` completed HOLD; its
  original 27,001-byte ZIP exactly matches GitHub SHA-256
  `ee461896...0dc9fe`. All 60 cells execute the exact hybrid, all actions remain
  graph-bounded, and every tick-8 handoff changes the action by `0.12019-0.12171`
  rad. Only `14/60` cells pass the complete 250-tick support gate: the hybrid
  recovers `9/55` Winner-v34 failures and preserves all `5/5` existing passes.
  The other 46 cells terminate at ticks 24-48. Thus V28's reported recovery was
  a short-horizon survival lead, not a full support-valid teacher.
  Classification: `HYBRID_TEACHER_NOT_FULL_HORIZON_FEASIBLE`; decision:
  `CLOSE_V28_HYBRID_TEACHER_ROUTE`. Do not represent, distill, extend, or deploy
  this hybrid. No checkpoint is selected and robot clearance remains false.
  See
  `outputs/analysis/WINNER_V35_FULL_HORIZON_SOURCE_CONTINUATION_RESULT_20260722.md`.
- 2026-07-22: One zero-update Winner-v36 support-oracle shooting feasibility
  screen is preregistered. It tests only the frozen `COM_X_NEG` (`-0.05 m`
  torso-X) anchor under both measured actuator plants for the complete 250-tick
  support gate. A deterministic receding-horizon CEM controller may change only
  the six pitch-chain actions `2/3/4/11/12/13`; population/elites/iterations
  are `64/8/4`, horizon/block are `8/2` ticks, and every candidate and selected
  action passes through the exact graph absolute/rate boundary and unchanged
  actuator bridge. Both cells must pass and closest-result selection is
  forbidden. Exactly one formal CPU-only screen is authorized, with zero
  optimizer updates, locomotion training, RDK-X5, or robot work. A pass may
  authorize only a separately frozen full-configuration oracle feasibility
  screen; a hold neither proves physical uncontrollability nor permits tuning.
  No controller deployment, checkpoint selection, Gate 5, or robot clearance
  is authorized. See
  `outputs/analysis/WINNER_V36_SUPPORT_ORACLE_SHOOTING_FEASIBILITY_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v36 formal run `29897378894` completed HOLD; its
  original 107,560-byte ZIP exactly matches GitHub SHA-256
  `43f09ee5...fd9ac907`. The exact bounded six-pitch-joint shooting controller
  produced `0/2` full-horizon support passes on `COM_X_NEG`. P30 terminates at
  tick 55 and P31/34 at tick 52; both fail only `roll_pitch`, with minimum base
  height still `0.13947/0.14032 m`, maximum tilt `0.40814/0.39300 rad`, and no
  torque/current gate setting. Classification:
  `THIS_SHOOTING_CONTROLLER_NOT_FULL_HORIZON_FEASIBLE`; decision:
  `DO_NOT_USE_V36_SHOOTING_CONTROLLER_AS_TEACHER`. Do not tune its horizon,
  population, pitch-joint set, objective, or use it as a policy/runtime action
  wrapper. This result closes the exact controller, not physical
  controllability. No checkpoint is selected and robot clearance remains
  false. See
  `outputs/analysis/WINNER_V36_SUPPORT_ORACLE_SHOOTING_FEASIBILITY_RESULT_20260722.md`.
- 2026-07-22: One zero-update Winner-v37 warm-started shooting feasibility
  screen is preregistered. It repeats only V36's two `COM_X_NEG` plant cells
  and preserves the six pitch-chain joints, 250 ticks, 8-tick horizon,
  2-tick blocks, `64/8/4` CEM compute, covariance reset, objective, action
  boundary, actuator plants, PRNG seed, and support gate. The sole change is
  proposal memory: after tick 0, shift the prior winning raw plan by one tick,
  repeat its terminal action, and average adjacent pairs back into four blocks
  for the next mean. Tick-0 actions must reproduce V36 exactly; every later
  tick must exercise the warm start. Both plants must pass; closest-result
  selection is forbidden. Exactly one formal CPU-only screen is authorized,
  with zero optimizer updates, locomotion training, RDK-X5, or robot work. A
  pass may authorize only a separately frozen full-configuration warm-started
  oracle screen; a hold closes this proposal-memory mechanism without tuning.
  No controller deployment, checkpoint selection, Gate 5, or robot clearance
  is authorized. See
  `outputs/analysis/WINNER_V37_WARM_STARTED_SHOOTING_FEASIBILITY_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v37 formal run `29898430330` completed HOLD; its
  original 99,031-byte ZIP exactly matches GitHub SHA-256
  `d9677b83...0cf30445`. Both tick-0 actions reproduce V36 exactly, every later
  tick uses a nontrivial shifted proposal mean, and all selected actions remain
  graph-bounded. Neither plant passes: P30 terminates on `roll_pitch` at tick 46
  and P31/34 at tick 37, respectively 9 and 15 ticks earlier than V36. The
  warm-started trajectory also develops more roll (`-0.07165/-0.15592 rad` at
  termination) while pitch crosses `-0.35514/-0.35911 rad`. Classification:
  `STATEFUL_PROPOSAL_NOT_FULL_HORIZON_FEASIBLE`; decision:
  `CLOSE_WARM_STARTED_SHOOTING_PROPOSAL_MECHANISM`. Do not alter the warm-start
  transform, covariance, horizon, population, pitch-joint set, or objective and
  rerun this route. No checkpoint is selected and robot clearance remains
  false. See
  `outputs/analysis/WINNER_V37_WARM_STARTED_SHOOTING_FEASIBILITY_RESULT_20260722.md`.
- 2026-07-22: One zero-update Winner-v38 mirrored-pitch shooting feasibility
  screen is preregistered. It repeats only the two `COM_X_NEG` plant cells and
  restores V36's cold per-tick proposal. The same six pitch joints remain
  controlled, but CEM samples the reviewed three-coordinate bilateral basis:
  opposite-sign hip-pitch magnitude and same-sign knee/ankle actions. The
  250-tick duration, 8/2-tick horizon/block, `64/8/4` compute, covariance,
  objective, graph action boundary, actuator plants, and support gate are
  unchanged. Both cells must pass; closest-result selection is forbidden.
  Exactly one formal CPU-only screen is authorized, with zero optimizer
  updates, locomotion training, RDK-X5, or robot work. A pass may authorize
  only a separately frozen negative-X mirrored-teacher contract; a hold closes
  this exact subspace without tuning or adding another action axis. No
  controller deployment, checkpoint selection, Gate 5, or robot clearance is
  authorized. See
  `outputs/analysis/WINNER_V38_MIRRORED_PITCH_SHOOTING_FEASIBILITY_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v38 formal run `29899217913` completed HOLD; its
  original 251,940-byte ZIP exactly matches GitHub SHA-256
  `25d3e19c...985abb0c`. Both cells use the exact three-dimensional mirrored
  basis and graph-bounded actions. Mirroring suppresses the V37 roll growth and
  extends survival versus V36 from `55/52` to `69/161` ticks, but neither plant
  passes the complete 250-tick gate. Both still terminate only on pitch-led
  `roll_pitch` crossings (`pitch=-0.40746/-0.37829 rad`,
  `roll=-0.01842/-0.01720 rad`). Classification:
  `MIRRORED_PITCH_SUBSPACE_NOT_FULL_HORIZON_FEASIBLE`; decision:
  `CLOSE_MIRRORED_PITCH_SHOOTING_MECHANISM`. The large P31/34 survival gain is
  evidence, not a selectable closest result. Do not tune the basis, horizon,
  population, objective, covariance, or add another axis to this route. No
  checkpoint is selected and robot clearance remains false. See
  `outputs/analysis/WINNER_V38_MIRRORED_PITCH_SHOOTING_FEASIBILITY_RESULT_20260722.md`.
- 2026-07-22: One zero-update Winner-v39 response-Jacobian feasibility screen
  is preregistered for only the two `COM_X_NEG` actuator-plant cells. At every
  real tick it snapshots the exact simulator state, starts from the projected
  previous action in the reviewed three-coordinate mirrored pitch basis, and
  measures the eight-tick signed pitch/pitch-rate response to plus/minus one
  minimum paired graph-action delta on each axis. It solves one deterministic
  minimum-norm `numpy.linalg.lstsq(rcond=None)` correction, clips each axis to
  that same finite-difference step, applies only the first graph-bounded tick,
  and relinearizes. Both plants must pass all 250 ticks, every Jacobian must
  retain full row rank, and closest-result selection is forbidden. Exactly one
  formal CPU-only screen is authorized with zero optimizer updates, locomotion
  training, RDK-X5, or robot work. A pass may authorize only a separately
  frozen teacher contract; a hold closes this exact local controller without
  tuning the response, perturbation, horizon, solver, or correction bound. It
  is not a runtime wrapper, checkpoint selection, Gate 5 authorization, or
  robot clearance. See
  `outputs/analysis/WINNER_V39_RESPONSE_JACOBIAN_FEASIBILITY_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v39 formal run `29900500665` completed INVALID;
  its original 82,534-byte ZIP exactly matches GitHub SHA-256
  `c283b291...c5b0cea`. Both graph-bounded cells fail support earlier than V38,
  at ticks `32/31`, and neither is a teacher candidate. The preregistered
  validity rule also fails: P30 Jacobian ranks fall below two at ticks
  `30/31/32`, and P31/34 at ticks `30/31`. In every rank-zero case all
  eight-tick perturbation branches terminate before the requested commands can
  produce distinct response samples, yielding identical pitch/pitch-rate
  responses rather than an identifiable local map. The formal decision is
  `DO_NOT_SELECT_NEXT_POLICY_MECHANISM`; do not relabel this INVALID artifact
  as HOLD, rerun it, weaken the rank rule, or infer a clean controller-family
  rejection from it. Any attribution or next mechanism requires a separate
  frozen saved-result analysis. No checkpoint is selected and robot clearance
  remains false. See
  `outputs/analysis/WINNER_V39_RESPONSE_JACOBIAN_FEASIBILITY_RESULT_20260722.md`.
- 2026-07-22: One Winner-v40 saved-result-only attribution is preregistered
  against the committed Winner-v39 INVALID artifact. It executes no simulator,
  controller, optimizer, training, RDK-X5, or robot work and cannot rerun V39.
  It tests whether every V39 Jacobian before the first rank loss is full-row-
  rank, whether all rank losses lie within two ticks of the actual terminal and
  are accounted for by terminal-truncated plus/minus branches with identical
  pitch/pitch-rate responses, and whether both bounded nonzero recorded
  controllers still fail support earlier than V38. A pass closes only the
  exact V39 controller without converting its INVALID result to HOLD or making
  a family/controllability claim; it may authorize only a separately frozen
  nonlocal support-controller feasibility design. A hold preserves
  `DO_NOT_SELECT_NEXT_POLICY_MECHANISM`. No checkpoint selection, simulation,
  training, Gate 5, deployment, or clearance is authorized. See
  `outputs/analysis/WINNER_V40_RESPONSE_JACOBIAN_INVALIDITY_ATTRIBUTION_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v40 attribution run `29901125171` passed; its
  original 1,895-byte ZIP exactly matches GitHub SHA-256
  `1536a460...51b5c1f4`. Every V39 Jacobian before tick 30 is full-row-rank.
  Rank loss begins at tick 30 in both plants and is confined to the final
  two/one ticks before the recorded terminals at `32/31`; every missing column
  is accounted for by plus/minus branches that terminate before the eight-tick
  horizon with identical pitch/pitch-rate responses. Both recorded controllers
  nevertheless use bounded nonzero actions, fail support, and terminate
  `37/130` ticks earlier than V38. Classification:
  `TERMINAL_TRUNCATION_EXPLAINS_RANK_INVALIDITY_NOT_SUPPORT_FAILURE`; decision:
  `CLOSE_EXACT_V39_CONTROLLER_WITHOUT_RERUN`. This does not convert V39 to a
  valid HOLD result and does not reject the response-inversion family or prove
  uncontrollability. It authorizes only a separately frozen nonlocal support-
  controller feasibility design. Simulation, training, checkpoint selection,
  RDK-X5, robot, Gate 5, deployment, and clearance remain unauthorized. See
  `outputs/analysis/WINNER_V40_RESPONSE_JACOBIAN_INVALIDITY_ATTRIBUTION_RESULT_20260722.md`.
- 2026-07-22: One Winner-v41 full-horizon static-equilibrium feasibility
  screen is preregistered for `COM_X_NEG`. It exhausts the fixed nine-level
  Cartesian grid over the unchanged reviewed bilateral hip-pitch/knee/ankle
  basis: `9^3=729` time-invariant targets and `1,458` target/plant cells. Each
  target is held for all 250 ticks and reaches the plant only through the exact
  graph absolute/rate boundary; one identical target must pass both P30 and
  P31/34. This is materially different from the closed shooting routes: there
  is no receding horizon, action sequence, CEM population update, covariance,
  elite selection, local pulse composition, response Jacobian, or changing
  plan. The finite grid is exhausted once with no refinement. A deterministic
  diagnostic best may be reported on HOLD but cannot be promoted. Exactly one
  formal CPU-only screen is authorized, with zero optimizer updates,
  locomotion training, RDK-X5, or robot work. A pass may authorize only a
  separately frozen static-target teacher contract; a hold closes this exact
  equilibrium route without changing the grid, bounds, basis, or promoting a
  closest result. It is not a runtime target/wrapper, checkpoint selection,
  Gate 5 authorization, or robot clearance. See
  `outputs/analysis/WINNER_V41_STATIC_EQUILIBRIUM_TARGET_FEASIBILITY_PREREGISTRATION_20260722.md`.
- 2026-07-22: Winner-v41 first attempt `29901924055` is preserved as
  `INVALID_WINNER_V41_FIRST_ATTEMPT_NO_RESULT`. It passed tests, source hashes,
  and environment preparation, then failed before candidate 0 reached MuJoCo:
  the runner passed a single `(1,3)` static target to the frozen Winner-v38
  helper that accepts exactly four `(4,3)` sequence blocks. No result or
  artifact was produced and candidate/plant execution counts are `0/0`. Do not
  rerun that workflow or infer efficacy. One versioned v2 correction is
  preregistered: replace only that call with the same reviewed mirror-matrix
  multiplication into indices `2/3/4/11/12/13`. The 729 targets, both plants,
  250 ticks, action boundary, selection/pass rules, execution counts, and
  authority are unchanged. Exactly one separately named corrected CPU run is
  authorized. Optimizer updates, training, runtime target/wrapper, RDK-X5,
  robot, Gate 5, deployment, and clearance remain unauthorized. See
  `outputs/analysis/WINNER_V41_FIRST_ATTEMPT_FAILURE_RECEIPT_20260722.md` and
  `outputs/analysis/WINNER_V41_V2_RUNNER_CORRECTION_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole corrected Winner-v41-v2 run `29902429818` passed; its
  original 472,127-byte ZIP exactly matches GitHub SHA-256
  `2ed01e17...788bf52d`. The complete 729-target grid produced 117 P30 passes,
  103 P31/34 passes, and 100 identical targets that pass both plants for all
  250 ticks. The deterministic selected target is candidate 275 with mirrored
  coordinates `[-0.25,-0.25,+0.25]`, equivalent to normalized actions
  `left hip pitch +0.25`, `right hip pitch -0.25`, both knees `-0.25`, and
  both ankles `+0.25` (all other actions zero). Its exact replay completes
  `250/250` under both plants, minimum base Z is `0.15 m`, maximum tilt is
  `0.03159/0.03432 rad`, final-window gyro maxima are
  `0.000344/0.000321 rad/s`, and current/torque maxima are
  `1.2877/1.3969 A` and `1.0102/1.0959 N.m`. Classification:
  `SHARED_FULL_HORIZON_STATIC_SUPPORT_TARGET_EXISTS`; decision:
  `AUTHORIZE_STATIC_TARGET_TEACHER_CONTRACT_ONLY`. This proves bounded support
  authority exists for the exact `COM_X_NEG` anchor; it does not authorize
  sending the target to the runtime/robot, treating it as a deployable policy,
  or assuming it generalizes to the full configuration population. A separate
  static-target teacher contract is required before any training design.
  Checkpoint selection, training, RDK-X5, robot, Gate 5, deployment, and
  clearance remain unauthorized. See
  `outputs/analysis/WINNER_V41_V2_STATIC_EQUILIBRIUM_TARGET_FEASIBILITY_RESULT_20260722.md`.
- 2026-07-22: One Winner-v42 static-target teacher-table screen is
  preregistered over the exact 15-configuration Winner-v33 failure union. For
  each configuration it exhausts the unchanged Winner-v41 `9^3=729` target
  grid for 250 ticks under both P30 and P31/34 measured actuator plants, for
  exactly `10,935` targets and at most `21,870` candidate/plant cells. The
  deterministic Winner-v41 selection key is unchanged. All 15 tables execute;
  a configuration with no shared two-plant support target records a diagnostic
  best but cannot promote it. Pass requires every configuration to have at
  least one shared target and may authorize only a separately frozen,
  default-off static-target teacher ABI CPU contract. Hold closes this exact
  table route without grid refinement, basis changes, or fitting only passing
  configurations. Exactly one formal CPU-only run is authorized, with zero
  optimizer updates, locomotion training, runtime target/wrapper, RDK-X5,
  robot, Gate 5, deployment, checkpoint selection, or clearance. See
  `outputs/analysis/WINNER_V42_STATIC_TARGET_TEACHER_TABLE_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v42 run `29903694895` passed; its original
  3,777,480-byte ZIP exactly matches GitHub SHA-256
  `301cad42...1f04550b`. All `15/15` Winner-v33 failure configurations have at
  least one shared 250-tick static support target under both measured actuator
  plants, with `2,351` shared targets across the tables and no holds. Per-
  configuration shared counts range from `39` (`COM_CORNER_03`) to `227`
  (`OPTIONAL_AGGREGATE_HEAVY_AFT`). All `21,870` candidate/plant cells retained
  graph-bounded actions, and the exact selected target for every configuration
  replayed identically under both plants. Classification:
  `FULL_FAILURE_SET_STATIC_TARGET_TEACHER_TABLE_EXISTS`; decision:
  `AUTHORIZE_STATIC_TARGET_TEACHER_ABI_CPU_CONTRACT_ONLY`. This establishes a
  complete simulator supervision table; it does not authorize copying targets
  into the runtime, training, selecting a checkpoint, RDK-X5/robot access,
  Gate 5, deployment, or clearance. See
  `outputs/analysis/WINNER_V42_STATIC_TARGET_TEACHER_TABLE_RESULT_20260722.md`.
- 2026-07-22: One zero-update Winner-v43 static-target teacher ABI CPU proof is
  preregistered against the exact imported Winner-v42 table. It converts each
  selected three-coordinate target into the reviewed 14-action mirror basis,
  applies the inherited inward graph boundary relative to the realized
  previous action, stops gradients through the target and previous-action
  path, and supervises only indices `2/3/4/11/12/13`. The exact proof covers
  15 configurations, both actuator-plant rows, 250 ticks, and 45,000 valid
  pitch elements. Privileged configuration IDs are training-label lookup keys
  only; they are not actor inputs and no deployable graph field is added.
  Non-pitch teacher gradients must be exact zero and the default-off loss and
  gradients must be bit-exact to baseline. The enabled unit scale is diagnostic
  only and cannot be carried into training. Exactly one hosted CPU proof is
  authorized with zero optimizer updates, simulator behavior ticks, training,
  graph export, RDK-X5, or robot work. A pass may authorize only a separately
  preregistered zero-update source-gradient contract; it cannot train, select a
  checkpoint, change the runtime, or grant clearance. See
  `outputs/analysis/WINNER_V43_STATIC_TARGET_TEACHER_ABI_CPU_CONTRACT_20260722.md`.
- 2026-07-22: The sole Winner-v43 run `29905544015` passed; its original
  2,860-byte ZIP exactly matches GitHub SHA-256
  `20b2e0a4...4166d539`. All 15 imported targets matched both Winner-v42 replay
  hashes, the exact 30-row/250-tick teacher batch contained 45,000 valid pitch
  elements, and the inherited inward boundary reached every selected raw
  target. The raw teacher loss is `0.1167156175` in the synthetic proof, with
  maximum raw/bounded target magnitude `0.75/0.75`. Teacher gradients are
  finite and nonzero on all six reviewed pitch indices, exact zero on all
  eight non-pitch indices, and exact zero through the stopped target/previous-
  action path. Default-off loss and gradients are bit-exact to baseline; the
  diagnostic unit-scale enabled path changes only pitch gradients.
  Classification decision:
  `AUTHORIZE_STATIC_TARGET_TEACHER_SOURCE_GRADIENT_CPU_CONTRACT_ONLY`. No unit
  scale is selected for training. A separate zero-update source-rollout proof
  must choose and bind the source checkpoint, measure the real teacher
  gradient, and derive a single scale before an optimizer update can even be
  considered. Training, graph changes, checkpoint selection, runtime work,
  RDK-X5/robot access, Gate 5, deployment, and clearance remain unauthorized.
  See `outputs/analysis/WINNER_V43_STATIC_TARGET_TEACHER_ABI_CPU_RESULT_20260722.md`.
- 2026-07-22: One zero-update Winner-v44 source-gradient CPU proof is
  preregistered. The continuation source is Winner-v32 half at update 251,
  selected only because it passed `99/124` identical Winner-v33 support cells
  versus final's `94/124`; this is not deployment-checkpoint selection. The
  proof reproduces its exact 80-slot update-251 rollout and complete existing
  objective (PPO + normalized predictor at `380.9135437011719` + prefix anchor
  at `197.3112030029297`), then measures the raw Winner-v43 teacher gradient.
  Teacher labels cover only the 11 V42 configurations present in the training
  population, exactly two plant rows each. `HELDOUT_04/07/09/15` labels are
  explicitly excluded to prevent heldout leakage. A single scale is derived by
  matching baseline and teacher gradient RMS over the same recurrent-core and
  action-head leaves; V43's diagnostic unit scale is not carried forward. The
  default-off gradient and transition arrays must remain bit-exact, and no
  action is replaced. Exactly one hosted CPU proof is authorized with zero
  optimizer updates, formal support cells, locomotion training, graph exports,
  RDK-X5, or robot work. A pass may authorize only a separately preregistered
  one-update CPU proof using the recorded scale. See
  `outputs/analysis/WINNER_V44_STATIC_TARGET_TEACHER_SOURCE_GRADIENT_CONTRACT_20260722.md`.
- 2026-07-22: The sole Winner-v44 run `29906883886` passed; its original
  5,429-byte ZIP exactly matches GitHub SHA-256
  `a799715b...e3895666`. The exact update-251 rollout reproduced 80 slots and
  17 roll/pitch failures. The training-only table selected 22 configuration/
  plant rows and 10,692 valid pitch elements; all four heldout labels remained
  absent. Raw teacher loss is `0.0119318310`. Baseline gradient RMS is
  `0.1813885089`, raw teacher gradient RMS is `0.00310403439`, and the sole
  derived float32 teacher scale is `58.436370849609375`, yielding scaled RMS
  `0.1813885045`. Teacher gradients are nonzero on all six recurrent/action
  leaves and exact zero on value, log-std, and predictor leaves. Default-off
  gradients and transition arrays are bit-exact; direct and composed enabled
  gradients pass the frozen tolerances. Decision:
  `AUTHORIZE_ONE_UPDATE_STATIC_TARGET_TEACHER_CPU_PROOF_PREREGISTRATION_ONLY`.
  No optimizer step, formal support gate, graph export, training continuation,
  deployment selection, RDK-X5/robot access, Gate 5, or clearance occurred. A
  separate one-update CPU contract must restore the source exactly, apply only
  this scale once, verify the changed/frozen leaves and export contract, then
  stop. See
  `outputs/analysis/WINNER_V44_STATIC_TARGET_TEACHER_SOURCE_GRADIENT_RESULT_20260722.md`.
- 2026-07-22: One Winner-v45 one-update static-target-teacher CPU proof is
  preregistered from Winner-v32 half at optimizer count `251`. It must
  reproduce the exact 80-slot update-251 rollout dimensions and unchanged
  Winner-v32 objective, attach only the 11 training-population teacher labels,
  exclude `HELDOUT_04/07/09/15`, and apply the sole frozen Winner-v44 float32
  scale `58.436370849609375`. Exactly one Adam update to count `252` is
  authorized. Pass requires lower same-batch teacher MSE, all 12 trainable
  leaves changed, every frozen parameter leaf bit-exact, exact snapshot
  readback, and an unchanged stateful `115/14/64` hard-bounded ONNX ABI with no
  teacher/configuration-table state. Cross-worker rollout byte hashes are
  recorded but are not pass gates; exact source artifact bytes, dimensions,
  masks, objective mechanics, and counts remain gates. The workflow performs
  zero formal support cells, continuation-training updates, RDK-X5/robot
  access, or motion. A pass may authorize only a separately frozen bounded
  continuation preregistration; it cannot select a deployment checkpoint or
  grant clearance. See
  `outputs/analysis/WINNER_V45_STATIC_TARGET_TEACHER_ONE_UPDATE_CPU_CONTRACT_20260722.md`.
- 2026-07-22: The sole Winner-v45 workflow run `29907921832` completed
  successfully and uploaded immutable artifact `8524663581`, whose original
  247,738-byte ZIP matches GitHub SHA-256 `5ff180cd...665523aa`. The frozen v1
  importer validated the raw result, snapshot, ONNX bytes, attribution, and
  complete pass contract, then failed only while rendering Markdown because
  local variables `before` and `after` were not bound in `main`. No workflow
  rerun or artifact mutation is authorized. One reporting-only importer-v2
  correction is preregistered: preserve the complete v1 validation, bind those
  two values from the already validated result, and import the same ZIP once.
  Optimizer updates, formal support cells, continuation training, RDK-X5/robot
  access, checkpoint selection, and clearance remain unauthorized. See
  `outputs/analysis/WINNER_V45_IMPORTER_V2_CORRECTION_PREREGISTRATION_20260722.md`.
- 2026-07-22: The preregistered Winner-v45 importer-v2 correction imported the
  same immutable run-`29907921832` artifact without rerun or mutation. All
  frozen proof checks pass. The sole Adam update advances count `251 -> 252`;
  same-batch static-target teacher loss decreases from `0.0119318310` to
  `0.0115688266`, the independently recomputed scale differs from the frozen
  `58.436370849609375` by only `6.53e-8` relative, all 12 trainable leaves
  change, and every frozen parameter leaf remains bit-exact. Snapshot SHA-256
  is `72c2e0bf...6e4832b`; ONNX SHA-256 is
  `8571f827...e490d242`. The graph preserves the exact stateful `115/14/64`
  ABI, JAX/ONNX agreement, previous-action chain, and contains no teacher or
  privileged configuration token. Decision:
  `AUTHORIZE_STATIC_TARGET_TEACHER_TRAINING_PREREGISTRATION_ONLY`. No formal
  support cell, continuation update, RDK-X5/robot access, checkpoint selection,
  or clearance occurred. See
  `outputs/analysis/WINNER_V45_STATIC_TARGET_TEACHER_ONE_UPDATE_CPU_RESULT_20260722.md`.
- 2026-07-22: One Winner-v46 bounded static-target-teacher continuation is
  preregistered from the exact passing Winner-v45 count-`252` snapshot. It
  inherits Winner-v32's unchanged 100-update persistence length without a
  coefficient or length search, yielding persistent half/final checkpoints at
  counts `302/352`. Every update uses the complete existing PPO + normalized
  predictor (`380.9135437011719`) + prefix anchor (`197.3112030029297`)
  objective plus the sole frozen static-target-teacher scale
  `58.436370849609375`. Labels cover exactly the 11 training configurations
  and 22 plant rows; all four heldout labels remain excluded, supervision is
  limited to pitch indices `2/3/4/11/12/13`, targets and previous-action paths
  are stopped, and actions are never replaced. The workflow must preserve the
  exact source snapshot/graph, Adam state, transition mechanics, bounded action
  graph, all 12 updating leaves, frozen parameter leaves, atomic snapshots,
  and stateful `115/14/64` ONNX ABI. Exactly one first-attempt CPU arm is
  authorized. It performs zero formal support cells, RDK-X5/robot access, or
  checkpoint selection. A pass may authorize only a separately frozen
  half/final support and context gate. See
  `outputs/analysis/WINNER_V46_STATIC_TARGET_TEACHER_TRAINING_PREREGISTRATION_20260722.md`.
- 2026-07-22: While the sole Winner-v46 arm is still running, the Winner-v47
  support-gate package is pre-specified but inert. It binds no checkpoint and
  cannot generate a contract until a strictly imported passing Winner-v46
  artifact exists. The proposed evaluator is exactly the unchanged reviewed
  124-cell-per-checkpoint physical support/context gate: both half and final,
  250 ticks per cell, 248 main cells total, 64 heldout repeat cells, all 16
  heldout contexts separate at both checkpoints, learned prediction beating
  the constant baseline separately per plant, and no closest-result promotion.
  This pre-specification occurs before observing either Winner-v46 checkpoint
  and performs zero gate cells, optimizer updates, RDK-X5/robot access,
  checkpoint selection, or clearance. Only a later hash-bound contract built
  from a passing imported Winner-v46 result can authorize execution.
- 2026-07-22: The sole Winner-v46 first-attempt CPU arm completed successfully
  at GitHub run `29909100403`, launch head
  `1a1f6d1803b390168f0bf9b60c257e0180ba8484`, and artifact ID
  `8527007840`. The preserved 19,252,851-byte original ZIP exactly matches
  GitHub SHA-256 `fb6edf22...372e12c2`. The strict importer validated all 104
  members, all 100 consecutive snapshots from counts `253..352`, every
  update receipt and objective invariant, all 12 nonzero cumulative leaf
  deltas, frozen parameter leaves, and both exact stateful `115/14/64` ONNX
  contracts. The count-302 half snapshot/graph SHA-256 values are
  `d6067047...ff1d476b` / `b4326259...cfe41ac1`; count-352 final values are
  `e32a7d5e...8c86e0df` / `e3d209fd...8ccaa7d2`. Static-target teacher loss is
  `0.0118446639` at the first continuation update, `0.0089533264` at half,
  and `0.0094035575` at final; these are training diagnostics, not behavior
  or checkpoint-selection evidence. Decision:
  `AUTHORIZE_STATIC_TARGET_TEACHER_SUPPORT_GATE_PREREGISTRATION_ONLY`.
  Formal support cells, locomotion training, checkpoint selection,
  RDK-X5/robot access, Gate 5, deployment, and clearance remain unauthorized.
  See
  `outputs/analysis/WINNER_V46_STATIC_TARGET_TEACHER_TRAINING_RESULT_20260722.md`.
- 2026-07-22: The passing imported Winner-v46 artifact now binds one exact
  Winner-v47 formal support/context gate. Source-manifest SHA-256 is
  `ab3d8718...4a779db`; the frozen checkpoint pairs are count-302 snapshot /
  ONNX `d6067047...ff1d476b` / `b4326259...cfe41ac1` and count-352
  `e32a7d5e...8c86e0df` / `e3d209fd...8ccaa7d2`. The reviewed physical
  evaluator, populations, thresholds, seeds, and all-or-nothing persistence
  rule are unchanged: 124 main cells and 32 heldout repeats at each of half
  and final, 250 ticks per cell, all 16 heldout contexts separate at both
  checkpoints, learned response prediction beating the constant baseline per
  plant, and no closest-result promotion. The normalized auxiliary predictor
  is projected exactly into the evaluator's raw scoring coordinates without
  changing checkpoint or ONNX bytes. Exactly one first-attempt CPU gate is
  authorized. It performs zero optimizer or locomotion-training steps and no
  RDK-X5/robot work. A pass may authorize only a separately reviewed
  response-conditioned locomotion-training preregistration; it is not
  checkpoint selection, deployment, or robot clearance. See
  `outputs/analysis/WINNER_V47_STATIC_TARGET_TEACHER_SUPPORT_GATE_PREREGISTRATION_20260722.md`.
- 2026-07-22: The first-attempt Winner-v47 workflow run `29914159165` failed
  during package composition before checkpoint loading or any formal cell. All
  checkout, dependency, source-manifest, Winner-v46 artifact, checkpoint-byte,
  and environment-preparation steps passed. The unchanged Winner-v12 evaluator
  then rejected the Winner-v47 manifest at `load_calibrator_design`: V47 named
  the correct design source `calibrator_design`, while the reviewed loader
  requires the provenance key `calibrator_design_preregistration`. The job
  produced no result artifact and executed exactly zero support cells. Its
  preserved 54,763-byte failed log has SHA-256
  `db26d747...47ab1d5`. This is an execution-package failure, not a policy HOLD,
  and the run is not retried or reclassified.
- 2026-07-22: Winner-v47b preregisters one separately named first-attempt CPU
  execution correction. Original V47 contract SHA-256 is
  `4b2e2000...a1276132`; correction source-manifest SHA-256 is
  `e0e8a438...318f4614`. The sole change routes the exact Winner-v12 full-
  training preregistration into its unchanged calibrator-design provenance
  loader. The exact Winner-v46 checkpoints, 124-cell/checkpoint population,
  32 heldout repeats/checkpoint, thresholds, seeds, normalized-to-raw predictor
  projection, both-checkpoint persistence rule, and no-closest-selection rule
  are byte-for-byte inherited. No policy, checkpoint, gate, behavior, or
  authority changes. One corrected CPU run is authorized; optimizer,
  locomotion, RDK-X5/robot, Gate 5, deployment, and clearance remain zero or
  false. See
  `outputs/analysis/WINNER_V47B_SUPPORT_GATE_EXECUTION_CORRECTION_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole corrected Winner-v47b run `29914814609` completed all
  `248` main cells and `64` heldout repeats and produced a genuine policy HOLD.
  Its original 248,630-byte ZIP exactly matches GitHub SHA-256
  `c26ee2fa...50a08bc0`. Half passes `108/124` support cells and final passes
  `112/124`; both fail the unchanged all-cells persistence rule, so neither
  checkpoint is selected. Every sensor/transport cell passes. Both checkpoints
  also pass exact cell counts, previous-action chaining, JAX/ONNX hidden-state
  agreement, all 32 heldout repeats, all 16 heldout context separations, and
  learned response prediction versus the constant baseline separately per
  plant. Every failed cell is an early roll/pitch-only terminal under both P30
  and P31/34. Persistent failures are `COM_CORNER_01`, `COM_CORNER_03`,
  `COM_X_NEG`, `DISCOVERY_03`, `HELDOUT_04`, and `HELDOUT_09`; half additionally
  fails `COM_CORNER_00` and `COM_CORNER_02`. Failure ticks span `30..66` at
  half and `29..55` at final. Decision:
  `DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION`. This closes the exact static-
  target-teacher continuation; no closest checkpoint, extra updates, or
  locomotion training is promoted. RDK-X5/robot access, Gate 5, deployment,
  and clearance remain unauthorized. See
  `outputs/analysis/WINNER_V47B_SUPPORT_GATE_EXECUTION_CORRECTION_RESULT_20260722.md`.
- 2026-07-22: Winner-v48 preregisters one read-only CPU causal diagnostic for
  the exact eight-configuration Winner-v47b failure union. Across both frozen
  checkpoints and both actuator plants it runs `128` cells: the unchanged
  graph, the full proven Winner-v42 static teacher, teacher pitch with graph
  non-pitch outputs, and graph pitch with non-pitch outputs driven toward zero
  through the unchanged action boundary. The unchanged graph arm must be
  bit-exact to all `32` imported V47b cells, and the `28` actually failed pairs
  are classified without a threshold or closest-result rule. The graph's
  action-independent `h_out` is retained while the actually applied
  intervention is chained as `previous_action`. This executes no optimizer,
  locomotion, RDK-X5, robot, torque, or motion work and cannot select a
  checkpoint or grant clearance. See
  `outputs/analysis/WINNER_V48_STATIC_TEACHER_CAUSAL_DIAGNOSTIC_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v48 execution completed all `128` frozen CPU
  cells but is formally `INVALID`, not a policy result, because the
  preregistered whole-public-dictionary bit-exact comparison rejected
  cross-host float64 MuJoCo evidence differences of roughly machine precision.
  The four float32 action/observation/prediction/hidden trace hashes match the
  imported V47b cells exactly, as do support outcomes and terminal ticks; the
  failed check is only `all_graph_cells_bit_exact_to_v47b`. The captured but
  not yet promotable causal values are full teacher `32/32`, pitch-only rescue
  `25/28`, and pitch/non-pitch interaction `3/28`. No rerun, optimizer,
  locomotion, RDK-X5, robot, torque, motion, checkpoint selection, or clearance
  is authorized by this invalid result. Result SHA-256:
  `cc4ec3cb...756e31cc`. A separately frozen evidence-only comparator
  correction is required before interpreting the captured cells.
- 2026-07-22: Winner-v48b preregisters that evidence-only correction with no
  physics rerun. It requires all four float32 trace hashes to match exactly for
  every one of the `32` graph cells; support outcomes, terminal ticks, checks,
  contacts, valid-tick counts, state chaining, and hashes remain exact. Only
  shared float64 terminal/summary diagnostics use absolute tolerance `1e-12`
  with relative tolerance zero. This is a bookkeeping comparator, not a
  behavior threshold. It audits the already captured `128` cells and executes
  zero new cells, optimizer updates, locomotion steps, RDK-X5/robot access,
  torque, or motion. A pass can authorize only a separate full-14D static-
  teacher mechanism preregistration; training and clearance remain false. See
  `outputs/analysis/WINNER_V48B_EVIDENCE_COMPARATOR_CORRECTION_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v48b captured-evidence audit is also formally
  `INVALID`; preserve it rather than widening its preregistered tolerance. Its
  maximum shared float64 diagnostic difference is
  `1.7110757255522913e-12`, above the frozen `1e-12` bookkeeping limit. One
  full-duration graph control (`final / COM_CORNER_02 / P30`) also differs only
  in its observation hash while retaining the exact action, prediction, and
  hidden hashes and the same full support outcome. All `28` graph-failing pairs
  that define the causal classification retain all four exact trace hashes and
  exact discrete outcomes. Result SHA-256:
  `dc764b82...00df91c`. This invalid audit authorizes no policy interpretation,
  training, deployment, or robot work. A separately frozen causal-population
  scope audit, with no movable float tolerance and no new physics cells, is
  required.
- 2026-07-22: Winner-v48c preregisters a no-tolerance scope audit over only the
  exact `28` V47b graph-failing checkpoint/configuration/plant pairs that
  define the causal claim. Every such pair must retain all four exact trace
  hashes plus exact support outcome, terminal tick, validity checks, contacts,
  valid-tick count, and previous-action chain. The four full-duration graph
  pairs that formally passed are controls and are not used to prove failure
  causality. The audit reads the already captured `128` intervention cells,
  executes zero new physics cells, and cannot move any float tolerance. A pass
  with any pitch/non-pitch interaction can authorize only a separate full-14D
  static-teacher mechanism preregistration. Training, RDK-X5/robot access,
  torque, motion, deployment, and clearance remain false. See
  `outputs/analysis/WINNER_V48C_CAUSAL_POPULATION_SCOPE_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v48c captured causal-population audit passes.
  All `28/28` formal V47b failure pairs retain all four exact trace hashes and
  exact discrete outcomes. The full 14-D Winner-v42 teacher passes `32/32`
  captured cells. Of the `28` failures, `25` are classified
  `pitch_output_causal` and `3` are `pitch_nonpitch_interaction`; none is
  teacher-insufficient or non-pitch-only. The evidence-selected problem class
  is therefore `FULL_14D_STATIC_TEACHER_MAPPING`, proving that the old
  six-pitch-element supervision omitted a necessary part of the control label.
  Decision: authorize only a separately preregistered full-14D static-teacher
  mechanism. No training, checkpoint selection, locomotion, RDK-X5/robot
  access, torque, motion, deployment, or clearance is authorized by this
  audit. See
  `outputs/analysis/WINNER_V48C_CAUSAL_POPULATION_SCOPE_RESULT_20260722.md`.
- 2026-07-22: Winner-v49 preregisters the evidence-selected full-action static-
  teacher ABI. It keeps the exact Winner-v42 raw and graph-bounded targets but
  expands supervision from the old pitch indices `[2,3,4,11,12,13]` to all
  `14` actions, including the eight causally required zero non-pitch targets.
  The scale is algebraic, not tuned: `58.436370849609375 * 14 / 6 =
  136.35153198242188`, making float32 scale-per-element bit-exact to the old
  pitch objective. The zero-update CPU proof must select exactly `105,000`
  valid elements, preserve the old scaled pitch gradient when non-pitch error
  is zero, add gradients on all eight non-pitch elements when they differ, and
  remain bit-exact when disabled. It executes no optimizer, simulator,
  locomotion, export, RDK-X5/robot, torque, or motion work. A pass authorizes
  only a separately preregistered source-gradient CPU contract; training and
  clearance remain false. See
  `outputs/analysis/WINNER_V49_FULL_ACTION_TEACHER_ABI_CPU_CONTRACT_20260722.md`.
- 2026-07-22: The sole Winner-v49 zero-update CPU ABI proof passes every check.
  It selects exactly `105,000` valid action elements, matches the old raw and
  graph-bounded targets bit-exactly, produces finite nonzero teacher gradients
  on all `14` action indices, stops the target and previous-action paths, and
  remains loss/gradient bit-exact when disabled. The algebraic full-action
  scale is `136.35153198242188`, or `9.739395141601562` per element, and its
  scaled pitch gradient differs from the old objective by exactly `0.0` when
  non-pitch error is zero. Result SHA-256:
  `9909e659...92856f9`. Decision: authorize only a separately preregistered
  source-gradient CPU contract. No optimizer update, training, simulator
  behavior, export, RDK-X5/robot access, torque, motion, deployment, checkpoint
  selection, or clearance is authorized.
- 2026-07-22: Winner-v50 preregisters one zero-update CPU source-gradient
  proof at the actual terminal Winner-v46 optimizer state (`final`, update
  `352`). This source is selected only because it is the terminal state of the
  sole completed V46 training arm; it is not a deployment-checkpoint
  selection. The exact `80 x 250` rollout replaces the old six-action teacher
  mean with the proven full-`14`-action mean at algebraic scale
  `136.35153198242188`, without additive double-counting, scale search, action
  replacement, or transition mutation. It must preserve the old pitch mask,
  add the eight valid non-pitch elements on exactly `22` frozen training plant
  rows, exclude all held-out teacher rows, change every policy-gradient leaf,
  preserve all non-policy gradients, and match both old and new direct
  gradients within `4e-6`. Default-off must reproduce the exact old V46
  gradient. This proof executes zero optimizer updates, support cells,
  locomotion-training steps, graph exports, RDK-X5/robot access, torque, or
  motion. A pass can authorize only a separately preregistered one-update
  CPU proof; training, checkpoint selection, deployment, and clearance remain
  false. See
  `outputs/analysis/WINNER_V50_FULL_ACTION_TEACHER_SOURCE_GRADIENT_CONTRACT_20260722.md`.
- 2026-07-22: The sole Winner-v50 zero-update source-gradient proof is a
  formal `HOLD`. Every source, rollout, transition, action-boundary, frozen
  teacher-population, full-14D mask, gradient-scope, default-off, finite-value,
  and no-mutation check passed. The replacement changed all six policy
  gradient leaves and preserved every non-policy gradient bit-exactly. The
  only failures were the separately computed old and new direct-versus-
  composed absolute-gradient checks: both measured exactly
  `4.76837158203125e-6`, just above the frozen `4e-6` bound. Result SHA-256:
  `7f1a6ae0...58b79b1`. Do not widen V50 post hoc and do not run an optimizer
  update. A separately frozen arithmetic-order audit with a mathematically
  derived elementwise floating-point bound is required. See
  `outputs/analysis/WINNER_V50_FULL_ACTION_TEACHER_SOURCE_GRADIENT_RESULT_20260722.md`.
- 2026-07-22: Winner-v50b preregisters one zero-update, CPU-only arithmetic
  attribution while preserving V50 as a hold. It reruns the exact V50
  `80 x 250` update-352 rollout and captures every element of the old and new
  direct/composed float32 gradient trees. The bound is the campaign's already
  preregistered Winner-v31 maximum of eight signed-float32 ULP per element; it
  was not selected from V50's unrecorded elementwise distances. Both
  `4.76837158203125e-6` absolute errors, all scalar/rollout evidence, and every
  non-composition check must reproduce exactly. The old `4e-6` V50 threshold
  is not changed and V50 is not rewritten. This attribution executes zero
  optimizer updates, support cells, locomotion-training steps, graph exports,
  RDK-X5/robot access, torque, or motion. A pass can authorize only a separately
  preregistered one-update CPU proof; training, deployment, checkpoint
  selection, and clearance remain false. See
  `outputs/analysis/WINNER_V50B_GRADIENT_COMPOSITION_ULP_ATTRIBUTION_CONTRACT_20260722.md`.
- 2026-07-22: The sole Winner-v50b ULP attribution is a formal `HOLD`. The
  exact V50 rollout, scalar evidence, source identity, both
  `4.76837158203125e-6` absolute errors, and every non-composition check
  reproduced bit-exactly. However, old/new direct-versus-composed gradients
  reach `36,608 / 16,440` signed-float32 ULP versus the frozen eight-ULP rule.
  Small absolute differences span many ULPs in gradient elements near zero,
  so the ULP metric is not scale-invariant here; do not widen it post hoc.
  Result SHA-256: `55b3b8ce...3db4469a`. No optimizer update, support gate,
  export, locomotion training, RDK-X5/robot access, torque, motion, deployment,
  checkpoint selection, or clearance is authorized. A separately
  preregistered scale-aware backward-error attribution derived from float32
  epsilon is required. See
  `outputs/analysis/WINNER_V50B_GRADIENT_COMPOSITION_ULP_ATTRIBUTION_RESULT_20260722.md`.
- 2026-07-22: Winner-v50c preregisters one zero-update, CPU-only scale-aware
  backward-error attribution. It preserves the V50 absolute-error and V50b ULP
  holds and reruns their exact `80 x 250` update-352 computation. Before any
  leaf scale is measured, the bound is fixed to
  `sqrt(float32 epsilon) = 0.00034526698300124393`. Every old and new gradient
  leaf must pass both maximum-error/leaf-maximum and RMS-error/leaf-RMS ratios;
  sign changes are allowed only inside that bound times the leaf maximum, and
  zero-reference leaves must remain bit-exact. Both original absolute errors
  and every non-composition check must reproduce. This changes neither prior
  limit and executes zero optimizer updates, support cells, locomotion-training
  steps, graph exports, RDK-X5/robot access, torque, or motion. A pass can
  authorize only a separately preregistered one-update CPU proof; training,
  deployment, checkpoint selection, and clearance remain false. See
  `outputs/analysis/WINNER_V50C_GRADIENT_BACKWARD_ERROR_ATTRIBUTION_CONTRACT_20260722.md`.
- 2026-07-22: The sole Winner-v50c scale-aware attribution passes every check.
  Against the frozen `sqrt(float32 epsilon) = 0.00034526698300124393` bound,
  old/new maximum relative error is only
  `7.29267879396252e-7 / 7.51381898651892e-7`, and maximum RMS-relative error
  is `2.6416685503084517e-7 / 2.6547401864741865e-7`. No material sign changes
  occur and zero-reference leaves remain bit-exact. The exact V50 absolute
  errors and all non-composition evidence reproduce. Result SHA-256:
  `ce3bbe55...1d2883d3`. V50 and V50b remain holds under their own unchanged
  metrics; this pass authorizes only preregistration of one exact CPU optimizer
  update from the frozen V46 terminal state. It does not authorize training,
  support evaluation, deployment, RDK-X5/robot access, torque, motion,
  checkpoint selection, or clearance. See
  `outputs/analysis/WINNER_V50C_GRADIENT_BACKWARD_ERROR_ATTRIBUTION_RESULT_20260722.md`.
- 2026-07-22: Winner-v51 preregisters exactly one CPU Adam update from the
  terminal Winner-v46 source at optimizer count `352` to `353`. It recomputes
  the exact V50 `80 x 250` update-352 rollout, replaces the old six-action
  teacher gradient with the proven full-`14`-action gradient at algebraic scale
  `136.35153198242188`, and performs no scale search or action replacement.
  The proof must supervise exactly `22` frozen training plant rows, exclude all
  held-out labels, reduce same-batch full-action teacher MSE, change every
  trainable leaf, preserve every frozen parameter leaf, round-trip the complete
  snapshot and Adam state, and export one non-selected candidate graph with the
  unchanged stateful hard-bounded `115/14/64` ABI and no training-only tensors.
  It executes zero support cells, continuation updates, RDK-X5/robot access,
  torque, or motion. A pass can authorize only a separately preregistered
  bounded continuation; it cannot select a deployment checkpoint or grant
  clearance. See
  `outputs/analysis/WINNER_V51_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_CONTRACT_20260722.md`.
- 2026-07-22: The first Winner-v51 invocation is `INVALID`, not a policy
  result. It completed the V50 recomputation and wrote a partial snapshot/ONNX,
  but crashed before result serialization with `KeyError: 'hidden_bias'`.
  Cause: the proof assigned the whole `objective_evidence` dictionary instead
  of its nested `full_teacher_gradient_max_abs` dictionary. The partial files
  are hash-recorded only to prevent accidental reuse and are not evidence.
  No continuation, support evaluation, deployment selection, RDK-X5/robot
  access, torque, motion, or clearance is authorized. Preserve the frozen V51
  runner; a separately preregistered one-line correction is required. See
  `outputs/analysis/WINNER_V51_FULL_ACTION_TEACHER_ONE_UPDATE_INVALID_INVOCATION_20260722.md`.
- 2026-07-22: Winner-v51b preregisters the exact correction for the invalid
  V51 proof without editing its frozen source. The correction replaces one and
  only one two-line fragment so `full_gradient_max` indexes
  `objective_evidence['full_teacher_gradient_max_abs']`; the complete corrected
  source SHA-256 is frozen in the contract. Optimizer, objective, source
  checkpoint, rollout, scale, snapshot, graph, and pass gates are unchanged.
  The original invalid partial artifacts remain forbidden. V51b may execute
  the same single CPU update from `352` to `353`, with zero support cells,
  continuation updates, RDK-X5/robot access, torque, or motion. A pass can
  authorize only a separately preregistered bounded continuation; it cannot
  select a checkpoint or grant clearance. See
  `outputs/analysis/WINNER_V51B_ONE_UPDATE_INDEXING_CORRECTION_CONTRACT_20260722.md`.
- 2026-07-22: The corrected Winner-v51b one-update proof passes every check.
  Optimizer count advances exactly `352 -> 353`; same-batch full-action teacher
  loss falls from `0.004192190710455179` to `0.004095083102583885`. Every
  trainable leaf changes, every frozen parameter leaf remains bit-exact, and
  the complete snapshot/Adam state round-trips. The stateful hard-bounded
  `115/14/64` candidate ONNX agrees with JAX within
  `1.4551915228366852e-11` and contains no teacher/training-only state.
  Snapshot SHA-256: `e0335fbc...e56a276e`; ONNX SHA-256:
  `6d300081...5486eca2`; result SHA-256: `9e08a08b...bf92aa7`. The equal hashes
  of the earlier invalid partial files now have an independently completed
  formal proof, but only the V51b result is authoritative. This pass authorizes
  only a separately preregistered bounded continuation. It does not select a
  deployment checkpoint, run support cells, or grant robot clearance. See
  `outputs/analysis/WINNER_V51B_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_RESULT_20260722.md`.
- 2026-07-22: Winner-v52 preregisters the sole bounded full-action-teacher
  continuation. It inherits the exact Winner-v46 persistence design: `100`
  optimizer updates, `80 x 250` scheduled ticks per update, immutable half/final
  checkpoints after `50/100` updates, and no coefficient or duration search.
  From the formal V51b source at count `353`, checkpoints are frozen at
  `403/453`. The old pitch-only loss is replaced by the proven full-`14`-action
  teacher at scale `136.35153198242188`; PPO, predictor, anchor, transition,
  population, seeds, learning rate, and action boundary remain unchanged. The
  execution source is an exact hash-bound transformation of the frozen V46
  runner, with every replacement count preregistered. Every update must preserve
  all source, mask, locality, finite-value, snapshot, and ONNX invariants.
  Neither checkpoint is selected during training, and no formal support cell,
  RDK-X5/robot access, torque, or motion is authorized. A pass authorizes only
  a separate half/final support-gate preregistration. See
  `outputs/analysis/WINNER_V52_FULL_ACTION_TEACHER_TRAINING_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v52 continuation passes all `22` checks after
  exactly `100` optimizer updates (`354` through `453`) and `2,000,000`
  scheduled episode slots on CPU. Every update selected the exact `22` frozen
  teacher rows, supervised all `14` actions over its valid transitions,
  excluded held-out labels, remained finite, preserved every action-boundary,
  transition, hidden-replay, and frozen-leaf invariant, and wrote one verified
  atomic snapshot. The count-`403` half graph SHA-256 is
  `9bd297d6...60ca23d`; the count-`453` final graph SHA-256 is
  `b710e8c1...b53b618b`. Both expose the exact stateful `115+14+64 ->
  14+14+64` ABI, pass a 250-tick chain, and agree with JAX within
  `8.731149137020111e-11`. Result SHA-256: `a964b30f...38b208b3`.
  Neither checkpoint is selected by this training result. It authorizes only
  preregistration of the unchanged half/final support gate and grants no robot
  clearance, deployment, X5/robot access, torque, or motion. See
  `outputs/analysis/WINNER_V52_FULL_ACTION_TEACHER_TRAINING_RESULT_20260722.md`.
- 2026-07-22: Winner-v53 preregisters exactly one unchanged `248`-cell CPU
  support gate over the verified V52 count-`403` and count-`453` artifacts.
  Each checkpoint must pass all `124` main cells, all `32` held-out repeats,
  all `16` held-out context-separation checks, and learned-predictor-versus-
  constant checks for both P30 and P31/34. The reviewed Winner-v12 physical
  evaluator, variable-configuration population, sensor/transport conditions,
  thresholds, seeds, and 250-tick duration are unchanged; the corrected base
  calibrator-design provenance is supplied explicitly. Selection by closest
  metric is forbidden. If and only if every check passes at both checkpoints,
  the fixed terminal endpoint at update `453` is selected; any hold selects
  nothing. Preregistration SHA-256: `c766c086...2b3d47e`. This gate is CPU-only
  and performs no optimizer updates, RDK-X5/robot access, serial/GPIO/I2C,
  torque, or motion. A pass may grant policy clearance only for a separately
  frozen, separately authorized suspended Gate 5 after runtime asset freeze
  and no-servo preflight. See
  `outputs/analysis/WINNER_V53_FULL_ACTION_TEACHER_SUPPORT_GATE_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v53 gate is a formal `HOLD`. The V52 half/final
  checkpoints pass `110/124` and `112/124` main cells, so the unchanged
  all-`248` rule fails and the preregistered fixed-endpoint rule selects no
  checkpoint. At both checkpoints every sensor/transport cell, all `32`
  held-out repeats, all `16` context-separation checks, both per-plant
  predictor-baseline checks, every previous-action chain, and every JAX/ONNX
  hidden comparison pass. All failures are early negative-pitch terminations
  in core variable-configuration cells across both P30 and P31/34; final fails
  the six IDs `COM_X_NEG`, `COM_CORNER_01`, `COM_CORNER_03`, `DISCOVERY_03`,
  `HELDOUT_04`, and `HELDOUT_09`. Current, torque, overcurrent, base height,
  contacts, finite values, ABI, and sensor transport do not set the hold.
  Result SHA-256: `6fb272a5...ab41579`. V53 is closed without a retry or
  threshold change. Robot clearance remains false; no asset freeze, runtime
  update, Gate 5, X5/robot access, torque, or motion is authorized. See
  `outputs/analysis/WINNER_V53_FULL_ACTION_TEACHER_SUPPORT_GATE_RESULT_20260722.md`.
- 2026-07-22: Winner-v54 preregisters one read-only residual-teacher causal
  diagnostic on the exact V52 final checkpoint and the exact `12` V53 final
  failures: six frozen configuration IDs across both P30 and P31/34. Four
  unchanged V48 intervention arms produce `48` cells: graph, full 14-D teacher,
  pitch teacher, and graph pitch with non-pitch outputs zeroed. Every graph cell
  must reproduce V53 bit-exactly before classification. Full-teacher failure
  means the table is insufficient; otherwise the two single interventions
  classify pitch output, non-pitch output, or their interaction. No arm,
  threshold, population, or classification rule may change post hoc.
  Preregistration SHA-256: `eeaca113...d1b2b24b`. This diagnostic performs no
  optimizer update, locomotion training, RDK-X5/robot access, torque, or motion
  and cannot select a checkpoint or grant clearance. See
  `outputs/analysis/WINNER_V54_RESIDUAL_TEACHER_CAUSAL_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v54 residual-teacher diagnostic passes all seven
  formal checks. All `12` unchanged graph cells reproduce Winner-v53
  bit-exactly and fail; the frozen full `14`-action teacher passes all `12`,
  the pitch-only teacher passes `11`, and zeroing non-pitch outputs passes none.
  The frozen classification is therefore `11` pitch-output-causal cells and
  one pitch/non-pitch interaction at
  `DISCOVERY_03 / P31_34_PITCH_WITH_P30_NONPITCH`; the teacher is sufficient
  in every cell. Candidate-versus-teacher RMS averages `0.08516398383512673`
  over pitch-chain actions and only `0.006177789539157603` over non-pitch
  actions. Result SHA-256: `74d2e7f2...a3de2680`. This selects an audit of
  early configuration identifiability before any new optimizer run; it does
  not authorize coefficient tuning, continuation, checkpoint selection,
  deployment, Gate 5, RDK-X5/robot access, torque, motion, or clearance. See
  `outputs/analysis/WINNER_V54_RESIDUAL_TEACHER_CAUSAL_RESULT_20260722.md`.
- 2026-07-22: Winner-v55 preregisters one read-only reset-label collision and
  delayed-teacher handoff diagnostic. The reset audit hashes the exact
  `115+14+64` float32 input and bounded privileged label over all `15` V42
  teacher configurations and both plants (`30` rows), with collision defined
  only by one exact input mapping to multiple exact labels. The handoff audit
  runs the six V54 failures across both plants at ticks
  `0/1/2/4/8/12/16/20/250` (`108` cells). Tick `0` must reproduce V54's full
  teacher and tick `250` its unchanged graph bit-exactly. If a collision exists,
  the greatest positive tick passing all `12` cells may select only a separate
  delayed-teacher mechanism CPU contract. Preregistration SHA-256:
  `1a37167f...ea72d66`. This executes no optimizer update, locomotion training,
  graph selection, RDK-X5/robot access, torque, or motion and cannot grant
  clearance. See
  `outputs/analysis/WINNER_V55_RESET_LABEL_HANDOFF_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v55 audit passes all seven checks and falsifies
  an exact raw-input reset collision: the `15` teacher configurations produce
  `15` distinct untransported float32 reset inputs, `15` graph actions, and
  four bounded teacher labels. Its handoff endpoints reproduce V54 bit-exactly,
  but only immediate teacher control passes `12/12`; first-teacher ticks
  `1/2/4/8/12/16/20/250` pass only `4/4/2/1/0/0/0/0`. One graph action is
  therefore causal to eight failures. Result SHA-256:
  `4ded36d4...3008ed0e`. The raw distinction is not yet a deployability claim:
  V55 did not apply the support gate's separately declared native sensor
  quantization, so that exact transport attribution must precede any training
  change. No optimizer update, checkpoint selection, deployment, Gate 5,
  RDK-X5/robot access, torque, motion, or clearance is authorized. See
  `outputs/analysis/WINNER_V55_RESET_LABEL_HANDOFF_RESULT_20260722.md`.
- 2026-07-22: Winner-v55b preregisters one zero-step, read-only native-reset
  quantization attribution. It reconstructs all `30` V55 reset rows, requires
  every raw observation hash to reproduce, then applies the support gate's
  already frozen BNO055 and servo quantization with no noise, delay, fitted
  threshold, or physics step. One exact quantized `115+14+64` input mapping to
  multiple bounded V42 labels is the sole collision rule. Preregistration
  SHA-256: `3944cc29...66921d2`. A conflict can select only a universal-first-
  action feasibility preregistration; preserved separability can select only a
  first-tick teacher-mapping CPU contract. No optimizer update, training,
  deployment, Gate 5, RDK-X5/robot access, torque, motion, or clearance is
  authorized. See
  `outputs/analysis/WINNER_V55B_NATIVE_RESET_QUANTIZATION_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v55b attribution passes all five checks. Every
  raw observation hash reproduces V55. Native sensor quantization changes
  `16` fields per row (maximum delta `0.004612922668457031`) but preserves all
  `15` reset inputs and all `15` graph actions; no quantized input maps to more
  than one of the four bounded teacher labels. Classification:
  `NATIVE_RESET_LABELS_REMAIN_SEPARABLE`. Result SHA-256:
  `303fee53...2ad78e99`. Combined with V55's one-tick handoff failure, this
  selects only a separately preregistered first-tick teacher-mapping CPU
  contract using training labels; held-out labels remain forbidden. It does
  not authorize an update, checkpoint selection, deployment, Gate 5,
  RDK-X5/robot access, torque, motion, or clearance. See
  `outputs/analysis/WINNER_V55B_NATIVE_RESET_QUANTIZATION_RESULT_20260722.md`.
- 2026-07-22: Winner-v56 preregisters one zero-update first-tick teacher
  gradient proof from the exact V52 final count-`453` snapshot. The batch is
  the `11` frozen training configurations x two plants x raw/native-quantized
  reset inputs (`44` rows, `616` full-action elements); held-out labels are
  forbidden. The loss receives the unchanged V52 full-action coefficient
  `136.35153198242188`, giving the complete critical reset map one objective-
  term weight without a scale search. With zero previous action and zero
  hidden input, only `obs_weight`, `hidden_bias`, `action_weight`, and
  `action_bias` may receive gradients. Contract SHA-256:
  `84774c59...7c0adca7`. This performs no simulator step, optimizer update,
  export, RDK-X5/robot access, torque, or motion. A pass can authorize only a
  separately preregistered single CPU Adam update, not training continuation,
  checkpoint selection, deployment, Gate 5, or clearance. See
  `outputs/analysis/WINNER_V56_FIRST_TICK_TEACHER_GRADIENT_CONTRACT_20260722.md`.
- 2026-07-22: The Winner-v56 zero-update proof passes all nine checks. Its
  `44` raw/native-quantized training rows and `616` full-action elements contain
  no held-out label. Reset loss is `0.004075534176081419`; pitch RMS is
  `0.0957130640745163` versus `0.01616910845041275` off-pitch, directly matching
  V54's causal localization. JAX/ONNX action error is at most
  `2.2351741790771484e-8`. At scale `136.35153198242188`, only the exact four
  mapping leaves `obs_weight/hidden_bias/action_weight/action_bias` have
  nonzero gradients; every recurrent, predictor, value, and distribution leaf
  is zero, and default-off is bit-exact. Result SHA-256:
  `6363c17a...9051c1a8`. This authorizes only preregistration of one CPU Adam
  update from count `453` to `454`; it does not authorize continuation,
  support evaluation, checkpoint selection, deployment, Gate 5, RDK-X5/robot
  access, torque, motion, or clearance. See
  `outputs/analysis/WINNER_V56_FIRST_TICK_TEACHER_GRADIENT_RESULT_20260722.md`.
- 2026-07-22: Winner-v57 preregisters exactly one isolated CPU Adam update from
  the V52 final optimizer count `453` to `454`. It must recompute the exact
  V56 `44`-row/`616`-element reset objective and scaled gradient, retain the
  complete inherited Adam moments, and reduce total, raw, and quantized reset
  losses. It performs no PPO rollout and makes no integrated-objective claim.
  The complete state must round-trip in one new snapshot, and one non-selected
  ONNX must preserve the stateful `115+14+64` ABI, bounds, action chain, and
  JAX agreement without privileged tokens. Contract SHA-256:
  `6dbdf0ab...804cf05`. No continuation, support cell, checkpoint selection,
  deployment, Gate 5, RDK-X5/robot access, torque, motion, or clearance is
  authorized. A pass can authorize only a separately preregistered integrated
  continuation. See
  `outputs/analysis/WINNER_V57_FIRST_TICK_TEACHER_ONE_UPDATE_CONTRACT_20260722.md`.
- 2026-07-22: The sole Winner-v57 update passes all `17` checks. It recomputes
  V56 exactly, retains the count-`453` Adam state, advances once to `454`, and
  changes all 12 trainable leaves while leaving the source state unchanged.
  Total/raw/quantized reset losses fall from
  `0.0040755342/0.0040754895/0.0040755789` to
  `0.0040571862/0.0040571410/0.0040572323`; pitch RMS falls from
  `0.0957130641` to `0.0955589563`. The complete snapshot restores exactly
  (SHA-256 `e111b81e...09e4f3c0`), and the non-selected stateful ONNX preserves
  ABI, bounds, action chain, and JAX agreement within `8.731149137020111e-11`
  (SHA-256 `3fdbac1f...27d64c8e`). Result SHA-256:
  `66c075dd...b63351d2`. This authorizes only a separately preregistered
  integrated continuation with the unchanged baseline objectives. It does not
  authorize support evaluation, checkpoint selection, deployment, Gate 5,
  RDK-X5/robot access, torque, motion, or clearance. See
  `outputs/analysis/WINNER_V57_FIRST_TICK_TEACHER_ONE_UPDATE_RESULT_20260722.md`.
- 2026-07-22: Winner-v58 preregisters the sole integrated `100`-update CPU
  continuation from the exact V57 count-`454` state to half/final counts
  `504/554`. It retains the unchanged V52 PPO, normalized-predictor, prefix-
  anchor, and full-horizon full-action-teacher objectives, and adds only the
  V56/V57 first-tick reset term over the frozen `44` raw/native rows and `616`
  action elements at scale `136.35153198242188`. No attention, flat-transport
  equation, ABI change, coefficient search, support evaluation, or checkpoint
  selection is included. Preregistration SHA-256:
  `28dc79f2...ac6fd9a`. A passing training artifact may authorize only a
  separately preregistered unchanged half/final support gate; it cannot grant
  deployment, Gate 5, RDK-X5/robot access, torque, motion, or clearance. See
  `outputs/analysis/WINNER_V58_INTEGRATED_FIRST_TICK_TRAINING_PREREGISTRATION_20260722.md`.
- 2026-07-22: The sole Winner-v58 run committed `22` atomic snapshots through
  optimizer count `476`, then stopped before the count-`477` Adam step because
  the inherited pre-update replay/teacher guard changed. No result, half/final
  graph, support cell, retry, hardware access, or clearance was produced. The
  count-`476` snapshot is SHA-256 `9835cbf0...b03bb54` and the exact stderr is
  retained outside Git. Winner-v58a preregisters one zero-update reconstruction
  of rollout index `476` that reports all `15` original guard predicates and
  their raw values. Preregistration SHA-256: `b738ee35...90696a7`. It can
  authorize only a separate retry preregistration when the sole failure is a
  changed nonzero set among the four already allowed first-tick mapping leaves
  while every forbidden gradient remains zero and all values remain finite.
  It does not authorize a retry, training update, support evaluation,
  checkpoint selection, deployment, Gate 5, RDK-X5/robot access, torque,
  motion, or clearance. See
  `outputs/analysis/WINNER_V58A_GUARD_FAILURE_ATTRIBUTION_PREREGISTRATION_20260722.md`.
- 2026-07-22: Winner-v58a executed zero rollouts and zero optimizer updates: it
  failed during source-snapshot validation because its transformed validator
  referenced a nonexistent `source_result["teacher"]` key. It created neither
  output nor work root. Winner-v58b corrects only that validation expression by
  comparing the snapshot metadata to the already frozen teacher snapshot hash
  `ddc8c4b9...bc48c806`; its rollout, reported predicates, zero-update boundary,
  and authority are otherwise unchanged. Preregistration SHA-256:
  `a7654ff5...ebb6d36`. It does not authorize retry, training, support
  evaluation, deployment, Gate 5, RDK-X5/robot access, torque, motion, or
  clearance. See
  `outputs/analysis/WINNER_V58B_GUARD_FAILURE_ATTRIBUTION_PREREGISTRATION_20260722.md`.
- 2026-07-22: Winner-v58b passes its zero-update attribution. The sole failed
  original predicate at rollout index `476` is hidden replay
  `1.1250376701355e-6 > 1.0e-6`; every other one of the `15` replay, predictor,
  teacher, anchor, and first-tick predicates passes. All four allowed first-
  tick mapping gradients remain nonzero, all forbidden leaves remain exactly
  zero, every value is finite, and optimizer count remains `476`. Result
  SHA-256: `2070bcca...e91d3c3`. This closes a blind Winner-v58 retry. It does
  not prove the hidden discrepancy harmless and does not authorize another
  optimizer update, support evaluation, checkpoint selection, deployment,
  Gate 5, RDK-X5/robot access, torque, motion, or clearance. See
  `outputs/analysis/WINNER_V58B_GUARD_FAILURE_ATTRIBUTION_RESULT_20260722.md`.
- 2026-07-22: Winner-v59 preregisters one zero-update CPU reconstruction of
  rollout index `476` to distinguish execution-path arithmetic from a changed
  recurrent policy. It compares the stored eager hidden trajectory with an
  eager replay and `jax.lax.scan`, then bounds the scan-induced action, value,
  log-probability, probability-ratio, and PPO-loss deltas. The hidden bound is
  fixed at `2e-6`, the next power-of-two bound above the observed
  `1.1250377e-6`; all downstream tolerances were frozen before execution.
  Preregistration SHA-256: `5f477d20...71eb1c2`. It performs no Adam update,
  support evaluation, checkpoint selection, deployment, Gate 5, RDK-X5/robot
  access, torque, motion, or clearance. A pass can authorize only a separately
  preregistered continuation with the exact numeric replay guard. See
  `outputs/analysis/WINNER_V59_HIDDEN_REPLAY_NUMERIC_ATTRIBUTION_PREREGISTRATION_20260722.md`.
- 2026-07-22: Winner-v59 passes all `12` zero-update numeric checks. Replaying
  the rollout through the original eager recurrence is bit-exact; only
  eager-versus-`jax.lax.scan` float32 ordering differs, with hidden maximum
  `1.125037670135498e-6`. Its maximum mean-action/value/log-probability/ratio
  deltas are `1.4901161e-7 / 1.1920929e-6 / 1.1444092e-5 / 1.1444092e-5`,
  and PPO-loss delta is exact zero. Result SHA-256:
  `2bc02511...c946c39b`. This authorizes only a separately preregistered new
  continuation with the exact `2e-6` replay guard; it does not authorize a
  Winner-v58 retry, support evaluation, checkpoint selection, deployment,
  Gate 5, RDK-X5/robot access, torque, motion, or clearance. See
  `outputs/analysis/WINNER_V59_HIDDEN_REPLAY_NUMERIC_ATTRIBUTION_RESULT_20260722.md`.
- 2026-07-22: Winner-v60 preregisters one new complete `100`-update CPU arm
  from the immutable V57 optimizer count `454`, with half/final counts
  `504/554`. A source diff proves that the only executable change from
  Winner-v58 is the V59-selected hidden-replay numeric guard
  `1e-6 -> 2e-6` plus contract/result names and guard validation. All PPO,
  predictor, prefix-anchor, full-action-teacher, and first-tick objectives,
  coefficients, population, seeds, ABI, and checkpoint schedule are unchanged.
  Preregistration SHA-256: `15db0395...8bf6860c`. No attention or flat-
  transport mechanism is added. A pass authorizes only a separately
  preregistered unchanged half/final support gate; it does not authorize
  deployment, Gate 5, RDK-X5/robot access, torque, motion, or clearance. See
  `outputs/analysis/WINNER_V60_INTEGRATED_NUMERIC_GUARD_TRAINING_PREREGISTRATION_20260722.md`.
- 2026-07-22: Winner-v60 completes all `100` CPU updates from count `454` to
  `554` with `100` digest-readback snapshots and all `23` artifact checks
  passing. The maximum hidden replay error is `1.6093254e-6 < 2e-6`; all 12
  trainable leaves change and every teacher, mask, boundary, finite-state, and
  locality invariant holds. Half/final ONNX SHA-256 values are
  `37e483f...7af0a02` / `4a6386d8...9ac3939`; both preserve the stateful ABI,
  bounds, exact action chain, and JAX agreement. Result SHA-256:
  `50622331...f6b8b57`. Neither checkpoint is selected. This authorizes only a
  separately preregistered unchanged half/final offline support gate, not
  deployment, Gate 5, RDK-X5/robot access, torque, motion, or clearance. See
  `outputs/analysis/WINNER_V60_INTEGRATED_NUMERIC_GUARD_TRAINING_RESULT_20260722.md`.
- 2026-07-22: Winner-v61 binds the exact Winner-v60 count-`504/554`
  snapshots and graphs to the unchanged reviewed Winner-v12 offline support
  gate: `124` main cells plus `32` heldout repeats per checkpoint, identical
  thresholds, seeds, P30/P31-34 plants, sensor/transport/context checks, and an
  all-or-nothing persistence rule. Preregistration SHA-256:
  `a52b2878...8bacbf6a`. A hold selects nothing; a complete two-checkpoint pass
  selects the fixed final count-`554` endpoint, never the closest metric. No
  optimizer update, locomotion training, robot/RDK access, torque, or motion is
  authorized. See
  `outputs/analysis/WINNER_V61_INTEGRATED_SUPPORT_GATE_PREREGISTRATION_20260722.md`.
- 2026-07-22: Winner-v61 executes the complete `248` main cells and `64`
  heldout repeats. Half/final fail `11/13` main cells, exclusively on the
  unchanged roll/pitch predicate; action chains, JAX/ONNX agreement,
  repeatability, context separation, predictor advantage, contacts, height,
  current, torque, and finite-state checks all pass. Result SHA-256:
  `a238ea45...a5257255`. The fixed all-or-nothing persistence rule selects no
  checkpoint, closes Winner-v60 as a deployment candidate, and leaves
  `robot_clearance: false`. No retry, deployment, Gate 5, RDK-X5/robot access,
  torque, or motion is authorized. See
  `outputs/analysis/WINNER_V61_INTEGRATED_SUPPORT_GATE_RESULT_20260722.md`.
- 2026-07-22: Winner-v62 preregisters one read-only CPU replay of the exact
  `13` Winner-v61 final failed configuration/plant pairs under the unchanged
  graph, full-teacher, pitch-teacher, and nonpitch-zero interventions (`52`
  cells total). It reports tick-zero and post-tick-zero pitch alignment
  separately and freezes the prior V48/V54 causal classification. Contract
  SHA-256: `d6415fa2...ba209f08`. It performs no optimizer update, locomotion
  training, robot/RDK access, torque, or motion. A valid result can authorize
  only a separately preregistered mechanism selected from the fixed causal
  classes. See
  `outputs/analysis/WINNER_V62_RESIDUAL_TEACHER_CAUSAL_PREREGISTRATION_20260722.md`.
- 2026-07-22: Winner-v62 passes all `8` causal checks over the exact `52`
  cells. Full-teacher intervention stabilizes `13/13`; pitch-only stabilizes
  `12/13`; nonpitch-zero stabilizes `0/13`. The fixed classification is `12`
  pitch-output-causal and one pitch/nonpitch interaction. Mean pitch mismatch
  is `0.0772829` rad RMS at tick zero and `0.0817888` after tick zero, proving
  the Winner-v60 hold is a persistent pre-fall pitch-control mismatch rather
  than a reset-only defect. Result SHA-256: `2da0c48a...235251f5`. This selects
  only a separately preregistered persistent-prefix mechanism; it authorizes no
  training, deployment, Gate 5, RDK-X5/robot access, torque, or motion. See
  `outputs/analysis/WINNER_V62_RESIDUAL_TEACHER_CAUSAL_RESULT_20260722.md`.
- 2026-07-22: Winner-v63 preregisters one zero-commit CPU attribution from the
  exact Winner-v60 final count-`554` state. It reconstructs the unchanged
  `80`-episode rollout at update index `554`, separates the scaled PPO,
  predictor, prefix-anchor, full-action persistent-teacher, and first-tick
  teacher gradients, and reports float64 alignment over the policy,
  recurrent-core, and action-head leaves. Two Adam steps are evaluated only in
  memory from the same inherited moments: one integrated and one teacher-only;
  neither state is written. The frozen classification distinguishes objective
  opposition, inherited-moment opposition, and a remaining teacher-trajectory
  distribution mismatch before selecting any new mechanism. Preregistration
  SHA-256: `c60abbd0...294fbc07`. It adds no attention or flat-transport
  equation and authorizes no committed update, support gate, deployment,
  Gate 5, RDK-X5/robot access, torque, motion, or clearance. See
  `outputs/analysis/WINNER_V63_PERSISTENT_TEACHER_CONFLICT_PREREGISTRATION_20260722.md`.
- 2026-07-22: The first Winner-v63 invocation stopped before constructing its
  rollout because it passed the exact count-`554` NPZ through the reviewed
  support-gate loader, which deliberately validates and then converts the
  snapshot to gate predictor coordinates and rewrites its stage to `stage2`.
  No rollout episode, counterfactual step, result, update, support cell, or
  robot access occurred. Winner-v63b freezes one source-fragment correction:
  load the immutable training-coordinate NPZ directly and apply the existing
  exact integrated-stage validator. Every objective, population, seed,
  gradient, Adam, classification, and authority rule remains byte-identical.
  Correction contract SHA-256: `45586f8d...3a024944`. The original V63 runner
  remains unmodified. See
  `outputs/analysis/WINNER_V63B_TRAINING_SNAPSHOT_LOADER_CORRECTION_20260722.md`.
- 2026-07-22: The corrected Winner-v63b attribution passes every frozen check
  on the exact count-`554` update-index-`554` rollout. The full persistent-
  teacher loss is `0.0034021961`. One counterfactual integrated step raises it
  to `0.0034065784`, while the same teacher gradient isolated through the same
  inherited Adam state lowers it to `0.0033936996`. The other objectives have
  teacher-gradient dot product `-85.6093`; even the total integrated gradient
  remains opposed at `-19.1884`. The action head carries the conflict while
  recurrent-core terms are aligned. Classification:
  `INTEGRATED_STEP_BLOCKS_PERSISTENT_TEACHER_DESCENT`. Result SHA-256:
  `5e9b44fd...094225fb`. This selects only a separately preregistered isolated
  persistent-teacher Adam-step proof. It does not select attention, coefficient
  tuning, a checkpoint, deployment, Gate 5, RDK-X5/robot access, torque,
  motion, or clearance. See
  `outputs/analysis/WINNER_V63B_PERSISTENT_TEACHER_CONFLICT_RESULT_20260722.md`.
- 2026-07-22: Winner-v64 preregisters exactly one isolated persistent-teacher
  Adam step from the immutable Winner-v60 final optimizer count `554` to
  `555`. It recomputes the exact update-index-`554` rollout and full-14D
  teacher gradient at scale `136.35153198242188`, retains the inherited Adam
  state, and excludes the measured-opposing PPO, predictor, prefix-anchor, and
  first-tick gradients. The frozen same-batch expectation is
  `0.0034021961 -> 0.0033936996`; there is no coefficient search. A complete
  snapshot and one non-selected stateful ONNX must round-trip with the
  `115+14+64` ABI and action chain. Contract SHA-256:
  `611c38f2...5a88ff40`. It authorizes one update only, with zero continuation,
  support cells, deployment selection, Gate 5, RDK-X5/robot access, torque,
  motion, or clearance. See
  `outputs/analysis/WINNER_V64_ISOLATED_PERSISTENT_TEACHER_STEP_CONTRACT_20260722.md`.
- 2026-07-22: The first Winner-v64 invocation reconstructed the frozen rollout
  and in-memory update, exported one non-selected graph, then stopped before
  snapshot or result persistence because the injected metadata block referred
  to `contract` while the validated base-runner local is `preregistration`.
  The partial graph is retained and hashed; no snapshot, result, support cell,
  or robot access occurred. Winner-v64b freezes one contiguous two-reference
  local-name correction. It changes no objective, rollout, gradient, Adam
  state, artifact schema, classification, or authority. Correction contract
  SHA-256: `7da49db3...f9d2af1a`. The original V64 transformed source remains
  frozen. See
  `outputs/analysis/WINNER_V64B_PREREGISTRATION_NAME_CORRECTION_20260722.md`.
- 2026-07-22: Winner-v64b passes the isolated persistent-teacher one-step
  proof from optimizer count `554` to `555`. The exact frozen loss reproduces
  and falls `0.0034021961 -> 0.0033936996`; all 12 trainable leaves change and
  all parameters, moments, losses, and metrics remain finite. The complete
  snapshot round-trips at SHA-256 `4ed0d458...ad1f0e9`; the non-selected
  stateful ONNX is `f6e341e2...ae45b80`, preserves the `115+14+64` ABI and
  exact previous-action chain, and agrees with JAX within `5.82e-11`. Result
  SHA-256: `03e83022...ca896800`. This authorizes only preregistration of a
  bounded isolated-teacher continuation. No continuation, support cell,
  checkpoint selection, deployment, Gate 5, RDK-X5/robot access, torque,
  motion, or clearance has occurred. See
  `outputs/analysis/WINNER_V64B_ISOLATED_PERSISTENT_TEACHER_STEP_RESULT_20260722.md`.
- 2026-07-22: Winner-v65 preregisters one bounded `100`-update isolated
  persistent-teacher continuation from optimizer count `555`, with unselected
  half/final endpoints at `605/655`. Each update uses the exact `80 x 250`
  on-policy rollout and the full-14D teacher at scale `136.35153198242188`.
  PPO, normalized predictor, prefix anchor, and first-tick teacher are computed
  only as invariance monitors and contribute exactly zero to the update.
  Every update must strictly lower its own frozen same-batch teacher loss;
  every state is atomically snapshotted. Contract SHA-256:
  `74b6f8a4...7294dbb1`. No attention, flat-transport equation, coefficient or
  length search, support evaluation, checkpoint selection, deployment,
  Gate 5, RDK-X5/robot access, torque, motion, or clearance is included. See
  `outputs/analysis/WINNER_V65_ISOLATED_PERSISTENT_TEACHER_TRAINING_PREREGISTRATION_20260722.md`.
