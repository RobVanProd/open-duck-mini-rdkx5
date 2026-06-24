# Movement Bootstrap V12 A100 Phase 1 Result

status: `HOLD_PHASE_FREEZE_OR_LOW_PROGRESS`

## Run

- PR head: `79c0e21`
- Colab session: `open-duck-a100`
- candidate: `movement_bootstrap_v12_a100_gatefix`
- phase: `phase1_progress_failure_low_command`
- training platform: A100 / JAX CUDA
- JAX pin: `0.7.2`
- robot_touched: `false`
- remote top-level exit: `1` because the staged phase gate stopped the run

## Phase 1 Training

- requested timesteps: `220000`
- final checkpoint step: `245760`
- final ONNX: `2026_06_24_051959_245760.onnx`
- final ONNX sha256: `f62dcee573572f4bdd96ed5b0c905f4d14e7fb2270ce108288f7eae84a684731`
- command range: `x = 0.04..0.06`
- fitted actuator bridge: enabled
- command-progress failure during training: enabled

## Phase Gate

The phase-1 ONNX was evaluated at `x=0.08` for 5 seconds with the fitted bridge.

- candidate_gate_status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
- termination: `duration_complete`
- forward tracking ratio: `0.0453689912421396`
- max action saturation pct: `0.0`
- max pitch tracking p95 rad: `0.0726340889930725`
- max sent target velocity p95 rad/s: `0.17286226153373718`
- max abs body pitch p95 rad: `0.14751879626581804`
- min base height m: `0.15368202328681946`
- min reward mean: `0.53465570884943`

## Interpretation

V12 phase 1 did not produce a usable forward policy. The candidate stayed upright for
the short gate and stayed within the actuator envelope, but it moved too little:
tracking ratio was about `0.045`, far below the `0.25` minimum. The corrected phase
gate stopped the staged curriculum before phase 2 could consolidate the no-motion
behavior.

This keeps the current diagnosis intact: V11/V12-style hard progress pressure plus
command-progress termination still falls into a stable low-motion solution under the
fitted actuator bridge. The next offline training change should target reward credit
assignment/episode mechanics more directly, not robot validation.

## Local Artifacts

Full phase artifacts are in:

`outputs/analysis/movement_bootstrap_v12_a100_phase1_gatefix/`

Large/raw files in that directory are kept local unless explicitly promoted.
