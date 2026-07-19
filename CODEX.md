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
default-off golden vector, and all negative tests.

Actuator-fit provenance and the frozen CPU observer-by-plant cross-fit now
resolve the remaining fit-selection question without new hardware capture.
The body runtime used P30 semantics, the valid fixed-target P30 telemetry has
747 samples with zero read/write/reset errors, and P31/34 was already rejected
as a live gain route. The 32-cell cross-fit spans both checkpoints, both plant
fits, both observer fits and all four commands; every cell passes. P30 observer
semantics remain below .20 rad tracking under both measured plant fits, with
minimum vx .084084972 m/s and zero rate/envelope excess. The winner-v2 runtime
is therefore pinned to the measured P30 fit hash and rejects P31/34 or gain
overrides before hardware initialization. This is an offline contract result,
not a claim of current hardware health.

The sole model-specific deployment measurement currently missing is the
as-built RDK-X5/battery torso COM ledger. A 2026-07-17 repository re-audit found
no new assembly CAD, component masses, common datum, X placements or uncertainty
bounds. Populate the committed template and compare its complete uncertainty
interval with the asymmetric COM bracket plus one 0.00078125 m margin. Do not
plan Gate 5 until that measurement passes its frozen contract.

The measurement handoff is now executable and fail-closed. Before any build
values existed, the v1 template's free-text-only frame transform was corrected
to a numeric v2 datum origin, datum uncertainty and axis sign. The CPU
calculator passes five contract cases, enumerates the frozen independent mass
box extrema, applies position and common-datum uncertainty, and reads the
certified bounds from the hashed break-radius result. The untouched template
reports all 46 missing fields, emits no numerical estimate and remains
`HOLD_REAL_BUILD_COM_INPUTS_INCOMPLETE`. Use
`REAL_BUILD_TORSO_COM_MEASUREMENT_PACKET_20260717.md`; do not populate any field
from nominal web weights or inference.

The referenced Frank Fu RDK-X5 material has now been audited as a possible
input source and closes negative. The authored article adapts OS, dependencies
and runtime software, while physical construction points to the stock upstream
Open Duck repository. The pinned 436-path upstream v2 tree has zero RDK/X5
paths and retains Pi Zero plus stock battery assets. Neither source contains an
RDK mount, installed masses, placements, datum or uncertainties; zero of 46
measurement fields can be promoted. Do not treat the existence of the Frank Fu
RDK runtime adaptation as mechanical equivalence evidence for this build.

A 2026-07-19 policy-readiness re-audit reran the fail-closed physical-COM
calculator and all five CPU contract tests. The untouched template still has
exactly 46 missing fields, reports no numerical estimate, and leaves status
`HOLD_REAL_BUILD_COM_INPUTS_INCOMPLETE`. The composite remains an offline
hardware candidate; robot clearance remains NO. See
`outputs/analysis/POLICY_ROBOT_READINESS_REAUDIT_20260719.md`.

The legacy 101x14.v1 golden vector already passes and remains only a legacy
stack contract. The policy-side response to native-runtime Comms.md is now
evidence-complete at artifacts/runtime_handoff/rdkx5_native_20260719/.
Disposition is REQUIRES_REVIEWED_115_RUNTIME_V2: both protected graphs consume
obs[1,115] plus previous_action[1,14] and return final action plus next state.
The package carries both persistence checkpoints, exact observation/action/
phase/P30 semantics, four lossless 600-tick traces, compact adjacent vectors,
and a CPU fail-closed verifier. It passes with zero ONNX golden/state/chain
error and exact x=0 zeros.

The old behavior tables did not contain a checkpoint-level tie-break, so the
project did not select one post hoc. The prospective native-representation
screen has now completed once: 16/16 cells and all 9,600 trace rows pass under
the two measured plant fits. Both persistent checkpoints pass all eight sibling
cells. The frozen first criterion selects the original 512000-step graph on
lower worst tracking p95, .1809259653 versus .1818299592 rad. The selected
ONNX SHA-256 is
99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de.
The finite-representation quantizer remains evaluation-only; it is not part of
the deployed graph. Training and simulator reward had no selection weight.

The runtime team may now accept the selected original graph through its
versioned 115-D v2 review using the existing handoff package and selected-
binary relay. Selection is not runtime acceptance. Gate 5, runtime deployment,
and robot authority remain unchanged. The other live blocker is unchanged:
complete a source-backed as-built torso COM measurement and pass the frozen
asymmetric bracket check.

The runtime's independent full assembler found and localized a metadata defect
in that package: its three embedded action-history slices were documented one
tick too recently. The preregistered correction now matches both evaluator
source and all 2,400 golden rows exactly: observation history is `t-2/t-3/t-4`
and the separate recurrent input is `t-1`. The selected 512000-step ONNX and
all golden evidence remain byte-identical. Corrected schema is v1.1 and the
replacement manifest SHA-256 is `d771d188...c6827c5`. Fully recursive
cross-CPU replay is still held for a separately frozen numeric-closure rule;
the direct `1e-6` replay limit is not retroactively broadened.

The 46-field component ledger remains valid, but it is no longer the only
measurement route. Before any physical value was read, a smaller direct route
was preregistered: isolate the complete powered-off torso at the modeled hip-
yaw and neck-pitch child boundaries, then measure its X COM from two support
reactions over three unload/reload trials. The clean upstream URDF and simulator
XML both place the physically identifiable bilateral hip-yaw-axis datum at
X=-.019 m in `trunk_assembly`. Exact specimen, support-span, scale uncertainty,
independent-total-mass, trial-overlap and unchanged COM comparison rules are
frozen. Only its blank-template CPU calculator and zero-measurement contract
was authorized next. That contract now passes all 14 checks: eight direct-route
unit cases and the five original component-ledger cases pass, source hashes and
datum are exact, and the blank template reports no numerical estimate. The
direct route needs 15 numeric readings/uncertainties instead of 40 component
numbers. The remaining policy-side datum must come from the powered-off
operator measurement packet; no physical value, robot action or clearance has
been inferred.

No training, hosted allocation, robot, RDK-X5, local GPU or iGPU access is
authorized. Robot clearance remains NO.
```

Robotics operating model:

```text
Use docs/ROBOTICIST_PLAYBOOK.md. Keep search and agent iteration out of the live robot loop, preserve frozen inspectable deployment code, and accept changes only through evidence gates.
```

Documentation rule:

```text
Keep README.md, PROJECT_GOAL.md, ROADMAP.md, evidence docs, and runbooks current with the latest robot state. Do not let important state live only in chat.
```
