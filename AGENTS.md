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
