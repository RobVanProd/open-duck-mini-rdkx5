# Open Duck Mini RDK-X5 Sim-To-Real Bridge

## Mission

Turn this repository into a safe, repeatable sim-to-real diagnostic and
bridging pipeline for the Open Duck Mini running `BEST_WALK_ONNX_2` on the
RDK-X5, then use the measured bridge to produce and validate a replacement
candidate policy.

The initial mission was to prove the deployed robot's sensor observations,
policy actions, joint commands, and real joint movement matched the policy and
simulation contract closely enough to rerun the known baseline responsibly.
That evidence has now shifted the project into an offline root-cause and
gate-reconciliation phase. T1 has reported, T2 is held by unavailable raw
evidence, and T4 is complete and independently audited. T5 proved that the
instantaneous stall-torque/current rule wrongly rejected at least three
complete policy matrices. T6 has now evaluated all four reopened frozen policy
pairs under the first previously failed configuration endpoint and found no
robust survivor. A hosted training run remains unearned until an automatic
configuration-response mechanism passes a prospective CPU-only falsifier.
Only a policy that clears the reviewed offline gates can be prepared for
robot-side suspended validation.

The repository itself is part of the robot state. Keep documentation, evidence manifests, snapshots, runbooks, and status notes current whenever the board runtime, robot config, diagnostic results, or recommended next gate changes.

## Current Robot Status

- Robot is mostly assembled.
- Battery is in the intended location.
- Missing only a thin PLA top/back shell piece.
- IMU is configured.
- Robot can hold home pose.
- Robot can hold static balance.
- The board policy hash matches the audited `BEST_WALK_ONNX_2.onnx`.
- The live RDK-X5 config snapshot is in `evidence/20260621T180046Z_rdkx5_config_snapshot.json`.
- The board runtime is an RDK-X5 fork captured under `runtime/`.

## Current Failure

`BEST_WALK_ONNX_2` leans the robot forward and the robot falls during walking.

The original unresolved question was whether this came from policy behavior or
from deployed observations/actions differing from the sim and policy contract.
The completed 440-cell T1 accelerometer-bias dose-response now proves that the
absolute attitude input is behaviorally first-order. With the unmodified
baseline policy and no actuator bridge, adding `+1.6 m/s^2` to `obs[3]` at
`x=0.08` reduced mean forward velocity from `0.0652339` to `0.00886518 m/s`,
an `86.41%` degradation against the preregistered `40%` trigger. All 16
primary cells completed without a fall. Mean body pitch shifted by only
`-0.00445 rad`, so T1 establishes propulsion collapse but does not by itself
reproduce or explain the direction of the physical forward lean.

The actuator bridge also independently degrades the baseline and remains a
real contributor. Its relative importance versus a static posture/IMU offset
is unresolved because the exact T2 corrected-replay raw JSONL is unavailable.
The preregistered T4 baseline-versus-all-gates matrix is now complete. All
`32/32` cells finish without a fall, and an independent audit reproduced every
cell contract, raw result hash, condition aggregate, gate row, and result hash.
The baseline nevertheless fails `13` current gate rows: its fitted-bridge
`x=0.08` mean track ratio is `0.474323`, its worst pitch-chain tracking p95 is
`0.266879 rad`, its worst p95 velocity-limit excess is `2.489999 rad/s`, and
its worst instantaneous excess is `3.239999 rad/s`. T4 therefore requires
those baseline-failed criteria to be relaxed to measured baseline evidence or
explicitly relabeled as stretch goals before they are used as feasibility
boundaries. It does not choose the replacement values automatically.

T5 independently found that the policy campaign's instantaneous protection
constraint was mis-specified. The V10 reference peak was the explicitly
configured MuJoCo force clamp (`1.9122966527938843 N.m`), and the old decimal
gate (`1.91229675 N.m`) lies below the next representable float32 value. No
float32 actuator-force value can exist strictly between them. Feetech's
documented protection is duration-triggered: current greater than `2 A` for
`2 s`, and overload above `80%` of stall for `2 s`. Replaying the immutable
V121, V123, and V128 traces with those two 100-tick rules changes all three to
complete `16/16` passes; post-handoff V177 also becomes `16/16`. This reopens
the affected closures but does not select a deployment policy.

T6 prospectively selected the existing R2 `TORSO_COM_X_NEG` (`-0.05 m`)
condition because it was the first failure after six prior R2 passes. It then
ran both checkpoints, both measured actuator fits, and all four commands for
V121, V123, V128, and V177: `64/64` cells in total. No frozen pair survives.
V121, V123, and V128 have `0/16` green cells; V177 has `1/16`. Worst moving
velocity is negative for every candidate (`-0.3216` to `-0.4140 m/s`), while
the longest corrected servo-protection run is only `5` ticks. This localizes
the blocker to configuration/support response rather than the old
instantaneous current/torque rule. A runner-independent audit reproduced all
source hashes, readbacks, trace metrics, classifications, aggregates, and the
zero-survivor decision with no issue.

## Known Policy Contract

Policy file:

```text
policy/BEST_WALK_ONNX_2.onnx
```

Policy hash:

```text
3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067
```

ONNX I/O:

```text
input:  obs, shape [1, 101], float32
output: continuous_actions, shape [1, 14], float32
```

Observation vector:

| Range | Meaning |
| ---: | --- |
| `0:3` | raw gyro |
| `3:6` | raw accelerometer |
| `6:13` | commands |
| `13:27` | joint position error |
| `27:41` | joint velocity scaled by `0.05` |
| `41:83` | action history |
| `83:97` | previous motor targets |
| `97:99` | foot contacts |
| `99:101` | gait phase |

Action vector:

```text
target_rad[i] = home_rad[i] + action[i] * 0.25
```

Runtime then applies rate limiting before sending servo targets.

## Current Root-Cause Ranking

1. Absolute pitch-reference mismatch: the real upright `accel_x` is about
   `+1.6 m/s^2` relative to the policy's near-zero training center, and T1
   shows this perturbation collapses vanilla-sim propulsion by `86.41%`.
2. Dynamic actuator bandwidth / delay mismatch between sim and the real
   pitch-chain joints. This remains independently supported, but is no longer
   ranked ahead of the measured observation mismatch.
3. Configuration/support observability and response are now the leading
   offline replacement-policy blocker. T6 proves that none of the four frozen
   nominal winners adapts to the first failed torso-COM endpoint. The next
   mechanism must infer configuration from runtime-available signals rather
   than require static mass or millimeter measurements.
4. Policy target waveform and training objective remain possible contributors,
   but no new optimizer run is earned until that mechanism passes a
   prospective CPU-only falsifier.
5. Servo bus CRC/read retries are a watch item, but not the leading cause
   unless they correlate with control damage.
6. Ground contact/load dynamics remain untested with a new candidate.
7. Contact/friction and TPU effects come later, after suspended candidate gates
   pass.

Gross IMU frame, foot-contact polarity, joint identity, and zero-command policy
explosion remain downranked by home pose, IMU tilt, foot contact, joint
identity, and suspended replay evidence. The newly promoted issue is a
constant accelerometer offset within the otherwise-correct IMU frame.

## Definition Of Done

The sim-to-real bridge is done when:

- The live board config, policy hash, runtime path, and package versions are captured and reproducible.
- Home pose telemetry shows stable gyro, upright accelerometer, small joint tracking errors, plausible foot contacts, and low bus errors.
- IMU tilt telemetry maps physical nose-forward/back and left/right tilt to the expected accelerometer axes and signs.
- Foot contact telemetry proves left/right polarity.
- Joint identity testing proves policy index, joint name, servo ID, physical joint, command sign, and measured response.
- Suspended policy replay shows bounded actions, reviewed bus-error behavior,
  and the measured actuator tracking limit is modeled in sim.
- CUDA closed-loop sim reproduction confirms that the fitted actuator bridge
  degrades `BEST_WALK_ONNX_2` in the same range as real suspended `x=0.08`.
- A CUDA-backed candidate policy is trained with the actuator bridge and passes
  offline `x=0.0` and `x=0.08` candidate gates.
- Robot-side suspended validation is attempted only after offline candidate
  gates pass and Rob explicitly approves the moving test.
- Grounded replay is attempted only after suspended candidate validation passes.
- Any runtime or hardware fix is a minimal reviewed patch tied to a specific
  failed gate.
- The README, roadmap, audit, evidence flow, and agent instructions match the latest known board state.
- Every evidence packet and decision is traceable to committed docs or manifests.
- No critical robot state exists only in chat history, local scratch files, or an untracked board directory.

## Non-Goals For Now

- No retraining before an automatic configuration-response mechanism passes a
  prospective CPU-only falsifier and explicitly earns a hosted continuation.
- No gain tuning.
- No joint offset edits.
- No IMU remap edits.
- No action-scale edits.
- No phase-timing edits.
- No friction/contact tuning before observation/action/joint truth tables pass.
