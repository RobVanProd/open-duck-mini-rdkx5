# Winner-v13 support-controller HOLD attribution

- Status: `PASS_WINNER_V13_SUPPORT_CONTROLLER_HOLD_ATTRIBUTION`
- Decision: `KEEP_GATE_HOLD_CORRECT_REPORTING_BEFORE_CAUSAL_REPAIR`
- Half/final physical failures: `15 / 11`
- Sensor/transport failures: `0`
- New training / behavior / robot access: `0 / 0 / 0`

The gate remains a real HOLD. Every physical failure is an early
negative-torso-X pitch-limit exit; both checkpoints still preserve all
16 context separations and all 32 heldout repeats exactly.

Separately, the gate imported the legacy raw-response scoring helper
for a Stage-1 head trained in normalized coordinates. That produces the
~4e10 predictor aggregate, especially from the two constant contact
dimensions. It is reporting-only: ONNX supplies the action, the recurrent
hidden-state equation is identical, and predictor output never enters the
physics path. A versioned scorer must correct this before the next causal
diagnostic; the frozen gate result itself is not rewritten.

The flat-transport kernel is not selected because context separation
passes and the failures happen by ticks 28-68, not after long-horizon
information decay.
