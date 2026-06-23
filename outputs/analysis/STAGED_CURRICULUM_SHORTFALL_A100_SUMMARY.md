# Staged Curriculum Shortfall A100 Summary

generated_at: `2026-06-23`

## Executive Summary

The full three-phase staged curriculum with the explicit `forward_shortfall`
term completed on a Colab A100 CUDA backend, but the final policy is **not a
robot candidate**.

The run confirms the current offline training failure mode:

```text
actuator-safe / low target velocity / stable
but still near standstill for x=0.08
```

The result does not justify robot motion, suspended validation, deployment, or
runtime tuning.

## Backend And Artifact

- backend: Colab A100-SXM4-40GB / CUDA
- JAX backend: `gpu`
- artifact bundle:
  `outputs/analysis/colab_cli/open-duck-a100a-staged-curriculum-20260623T143239Z/open_duck_colab_cli_staged-curriculum_20260623T143249Z_artifacts.final.tar.gz`
- artifact bundle sha256:
  `cdab6dc48b5ab52127c051a4756337915675a68f992b9b3f806d6f56b906344e`
- final policy sha256:
  `5b7d67d2f3bc8f4fc27f7cda0f8cb5af651915deada70a68cf3031e6a8a148c6`
- final policy source path:
  `/content/open_duck_staged_curriculum_cli/03_phase3_fitted_bridge_consolidation/smoke_20260623T145142Z_gpu/2026_06_23_145958_307200.onnx`

Training phase elapsed times:

| phase | elapsed |
|---|---:|
| phase 1 | `579.2 s` |
| phase 2 | `522.9 s` |
| phase 3 | `506.6 s` |
| total training | `1608.7 s` |

## Candidate Gates

### `x=0.0`

Status: `HOLD_CANDIDATE_TRACKING`

| metric | value | threshold |
|---|---:|---:|
| max action saturation | `0.0000 %` | `1.0000 %` |
| max pitch tracking p95 | `0.0851 rad` | `0.0800 rad` |
| max sent target velocity p95 | `0.4982 rad/s` | `2.5000 rad/s` |
| max abs body pitch p95 | `0.0947 rad` | `0.2500 rad` |
| min base height | `0.1535 m` | `0.1200 m` |
| min reward mean | `0.4851` | `0.3000` |
| max abs forward velocity error | `0.0005 m/s` | n/a |

Interpretation: the candidate is stable and low-velocity at zero command, but
one pitch-chain tracking gate narrowly fails.

### `x=0.08`

Status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`

| metric | value | threshold |
|---|---:|---:|
| max action saturation | `0.0000 %` | `1.0000 %` |
| max pitch tracking p95 | `0.0958 rad` | `0.0800 rad` |
| max sent target velocity p95 | `0.4080 rad/s` | `2.5000 rad/s` |
| max abs body pitch p95 | `0.2177 rad` | `0.2500 rad` |
| min base height | `0.1458 m` | `0.1200 m` |
| min reward mean | `0.4684` | `0.3000` |
| min forward command tracking ratio | `0.0145` | `0.2500` |
| max abs forward velocity error | `0.0788 m/s` | n/a |

Mode tracking ratios:

| mode | mean local forward velocity | command tracking ratio |
|---|---:|---:|
| vanilla | `0.0012 m/s` | `0.0145` |
| fitted | `0.0017 m/s` | `0.0211` |
| stress | `0.0017 m/s` | `0.0216` |

Interpretation: the policy remains near standstill under a nonzero forward
command. The `forward_shortfall` curriculum did not escape the safe standstill
optimum.

## Decision

Do not run this policy on the robot.

Next offline work should focus on a stronger locomotion bootstrap or motion
prior instead of simply increasing smoothness/actuator penalties:

- verify the `forward_shortfall` term is visible in training/eval reward
  metrics
- consider warm-start or imitation from `BEST_WALK_ONNX_2` movement structure
- add an episode-level displacement or minimum-progress requirement
- keep actuator constraints staged rather than harsh from the first phase
- preserve the existing sim gates before any robot validation

No robot tests, SSH, deployment, runtime behavior changes, or policy overwrite
were performed for this result.
