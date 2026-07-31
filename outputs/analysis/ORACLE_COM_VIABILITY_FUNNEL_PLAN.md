# Oracle COM Viability-Funnel Plan

Frozen: 2026-07-16 (America/New_York), before Stage-A localization output or
Stage-B sequence-search output was generated.

## Question and authority boundary

This CPU-only study asks whether the protected nominal G1/T2 gait and the
already-demonstrated bounded local pitch-chain authority compose into a
sustained signed torso-COM rescue. It is a narrow feasibility/localization
study. It is not training, policy selection, deployment, runtime design, robot
clearance, or permission to use the RDK-X5, robot, GPU/iGPU, Colab, or hosted
compute. Robot clearance remains `NO`.

The protected policies, P30/P31-34 fits, deterministic home reset, reference,
command normalization, zero-command deadband, measured hard-vector projection,
actual-centered guard, conservative actuator envelope, thresholds, seed and
600-tick horizon remain unchanged. The failed affine residual is evidence, not
a new protected policy.

## Stage A: frozen failure localization

Localize all 24 committed failing moving-command endpoint cells: two signed
conditions, two checkpoints, two actuator fits and x=.074/.077/.080. Each is
compared with its exact matched nominal trace. Meaningful divergence is the
first contact mismatch or the first threshold crossing: local-velocity Linf
.05 m/s, pitch/roll .05 rad, pitch/roll-rate .5 rad/s, support-relative COM
.01 m, base actor action .04 normalized, or applied target .01 rad. A velocity
event is three consecutive ticks at vx<=-.02 m/s for X_NEG or
vx>=max(command+.10, 2*command) for X_POS.

Freeze an exact pre-action state every four ticks from tick 0 through the last
recorded pre-termination tick. Each state stores qpos, qvel, ctrl, observation,
oracle state, previous combined action, previous sent target, reconstructed
actuator-bridge value and queues, source/matched trace hashes, and distance to
termination. Bridge reconstruction must agree with the committed applied
target to 1e-6 rad.

## Stage B: bounded sequence-rescue screen

The design subset is fixed to the four prior authority cells only: P30,
x=.077, seed 167931544, both persistent checkpoints and both signed endpoints.
Every four-tick cadence state in those four cells is screened. This restriction
is a causal design choice, not a claim about P31/34 or other commands.

Search horizons are exactly 8, 16 and 32 ticks. A deterministic beam of width
16 expands one four-tick piecewise-constant residual block at a time. Its only
25 block choices are zero or one of the six already-supported pitch-chain
joints at -0.08, -0.04, +0.04 or +0.08 normalized action. There is no
unrestricted 14-joint search, stochastic optimizer, retry, tuning, or new
basis. Each residual is added to the frozen actor action and then passes the
same normalized clip, hard-vector projection, actual-centered .20-rad guard,
global target-rate stage and measured P30 bridge.

The open-loop base-action tape uses the committed endpoint trace's
`policy_base_action` at available ticks. Beyond its termination it uses the
matched nominal trace's `policy_base_action` at the same absolute tick. This
rule permits every frozen near-termination state to receive all three horizons
without inventing actions or shortening the screen. It makes Stage B a local
sequence-existence test, not an online-controller result.

The velocity/attitude envelope is frozen before search outcomes by a mechanical
formula over the four hash-locked nominal x=.077 traces (both checkpoints and
fits). At each start tick and horizon, allowable mean body vx is the minimum to
maximum nominal rolling mean plus/minus .03 m/s. After tick 4 mean vx must also
be positive. Allowable absolute terminal pitch and roll are the maximum matched
nominal value plus .05 rad. Candidate priority is lexicographic:

1. finite horizon and base height >=.12 m;
2. no more than one consecutive no-support tick;
3. tracking p95 <=.20 rad, zero saturation, zero measured rate excess and zero
   envelope excess;
4. correct velocity direction and the frozen nominal-derived velocity envelope;
5. pitch/roll viability;
6. smaller command error, COM/support distance and residual L1;
7. fixed action-order tiebreak.

One single horizon advances only if it has a valid sequence from every frozen
design state for both signs and both checkpoints. If no horizon does, stop with
`HOLD_LOCAL_AUTHORITY_NOT_COMPOSABLE`; do not promote a closest state, sign,
checkpoint or horizon and do not run Stage C.

## Stage C: conditional online test

Stage C exists only if Stage B passes. Choose the first globally passing
horizon in the frozen order 8,16,32. Use the identical beam, basis, limits and
objective, replan at the fixed four-tick cadence from live simulator state,
apply only its first four-tick bounded block, then replan. Nominal COM disables
the residual exactly. First prove default-off equivalence, then run the exact
unchanged 48 cells: NOMINAL/X_NEG/X_POS, both checkpoints, both P30 and P31/34,
x=0/.074/.077/.080, seed 167931544 and 600 ticks.

`PASS_ORACLE_RECEDING_HORIZON` requires every cell to pass every prior gate.
If offline sequences exist but online replanning fails, use
`HOLD_SEQUENCE_EXISTS_PLANNER_FAILS`; if only one sign survives use
`HOLD_SIGNED_ASYMMETRY`. No closest configuration advances.

## Hard stop and artifacts

After outcomes, do not add a horizon, basis vector, amplitude, beam budget,
margin, threshold, training arm, hosted job, GPU path, or hardware test.
Required artifacts are the plan and contract, Stage-A localization MD/JSON,
Stage-B sequence MD/JSON plus per-state records, and a final receding-horizon
MD/JSON with one explicit decision token. Per-cell formal traces are required
only if Stage C is authorized by Stage B and actually runs.
