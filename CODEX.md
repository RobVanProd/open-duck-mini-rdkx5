# Codex Notes

Use `AGENTS.md` as the authoritative instruction file for coding agents working in this repository.

Current project mission:

```text
Build a robust reference-motion walking policy for Open Duck Mini through frozen, evidence-selected offline gates. Do not substitute training reward, visual preference, or robot improvisation for preregistered behavior evidence.
```

Current next step:

```text
The project has its first persistent full-horizon nominal winner: the protected
G1_EXACT_BOUNDARY/T2_EQUAL checkpoint pair, composed with the exact x=0
deadband and the conservative left-ankle envelope repair. Both checkpoints pass
the complete R1 matrix under P30 and P31/34. Worst tracking p95 is .183170038
rad, minimum forward velocity is .084911748 m/s, and measured saturation,
rate excess and envelope excess are zero. This is a narrow-command offline
hardware candidate, not robot clearance.

"Remediation winner: NONE" applies only to the closed torso-COM remediation
arms. The composite winner remains valid at nominal torso COM and through R2
floor-friction, joint-friction and armature conditions, but fails the corrected
signed torso-COM endpoint. Seven generic COM branches are closed. Do not reopen
generic COM training.

Review-authorized deployment-specific CPU work is complete. The signed X-axis
torso-COM break-radius study passes its evidence contract over 15 points,
60 matrices and 240 cells. Every sampled curve is monotone and every body-2
X-only readback is exact. The composite winner's certified inner offsets are
-0.02265625 m and +0.00546875 m; nearest observed failures are -0.02343750 m
and +0.00625000 m. Do not symmetrize this sharply asymmetric envelope.

The real-build COM audit is correctly held for missing as-built RDK-X5/battery
masses, X placements and datum; do not invent those inputs from stock Pi
geometry or nominal web weights. Populate the committed measurement template,
then compare the complete uncertainty interval with one 0.00078125 m curve-
resolution margin. Generic COM training remains forbidden.

C1 and the default-off native-runtime implementation are resolved offline. The
winner's 115-D stateful graph does not internalize the per-joint delay queues
or lag state; its 14-D `previous_action` is the bounded-action chain. The new
explicit v2 path supplies obs[83:97] from the fitted-bridge observer, appends
the exact projected-reference feature, carries ONNX state, preserves observe-
then-advance ordering, and fails closed outside the protected command/timing/
artifact contract. It passes 40,520 frozen observation rows, 9,600 bridge rows
with zero reconstruction error, both persistent checkpoints, the legacy
default-off golden vector, and all negative tests. It deliberately embeds no
default hardware fit.

The two live deployment questions are measurements, not another policy search:
(1) populate the committed as-built RDK-X5/battery mass, X-placement and datum
template and compare its full uncertainty interval with the asymmetric COM
bracket plus one 0.00078125 m margin; and (2) separately contract a read-only
hardware actuator-response capture that selects or refits the v2 observer.
Do not plan Gate 5 until both measurements pass their own frozen contracts.
The legacy 101x14.v1 golden vector already passes and remains only a legacy
stack contract. No training, hosted allocation, robot, RDK-X5, local GPU or
iGPU access is authorized. Robot clearance remains NO.
```

Robotics operating model:

```text
Use docs/ROBOTICIST_PLAYBOOK.md. Keep search and agent iteration out of the live robot loop, preserve frozen inspectable deployment code, and accept changes only through evidence gates.
```

Documentation rule:

```text
Keep README.md, PROJECT_GOAL.md, ROADMAP.md, evidence docs, and runbooks current with the latest robot state. Do not let important state live only in chat.
```
