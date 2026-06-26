# Deployable Source-VX Policy Validation

status: `HOLD_DEPLOYABLE_POLICY_TRACKING_RATE_TRADEOFF`

This is an offline validation artifact. It did not train, deploy, SSH, run
robot tests, or change robot runtime behavior.

## Scope

The source-VX selector already proved in-envelope forward walking is possible
through the fitted actuator bridge, but the selector is non-deployable. This
artifact validates the exported DAgger-2 neural ONNX candidates before any PPO
warm-start or robot discussion:

```text
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_candidate/candidate.onnx
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_rate_reg_candidate/candidate.onnx
```

Validation used:

```text
command: straight x=0.08
bridge: fitted
duration: 10s
seeds: 0-7
platform: local CPU MJX/JAX
```

## Default Task Strict Gate

Artifact fragments:

```text
outputs/analysis/deployable_source_vx_policy_validation_fitted/
outputs/analysis/deployable_source_vx_policy_validation_fitted_rate_reg_tail/
```

The first run used the default `flat_terrain` task. It is stricter than the
DAgger smoke task and confirms that neither candidate is promotion-ready:

| policy | runs | falls | duration complete | mean vx | mean track ratio | max sent vel p95 | max tracking p95 | result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `dagger2` | 8 | 2 | 6 | 0.0202 | 0.2526 | 3.9048 | 0.3058 | `HOLD` |
| `dagger2_rate_reg` | 8 | 2 | 6 | 0.0157 | 0.1967 | 3.0938 | 0.3134 | `HOLD` |

Interpretation: the default-task standard evaluator exposes low progress,
fall/termination, and tracking failures. This is useful as a harsh baseline,
but the task does not match the source-VX/DAgger smoke path.

## Task-Matched Backlash Gate

Primary artifact:

```text
outputs/analysis/DEPLOYABLE_SOURCE_VX_POLICY_VALIDATION_FITTED_BACKLASH.md
outputs/analysis/deployable_source_vx_policy_validation_fitted_backlash.json
```

Task-matched `flat_terrain_backlash` removes the fall/termination issue:

| policy | runs | falls | duration complete | mean vx | mean track ratio | sent vel p95 range | tracking p95 range | result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `dagger2` | 8 | 0 | 8 | 0.0433 | 0.5409 | 4.5943-4.8522 | 0.2626-0.2650 | `HOLD_CANDIDATE_TRACKING` |
| `dagger2_rate_reg` | 8 | 0 | 8 | 0.0364 | 0.4550 | 3.6172-3.6824 | 0.2419-0.2472 | `HOLD_CANDIDATE_TRACKING` |

The task-matched result is better than the default task result:

```text
both candidates complete all eight seeds
dagger2 preserves command tracking better
rate-reg lowers target rate into the fitted-envelope region
both still exceed the tracking gate by a large margin
```

## Decision

Do not promote either ONNX candidate to robot validation.

Do not run stress-bridge validation yet. The fitted-bridge gate already holds
on pitch-chain tracking, so stress validation would only confirm a known hold
at higher cost.

The useful split is:

```text
dagger2:
  better forward progress
  target rate too high, 4.59-4.85 rad/s
  tracking p95 about 0.263 rad

dagger2_rate_reg:
  target rate closer to fitted envelope, 3.62-3.68 rad/s
  forward progress weaker
  tracking p95 still about 0.242-0.247 rad
```

The next deployable-policy branch should not tune the non-deployable selector.
It should target the neural student tracking/rate tradeoff directly:

1. Use the DAgger-2/rate-reg candidates as warm-start evidence, not as robot
   candidates.
2. Expand on-policy selector/student rollouts where the neural policy visits
   off-teacher states.
3. Relabel those states with the source-VX selector or a safer successor.
4. Add closed-loop tracking-aware loss or PPO fine-tuning with the fitted bridge
   active.
5. Re-run the task-matched fitted gate before any stress bridge or robot gate.

## Stop Rules

- No robot validation from these candidates.
- No deployment.
- No stress gate until fitted tracking improves.
- No relaxed actuator envelope.
- No more source-VX selector knob tuning unless it is needed to relabel a
  specific student-visited state distribution.
