# Phase 2 Iter2 Right-Ankle Limit198 Rate165 Candidate

status: `PASS_OFFLINE_CORRECTED_BRIDGE_CANDIDATE_READY`

This candidate is an offline corrected-bridge Phase 2 baseline. It was trained
from the live-oracle iteration-2 aggregate manifest after applying a surgical
right-ankle label clamp at `1.98 rad/s`.

It preserves the deployed policy contract:

```text
obs[1,101] -> continuous_actions[1,14]
```

## Files

```text
candidate.onnx
candidate_mlp.npz
SHA256SUMS
```

## Hashes

- ONNX:
  `eacc7c69e517b7cef32daeedeb6b110cd766e129183b071a7254f6fa0af5c1e2`
- NPZ:
  `053accd4d916c6ec0286ff1a4eadea3b285af4c8381b27689f39b10fcfbaa5ec`

## Gate Evidence

- x=0.08 corrected bridge:
  `outputs/analysis/PHASE2_ITER2_RIGHT_ANKLE_LIMIT198_RATE165_STUDENT_X008_GATE.md`
- x=0.0 corrected bridge:
  `outputs/analysis/PHASE2_ITER2_RIGHT_ANKLE_LIMIT198_RATE165_STUDENT_X0_GATE.md`
- decision:
  `outputs/analysis/PHASE2_ITER2_RIGHT_ANKLE_LIMIT198_RATE165_CANDIDATE_DECISION.md`

## Scope

Offline sim candidate only. This file does not authorize robot tests, SSH,
deployment, grounded replay, or runtime behavior changes.
