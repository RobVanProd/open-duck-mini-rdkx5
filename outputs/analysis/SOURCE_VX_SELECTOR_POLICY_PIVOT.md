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
