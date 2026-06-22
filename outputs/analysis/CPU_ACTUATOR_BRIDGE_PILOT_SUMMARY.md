# CPU Actuator Bridge Pilot Summary

Generated: 2026-06-22

## Summary

After merging the default-off Playground actuator bridge and the RDK training
workflow, three local CPU pilot runs were executed to validate the offline
training/export/package path.

These runs are **not deployable policies**. They prove that the training loop,
ONNX export, summarizer, and candidate packaging checks work on the merged
`main` branches. They do not satisfy the sim-side candidate gates.

## Source Revisions

| repo | branch | commit |
|---|---|---|
| `open-duck-mini-rdkx5` | `main` | `36a686bd138e06f3a3a38f02954240d45a370f9a` |
| `Open_Duck_Playground` | `main` | `bdf37aa850dae0cc383d3817d97c4f3f35edd487` |

## Environment Checks

| check | result |
|---|---|
| actuator bridge default config | `PASS_ACTUATOR_BRIDGE_CONTRACT` |
| training env Python | `/home/lsd/robots/envs/open-duck-playground/bin/python` |
| JAX backend visibility | `rocm:0` visible, but Playground GPU step remains blocked |
| CPU step-level bridge smoke | `PASS_ACTUATOR_BRIDGE_SMOKE` |
| robot touched | no |

## Pilot Runs

Raw outputs, TensorBoard logs, checkpoints, and ONNX exports were left under
`/tmp` and are not committed.

| run | timesteps | target_rate_scale | actuator_tracking_scale | latest step | reward | ONNX SHA256 | status |
|---|---:|---:|---:|---:|---:|---|---|
| tiny smoke | 256 | `0.0` | `0.0` | 320 | `15.308966636657715` | `a6e44dd3866838f4bfd76641f6d0175a7c4df0395ee64f766ac0360819dd4c89` | non-deployable |
| pilot target-rate | 8192 | `0.01` | `0.0` | 8240 | `14.813603401184082` | `32191fc9bc930fc2018bc3cc06acafaa49277aafad057456ab05f4d1cb6f8b74` | non-deployable |
| pilot zero-penalty | 8192 | `0.0` | `0.0` | 8240 | `16.19684600830078` | `ae48fe2678ef3ab1ef2d791b7eefb92218f790774ddaa6525ce6d2838bef2590` | non-deployable |
| longer zero-penalty | 32768 | `0.0` | `0.0` | 32800 | `11.204126358032227` | `eedb5cd560607b41edee1c43d5abcb57a1fd314e0f35c883b67d02097dad6580` | non-deployable |

## Candidate-Mode Closed-Loop CPU Eval

Candidate-mode eval was added after these pilots because the original
closed-loop reproduction status was only meaningful for the baseline policy.

Small committed reports:

- `outputs/analysis/CPU_CANDIDATE_GATE_STEP8240_ZERO_X0_15S.md`
- `outputs/analysis/CPU_CANDIDATE_GATE_STEP8240_ZERO_X004_15S.md`
- `outputs/analysis/CPU_CANDIDATE_GATE_STEP8240_ZERO_15S.md`
- `outputs/analysis/CPU_CANDIDATE_GATE_STEP8240_TARGET_RATE_X008_HOLD.md`
- `outputs/analysis/CPU_CANDIDATE_GATE_STEP8240_NEG_TARGET_RATE_X008_HOLD.md`
- `outputs/analysis/CPU_CANDIDATE_GATE_STEP32800_HOLD.md`

Results:

| pilot | duration | status | main reason |
|---|---:|---|---|
| `step8240_zero_penalty`, `x=0.0` | `15 s` | `PASS_CANDIDATE_SIM_GATE` | survived vanilla/fitted/stress with low action saturation and pitch tracking below threshold |
| `step8240_zero_penalty`, `x=0.04` | `15 s` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | stable but mean forward velocity stayed near zero |
| `step8240_zero_penalty`, `x=0.08` | `15 s` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | stable but mean forward velocity stayed near zero |
| `step8240_target_rate`, `x=0.08` | `15 s` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | positive target-rate scale did not produce command-tracking walking in this tiny CPU run |
| `step8240_negative_target_rate`, `x=0.08` | `15 s` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | true negative target-rate penalty still produced near-zero mean forward velocity in this tiny CPU run |
| `step32800_zero_penalty` | `2 s` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | fell/terminated early with high action saturation and large pitch tracking error |

The `step8240_zero_penalty` pilot is preserved only as a pipeline artifact. It
is not robot-approved because it does not track nonzero forward commands. The
target-rate pilots confirm that neither the first positive-scale control
(`+0.01`) nor a matching true negative penalty (`-0.01`) solves command tracking
in this tiny CPU run.

## Interpretation

- The merged actuator bridge can be used by the training runner without
  changing default behavior.
- ONNX export and candidate packaging preserve the deployed runtime contract:
  `obs[1,101] -> continuous_actions[1,14]`.
- The tiny CPU training shape is useful for correctness checks, not for
  producing a robot candidate.
- The positive and negative target-rate scale pilots did not improve reward or
  nonzero-command forward progress in this small CPU configuration.
- The longer zero-penalty pilot reward decreased, so continuing to scale this
  exact CPU smoke shape is not the right candidate-training path.

## Next Step

Use CUDA for meaningful candidate training/evaluation where possible. If CUDA
is unavailable, adjust the training recipe before spending more CPU time: the
next candidate likely needs a larger training shape and command-tracking
pressure, not just smoother targets.

Robot motion remains blocked until a candidate passes the documented sim-side
gates and Rob explicitly approves suspended validation.

## Follow-Up Candidate Eval Note

The first closed-loop CPU candidate evals showed why candidate-specific gates
are needed. The baseline reproduction status `HOLD_MODEL_DOES_NOT_REPRODUCE`
is not meaningful for new candidate policies because a good candidate should
avoid reproducing the original `x=0.08` failure.

The eval tool now supports:

```bash
--eval-role candidate
```

Use that mode for candidate ONNX files.
