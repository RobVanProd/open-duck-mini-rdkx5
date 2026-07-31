# Winner-v6 Dynamic Calibration Interface Preregistration

status: `PREREGISTERED_PENDING_RUNTIME_REVIEW`

JSON SHA-256: `a66ff7138bdc474c5bd6d0a8899eba041d00305a3d3bd38fc13b0c00e4c3007e`

Winner-v5 closed the one-shot threshold/fixed-pose controller. This proposal uses a separate 250-tick recurrent support calibrator whose action changes every tick and whose final 64-D learned response state conditions locomotion. It uses only deployable sensor/action history—no mass, COM, dimensions, component inventory, scales, or calipers.

The frozen runtime-v1 101x14 path remains unchanged. This is a default-off, versioned runtime-v2 schema request only. No training or implementation is authorized until runtime reviews the exact graph, state, phase, handoff, pause, and fail-closed semantics.
