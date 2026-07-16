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

Review-authorized work is deployment-specific and CPU/read-only. The signed
X-axis torso-COM break-radius curve is formally running across the complete
16-cell matrix at every queried offset. The real-build COM audit is correctly
held for missing as-built RDK-X5/battery masses, X placements and datum; do not
invent those inputs from stock Pi geometry or nominal web weights.

C1 is resolved at the offline contract boundary. The winner's 115-D stateful
graph does not internalize the per-joint delay queues or lag state; its 14-D
`previous_action` is the bounded-action chain. Therefore obs[83:97] must be
provided by an external fitted-bridge forward observer. The existing observer
reconstructs all 9,600 frozen composite trace targets under both fits with zero
error and is pinned for the v2 contract. Native-runtime integration and the
hardware-fit choice remain separately blocked before any Gate 5 plan.
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
