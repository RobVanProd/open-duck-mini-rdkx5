# Phase 2 Parent-Pair Lateral Seed-7 Weighted Student Decision

status: `HOLD_COMMAND_SEMANTICS_X0`

Offline sim/training analysis only. No robot tests, SSH, deploy, grounded replay, runtime behavior change, or domain-randomized training were performed.

## Summary

The parent-pair prefix-lateral router produced a passing eval-only source. A seed-7-weighted rich-context phase-modulated student distilled that source into a single ONNX parent.

It cleared the compact rough+push `x=0.08` corrected-bridge gate on all five compact seeds, but it failed the `x=0.0` command-semantics gate. Phase 2 domain-randomized training remains blocked until zero-command behavior is preserved.

## Artifacts

- candidate: `outputs/analysis/phase2_parent_pair_lateral_seed7_weighted_student/candidate.onnx`
- fit report: `outputs/analysis/phase2_parent_pair_lateral_seed7_weighted_student.json`
- source manifest: `outputs/analysis/phase2_parent_pair_lateral_seed7_weighted_manifest.json`
- source manifest dataset_id: `cbca4cd9878899ea`
- x=0.08 gate: `outputs/analysis/phase2_parent_pair_lateral_seed7_weighted_student_gate.json`
- x=0.0 gate: `outputs/analysis/phase2_parent_pair_lateral_seed7_weighted_student_x0_gate.json`

## Fit

- MAE: `0.002721`
- p95 abs error: `0.006911`
- target-rate p95: `1.422418` rad/s
- ONNX max abs error: `0.000000298`

## x=0.08 Compact Gate

pass_count: `5/5`

| seed | status | samples | mean vx | track ratio | pitch p95 | base min | p95 vel excess |
|---:|---|---:|---:|---:|---:|---:|---:|
| `0` | `PASS_CANDIDATE_SIM_GATE` | `750` | `0.0272` | `0.3403` | `0.1737` | `0.1581` | `0.0000` |
| `1` | `PASS_CANDIDATE_SIM_GATE` | `750` | `0.0254` | `0.3170` | `0.1876` | `0.1581` | `0.0000` |
| `2` | `PASS_CANDIDATE_SIM_GATE` | `750` | `0.0269` | `0.3367` | `0.1894` | `0.1581` | `0.0000` |
| `6` | `PASS_CANDIDATE_SIM_GATE` | `750` | `0.0232` | `0.2896` | `0.1917` | `0.1581` | `0.0000` |
| `7` | `PASS_CANDIDATE_SIM_GATE` | `750` | `0.0265` | `0.3311` | `0.1724` | `0.1581` | `0.0000` |

## x=0.0 Command-Semantics Gate

pass_count: `3/5`

| seed | status | samples | termination | mean vx | pitch p95 | base min | p95 vel excess |
|---:|---|---:|---|---:|---:|---:|---:|
| `0` | `PASS_CANDIDATE_SIM_GATE` | `750` | `duration_complete` | `0.0235` | `0.1964` | `0.1581` | `0.0000` |
| `1` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `147` | `fall_or_nan` | `0.1431` | `0.9095` | `0.0048` | `0.0000` |
| `2` | `PASS_CANDIDATE_SIM_GATE` | `750` | `duration_complete` | `0.0295` | `0.1909` | `0.1581` | `0.0000` |
| `6` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `206` | `fall_or_nan` | `0.1107` | `0.7060` | `-0.0007` | `0.0000` |
| `7` | `PASS_CANDIDATE_SIM_GATE` | `750` | `duration_complete` | `0.0259` | `0.1725` | `0.1581` | `0.0000` |

## Decision

- `x=0.08` behavior preservation is now achievable by a single ONNX parent on the compact rough+push screen.
- The same parent is not command-safe: at `x=0.0`, seeds `1` and `6` fall and the pass seeds still drift forward.
- Do not start Phase 2 domain randomization from this parent yet.
- Next aligned branch: add a command-gated zero-command behavior path or include x=0.0 traces in the parent manifest, then re-run both compact gates.
