# Live-Oracle Phase-Smooth-Blend Iter0 X008 Decision

status: `HOLD_SMOOTH_PHASE_BLEND_STABLE_BUT_REGRESSED`

This diagnostic uses the same four phase-head students as the hard
phase-quadrant test, but blends them smoothly from `obs[99:101]` instead of
hard-switching at quadrant boundaries. It preserves the deployed contract:

`obs[1,101] -> continuous_actions[1,14]`

It did not train PPO, deploy, SSH, run robot tests, or change robot runtime
behavior.

## Setup

Tool:

`tools/wrap_policy_phase_smooth_blend.py`

Output policy:

`outputs/analysis/live_oracle_phase_smooth_blend_iter0_x008_candidate/candidate.onnx`

Blend rule:

```text
s_a = clip((obs[99] + 1) / 2, 0, 1)
s_b = clip((obs[100] + 1) / 2, 0, 1)
w0 = s_a       * s_b
w1 = (1 - s_a) * s_b
w2 = (1 - s_a) * (1 - s_b)
w3 = s_a       * (1 - s_b)
action = w0 * head0 + w1 * head1 + w2 * head2 + w3 * head3
```

ONNX verification:

- artifact: `outputs/analysis/live_oracle_phase_smooth_blend_iter0_x008_onnx_verify.json`
- status: `PASS_ONNX_PHASE_SMOOTH_BLEND_VERIFY`
- max action error versus expected weighted blend: `5.960464477539063e-08`

## Canonical X008 Gate

Artifact:

`outputs/analysis/LIVE_ORACLE_PHASE_SMOOTH_BLEND_ITER0_X008_GATE.md`

Canonical gate:

- task: `flat_terrain_backlash`
- bridge: `fitted`
- duration: `15s`
- seeds: `0-7`

Result:

- duration complete: `8 / 8`
- falls/terminations: `0 / 8`
- mean track ratio: `0.4564`
- mean local vx: `0.0365 m/s`
- max pitch-chain sent velocity p95: `4.4742 rad/s`
- max pitch-chain tracking p95: `0.2708 rad`

## Comparison

Compared with hard phase-quadrant gating:

- fixed the seed-2 fall/termination
- restored `8 / 8` duration completion
- reduced max pitch-chain sent velocity from `5.2400` to `4.4742 rad/s`

Compared with the shared live-oracle iteration-0 movement student:

- track ratio regressed from `0.5613` to `0.4564`
- max pitch-chain sent velocity worsened from `3.6791` to `4.4742 rad/s`
- max pitch-chain tracking worsened from `0.2665` to `0.2708 rad`

## Interpretation

Smooth phase blending fixes the hard-boundary instability but still fails the
strict fitted-bridge gate and remains worse than the shared iter0 movement
student.

This rejects both naive phase-head variants:

- hard quadrant selection: unstable / rate-spiky
- smooth bilinear blending: stable but higher-rate and lower-progress

The tracking plateau is not solved by simply splitting the existing labels by
phase and recombining phase heads. The next representation escalation should
use a shared representation with phase-conditioned modulation or a recurrent
student with live-oracle labels, rather than independent phase heads.

Do not promote this policy to robot validation.
