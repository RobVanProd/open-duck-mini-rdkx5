# Phase 2 Command-Gated Compact Warm-Start

This package contains the deployable-shape ONNX command-gated candidate that
resolved the compact zero-command semantics blocker.

- candidate: `candidate.onnx`
- sha256: `f3d5d735e96cf88bfe037bd4c6c1289eebc5d25bcc7722416f62dcee292866d0`
- command gate: `abs(obs[6]) <= 0.02`
- low-command branch: zero-action/home policy
- high-command branch: seed-7-weighted parent-pair lateral student

Compact corrected-bridge rough+push results:

- `x=0.08`: `5/5` pass, zero velocity-envelope excess
- `x=0.0`: `5/5` pass, mean vx `0.0008` m/s, zero velocity-envelope excess

This is an offline Phase 2 domain-randomization warm-start candidate, not robot
approval.
