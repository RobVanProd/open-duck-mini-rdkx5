# Phase 2 Stage A Rate165 Narrow Flat Result

status: `HOLD_STAGE_A_RATE165_STANDSTILL_REGRESSION`

## Summary

The Stage A narrow flat/no-push domain-randomization run completed on Colab A100
from the verified rate165 PPO-loc warm-start checkpoint, but the resulting
policy collapsed into a safe standstill. This run must not advance to Stage B,
pushes, rougher terrain, or robot validation.

## Training Run

- session: `open-duck-stage-a`
- hardware: Colab A100
- source checkpoint:
  `outputs/analysis/phase2_rate165_ppo_loc_warmstart_step0_checkpoint`
- behavior prior:
  `outputs/analysis/phase2_rate165_ppo_loc_warmstart_candidate/candidate_mlp.npz`
- stage: `stage_a_narrow_flat_no_push`
- task: `flat_terrain_backlash`
- actuator bridge: enabled
- bridge delay: `3-4` ticks
- bridge velocity range: `2.0-3.25 rad/s`
- pushes: disabled
- elapsed: `810.07 s`
- remote status: `PASS_SMOKE_RUN`
- final exported step: `4,587,520`
- final exported ONNX:
  `outputs/analysis/phase2_stage_a_rate165_narrow_flat_no_push_candidate/candidate.onnx`
- final exported ONNX sha256:
  `7d83b2a24ca2874286d80eb27743fb5a5f498fa9ecb8bd1ad2effde7c0966982`
- downloaded artifact bundle sha256:
  `2729b49a124b001f6389529daa818cb65c27dc02929caab1fed8858d70a4fcb1`

## Final x=0.08 Gate

Gate:

```text
rough_terrain_backlash
terrain_hfield_z_scale=0.0026
reset_mode=home-support
bridge=fitted
seeds=0-7
duration=15s
```

Result:

- status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
- duration complete: `8/8`
- falls: `0/8`
- mean local vx: `0.0007 m/s`
- track ratio: `0.0091`
- body pitch p95: `0.0305 rad`
- base height min: `0.1523 m`
- max pitch-chain velocity p95: `0.0838 rad/s`
- corrected p95/max velocity excess: `0`
- max tracking p95: `0.0385 rad`
- single support: `0%`
- double support: `100%`

## Checkpoint Triage

Seed-0 triage across all exported Stage A checkpoints also held on low forward
progress:

| checkpoint step | status | track ratio | mean local vx | single support | double support |
|---:|---|---:|---:|---:|---:|
| 655360 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0065 | 0.0005 | 0.0% | 100.0% |
| 1310720 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0066 | 0.0005 | 0.0% | 100.0% |
| 1966080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0076 | 0.0006 | 0.0% | 100.0% |
| 2621440 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0081 | 0.0006 | 0.0% | 100.0% |
| 3276800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0085 | 0.0007 | 0.0% | 100.0% |
| 3932160 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0089 | 0.0007 | 0.0% | 100.0% |
| 4587520 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0091 | 0.0007 | 0.0% | 100.0% |

## Decision

Reject this Stage A run. The failure is not actuator envelope excess or falling;
it is motion collapse. The next Stage A attempt must preserve nonzero forward
motion before any robustness escalation. Use immediate seed-0 checkpoint gates
to kill standstill regressions early.
