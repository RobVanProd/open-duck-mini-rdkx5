# Winner-v2 Observer Cross-Fit Preregistration

Status: `PREREGISTERED_BEFORE_EVALUATOR_CHANGE_AND_OUTCOMES`

## Question

Does the evidence-selected P30 forward observer preserve the complete composite
winner R1 gate when the simulated plant follows either independently measured
P30 or P31/34 actuator dynamics?

This separates gain-configuration selection from model mismatch. It is a
CPU-only simulator study, not a new policy search or hardware identification.

## Frozen inputs

- Protected composite policies:
  - 512000 SHA-256
    `99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de`
  - 1024000 SHA-256
    `0dfc24bde5d839e4d346dd8c08d9a7d0222a3847764ec6738bfc7f8d947f4ece`
- P30 fit SHA-256:
  `908ddb01e5d82e661d77b8f3cb186a84665695660b86b304c6d1ae89c79cdb0b`
- P31/34 fit SHA-256:
  `a39776c06c5e26425e24b50e7dab3f441823e23904cad4977b8c921d9c9ca276`
- Projected reference SHA-256:
  `8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212`
- Pre-change evaluator SHA-256:
  `f35d35789d50baf557d3b2427dfe326ccc60c7607e79069e5a9dd51f2f01f8d6`
- Playground base commit: `b9be205ac64488c23504ca42e5ec790337adeec3`
- Composed joystick SHA-256:
  `4ddcfbda6f06f9d04acf4ee82deb364993da750adfb8487d032c16be38db3186`
- Gain semantics decision:
  `SELECT_P30_GAIN_SEMANTICS_CROSSFIT_REQUIRED`.

## Evaluator change

Add one default-`None` policy-observer fit input. With `None`, policy
obs[83:97] continues to receive the same plant bridge output and behavior must
remain byte-identical on a frozen 600-row trace. When supplied, instantiate a
second `ActuatorBridgeModel` at the exact same home target. Step both plant and
observer once per sent target at 0.02 seconds. Use plant output for physics,
tracking, rate/envelope gates and `applied_target_rad`; use observer output only
for policy obs[83:97] and record it separately as
`policy_observer_applied_target_rad`.

No policy, plant, reset, command, phase, reference, graph state, action,
projection, reward or gate changes are permitted.

## Frozen matrix

- checkpoints: 512000, 1024000;
- plant fits: P30, P31/34;
- policy-observer fits: P30, P31/34;
- commands x: 0, .074, .077, .080 m/s;
- seed: 167931544;
- reset: deterministic home-support;
- task: `flat_terrain_backlash`;
- duration: 600 ticks at 0.02 seconds;
- reference start phase: 0, observe then advance;
- applied-target observation enabled;
- total: 2 x 2 x 2 x 4 = 32 cells.

Every run records exact policy, plant-fit, observer-fit and environment hashes;
600-row traces; plant and observer applied targets; sent targets; actual joint
positions; tracking; saturation; rate/envelope excess; contacts; velocity and
termination. Both bridge states initialize at the frozen home vector.

## Frozen gates

Use the unchanged R1 gates. Every moving cell must complete 600 ticks, preserve
bilateral gait, have zero saturation, zero measured rate/envelope excess,
tracking p95 <= .20 rad, and pass all prior forward-motion/support thresholds.
Every x=0 cell must complete 600 ticks, preserve the prior home/zero-command
thresholds, have maximum absolute mean local velocity <= .02 m/s, body-pitch
p95 <= .25 rad, minimum base height >= .12 m, tracking p95 <= .20 rad, and
zero saturation/rate excess.

## Selection rule

The P30 observer advances only if both persistent checkpoints pass all 16 cells
formed by both plant fits and all four commands. If P30 fails any cell, do not
promote P31/34 as a closest alternative; hold for a separately contracted
hardware identification or observer-model study.

P31/34 observer cells are reporting/causal controls. If P30 passes, P31/34
cannot displace it because P31/34 gain semantics were already rejected. No
metric ranking or training reward is used.

- P30 passes all 16: `PASS_P30_OBSERVER_MEASURED_CROSS_FIT_BRACKET`.
- P30 fails any cell: `HOLD_P30_OBSERVER_CROSS_FIT_MISMATCH`.
- Any contract/default-off/readback defect: `INVALID_OBSERVER_CROSS_FIT_EVIDENCE`.

## Authority

A pass authorizes pinning the P30 observer artifact in the offline winner-v2
configuration contract. It does not authorize Gate 5, deployment, robot/RDK-X5
access, motors, or claim current hardware health. A hold selects only a new
measurement/observer preregistration. No GPU/iGPU, hosted compute or training.

Required artifacts:

- `winner_v2_observer_cross_fit_default_off_contract.json`
- `WINNER_V2_OBSERVER_CROSS_FIT_DEFAULT_OFF_CONTRACT_20260717.md`
- per-cell JSON and JSONL under
  `outputs/analysis/winner_v2_observer_cross_fit/`
- `winner_v2_observer_cross_fit_result.json`
- `WINNER_V2_OBSERVER_CROSS_FIT_RESULT_20260717.md`
