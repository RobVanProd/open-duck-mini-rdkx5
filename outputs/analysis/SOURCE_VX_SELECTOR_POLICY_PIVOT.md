# Source-VX Selector Policy Pivot

status: `PLAN_DEPLOYABLE_POLICY_VALIDATION_AND_WARMSTART`

This is an offline decision artifact. It does not train, deploy, SSH, run robot
tests, or change robot runtime behavior.

## Executive Summary

The source-VX selector proved that in-envelope forward walking is achievable in
simulation through the fitted actuator bridge:

```text
artifact: outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_SOURCE_VX_BLEND080_100_SRCVX002_ALT_EXCLUDE_SEED4_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
command: straight x=0.08
duration: 10 s
moving seeds: 8 / 8
terminated seeds: 0 / 8
track ratio range: 0.5491-0.6172
sent-target velocity p95 range: 2.2569-2.3622 rad/s
joint tracking p95 range: 0.1809-0.1863 rad
```

That result kills the morphology-wall hypothesis for the current offline sim
proxy: forward motion exists across all eight seeds while staying inside the
measured actuator bridge target-rate budget.

The caveat is equally important: the source-VX selector is a diagnostic lookup
and blend over teacher windows, not a deployable learned policy. It has done
its job. The next branch should not refine the selector further by default.

## Deployable Policy Evidence

Early plain MLP distillation failed:

```text
artifact: outputs/analysis/SOURCE_VX_SELECTOR_TRACE_MLP128_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: HOLD_BC_REPLAY_TERMINATED
result: all seeds fall/progress-fail with reverse velocity and high target rate
```

Later DAgger relabeling changed that picture. The DAgger-2 128x128 MLP passed
the 10-second fitted-bridge smoke and was exported to ONNX:

```text
artifact: outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER2_MLP128_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
exported ONNX: outputs/analysis/source_vx_selector_trace_dagger2_mlp128_candidate/candidate.onnx
moving seeds: 8 / 8
terminated seeds: 0 / 8
track ratio range: 0.5208-0.6182
sent-target velocity p95 range: 2.1174-2.1601 rad/s
```

The rate-regularized DAgger-2 MLP also passed the same fitted-bridge smoke:

```text
artifact: outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER2_MLP128_RATE_REG_ONNX_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
exported ONNX: outputs/analysis/source_vx_selector_trace_dagger2_mlp128_rate_reg_candidate/candidate.onnx
moving seeds: 8 / 8
terminated seeds: 0 / 8
track ratio range: 0.4124-0.5334
sent-target velocity p95 range: 2.1256-2.1971 rad/s
```

So the current truth is not "MLP distillation always fails." It is:

```text
early MLP: failed
DAgger-2 MLP: fitted-bridge smoke pass, ONNX exported
DAgger-2 rate-reg MLP: fitted-bridge smoke pass, ONNX exported
strict deployment-grade validation: still pending
```

## Current Decision

Stop optimizing the non-deployable source-VX selector as the primary path.

Promote the workstream to deployable-policy validation:

1. Validate the DAgger-2 and DAgger-2 rate-reg ONNX candidates under the same
   task, command, fitted-bridge, stress-bridge, and multi-seed gates.
2. Compare them against the source-VX selector pass, not against old failed
   plain-MLP baselines.
3. If one candidate keeps forward motion, target-rate, tracking, and stability
   margin under stricter gates, use it as the warm-start policy for PPO with the
   actuator bridge active.
4. If both candidates fail strict validation, expand selector rollouts into a
   larger on-policy teacher dataset and repeat DAgger/BC before PPO.

## Stop Rules

- Do not run robot validation from the selector result.
- Do not deploy the source-VX selector.
- Do not treat a 10-second smoke as a robot-ready gate.
- Do not continue selector knob tuning unless candidate validation shows a
  specific missing teacher state that only the selector can provide.
- Do not relax the fitted actuator envelope to make a candidate pass.

## Next Branch

```text
PLAN_DEPLOYABLE_POLICY_VALIDATION_AND_WARMSTART
```

Recommended first offline artifact:

```text
DEPLOYABLE_SOURCE_VX_POLICY_VALIDATION
```

It should compare:

```text
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_candidate/candidate.onnx
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_rate_reg_candidate/candidate.onnx
```

using:

```text
straight x=0.08
fitted bridge
stress bridge
8+ seeds
10 s minimum
target-rate p95 and max checks
tracking p95 checks
track-ratio / forward-progress checks
termination checks
```

If a deployable ONNX candidate survives that review, the next training move is
PPO fine-tuning from the BC/DAgger policy with the fitted actuator bridge active,
not PPO from scratch and not another open-loop target-source campaign.

## Strict Validation Update

The first strict deployable-policy validation was run after the behavior-prior
PPO branch held:

```text
artifact: outputs/analysis/DEPLOYABLE_SOURCE_VX_POLICY_VALIDATION_X008_FITTED_15S.md
command: straight x=0.08
bridge: fitted
duration: 15 s
seeds: 0-7
policies:
  - source_vx_selector_trace_dagger2_mlp128_candidate/candidate.onnx
  - source_vx_selector_trace_dagger2_mlp128_rate_reg_candidate/candidate.onnx
```

Result:

```text
dagger2:
  pass: 0 / 8
  falls: 2 / 8
  duration complete: 6 / 8
  mean track ratio: 0.2487
  mean vx: 0.0199 m/s
  failure modes: low progress, tracking, fall/termination

dagger2_rate:
  pass: 0 / 8
  falls: 2 / 8
  duration complete: 6 / 8
  mean track ratio: 0.1847
  mean vx: 0.0148 m/s
  failure modes: low progress, fall/termination
```

The 10-second fitted-bridge smoke result was therefore useful but not strong
enough to promote either ONNX candidate to PPO warm-start or robot validation.
The deployable MLPs can reproduce some forward motion, but over the longer
15-second gate they either lose forward progress, exceed tracking limits, or
fall on hard seeds.

The current next step is not robot testing and not another selector knob tweak.
It is to expand the selector-generated on-distribution rollout dataset and
repeat DAgger/BC with stricter 15-second fitted-bridge validation as the primary
gate.

The later DAgger-3 candidates were also checked against the same strict gate:

```text
artifact: outputs/analysis/DEPLOYABLE_SOURCE_VX_POLICY_VALIDATION_DAGGER3_X008_FITTED_15S.md
command: straight x=0.08
bridge: fitted
duration: 15 s
seeds: 0-7
policies:
  - source_vx_selector_trace_dagger3_mlp128_rate_reg_candidate/candidate.onnx
  - source_vx_selector_trace_dagger3_mlp512_256_128_rate_reg_candidate/candidate.onnx
```

Result:

```text
dagger3_128:
  pass: 0 / 8
  falls: 2 / 8
  duration complete: 6 / 8
  mean track ratio: 0.2729
  mean vx: 0.0218 m/s

dagger3_512:
  pass: 0 / 8
  falls: 3 / 8
  duration complete: 5 / 8
  mean track ratio: -0.0873
  mean vx: -0.0070 m/s
```

This confirms the DAgger-2 conclusion. More capacity and one more DAgger
iteration do not solve the strict 15-second fitted-bridge gate. The 128-wide
DAgger-3 model is the best of this group by mean forward progress, but it still
fails on tracking and hard-seed falls. The 512/256/128 model overfits or
destabilizes badly enough to produce negative mean velocity.
