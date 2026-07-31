# Oracle Phase-Conditioned COM Compensation Plan

Date frozen: 2026-07-15 (America/New_York)

## Question and authority boundary

This CPU-only simulator study asks whether the protected nominal G1/T2_EQUAL
walking controller can pass the already-frozen signed torso-COM endpoint matrix
when a small residual controller receives simulator-oracle stability state.  It
is a feasibility test only.  It does not authorize training, deployment,
runtime design, robot or RDK-X5 access, GPU/iGPU use, Colab use, policy
replacement, or robot clearance.  The frozen ONNX files are read-only.

## Protected baseline

- policies: repaired `T2_EQUAL_512000.onnx` and `T2_EQUAL_1024000.onnx`;
- policy hashes: `99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de`
  and `0dfc24bde5d839e4d346dd8c08d9a7d0222a3847764ec6738bfc7f8d947f4ece`;
- P30 and P31/34 actuator fits, hashes
  `908ddb01e5d82e661d77b8f3cb186a84665695660b86b304c6d1ae89c79cdb0b`
  and `a39776c06c5e26425e24b50e7dab3f441823e23904cad4977b8c921d9c9ca276`;
- projected reference table hash
  `8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212`;
- exact composed simulator sources from the closed reset-estimator evaluation:
  `joystick.py` hash
  `4ddcfbda6f06f9d04acf4ee82deb364993da750adfb8487d032c16be38db3186`
  and `runner.py` hash
  `e5ed1bac7ed181f02014487827f05f35fd421ff97ae50614de1b2ce8089f87a2`;
- deterministic home-support reset, applied-target observation, zero-command
  deadband, measured hard-vector projection, actual-centered tracking guard,
  conservative actuator-envelope repair, command normalization, reference,
  actuator models, 600-tick horizon, seed and all behavior thresholds remain
  unchanged.

The endpoint intervention is name-resolved `trunk_assembly` body 2 and changes
only `body_ipos[2,0]` by the exact model-dtype representation of -0.05 or
+0.05 m.  Every run must independently report the full model-difference
readback before its result is eligible.

## Frozen residual law

The residual is one phase/contact-conditioned affine controller.  It has a
separate coefficient bank for endpoint sign and for four mutually exclusive
contact modes: left stance, right stance, double support and transition/no
support.  Each bank maps these eleven oracle features to six residual outputs:

`[1, sin(phase), cos(phase), support_relative_com_x,
com_vx-command_x, pitch, pitch_rate, support_relative_com_y, com_vy,
roll, roll_rate]`.

The six outputs may correct only left/right hip pitch, knee and ankle.  Every
other action element is exactly unchanged.  The signed endpoint parameter only
selects the frozen negative or positive bank; at nominal COM the residual is
identically zero, including x=0.  Support-relative COM is measured against the
active contacting-foot centroid, or the two-foot centroid in transition/no
support.  Phase comes from the simulator's reference phase; contacts, whole-
body subtree COM and velocity, torso attitude/rates, applied target and command
are simulator-oracle values.  Applied target is recorded but is not an affine
feature because the protected actor already receives it.

Each corrected normalized action component is clipped to +/-0.08 (equivalent
to +/-0.02 rad before downstream constraints).  The combined base-plus-
residual action is then clipped to [-1,1], projected through the exact graph
hard-vector per-joint delta limits, and constrained to the existing actual-
centered +/-0.20 rad guard before the unchanged actuator bridge.  The final
combined action, rather than the uncorrected base action, is fed into the
policy's `previous_action` state on the next tick.  No residual may bypass a
rate, guard or envelope constraint.

## Frozen design procedure

### Default-off contract

With the residual disabled, execute both policies at P30 for nominal x=0 and
x=.077.  Compare every numeric field of the newly generated 600-row traces
against a second execution through the unmodified evaluator path.  Require
identical tick counts, decisions and arrays, with maximum absolute numeric
difference <=1e-7.  Also require zero residual at every nominal tick when the
controller path is enabled.  Failure stops the study.

### Corrective-authority screen

Generate design traces only at P30, x=.077, seed 167931544, for both protected
checkpoints and both signed endpoints.  At ticks 0,4,...,36 that precede a
termination, branch the exact simulator and actuator-bridge state for eight
ticks.  Hold the already-produced frozen base-action sequence fixed.  Compare
zero residual with a fixed pulse bank: +/-0.04 and +/-0.08 normalized action on
each of the six permitted joints, one joint at a time (25 branches including
zero).  Every branch passes through the same final-action constraints.

Rank branches lexicographically by: (1) eight-tick survival, (2) no tracking,
rate, envelope or saturation violation, (3) larger minimum base height, (4)
lower maximum absolute pitch, (5) lower maximum absolute roll, (6) lower
terminal COM distance from the active support centroid, (7) lower residual L2
norm, then fixed joint-index/amplitude order.  A state has corrective authority
only when its selected nonzero branch strictly improves this tuple over zero.
An endpoint/checkpoint has authority only if at least one state in every
observed contact mode improves and at least half of all its screened states
improve.  If either endpoint lacks authority at either checkpoint, stop with
`HOLD_NO_CORRECTIVE_AUTHORITY`; do not fit a controller.

For every branch record phase, contacts, COM error/velocity, residual, the
first-order finite-difference prediction from the +/-0.04 pair, realized
pitch/roll change, tracking p95, saturation, rate excess and envelope excess.

### Deterministic fit

For each endpoint-sign/contact bank, fit the eleven features to the selected
six-joint authority labels by deterministic ridge regression with intercept
already present, lambda=1e-3, float64 solve and no outcome-dependent feature or
regularization changes.  Missing banks are all-zero and therefore cannot pass
the authority rule.  Freeze feature mean/scale from the design corpus (constant
feature is not standardized); scales below 1e-9 become 1.0.

Choose one global coefficient scale from the fixed ordered set
`[0.25, 0.50, 0.75, 1.00]` using only the four design cells (two checkpoints x
two endpoints, P30, x=.077).  Rank scales by the required lexicographic
objective: full-duration survival; tracking threshold; zero rate/envelope
excess; bilateral transitions; command-consistent forward motion; nominal
preservation; then lower worst tracking p95 and smaller scale.  Freeze the
first best scale and controller JSON hash before any formal outcome cell is
read.  No retry or parameter change follows.

## Frozen formal matrix and decision

Run exactly 48 cells: NOMINAL, X_NEG=-.05 and X_POS=+.05; both protected
checkpoints; P30 and P31/34; commands x=0/.074/.077/.080; seed 167931544; 600
ticks.  Each cell requires deterministic reset, exact model readback, bilateral
gait where moving, zero saturation, zero measured rate excess, zero envelope
excess, tracking p95 <=.20 rad, and every prior nominal/x=0 gate.  Nominal
traces must also prove an exactly zero residual.  No stop-at-first-failure rule
applies.

- `PASS_ORACLE_DYNAMIC_COMPENSATION`: one frozen controller passes all 48.
- `HOLD_NO_CORRECTIVE_AUTHORITY`: the bounded pulse screen fails its frozen
  authority rule before fitting.
- `HOLD_ORACLE_PARTIAL`: authority exists but the frozen controller fails one
  or more formal cells.

No closest configuration is promoted.  A pass supports only a separately
preregistered oracle-distillation/estimator direction; a failure supports the
corresponding causal conclusion in the goal, not robot clearance.

## Frozen artifact paths

- `outputs/analysis/ORACLE_PHASE_COM_COMPENSATION_PLAN.md`
- `outputs/analysis/oracle_phase_com_compensation_contract.json`
- `outputs/analysis/ORACLE_PHASE_COM_CORRECTIVE_AUTHORITY.md`
- `outputs/analysis/oracle_phase_com_corrective_authority.json`
- `outputs/analysis/ORACLE_PHASE_COM_COMPENSATION_RESULT.md`
- `outputs/analysis/oracle_phase_com_compensation_result.json`
- `outputs/analysis/oracle_phase_com_compensation_traces/`

