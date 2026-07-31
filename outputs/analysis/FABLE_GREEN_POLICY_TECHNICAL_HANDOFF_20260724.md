# Fable technical handoff: Open Duck Mini green-policy blocker

Date: 2026-07-24

Status: paused for external review. No Colab session is active, no robot or
RDK-X5 access is authorized by this handoff, and Gate 5 is closed.

## The question we need answered

We have a deterministic, measured RDK-X5 runtime and a simulated policy that
walks stably, tracks well, stays inside the measured target-rate envelopes, and
holds home at zero command. The remaining nominal failure is an instantaneous
physical motor limit:

- peak current must be at most 2.5 A;
- peak torque must be at most 1.91229675 N.m (19.5 kg.cm);
- a strict-current excursion above 2.0 A may not last more than 99 ticks;
- both independently trained post-update checkpoints must pass every cell;
- no checkpoint cherry-picking, reward-curve selection, threshold relaxation,
  or robot trial may be used to choose a policy.

Recent reward-based attempts made the torque/current problem worse while
preserving gait and tracking. We need a distinct mechanism that makes the hard
physical constraint compatible with the policy, actuator bridge, and deployed
runtime. We specifically want Fable to decide whether the right next step is a
torque-aware action projection, constrained optimization, a change to the
training credit path, or another mechanism. We do not want another speculative
reward scalar.

## What is already working

### The X5-native runtime

The original RDK-X5 software was a Pi-derived Python/rustypot/pypot stack. The
measured original signature was:

- read failures: 1.07% at command x=0.0 and 2.68% at x=0.08 with bursts;
- tick maximum: 26 ms against a 20 ms period;
- a retry/error-handling patch later reported zero errors, but the robot still
  behaved strangely.

That established the governing diagnosis: an empty error counter was not the
success metric; deterministic loop timing was.

The replacement runtime was built directly for the X5. It uses:

- direct Feetech STS3215 packets;
- one all-14 SyncWrite and one fixed-frame all-14 SyncRead per tick;
- the empirically required read order
  `20,21,22,23,24,30,31,32,33,10,11,12,14,13`;
- direct UART `/dev/ttyS1` at 1 Mbit/s rather than the USB bridge;
- Python under `SCHED_FIFO 80` on isolated CPU 7;
- bounded ring-buffer telemetry flushed outside the hot loop;
- round-robin current, voltage, and temperature telemetry;
- explicit timeout/CRC/partial/unexpected-ID error classes;
- stale-sample rejection rather than silent reuse;
- torque-off on every exit/crash/watchdog path.

Hardware Gates 1-4 are reviewed green:

1. Gate 1, single-servo torque-off, 10,000 reads: zero failures/bursts, tick
   p99 20.083874 ms, tick p99.9 20.090855 ms.
2. Gate 2, all-14 torque-off preflight plus home hold, 10,000 ticks per stage:
   zero failures/bursts; home-hold tick p99 20.002683 ms, p99.9 20.008892 ms;
   complete-sweep max 4.721847 ms; worst joint tracking p95 0.005516521 rad.
3. Gate 3, BNO055 plus contacts: all nine physically labeled populations
   passed, with fresh timestamps and exact dedicated contact states.
4. Gate 4, 0.03-rad left-hip-yaw sine sweeps: tracking p95 0.006940 rad at
   0.25 Hz and 0.009892 rad at 0.5 Hz; zero transport failures and timing
   remained green.

Therefore the runtime is not the current blocker. Gate 5 is blocked only
because no new policy has passed every frozen offline gate.

## Frozen interfaces and policy structure

### Runtime contract

The runtime contract is frozen:

- 101 observations;
- 14 actions;
- ONNX Runtime;
- 50 Hz / 20 ms;
- action scale 0.25 rad;
- fixed home pose, joint order, servo IDs, offsets, IMU mapping, contact
  polarity, and phase timing.

The canonical 101 observation is:

| Slice | Meaning |
| --- | --- |
| `0:3` | gyro |
| `3:6` | accelerometer |
| `6:13` | command |
| `13:27` | joint position error |
| `27:41` | joint velocity times 0.05 |
| `41:83` | three-action history |
| `83:97` | previous/applied motor target slot |
| `97:99` | foot contacts |
| `99:101` | phase |

### Current training/export ABI

The current policy is a stateful reference-residual recurrent actor:

```text
inputs:
  obs[1,115]
  previous_action[1,14]
  h_in[1,64]

outputs:
  continuous_actions[1,14]
  previous_action_out[1,14]
  h_out[1,64]
```

The 115-vector is the canonical 101-vector plus a deterministic 14-value
projected-reference feature. It is not an unrelated new observation contract.
The eventual RDK bridge must construct the same 115 values from the frozen
runtime 101-vector and the frozen reference table.

The policy/action path is:

```text
reference-residual recurrent actor
  -> hard per-joint train-time target-rate projection
  -> actual-position-centered pitch-chain guard
  -> x=0 deadband/home branch
  -> exact previous-action-centered final rate projection
  -> measured delay/tau/gain actuator bridge
  -> MuJoCo position actuator
  -> physics
```

The final bounded action is fed back as `previous_action_out`. The actuator
bridge's applied target is exposed to the policy in the applied-target slot so
the actor is not blind to the bridge state.

One deployment issue remains to be resolved even after an offline winner:
training's `obs[83:97]` is the bridge-applied target, while the hardware
runtime describes this slot as the post-slew commanded motor target. Those are
equivalent only if “applied target” means the post-limit command, not the
bridge's delayed realized target. The golden-vector bridge must prove the
definition, not assume it.

### Current exact rate limits

The current all-joint limits in rad/s are:

```text
[1.0, 0.75, 1.4736209, 1.4300791, 1.3976470,
 0.5, 0.5, 0.5, 0.5,
 0.5, 0.75, 1.25, 1.0, 1.2215288]
```

These are applied identically at training and deployment. The left-ankle
limit was previously reduced from 1.75 to 1.50 rad/s for the conservative
cross-fit gate, and the trained transition later learned a still more
conservative effective limit.

## Frozen nominal gate

Every new trained arm must export at:

- 1,003,520 steps (“half”);
- 2,007,040 steps (“final”).

Both exports must pass the same 16 CPU-only, 600-tick cells:

```text
2 checkpoints
x 2 measured actuator fits: P30 and P31/34 pitch with P30 non-pitch
x 4 commands: x=0.000, 0.074, 0.077, 0.080 m/s
= 16 cells
```

The gate includes:

- duration-complete upright walking for moving commands;
- bilateral contact transitions;
- x=0 exact home hold;
- pitch-chain tracking p95 at most 0.20 rad;
- zero action saturation;
- zero measured rate-envelope excess;
- peak current at most 2.5 A;
- peak torque at most 1.91229675 N.m;
- no strict >2.0 A run longer than 99 ticks.

Passing only one checkpoint is a failure. Passing nominal only authorizes a
separately preregistered full robustness matrix; it does not authorize Gate 5
or the robot.

## Major policy directions already tried and closed

### Early architecture and reward work

The project did not jump directly to the present policy. It closed many
plausible directions under frozen gates:

- learning-rate, entropy, imitation-scale, discount, and unroll searches did
  not produce persistent gait;
- an upstream actor, reference-conditioned actor, phase mixture-of-experts,
  recurrent mechanism, and symmetric critic did not pass the structural
  advancement screen;
- the original training bootstrap used full randomization, delays, noise, and
  pushes from update one, plus a bad zero-norm phase/reset condition;
- correcting nominal phase/reset and curriculum sequencing alone still failed;
- signed-progress and progress-conditioned-survival rewards did not create a
  persistent winner;
- direct reference execution was not a valid cloning label;
- oracle shooting produced propulsion but exploited it, overshot velocity,
  saturated, or fell;
- lexicographic viability removed the propulsion exploit but did not create a
  teacher;
- a bad randomized reset created unsupported no-contact states; constraining
  evaluation to physically representative home reset removed that false
  blocker but did not solve gait quality by itself.

### Contract and observability corrections that did matter

Several real defects were found and fixed:

- the command table lacked a zero lateral/yaw cell, so exact command
  `[.074,0,0]` aliased to `[.074,-.037,-.074]`;
- fixed-command training made x=.080 appear roughly 6,000 standard deviations
  from x=.074, saturating the actor; training now samples x=.074-.080;
- world-X displacement was replaced by body-frame forward displacement;
- reset evaluation was corrected from randomized unsupported states to the
  preregistered deterministic home state;
- the measured 2-3 tick actuator delay/lag bridge was integrated;
- `obs[83:97]` was changed from a redundant sent-target value to the
  bridge-applied target, resolving the observation-blindness class in sim;
- stateful ONNX exports now carry exact hard action bounds and recurrent state.

These changes created stable walking, but full-horizon tracking initially
failed. A 54-tick pass was invalidated when the gate was extended to all 600
ticks.

### Tracking-tail and temporal-credit work

The following did not pass persistence:

- mean and squared pitch-chain tracking objectives;
- three exact tail-exceedance scales;
- stateful pitch-rate boundary variants;
- smooth temporal-occupancy surrogates;
- actor-only cumulative averaging;
- feedforward bridge-only continuation;
- applied-target continuation.

Trace decomposition showed the tracking failures were compound:
sub-threshold bridge error and servo error aligned in sign and summed above the
0.20-rad gate. An actual-position-centered guard repaired that exact
mechanism.

### First strong gait and robustness result

`G1/T2 + x=0 repair` became the first persistent nominal gait winner under the
then-current gate:

- all moving cells walked with bilateral transitions;
- tracking worst case was about 0.18167 rad;
- x=0 held home after an exact command deadband wrapper;
- rate excess and saturation were zero.

The first measured-actuator robustness stage exposed one left-ankle rate
violation. A single conservative change repaired it, and both measured
actuator fits passed. Subsequent isolated floor-friction and joint-friction
conditions also passed.

This was still not robot clearance. A later manufacturer-backed physical
current/torque gate exposed instantaneous load peaks that older p95-current
criteria had not rejected.

## Recent current/torque sequence

The latest sequence deliberately used no checkpoint cherry-picking and no
reward-curve selection.

### V109/V110: recurrent source and G3 repair

- V109 nominal: 4/16 pass; tracking remained good, but peak current reached
  2.91479 A.
- V110 G3-repaired nominal: 4/16 pass; worst current 2.82943 A and torque
  2.21978 N.m.

This showed that stable behavior plus an actual-centered tracking guard did
not itself enforce the manufacturer peak limit.

### V112/V113: squared peak-torque hinge

The objective was a mean squared all-joint hinge above 1.91229675 N.m, scale
`-1000`, with the existing tracking-tail objective. CPU restore/update/export
contracts passed before hosted training.

V113 nominal passed 5/16:

- worst torque 2.06485 N.m;
- worst current 2.63195 A;
- worst tracking p95 0.15078 rad.

It improved physical peaks somewhat but did not pass persistence.

### V114/V115: linear peak-torque hinge

The squared hinge was replaced by:

```text
mean_j(max(abs(torque_j) - 1.91229675, 0))
```

The scale `-307.48131091308585` was derived once from frozen source statistics;
there was no scalar search.

V115 nominal passed 9/16:

- worst torque 2.05234 N.m;
- worst current 2.61600 A;
- worst tracking p95 0.15029 rad.

This was better, but still not green.

### V117/V118: post-guard rate projections

No training credit was used. Exact ONNX transforms tested whether the residual
peaks were caused by the order of the G3 guard and the final rate projection.

- V117 passed 11/16; worst torque 1.98338 N.m, current 2.52810 A.
- V118 passed 10/16; worst torque 2.01314 N.m, current 2.56604 A.

V117 was the better causal result but still failed both-checkpoint persistence.

### V119/V121: train the deployment transition itself

Training was changed so the environment used the same hierarchy as deployment:
actual-centered guard followed by the exact final rate projection. Both
post-update checkpoints were then wrapped with the identical x=0 deadband and
final feedback contract.

V121 passed 11/16:

- half checkpoint: 8/8 pass;
- final checkpoint: 3/8 pass;
- worst tracking p95 0.148289 rad;
- worst torque 2.098969 N.m;
- worst current 2.675440 A.

The final checkpoint had only 15 torque-exceedance events across the complete
matrix: 13 left-knee events in ticks 0-31 and two later right-ankle events.
There were no simultaneous multi-joint events. Only three were within two
ticks of a target-rate boundary.

That evidence selected an episode-global peak objective rather than another
rate clamp.

### V122/V123: exact episode-global peak objective

The new cost was:

```text
e_t = max(0, max_j(abs(torque_tj)) - 1.91229675)
m_t = max(m_(t-1), e_t), m_reset = 0
cost_t = (m_t - m_(t-1)) / 0.02
```

Its episode integral is mathematically exact:

```text
sum_t cost_t * 0.02
  = max_t,j max(0, abs(torque_tj) - 1.91229675)
```

The CPU contract proved exact restore, finite update, all 15 policy leaves
changing, exact step-0 and step-1024 exports, and exact default-off behavior.
One hosted run then produced both frozen checkpoints; no retry or resume was
used.

V123 decisively failed:

- only 4/16 pass, exactly the four x=0 holds;
- half checkpoint 2/8, final checkpoint 2/8;
- all 12 moving cells failed the torque gate;
- 11/12 moving cells also failed peak current;
- worst torque 2.246964 N.m;
- worst current 2.864083 A;
- worst tracking p95 remained excellent at 0.148293 rad;
- minimum moving mean forward velocity remained healthy at 0.105310 m/s;
- saturation and rate excess remained zero.

The torque failures expanded from V121's 15 events to V123's 184 events:

```text
left knee:   148
left ankle:   13
right knee:    5
right ankle:  18
```

Only five of those events were in ticks 0-31. The objective did not merely
miss the old startup spike; it redistributed load into repeated gait-cycle
peaks. This exact episode-peak formulation is closed. Repeating it, changing
its scalar, or selecting one checkpoint is not allowed.

Training also uses a nonnegative-clipped per-step reward:

```text
reward = clip(sum(scaled_reward_terms) * 0.02, 0, 10000)
```

A new peak increment can therefore zero a step's reward, but sufficiently
large peak increments do not remain proportional after clipping. Combined
with the one-time running-maximum increment, that creates sparse,
high-variance credit. This is a plausible explanation, not yet a proven sole
cause. The hosted training KL was also large (about 3.33-3.99), but training
metrics are not used for policy selection.

## Important preliminary mechanics clue

The deployed G3 actual-centered pitch guard uses a `0.165 rad` margin. The
nominal MuJoCo position-actuator gain is `kp=13.37`, so the static ratio

```text
1.91229675 / 13.37 = 0.14302893 rad
```

is smaller than the guard margin. This means the guard was designed to repair
tracking accumulation, not to guarantee the torque limit.

However, simply changing `0.165` to `0.143` is not yet justified:

- in V123, 149/184 torque events had sent-target/actual error above 0.143 rad,
  but 35/184 did not;
- the measured actuator bridge can leave the applied target behind the sent
  target;
- among high-load samples, applied-vs-sent lag had roughly 0.061 rad p95 and
  reached about 0.092 rad in the inspected V123 nominal traces;
- therefore a sent-target-centered static guard is not an exact applied-force
  constraint.

This suggests that the hard constraint may need to operate on the predicted
next bridge-applied target/force, not merely the raw or sent target. Any such
mechanism must still be implementable from deployed observations and must not
silently assume sim-only bridge state.

## The long-range transport equation

The proposed equation

```text
K_n,L = rho^L I_n + q(1-rho^L) C_n
```

with the final row of `C_n` equal to `(1/n,...,1/n)` has not been used in the
current policy. It is mathematically interesting for flat long-range
information transport without quadratic attention, but the current evidence
does not identify attention or long-context transport as the active blocker:

- a 64-state recurrent actor is already present;
- the important actuator state was made directly observable;
- the policy walks and tracks for the full 600 ticks;
- the only nominal failure is the instantaneous physical load envelope.

Fable should use the equation only if it can connect it to a specific missing
state-estimation or credit-assignment mechanism. “Use a different sequence
model” by itself would not explain the current torque peaks.

## Constraints on any proposed solution

A valid recommendation must respect all of these:

1. Do not change the frozen 101-observation runtime contract or 14-action
   semantics merely to make training easier.
2. If the policy ABI stays at 115, the extra 14 values must remain a
   deterministic runtime-computable projection appended to the canonical 101.
3. Both post-update checkpoints must pass; no cherry-picking.
4. Training reward and visual preference have zero selection weight.
5. No threshold relaxation: 2.5 A and 1.91229675 N.m remain frozen.
6. No scalar sweep or retry of a closed formulation.
7. Every hosted training run must first pass a hash-frozen CPU
   restore/update/export/mechanics contract.
8. Prefer a zero-credit causal screen or exact transform before training when
   it can falsify the mechanism.
9. A stale servo/sensor sample invalidates a runtime tick; it is never reused.
10. No policy reaches the robot until nominal and the entire frozen robustness
    matrix pass.

## Questions for Fable

Please answer concretely and rank the options.

1. Is the correct formulation a hard torque-aware projection on the predicted
   bridge-applied target/force, rather than another reward penalty?
2. If so, what is the minimal causal state and equation for a projection that
   is robust to both P30 and P31/34 delay/tau fits and can be reproduced on the
   RDK from its actual observations?
3. Can that projection be embedded in ONNX while preserving final-action
   recurrent feedback, x=0 exactness, action order, scale, and rate limits?
4. Would a one-step robust/QP projection create a worse hidden-state mismatch
   because the actor's recurrent state was trained on unprojected actions?
   If yes, what exact feedback signal must be returned?
5. Is the reward clipping plus running-maximum increment the likely reason the
   episode-peak objective redistributed rather than reduced load? What
   falsification test can prove or reject that without a hosted run?
6. Would a cost-constrained PPO/Lagrangian with a separate undiscounted
   episode-peak cost critic be materially different from the squared and
   linear hinge objectives already closed, or would it repeat the same credit
   problem?
7. Can we construct a projected teacher from the already walking V121 half
   policy, then distill/continue the actor on exact torque-safe actions, without
   relying on simulator reward for selection?
8. How should the train-time bridge-applied target in `obs[83:97]` be reconciled
   with the RDK's post-slew commanded-target slot so the solution does not
   recreate the observation-blindness bug?
9. What is the cheapest ordered sequence of CPU-only tests that would
   distinguish these hypotheses before any new Colab credit is spent?
10. Give a preregisterable stop rule for the next mechanism: exact inputs,
    outputs, invariants, falsifier, and the evidence required before one hosted
    run is earned.

## Requested form of response

Please do not suggest general reward tuning, a broad hyperparameter search, a
larger model, or testing on the robot. Provide:

1. a causal diagnosis tied to the numbers above;
2. one primary mechanism and at most one fallback;
3. equations/pseudocode for the mechanism;
4. a CPU-only falsification plan;
5. deployment-state requirements;
6. conditions under which no new training run should be made;
7. conditions under which exactly one hosted run would be earned.
