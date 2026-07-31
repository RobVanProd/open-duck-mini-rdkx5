# Oracle COM Sequence-Rescue Queue-Restore Correction

Date: 2026-07-16 (America/New_York)

The first Stage-B invocation stopped during the first state's first candidate,
before a horizon result or per-state output was produced. The frozen actuator
bridge uses mutable Python lists for its delay queues. The state artifact is
JSON, and the search restore path incorrectly converted those lists to NumPy
arrays; `ActuatorBridgeModel.step` therefore failed on `queue.append`.

The sole correction restores each JSON queue as a Python list. Queue values,
lengths, order, bridge parameters, search basis, amplitudes, beam width,
horizons, constraints, nominal envelope, ranking, advancement rule, and every
other preregistered variable are unchanged. No search outcome was available to
inform this correction.

Corrected search-tool SHA-256:
`fcaf9fb583f999fe48f363064f3aa5fd38d4b51a5ee52b320d89a36c44b1523e`.

This artifact authorizes only rerunning the already-frozen Stage-B screen with
the corrected tool hash. It does not authorize Stage C, training, hosted
compute, GPU/iGPU, RDK-X5, robot access, or deployment.
