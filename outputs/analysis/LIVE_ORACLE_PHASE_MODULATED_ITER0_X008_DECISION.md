# Live-Oracle Phase-Modulated Iter0 X008 Decision

status: `HOLD_PHASE_MODULATED_SEED5_COLLAPSE`

This diagnostic tests a shared-trunk phase/command-modulated behavior-cloning
student after both hard and smooth independent phase-head approaches failed.
It preserves the deployed policy contract:

`obs[1,101] -> continuous_actions[1,14]`

It did not train PPO, deploy, SSH, run robot tests, or change robot runtime
behavior.

## Architecture

Tool:

`tools/train_phase_modulated_bc_student.py`

Architecture:

```text
obs -> normalize -> shared trunk -> hidden
obs[6,99,100] -> normalize -> context MLP -> gamma,beta
hidden_mod = hidden * (1 + scale * tanh(gamma)) + scale * tanh(beta)
hidden_mod -> output loc -> tanh(loc) -> action
```

Configuration:

- source manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_000/live_oracle_dagger_x008_manifest.json`
- trunk hidden sizes: `512,256`
- context hidden sizes: `64`
- context indices: `[6, 99, 100]`
- modulation scale: `0.5`
- target-rate penalty scale: `0.1`
- target-rate limit: `3.75 rad/s`
- output policy: `outputs/analysis/live_oracle_phase_modulated_iter0_x008_candidate/candidate.onnx`

## Supervised Fit

Artifact:

`outputs/analysis/LIVE_ORACLE_PHASE_MODULATED_ITER0_X008_FIT.md`

Fit summary:

- MAE: `0.010803`
- p95 abs error: `0.032824`
- max abs error: `0.190804`
- fit target-rate p95: `2.228043 rad/s`
- fit target-rate max: `3.990272 rad/s`
- ONNX max action error: `2.682209014892578e-07`

The supervised fit is plausible and export fidelity is good.

## Canonical X008 Gate

Artifact:

`outputs/analysis/LIVE_ORACLE_PHASE_MODULATED_ITER0_X008_GATE.md`

Canonical gate:

- task: `flat_terrain_backlash`
- bridge: `fitted`
- duration: `15s`
- seeds: `0-7`

Result:

- duration complete: `7 / 8`
- falls/terminations: `1 / 8`
- failed seed: `5`
- seed-5 samples: `70`
- seed-5 mean local vx: `-0.2075 m/s`
- seed-5 max tracking p95: `0.2969 rad`
- aggregate mean track ratio: `0.1388`
- aggregate mean local vx: `0.0111 m/s`
- max pitch-chain sent velocity p95: `3.8548 rad/s`
- max pitch-chain tracking p95: `0.2969 rad`

Completed seeds mostly remained close to the original iter0 moving behavior,
but the seed-5 early reverse/fall makes the policy non-promotable.

## Comparison

Compared with live-oracle iteration 0:

- iter0 duration complete: `8 / 8`
- iter0 falls: `0 / 8`
- iter0 mean track ratio: `0.5613`
- iter0 max pitch-chain sent velocity p95: `3.6791 rad/s`
- iter0 max pitch-chain tracking p95: `0.2665 rad`

The phase-modulated student did not break the tracking plateau and introduced
a seed-5 collapse. Its completed seeds show slightly lower tracking on some
runs, but the distribution is worse because the policy is not robust.

## Interpretation

The shared-trunk phase/command modulation rung is rejected in this form.

This is a better failure than the independent phase-head variants because it
does not globally rate-spike above `4.4-5.2 rad/s`, but it still does not solve
the core deployable-policy problem:

- no strict tracking pass
- one hard seed collapse
- aggregate forward progress destroyed by the collapse

The remaining evidence points away from feed-forward architectural variants
trained by one-shot BC. The next rung should use recurrent/live-state memory or
closed-loop fine-tuning from a walking prior, not more static feed-forward phase
heads/modulators.

Do not promote this policy to robot validation.
