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
The G1/T2 composite remains the first persistent full-horizon nominal/R1
winner, but it is held from the supported-configuration and robot roles. The
single preregistered winner-v3 replacement branch is now complete and closes
negative. No replacement graph is selected.

R64_ZERO_INIT_RECURRENT_ADAPTER completed its only seed-100 no-retry CPU
curriculum and produced two persistent full-domain checkpoints. The evaluation
graphs preserve the learned initializers and bake in the frozen hard-vector,
actual-centered guard, conservative envelope and x=0 deadband. The exact
1,024-cell matrix then ran once in one CPU process over nominal, 24 fixed
anchors, 16 discovery samples, 16 independently seeded heldout samples and six
sensor/transport conditions, crossed with both checkpoints, both measured
actuator plants and x=0/.074/.077/.080.

The raw aggregate is preserved as INVALID because its reporter required a JAX
device display string containing CpuDevice although this environment exposes
TFRT_CPU_0, and because it treated each expected early-termination trace as
missing evidence. The read-only reporting correction reran zero behavior cells
and changed no graph, model, trace, threshold, seed, gate or physics value. It
verifies all 1,024 cell/trace hashes, exact trace-row versus recorded-sample
counts, finite/schema/reset audits and every per-run model readback; it accepts
CPU through device.platform == cpu while preserving duration and trace-contract
behavior failures.

Corrected decision: HOLD_WINNER_V3_VARIABLE_CONFIGURATION_REPLACEMENT. Only
48/1,024 cells pass the physical gates; each checkpoint passes 24/512 and fails
the frozen all-cells rule. Nominal passes 0/32 and sensor/transport passes 0/96.
There are 944 all-joint current-p95 failures against the frozen .65 A cap, 239
early terminations, 251 candidate-gate failures, 107 wrong-direction moving
cells, four tracking failures, 38 saturation failures, 34 guard-envelope
failures and 12 rate failures. The signed X mechanism also persists: negative
X reverses and falls, while positive X runs away forward and falls. No closest
cell, sibling checkpoint, aggregate score or training reward is promoted.

The 7.6 GiB local trace corpus is preserved byte-for-byte and represented in
Git by a verified 1,024-entry path/SHA/size/row manifest plus every compact cell
and condition summary. The raw invalid result and corrected hold are both
retained so the reporting history is auditable.

The runtime-requested read-only causal audit is complete at policy commit
`9663c059adb3919ee414550097bba6bd31cecdc4`. All 1,024 trace hashes and replayed
current/tracking metrics match. Removing only current for attribution, never
reclassification, leaves 753 otherwise-passing cells; 705 cells fail current
alone. Current exceedance follows the wrong-direction event in all 107
wrong-direction/current failures, so it does not explain the signed sagittal
failure. Negative X readback is exact and reverses/falls; positive X readback
is exact and overspeeds/falls.

Primary-source correction: Feetech's 2024 catalog does support 0.65 A as the
ST-3215-C001 rated current at 7.4 V. It does not support the repository's exact
0.784532 N.m/A conversion or define p95 over a 600-tick simulation as the rated
current gate. The catalog rated-point quotient is 0.754357692 N.m/A, 4% below
the repository conversion. The frozen outcome remains unchanged: all eight
nominal x=0 cells take exact-zero graph action for 600 ticks, yet the identical
home-hold result is 0.661276083 A, so policy training cannot make that frozen
cell pass.

This exact replacement branch is closed. Runtime must keep its pending
sentinels: REPLACEMENT_SELECTED_ONNX, POLICY_ROBOT_CLEARANCE_ARTIFACT and
SUPPORTED_CONFIGURATION_ENVELOPE_V2 remain NOT_AVAILABLE; robot_clearance is
false and X5_CPU_PREFLIGHT/AUTOMATIC_CONFIGURATION/GATE_5 remain NOT_RUN. The
next evidence boundary is prospective: freeze the current-gate application and
conversion semantics from primary motor plus telemetry evidence, then freeze a
runtime-reviewed automatic-response-conditioned ABI. Only if both contracts
pass may one new training run be preregistered. No robot, RDK-X5, serial,
torque, motion, local GPU/iGPU, hosted training, Gate 5 or deployment action is
authorized.
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
