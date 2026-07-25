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
gate-reconciliation phase. A new hosted training run is not earned until the
preregistered T1/T2/T4 evidence packet has reported and the resulting
mechanism is reviewed. Only a policy that clears the frozen offline gates can
be prepared for robot-side suspended validation.

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
The next offline decision evidence is the preregistered T4 baseline-versus-all-
gates matrix; no optimizer run is authorized before that report.

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
3. Policy target waveform and training objective may be too sharp for the
   measured effective velocity limits; current feasibility gates themselves
   still require T4 reconciliation against the baseline.
4. Servo bus CRC/read retries are a watch item, but not the leading cause
   unless they correlate with control damage.
5. Ground contact/load dynamics remain untested with a new candidate.
6. Contact/friction and TPU effects come later, after suspended candidate gates
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

- No retraining before the T1/T2/T4 decision packet is complete and a new run
  is earned by a preregistered falsifier.
- No gain tuning.
- No joint offset edits.
- No IMU remap edits.
- No action-scale edits.
- No phase-timing edits.
- No friction/contact tuning before observation/action/joint truth tables pass.
