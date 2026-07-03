# Phase 2 z=0.0025 BEST x0 / rate1p9 x0.08 Command-Gated Support Screen

status: `HOLD_BEST_X0_SUPPORT_REQUIRES_OVER_ENVELOPE_TRANSIENT`

superseded_for_current_z0025_baseline_by:
`outputs/analysis/PHASE2_Z0025_COMMAND_GATED_BESTREC70_RATE1P9_TARGETLIMITED0999_STRONGER_PUSH_DECISION_20260701.md`

## Summary

A command-gated diagnostic policy confirmed that the current z=0.0025
positive-command parent can be combined with BEST's active zero-command support
behavior in one ONNX graph, but BEST's zero-command support component is not
corrected-envelope clean.

The full-strength command-gated policy stabilizes the hard `x=0.0`, seed-5
rough reset pocket for the 2-second short gate, and the `x=0.08` branch behaves
like the rate1p9 parent. However, the zero-command support branch uses the
known BEST instantaneous target-velocity spike. Scaling BEST down enough to
reduce that spike causes the hard reset to fall; scales that survive still
exceed the corrected envelope.

This was offline sim/eval only. No robot test, SSH, deploy, grounded replay,
training, runtime behavior change, or policy overwrite was performed.

## Inputs

- low/zero-command policy: `policy/BEST_WALK_ONNX_2.onnx`
- high/positive-command policy: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0_contactphase_rate1p9_bc_candidate/candidate.onnx`
- composed candidate: `outputs/analysis/phase2_z0025_best_x0_rate1p9_x008_command_gated_candidate/candidate.onnx`
- composed candidate sha256: `f4877984086b687206a79ae259bbcf30b393d05a05e58a34cb1d0e55351036ba`
- bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0025`
- bridge_mode: `fitted`
- jax_platform: `cpu`

The command gate is:

```text
high_weight = clip(abs(obs[6]) / 0.08, 0, 1)
```

So `x=0.0` uses the low/BEST branch and `x=0.08` uses the high/rate1p9 branch.

## Full-Strength Command-Gated Result

Artifacts:

- `outputs/analysis/PHASE2_Z0025_BEST_X0_RATE1P9_X008_GATED_X0_SEED5.md`
- `outputs/analysis/phase2_z0025_best_x0_rate1p9_x008_gated_x0_seed5.json`
- `outputs/analysis/PHASE2_Z0025_BEST_X0_RATE1P9_X008_GATED_X008_SEED5.md`
- `outputs/analysis/phase2_z0025_best_x0_rate1p9_x008_gated_x008_seed5.json`

| command | seed | status | samples | mean vx | track ratio | base min | max pitch vel p95 | p95 vel excess | max vel excess | tracking p95 |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `0.00` | 5 | `HOLD_CANDIDATE_TRACKING` | 100 | 0.0148 | NA | 0.1456 | 4.0629 | 1.3673 | 2.9900 | 0.2363 |
| `0.08` | 5 | `HOLD_CANDIDATE_TRACKING` | 100 | 0.0401 | 0.5011 | 0.1464 | 1.9059 | 0.0000 | 0.0000 | 0.2003 |

Interpretation:

- The command split works mechanically.
- The high-command branch preserves the current parent behavior on this short
  seed-5 check.
- The zero-command branch catches the hard reset but is not promotable because
  it violates the corrected envelope.

## Scaled BEST Zero-Command Screen

Artifacts:

- `outputs/analysis/PHASE2_Z0025_SCALED_BEST_X0_RATE1P9_X008_SCREEN_X0_SEED5.md`
- `outputs/analysis/phase2_z0025_scaled_best_x0_rate1p9_x008_screen_x0_seed5.json`
- `outputs/analysis/PHASE2_Z0025_SCALED_BEST_X0_RATE1P9_X008_SCREEN_X0_SEED5_MIDPOINT.md`
- `outputs/analysis/phase2_z0025_scaled_best_x0_rate1p9_x008_screen_x0_seed5_midpoint.json`

| BEST x0 scale | candidate sha256 | status | samples | mean vx | base min | max pitch vel p95 | p95 vel excess | max vel excess | tracking p95 |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 0.50 | `c74f7f218ce5104663f35b80d904ce9f6dde6641982e5fe66e144d84eaac4ca5` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 60 | -0.2724 | 0.0486 | 2.1520 | 0.0000 | 1.2818 | 0.1677 |
| 0.60 | `d137b8551b465bb3a25316ef7ad4ede4f6c1630f36669e4309604a56947bde73` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | -0.2871 | 0.0633 | 4.2458 | 1.7458 | 2.7400 | 0.2123 |
| 0.65 | `785d9c06eca045c46256b701b199b3870744a2ca2aea52476f7468a07cf2f56c` | `HOLD_CANDIDATE_TARGET_VELOCITY` | 100 | 0.0137 | 0.1458 | 3.1015 | 0.3515 | 2.7400 | 0.1937 |
| 0.70 | `6584bf9a518dc83402dee21a3c75a59fa08a03773062886590cb246d725b8fa3` | `HOLD_CANDIDATE_TRACKING` | 100 | 0.0109 | 0.1457 | 3.3804 | 0.6304 | 2.7400 | 0.2067 |

## Decision

Do not promote the BEST zero-command command-gated policy or the scaled variants.

The result is still useful: it proves the hard `x=0.0`, seed-5 rough reset
pocket needs an active support catch rather than static zero action, and that
the existing BEST catch is near the boundary between falling and over-envelope
support. A deployable repair should learn or synthesize an envelope-clean
active support recovery in the current rough-terrain reset distribution, not
reuse BEST's spike as the final component.

## Reconciliation With Existing Target-Limited Candidate

After this bounded screen, the existing target-limited command-gated candidate
was re-checked:

- candidate: `outputs/analysis/phase2_z0025_command_gated_bestrec70_rate1p9_targetlimited0999_candidate/candidate.onnx`
- candidate_sha256: `6ba399528c6bc7543e0a5a3a43c30b0804357a4b98e21d723cbb5188e446b2a2`
- decision: `outputs/analysis/PHASE2_Z0025_COMMAND_GATED_BESTREC70_RATE1P9_TARGETLIMITED0999_STRONGER_PUSH_DECISION_20260701.md`

That candidate already passes the current `z=0.0025` rough-terrain stronger-push
gate at both `x=0.0` and `x=0.08` for all eight seeds, with no corrected
velocity-envelope excess:

- `x=0.0`: 8/8 duration complete, mean `vx=-0.0004 m/s`, max pitch vel p95 mean `2.7605 rad/s`
- `x=0.08`: 8/8 duration complete, mean track ratio `0.3821`, max pitch vel p95 mean `1.9132 rad/s`

So the weaker BEST-only support screen should not become the next parent.
For the current rung, the target-limited command-gated candidate is the stronger
z=0.0025 baseline. Its documented blocker is the seed-5 support cliff at
`z=0.0026+`, not the already-solved z=0.0025 support pocket.

Recommended next branch:

```text
Use the target-limited command-gated candidate as the current z=0.0025 baseline
and target the smallest failing terrain step, z=0.0026, with seed-5 support
survival as the first gate.
```

Do not run full A100 training, robot validation, or another global scalar
progress-pressure run from these diagnostic command-gated policies.
