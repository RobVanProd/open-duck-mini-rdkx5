# Phase 2 Stage A Decision

status: `HOLD_STAGE_A_LOW_FORWARD_PROGRESS`

## Summary

Stage A narrow domain-randomized PPO training completed on the local ROCm GPU
without touching the robot, deploying code, using SSH, or running grounded
hardware.

The training run produced checkpoints through step `4587520` and ended with
`PASS_SMOKE_RUN`, but the latest exported policy is not promotable. It preserves
zero-command standing and remains inside the corrected actuator envelope, but it
regresses the `x=0.08` command-conditioned gait into low forward progress.

## Training Run

```text
output_dir:
  outputs/phase2_domain_randomization/stage_a_narrow_flat_no_push_gpu/smoke_20260628T015607Z_gpu

final_export:
  outputs/phase2_domain_randomization/stage_a_narrow_flat_no_push_gpu/smoke_20260628T015607Z_gpu/2026_06_27_220729_4587520.onnx

final_export_sha256:
  d20e5546be2b67a776950c7996e289c07e8f6731d489b5dff3ffaa8909329728

manifest:
  outputs/phase2_domain_randomization/stage_a_narrow_flat_no_push_gpu/smoke_20260628T015607Z_gpu/smoke_manifest.final.json

manifest_sha256:
  b4b4089f4ed0f78f1275a42b3b06b0be9deac2cb9e7179876177625878842e4f

status:
  PASS_SMOKE_RUN

elapsed:
  702.75 s

final_reward:
  STEP: 4587520 reward: 64.56953430175781 reward_std: 40.920589447021484
```

Export hashes:

```text
655360:  0bfcd80d66cd17b3da973731f202cc040549ae0651abf912c642b7f86fa52d5d
1310720: 360871a1093573f41a859893141d0616bc329ad7596f9038bbdb3514850c306a
1966080: d1ed74eb5b8033b9cf141989f56ec214af0e33f729a660f18d49ec00bd0d47c9
2621440: cad7de02dfd6accaa78e0dbf0277aa76535aceda5990aea069192c537b4a4d2b
3276800: 8a7f8150fec91ad4a8588698b0f246b7c51a3ebbf2a096536d29cc5821c65102
3932160: 0bef6a8280982d9d11998e23abfd1a19fd930fccf537a4e82da55ebe1fb7acbf
4587520: d20e5546be2b67a776950c7996e289c07e8f6731d489b5dff3ffaa8909329728
```

## Canonical Gates

### x=0.08

Artifact:

```text
outputs/analysis/PHASE2_STAGE_A_X008_GATE.md
outputs/analysis/phase2_stage_a_x008_gate.json
```

Result:

```text
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS on 8/8 seeds
falls: 0/8
duration_complete: 8/8
mean track ratio: 0.0984
mean vx: 0.0079 m/s
max pitch velocity p95 excess: 0.0 rad/s
max tracking p95: 0.1712 rad
```

### x=0.0

Artifact:

```text
outputs/analysis/PHASE2_STAGE_A_X000_GATE.md
outputs/analysis/phase2_stage_a_x000_gate.json
```

Result:

```text
status: PASS_CANDIDATE_SIM_GATE on 8/8 seeds
falls: 0/8
duration_complete: 8/8
mean vx: 0.0004 m/s
max pitch velocity p95 excess: 0.0 rad/s
max tracking p95: 0.0594 rad
```

## Warm-Start Control

The trainable PPO step-0 export still matches the packaged Phase 1 behavior in
closed-loop rollout. This rules out a broken warm-start artifact.

Artifact:

```text
outputs/analysis/PHASE2_STAGE_A_STEP0_VS_PHASE1_SCREEN_X008.md
outputs/analysis/phase2_stage_a_step0_vs_phase1_screen_x008.json
```

Seed-0, 5 s, `x=0.08`, corrected bridge:

```text
step0:
  status: PASS_CANDIDATE_SIM_GATE
  track ratio: 0.4419
  vx: 0.0354 m/s
  max pitch velocity p95 excess: 0.0 rad/s
  max tracking p95: 0.1938 rad

phase1 packaged candidate:
  status: PASS_CANDIDATE_SIM_GATE
  track ratio: 0.4229
  vx: 0.0338 m/s
  max pitch velocity p95 excess: 0.0 rad/s
  max tracking p95: 0.1961 rad
```

## Checkpoint Screen

The corrected-task short screen did not find a better intermediate checkpoint.
Every Stage A export held on low forward progress under
`flat_terrain_backlash`.

Artifact:

```text
outputs/analysis/PHASE2_STAGE_A_CHECKPOINT_SCREEN_X008_BACKLASH.md
outputs/analysis/phase2_stage_a_checkpoint_screen_x008_backlash.json
```

Best short-screen checkpoint:

```text
s1310k:
  track ratio: 0.2165
  vx: 0.0173 m/s
  max pitch velocity p95 excess: 0.0 rad/s
  max tracking p95: 0.1738 rad
```

This is below the promotion threshold and below the Phase 1 baseline.

## Interpretation

Stage A did not fail by falling or violating the actuator envelope. It failed
by preserving stillness better than forward command response. The policy stayed
safe, but PPO updates under narrow DR reduced the in-envelope walking gait.

The next Stage A attempt should be behavior-preserving before it is
robustness-seeking:

- stronger restore-policy KL,
- lower learning rate,
- shorter update horizon with more frequent checkpointing,
- stronger behavior prior or teacher-action continuity,
- no advancement to Stage B until `x=0.08` recovers the Phase 1 movement gate.

Robot validation remains blocked.
