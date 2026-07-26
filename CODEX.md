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
complete 16/16 passes, meeting the exact three-candidate reopen trigger.
V157's and V162's early-stop cells also pass, so their stop rules are
invalidated but their unrun cells remain missing. V174 remains green over its
recorded endpoint population. Post-handoff V177 changes from 8/16 to 16/16.
No audited V121-V177 trace hits the canonical +/-3.23-N.m MuJoCo force clamp,
and exact force reconstruction closes within 5e-6 N.m.

T5 reopens the V121-V175 campaign closures; it does not select a policy. The
next step is to preregister a corrected-gate robustness comparison of the
already-frozen surviving policies, using T4 for baseline feasibility and T5
for manufacturer-derived servo protection, before considering any new
optimizer run. No robot, RDK-X5, serial, torque, motion, hosted training,
Gate 5, checkpoint selection, or deployment action is authorized.
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
