# Phase 2 Stage B Decision

status: `HOLD_STAGE_B_PUSH_DR_ERODES_FORWARD_MOTION`

## Summary

Stage A produced a deployable corrected-bridge sim candidate:

```text
policy/candidates/phase2_stage_a2_gain099_20260628/candidate.onnx
sha256: a082be6cf5c486073523bbd0fba4ea3645dc448270ca0a8e28c4ce5a4e8d31c4
```

It passes both corrected-bridge gates at `x=0.08` and `x=0.0`, but it is a
slow walker. Stage B tested whether the trainable A2 lineage can absorb flat
domain randomization and push perturbations without losing forward motion.

Result: Stage B does not pass. Both attempts completed offline training, but
the exported checkpoints regressed toward low-progress standing. Do not advance
to rough terrain yet.

No robot motion, SSH, deployment, grounded replay, or runtime behavior change
was performed.

## Inputs

Trainable warm-start:

```text
outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/
  smoke_20260628T031553Z_gpu/2026_06_27_231931_163840
```

This is the raw A2 164k Orbax checkpoint. It is the trainable lineage behind
the Stage A gain099 deployment wrapper.

Corrected bridge:

```text
outputs/analysis/actuator_response_fit_corrected_knee.json
```

## Stage B1: Full Flat DR + Gentle Push

Run artifact:

```text
outputs/phase2_domain_randomization/stage_b1_full_flat_gentle_push_from_a2_gpu/
  smoke_20260628T073620Z_gpu/
```

Training status:

```text
PASS_SMOKE_RUN
```

Recipe:

```text
task: flat_terrain_backlash
restore_checkpoint: A2 164k
restore_policy_kl_scale: 0.8
behavior_prior_scale: -0.3
friction: 0.5-1.25
mass: 0.9-1.1
COM jitter: 0.03 m
actuator gain: 0.9-1.1
leg geometry jitter: 0.015
push: enabled, 0.05-0.25
noise: full Stage B levels
bridge velocity range: 2.0-3.25 rad/s
```

Screen artifact:

```text
outputs/analysis/PHASE2_STAGE_B1_CHECKPOINT_SCREEN_X008.md
outputs/analysis/phase2_stage_b1_checkpoint_screen_x008.json
```

Best x=0.08 screen result:

```text
checkpoint: 163840
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
duration_complete: yes
max pitch velocity p95: 1.4199 rad/s
max tracking p95: 0.1615 rad
track ratio: 0.0467
mean vx: 0.0037 m/s
```

Interpretation: jumping directly from Stage A to full flat DR plus gentle push
is too hard. The policy stays stable and in-envelope by largely stopping.

## Stage B0: Narrow DR + Mild Push

Run artifact:

```text
outputs/phase2_domain_randomization/stage_b0_mild_push_from_a2_gpu/
  smoke_20260628T075006Z_gpu/
```

Training status:

```text
PASS_SMOKE_RUN
```

Recipe:

```text
task: flat_terrain_backlash
restore_checkpoint: A2 164k
restore_policy_kl_scale: 1.0
behavior_prior_scale: -0.4
friction: 0.8-1.1
mass: 0.98-1.02
COM jitter: 0.01 m
actuator gain: 0.98-1.02
leg geometry jitter: 0.003
push: enabled, 0.02-0.10
noise: half Stage B levels
bridge velocity range: 2.0-3.25 rad/s
```

Screen artifact:

```text
outputs/analysis/PHASE2_STAGE_B0_CHECKPOINT_SCREEN_X008.md
outputs/analysis/phase2_stage_b0_checkpoint_screen_x008.json
```

Best raw x=0.08 screen result:

```text
checkpoint: 491520
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
duration_complete: yes
max pitch velocity p95: 1.6286 rad/s
max tracking p95: 0.1918 rad
track ratio: 0.1898
mean vx: 0.0152 m/s
```

This is better than B1, but still below the Stage A candidate and below the
minimum useful forward-progress screen.

## B0 Action-Gain Screen

The B0 491k checkpoint was under-driving, so constant action-gain wrappers were
screened at `1.05`, `1.10`, `1.15`, and `1.20`.

Artifacts:

```text
outputs/analysis/phase2_stage_b0_491k_action_gain/
outputs/analysis/PHASE2_STAGE_B0_GAIN_SCREEN_X008.md
outputs/analysis/phase2_stage_b0_gain_screen_x008.json
```

Best gain result:

```text
policy: b0_491k_gain105.onnx
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
duration_complete: yes
max pitch velocity p95: 1.6641 rad/s
max tracking p95: 0.1925 rad
track ratio: 0.2176
mean vx: 0.0174 m/s
```

Higher gains did not improve the result. `1.15` and `1.20` collapsed toward
near-standstill despite remaining under the measured envelope.

## Decision

Stage B is held:

```text
HOLD_STAGE_B_PUSH_DR_ERODES_FORWARD_MOTION
```

Do not advance to terrain stages C/D. The failure happens before terrain: even
mild push perturbation and narrow randomization reduce the A2 lineage's forward
motion below the candidate gate.

## Next Recommendation

The next Stage B attempt should preserve the Stage A gait with a stronger
continuity signal than scalar reward/KL alone. Reasonable next options:

- train from the A2 164k checkpoint with a teacher-action continuity loss
  against the Stage A gain099 behavior, not just restore-policy KL;
- introduce push perturbations as an evaluation-only robustness metric first,
  then train only against the smallest perturbation that the Stage A candidate
  actually fails;
- keep the corrected bridge and per-joint envelope unchanged;
- do not widen randomization or move to rough terrain until a flat mild-push
  stage preserves meaningful `x=0.08` motion.

Robot validation remains blocked.
