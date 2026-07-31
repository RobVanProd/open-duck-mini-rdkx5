# Composite-Winner Torso-COM Break-Radius Preregistration

Status: `PREREGISTERED_CPU_ONLY`

## Question

For the frozen G1/T2 composite winner, what signed X-axis torso-COM offset is
certified to pass the complete R1 behavior matrix, and where is the first
observed aggregate failure outside it?

This is a deployment-model measurement, not a generic robustness campaign.

## Frozen controller and evaluator

- Policies: T2_EQUAL steps 512000 and 1024000, SHA-256
  `99d3afce...04de` and `0dfc24bd...f4ece`.
- Baked transforms: actual-centered guard, exact x=0 deadband, conservative
  left-ankle 0.14-to-0.12 repair.
- Fits: P30 `908ddb01...db0b`, P31/34 `a39776c0...a276`.
- Commands: x=0, 0.074, 0.077, 0.080 m/s.
- Seed: 167931544; deterministic home-support reset; 600 ticks; phase 0.
- Observation: 115-D, obs[83:97] bridge-realized applied target.
- Corrected torso mutation: body 2 `trunk_assembly`, X component of
  `body_ipos`, with per-run before/after readback. Y/Z deltas must be zero.
- CPU only; CUDA devices hidden; no GPU/iGPU, hosted allocation, RDK-X5 or
  robot access.

Every matrix must retain the unchanged R1 gates: complete 600-tick x=0 hold or
bilateral moving gait, tracking p95 <=0.20 rad, zero measured rate/envelope
excess, zero saturation, command-consistent motion, and exact readback.

## Frozen adaptive curve

Run the full 16-cell matrix at 0 and at each signed 0.05-m endpoint. For each
sign independently, maintain `[inner_pass, outer_fail]`, initially `[0, .05]`,
then run exactly six bisection midpoints. A midpoint becomes the inner bound
only if every one of its 16 cells passes; otherwise it becomes the outer bound.
The final bracket width is 0.00078125 m.

All sampled magnitudes must also be monotone for each sign: no aggregate pass
may appear at a larger magnitude after an aggregate failure. A non-monotone
sample set closes without reporting a single break radius.

No midpoint, endpoint, checkpoint, fit, command or failed cell may be removed,
retried, shortened or replaced. Existing endpoint artifacts are comparators;
all formal cells are rerun by this contract.

## Decisions

- `PASS_COM_BREAK_RADIUS_BRACKETED`: both signs have a monotone certified inner
  pass and observed outer failure separated by 0.00078125 m.
- `HOLD_COM_CURVE_NON_MONOTONIC`: sampled results cannot support a radius.
- `HOLD_COM_CURVE_EVIDENCE_INVALID`: any cell/readback/hash/platform contract
  is invalid.

A valid bracket authorizes comparison with a separately contracted real-build
COM estimate only. It does not authorize model correction, training, Gate 5,
deployment or robot clearance.

