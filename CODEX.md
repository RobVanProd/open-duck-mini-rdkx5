# Codex Notes

Use `AGENTS.md` as the authoritative instruction file for coding agents working
in this repository.

Current project mission:

```text
Build a robust reference-motion walking policy for Open Duck Mini through
frozen, evidence-selected offline gates. Do not substitute training reward,
visual preference, or robot improvisation for preregistered behavior evidence.
```

Current next step:

```text
Work only from the permanent checkout at
`D:\CodexProjects\open-duck-mini-rdkx5-policy`; evidence caches and the Python
environment live under `D:\CodexArtifacts`. Do not depend on Windows Temp.

T1 is complete and proves the absolute accelerometer mismatch is first-order:
adding the robot's measured +1.6 m/s^2 accel_x offset to the unmodified policy
reduced vanilla-sim forward velocity by 86.41%. T2 is held because the exact
corrected-replay raw JSONL is unavailable.

T4 is complete. All 32 baseline cells are hash-verified in
`D:\CodexArtifacts\open-duck-policy\t4_baseline_all_gates_v1`. An independent
audit reproduced every cell contract, raw result hash, condition aggregate,
gate row, and final result hash. The baseline completes all 32 cells without a
fall but fails 13 current gate rows. Per the frozen T4 rule, any gate the
baseline fails must be relaxed to measured baseline evidence or explicitly
relabeled as a stretch goal; T4 makes no automatic change.

T5 is complete and changes the policy decision boundary. The old
1.91229675-N.m one-tick torque gate was the 19.5-kgf.cm stall point, while V10
forced MuJoCo's actuator range to its lower adjacent float32 value. The V10
"baseline peak" is therefore a model clamp, and no float32 value exists between
that clamp and the decimal gate. Feetech instead documents protection after
two seconds above 2 A and two seconds blocked above 80% stall.

The preregistered read-only reanalysis verified every stored cell/trace hash and
recomputed both duration rules per joint. V121, V123, and V128 each change to
complete 16/16 nominal passes, meeting the exact three-candidate reopen
trigger. Post-handoff V177 also changes to 16/16.

T6 is complete. It prospectively selected the existing R2
TORSO_COM_X_NEG=-0.05-m endpoint, then evaluated V121, V123, V128, and V177
across both checkpoints, both measured actuator fits, and x=0/.074/.077/.080:
64/64 cells. No pair survives. V121/V123/V128 score 0/16 and V177 scores 1/16.
Every candidate has negative worst-case moving velocity; corrected
over-current/overload runs remain only 3-5 ticks. The independent auditor,
which does not import the runner, reproduced 16 manifests, 16 evaluations, 64
trace hashes, 64 exact COM readbacks, all metrics/aggregates, and the final
zero-survivor decision. Audit SHA:
70a9b3ca045522ceda1df86f4712878e81aaba07d97283441f8a2ea82bb4d9c3.

The next step is to preregister a CPU-only automatic
configuration-response mechanism falsifier. It must use runtime-available
signals and cannot require manual weighing, calipers, or a static COM ledger.
The old passive response73 route remains closed because its corrected -0.05-m
support reset falls; do not resurrect it without new prospective evidence.
No robot, RDK-X5, serial, torque, motion, hosted training, Gate 5, checkpoint
selection, or deployment action is authorized.
```

Robotics operating model:

```text
Use docs/ROBOTICIST_PLAYBOOK.md. Keep search and agent iteration out of the live
robot loop, preserve frozen inspectable deployment code, and accept changes
only through evidence gates.
```

Documentation rule:

```text
Keep README.md, PROJECT_GOAL.md, ROADMAP.md, evidence docs, and runbooks current
with the latest robot state. Do not let important state live only in chat.
```
