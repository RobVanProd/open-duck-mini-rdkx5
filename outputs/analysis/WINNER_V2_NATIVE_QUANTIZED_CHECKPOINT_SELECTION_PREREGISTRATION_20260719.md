# Winner-v2 Native-Quantized Checkpoint Selection Preregistration

status: `PREREGISTERED_BEFORE_TRANSFORM_OR_BEHAVIOR_OUTCOMES`

## Question

Which one of the two already-protected persistent `G1_EXACT_BOUNDARY/T2_EQUAL`
checkpoints should be the single deployment binary when the actor receives the
finite-resolution direct inputs produced by the reviewed RDK-X5 native sensor
and servo stack?

This is a prospective checkpoint-selection study, not a reopening of policy
training or torso-COM remediation. The prior matrices establish that the
checkpoint pair is persistent; they contain no rule that selects half versus
final. Their already-observed metrics therefore have no selection weight here.

## Frozen sources

- policy branch before this preregistration: `codex/torso-com-decode-probe`;
- handoff manifest SHA-256:
  `ba7143f5c653c0bb2f3f27930a7997dd5a2b90e3258bca516b7240bd0f21abd7`;
- 512,000 ONNX SHA-256:
  `99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de`;
- 1,024,000 ONNX SHA-256:
  `0dfc24bde5d839e4d346dd8c08d9a7d0222a3847764ec6738bfc7f8d947f4ece`;
- P30 fit SHA-256:
  `908ddb01e5d82e661d77b8f3cb186a84665695660b86b304c6d1ae89c79cdb0b`;
- P31/34 fit SHA-256:
  `a39776c06c5e26425e24b50e7dab3f441823e23904cad4977b8c921d9c9ca276`;
- projected-reference table SHA-256:
  `8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212`;
- frozen evaluator SHA-256:
  `6ab3a05f01fc0820ad03b05dfe238f84945d493cdcd66be6cd92b6ed5a26b923`;
- native-runtime evidence commit:
  `5834400b7e23cf76c6b8afa7047b8052b60ff3b7`;
- native BNO055 conversion source SHA-256:
  `ebdbafb1be185541604f7dde206aacbd325bbb0e8feaf66ef4a03d534f39d303`;
- native STS3215 conversion source SHA-256:
  `a52b5a1551dce7940aadbd1b6446b91a796d279875d77ee247e4ef1cd43b4aa8`;
- deployed soft-offset snapshot SHA-256:
  `298753fb30c658321161df50f668ad7ab25121a1958c4b7bbdb1c543caf06bff`.

Both source graphs retain their baked-in normalization, reference-residual
composition, measured hard-vector projection, actual-centered guard, exact x=0
deadband, and conservative left-ankle repair. The evaluated plant uses the
already-pinned P30 forward observer for `obs[83:97]` under both measured plant
fits. No source graph initializer, action, command, phase, reference, observer,
reset, actuator model, or behavior threshold may change.

## Frozen eval-only native quantizer

Create one eval-only wrapper for each source graph. The public ABI remains
`obs float32[1,115] + previous_action float32[1,14]` to
`continuous_actions float32[1,14] + previous_action_out float32[1,14]`.
The wrapper quantizes only values that are direct native hardware reads before
passing the resulting 115-vector to the unchanged source graph.

All arithmetic is float32 and ONNX `Round` (round-to-nearest, ties-to-even):

1. `obs[0:3]`, BNO055 gyro, to multiples of
   `pi / (180 * 16) rad/s`, exactly matching `gx / 16 deg/s` converted to
   radians by the native source.
2. `obs[3:6]`, BNO055 acceleration, to multiples of `0.01 m/s^2`, exactly
   matching native `raw / 100` conversion.
3. `obs[13:27]`, logical joint-position offset, through the STS3215 physical
   encoder grid `2*pi/4096 rad`. Reconstruct absolute physical position as
   `obs_offset + HOME_RAD + SOFT_OFFSET_RAD`, quantize `(physical + pi)` to the
   grid, then subtract `pi`, `SOFT_OFFSET_RAD`, and `HOME_RAD`.
4. `obs[27:41]`, logical joint velocity already scaled by `0.05`, to multiples
   of `(2*pi/4095)*0.05`, matching native speed conversion before the existing
   observation scale.
5. `obs[6:13]` and `obs[41:115]` remain bit-exact. Contacts at `97:99` must
   already be binary and remain bit-exact.

The frozen deployed soft-offset vector, in policy joint order, is:

```text
[0.0844, 0.0721, -0.0890, 0.0371, -0.0767, 0.0245, 0.0,
 -0.0890, -0.0399, 0.0951, -0.0476, 0.0660, 0.0798, 0.1887]
```

This is a finite-representation screen only. It does not model sensor bias,
noise, mounting error, sample age, packet loss, or real torso COM, and a pass
must not be reported as covering those axes.

## Required transform contract

Before any behavior cell is read, the contract must prove:

1. every frozen source and architecture hash above;
2. CPU-only ONNX Runtime and no available accelerator provider selected;
3. unchanged public ABI, source node/initializer identity, and output/state
   semantics after the quantizer prefix;
4. exact slice isolation and bit-exact identity for `obs[6:13]` and
   `obs[41:115]` over fixed boundary and deterministic pseudorandom vectors;
5. equality within `1e-7` to an independent NumPy implementation of all four
   quantization formulas, including negative values and half-grid controls;
6. binary contacts remain exact and nonbinary contact controls are rejected by
   the contract checker;
7. default-off/source inference remains bit-exact to each source graph;
8. x=0 still returns bit-exact zero action and state; and
9. chained state feedback is finite for at least 256 ticks at x=.080.

The transform and contract tools are frozen by name as
`tools/build_winner_v2_native_quantized_eval_policies.py` and
`tools/check_winner_v2_native_quantized_eval_contract.py`. Their hashes and the
two wrapper hashes must be recorded by the contract result before behavior.

## Frozen behavior matrix

Run exactly 16 CPU cells:

- checkpoints: `512000`, `1024000`;
- P30 observer only;
- plant fits: P30 and P31/34;
- commands: x=`0`, `.074`, `.077`, `.080`, with all other commands zero;
- seed: `167931544`;
- deterministic `home-support` reset, phase index 0;
- 600 ticks at 50 Hz, 10 physics substeps per control tick;
- flat-terrain backlash task;
- no training noise, extra delay, push, terrain, dynamics perturbation, gain,
  head overlay, host filter, or second action projection.

Every cell must record the source and wrapper hashes, plant/observer hashes,
CPU provider, exact quantizer constants, quantized slice readback, full 115-D
pre/post input vectors, action/state, sent/applied/actual targets, contacts,
tracking, saturation, and measured rate/envelope excess.

Each checkpoint passes only if all eight of its cells complete 600 ticks,
retain the established x=0 behavior and bilateral moving gait, pass the
unchanged candidate gate, have zero measured action saturation, zero rate
excess, zero actuator-envelope excess, and pitch-chain tracking p95
`<=0.20 rad`. Both checkpoints must pass all cells before selection; a single
checkpoint failure closes the screen without promoting its sibling.

## Frozen selection rule

If and only if both checkpoints pass every cell, select exactly one original
source graph, not its eval-only quantized wrapper, by:

1. lower worst pitch-chain tracking p95 across its eight cells;
2. higher minimum moving-command mean local vx across its six moving cells;
3. fixed tiebreak `512000`, then `1024000`.

Metrics are compared as stored float64 aggregates with no rounding before
ranking. Training reward, simulator reward, prior behavior tables, graph step,
visual preference, and runtime implementation convenience have zero selection
weight.

Decision tokens are exactly:

- `SELECT_WINNER_V2_512000_NATIVE_QUANTIZED`;
- `SELECT_WINNER_V2_1024000_NATIVE_QUANTIZED`;
- `HOLD_NATIVE_QUANTIZED_PERSISTENCE_NO_SELECTION`; or
- `INVALID_NATIVE_QUANTIZED_SELECTION_STUDY`.

## Required artifacts and authority

- `WINNER_V2_NATIVE_QUANTIZED_EVAL_CONTRACT_20260719.md`;
- `winner_v2_native_quantized_eval_contract.json`;
- per-cell JSON/MD and JSONL traces under
  `outputs/analysis/winner_v2_native_quantized_checkpoint_selection/`;
- `WINNER_V2_NATIVE_QUANTIZED_CHECKPOINT_SELECTION_RESULT_20260719.md`;
- `winner_v2_native_quantized_checkpoint_selection_result.json`.

A valid selection may populate `SELECTED_ONNX_SHA256` in a new policy handoff
response and authorize independent CPU runtime-v2 acceptance of that exact
binary. It does not authorize Gate 5, staging, installation, SSH/RDK access,
robot use, torque, motors, deployment, a COM model correction, or robot
clearance. The 46-field as-built torso COM/inertia measurement remains an
independent mandatory blocker.

CPU simulation only. No training, Colab, hosted allocation, local GPU/iGPU,
RDK-X5, or robot access is authorized by this preregistration.
