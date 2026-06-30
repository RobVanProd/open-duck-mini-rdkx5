# Phase 2 z=0.002 C2 Tracking-Margin A100 Result

status: `HOLD_TRACKING_MARGIN`
generated_at: `2026-06-30T10:55:00Z`

## Run

- workflow: `phase2-z002-tracking-margin`
- session: `open-duck-a100-phase2c`
- hardware: Colab A100
- JAX/JAXLIB: `0.7.2`
- restore checkpoint: `outputs/phase2_domain_randomization/stage_c2_terrain_z002_targetrate_from_c1_gpu/smoke_20260628T113221Z_gpu/2026_06_28_073829_163840`
- output preserved at: `outputs/phase2_domain_randomization/stage_z002_tracking_margin_c2_a100/smoke_20260630T102226Z_gpu`
- robot touched: `false`

Training completed successfully in `812.6 s` and exported checkpoints at
`40960`, `81920`, and `122880` steps.

## ONNX Hashes

| step | sha256 |
|---:|---|
| 40960 | `32b750b829129d442db34cf96d2bb310341c2e27e0f83e2eaf1ba4d70e10514d` |
| 81920 | `5091a128d740b94015093c35b82a2574a1a45d4963289a2ecb7885418fca1186` |
| 122880 | `747cd1e3bb2eea0d3eb09efa23b6fed273fa54dc8a05c53684ba65f09f87b316` |

## Compact Sweep

Local CPU sweep, fitted corrected bridge, commands `0.0,0.08`, duration `1.0 s`.

| step | command_x | status | vel p95 | tracking p95 | track ratio | mean local vx |
|---:|---:|---|---:|---:|---:|---:|
| 40960 | 0.00 | `PASS_CANDIDATE_SIM_GATE` | 1.0943 | 0.1936 | NA | 0.0065 |
| 40960 | 0.08 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 1.5550 | 0.2198 | 0.2001 | 0.0160 |
| 81920 | 0.00 | `PASS_CANDIDATE_SIM_GATE` | 1.1165 | 0.1939 | NA | 0.0053 |
| 81920 | 0.08 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 1.5586 | 0.2205 | 0.2368 | 0.0189 |
| 122880 | 0.00 | `PASS_CANDIDATE_SIM_GATE` | 1.0666 | 0.1940 | NA | 0.0064 |
| 122880 | 0.08 | `HOLD_CANDIDATE_TRACKING` | 1.5238 | 0.2163 | 0.3018 | 0.0241 |

## Interpretation

The final checkpoint restores meaningful in-envelope x=0.08 motion:
track ratio `0.3018`, mean local vx `0.0241 m/s`, max pitch-chain velocity p95
`1.5238 rad/s`, and no envelope excess.

It is not promotable because corrected-bridge tracking p95 remains `0.2163 rad`,
above the `0.20 rad` gate. The next aligned run should warm-start from the
`122880` checkpoint and polish tracking margin while preserving command progress.

No robot test, SSH, deployment, grounded replay, or runtime behavior change was
performed.
