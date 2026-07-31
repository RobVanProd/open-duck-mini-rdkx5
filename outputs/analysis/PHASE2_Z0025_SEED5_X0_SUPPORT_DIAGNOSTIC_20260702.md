# Phase 2 z=0.0025 Seed-5 x=0 Support Diagnostic

status: `HOLD_RESET_SUPPORT_COLLAPSE_DIAGNOSED`
generated_at: `2026-07-02T07:45:00Z`

This is an offline trace diagnostic. It did not train, SSH, deploy, run robot
tests, touch hardware, or change runtime behavior.

## Question

Why does the z=0.0025 contact+phase rate1p9 candidate pass x=0.08 for all
eight seeds but fail x=0.0 on seed 5?

## Trace Inputs

- passing baseline: `outputs/analysis/phase2_z0025_x0_seed5_support_diag/baseline_seed0_x000/parent_z0025_contactphase_rate1p9/seed_000/trace.jsonl`
- failing seed: `outputs/analysis/phase2_z0025_x0_seed5_recovery_dagger_iter0/rollouts_x0/student/seed_005/trace.jsonl`
- passing positive-command seed: `outputs/analysis/phase2_z0025_x0_seed5_recovery_dagger_iter0/rollouts_x008/student/seed_005/trace.jsonl`

## Key Comparison

| case | status | samples | first contacts | first reverse | first low height | base min | mean vx | pitch min |
|---|---|---:|---|---:|---:|---:|---:|---:|
| seed0 x=0.0 | `PASS_SHORT_BASELINE` | 100 | `[0, 1]`, then double support | tick 0 transient | NA | 0.1520 | -0.0015 | -0.0327 |
| seed5 x=0.0 | `REVERSE_HEIGHT_COLLAPSE` | 43 | `[0, 0]` | tick 8 | tick 39 | 0.0575 | -0.3468 | -1.5333 |
| seed5 x=0.08 | `PASS_SHORT_POSITIVE` | 100 | `[0, 0]` | none sustained | NA | 0.1464 | 0.0401 | -0.2215 |

At z=0.0025, seed 5 starts with both feet off contact. The same reset is
recoverable under positive command for at least the 2-second short gate, but the
x=0.0 policy collapses into backward motion and height loss before one second.

## Tick-Level Evidence

### Passing seed0 x=0.0

| tick | vx | base height | pitch | contacts | foot z |
|---:|---:|---:|---:|---|---|
| 0 | -0.0609 | 0.1520 | 0.0071 | `[0, 1]` | `[0.0250, -0.0021]` |
| 5 | -0.0337 | 0.1655 | -0.0132 | `[1, 1]` | `[0.0045, 0.0060]` |
| 39 | -0.0063 | 0.1619 | 0.0012 | `[1, 1]` | `[0.0042, 0.0044]` |
| 99 | 0.0025 | 0.1607 | -0.0051 | `[1, 1]` | `[0.0041, 0.0043]` |

### Failing seed5 x=0.0

| tick | vx | base height | pitch | contacts | foot z |
|---:|---:|---:|---:|---|---|
| 0 | 0.0154 | 0.1500 | -0.0074 | `[0, 0]` | `[0.0235, 0.0555]` |
| 5 | 0.1293 | 0.1694 | -0.1819 | `[1, 0]` | `[0.0049, 0.0081]` |
| 8 | -0.0791 | 0.1715 | -0.2241 | `[1, 1]` | `[0.0071, 0.0041]` |
| 39 | -1.1838 | 0.1130 | -1.2073 | `[1, 1]` | `[0.0351, 0.0355]` |
| 42 | -1.4854 | 0.0575 | -1.5333 | `[0, 1]` | `[0.0403, 0.0406]` |

## Pitch-Chain Evidence

The x=0.0 failure is not target-rate bound:

| case | max pitch target-rate p95 | max pitch tracking p95 |
|---|---:|---:|
| seed0 x=0.0 | 0.3002 rad/s | 0.0742 rad |
| seed5 x=0.0 | 0.5828 rad/s | 0.2106 rad |
| seed5 x=0.08 short | 1.9072 rad/s | 0.2003 rad |

The failing x=0.0 seed has low commanded target velocity but high tracking
error and early reverse/height collapse. The failure is therefore a reset/support
recovery problem, not an actuator-envelope demand problem.

## Decision

```text
HOLD_RESET_SUPPORT_COLLAPSE_DIAGNOSED
```

The seed-5 zero-command failure should be treated as an unsupported rough-reset
recovery problem. Zero-action relabels are structurally weak here because the
student is not in a settled standing state when the failure begins.

Next repair branches should target active support recovery from unsupported or
partially-supported reset states, while preserving x=0 command semantics after
the base has recovered. Do not treat another static zero-action relabel as a
new mechanism.
