# T7 universal response-support preregistration

- Status: `PREREGISTERED_T7_UNIVERSAL_RESPONSE_SUPPORT`
- Contract SHA-256: `bbdd7abe35de8ed5b9d57cb64aa89793f761468f2b35b6f96d21fa6d95ac4a62`
- Cells: `12` (`3 configurations × 2 fits × 2 exact repeats`)
- Training: `0 steps`
- Robot/RDK-X5 access: `forbidden`

## Causal question

Does the frozen V91/V96 universal target keep the exact current composed robot supported for 600 ticks while producing a repeatable, configuration-sensitive 64-D response context?

## Historical mismatch

The V98/V102 training wrapper computes hidden state from the frozen calibrator weights but replaces the action head with the V91 universal target before the graph rate boundary.

The V103 formal evaluator instead executed the calibrator ONNX calibration_actions output directly. Therefore its negative-X prefix failures did not test the training action semantics.

T7 therefore runs the preserved universal-target graph directly. It does not treat the old V103 prefix failure as evidence against this mechanism.

## Decision

- Pass: authorize one separately preregistered, zero-training, state-coherent support-to-locomotion handoff screen; do not authorize hosted training yet.
- Fail: close transfer of the V91/V96 universal response-support mechanism to the current stack; do not train this mechanism.

A pass does not authorize training, Gate 5, robot access, torque, motion, or deployment.
