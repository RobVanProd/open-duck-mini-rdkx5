# Phase 2 Z0.005 Motion-Prior T4 Partial Decision

status: `HOLD_PARTIAL_NO_PROMOTABLE_CHECKPOINT`

## Summary

The T4 run for `phase2_z005_motion_prior_cuda` completed training and exported three ONNX checkpoints, but the Colab session dropped during the compact CPU checkpoint sweep before the final `122880 / x=0.08` row and before the final artifact bundle was written.

The completed rows are enough to reject promotion from this run: the two completed `x=0.08` rows remain safe and under-envelope, but both fail for low forward progress.

No robot test, SSH, deploy, grounded replay, or runtime change was performed.

## Run

- workflow: `phase2-z005-motion-floor`
- session: `open-duck-l4`
- backend: Colab T4
- candidate: `phase2_z005_motion_prior_cuda`
- behavior prior: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz`
- behavior prior scale: `-0.25`
- behavior prior Huber delta: `0.05`
- corrected bridge fit: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- partial artifact: `outputs/analysis/colab_cli/open-duck-l4-phase2-z005-motion-floor-20260629T213257Z/open_duck_colab_cli_phase2-z005-motion-floor_20260629T213307Z_artifacts.tar.gz.partial`
- partial artifact sha256: `ad1fd59f1fc1b04806b1ca182e5370f370f942b113663ee5cdaffff0b63018b2`

## Exported Checkpoints

| checkpoint | sha256 |
|---:|---|
| `40960` | `98a68874cac0831932923ebec8c1ed6c302d2ab55e855e3bca61bf891859aeaf` |
| `81920` | `0c878e732f4926933d33f0ae589cb581b2d197f7401aedd01f7641ba33569dc4` |
| `122880` | `e003688a910e6baf1637ccfe5edbbfe194a7d6c2a14d3ff8e5ee1ebaf791fb91` |

## Completed Compact Sweep Rows

Compact sweep settings: fitted corrected bridge, `flat_terrain`, commands `x=0.0` and `x=0.08`, duration `1.0s`, CPU evaluator.

| checkpoint | command x | status | track ratio | max pitch tracking p95 rad | max sent vel p95 rad/s |
|---:|---:|---|---:|---:|---:|
| `40960` | `0.00` | `PASS_CANDIDATE_SIM_GATE` | NA | `0.19149` | `1.10695` |
| `40960` | `0.08` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `0.16213` | `0.21356` | `1.40853` |
| `81920` | `0.00` | `PASS_CANDIDATE_SIM_GATE` | NA | `0.19145` | `1.17522` |
| `81920` | `0.08` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `0.17026` | `0.21341` | `1.42491` |
| `122880` | `0.00` | `PASS_CANDIDATE_SIM_GATE` | NA | `0.19187` | `1.16526` |
| `122880` | `0.08` | `INCOMPLETE_SESSION_LOST` | NA | NA | NA |

## Decision

No checkpoint is promotable.

Reasons:

- The run did not complete the full compact sweep because the Colab session was lost.
- The completed `x=0.08` rows are below the forward-progress floor.
- The best completed `x=0.08` track ratio was `0.17026`, below the compact promotion threshold of `0.25`.
- The behavior-prior recipe remained safe and under-envelope, but it did not recover meaningful forward motion on z0.005 terrain.

## Next Read

The behavior prior did not materially improve over the prior motion-floor run. The current failure mode remains under-motion, not target-rate excess. Further Phase 2 work should avoid simply adding more regularization to this recipe; it needs a stronger locomotion-preservation mechanism or a return to a known moving candidate before adding z0.005 terrain.
