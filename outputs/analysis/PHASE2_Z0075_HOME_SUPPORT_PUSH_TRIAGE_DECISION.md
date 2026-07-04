# Phase 2 z=0.0075 Home-Support Push Triage Decision

status: `PASS_HOME_SUPPORT_PUSH_TRIAGE_DIAGNOSTIC`
verdict: `PUSH_RECOVERY_LIMITED_AFTER_RESET_ALIGNMENT`

This diagnostic is offline sim analysis only. It did not SSH, deploy, train, run robot tests, or change robot runtime behavior.

## Executive Summary

The previous seed 5 diagnostic showed a real `playground` reset sensitivity. This follow-up reran the Iter10 z=0.0075 candidate from `home-support` reset across all 8 seeds with intermediate pushes.

Result: `5/8` seeds pass the 15 second rough-terrain intermediate-push diagnostic from `home-support` reset. The rescued seed 5 now passes full duration. However, seeds 0, 2, and 6 still fail.

A targeted no-push triage on the failed seeds shows all three pass 15 seconds on rough z=0.0075 from `home-support` when pushes are removed. The residual blocker is therefore push recovery after reset alignment, not baseline rough-terrain locomotion and not actuator-envelope excess.

## Candidate

- policy: `policy/candidates/phase2_z0075_spike_local_rate150_20260704/candidate.onnx`
- candidate hash: `3874e11e4a132ac90e14a0600071e41b5f147ef1a1486e06934a69368ecca70f`
- command_x: `0.08`
- bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- bridge_mode: `fitted`
- platform: `cpu`

## Home-Support Rough z=0.0075 Intermediate Push Gate

| seed | status | samples | vx | track | pitch p95 | base min | p95 excess | max excess | tracking p95 | push events | push success |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 114 | 0.1756 | 2.1946 | 0.9954 | 0.0059 | 0.0000 | 0.0000 | 0.1950 | 1 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0300 | 0.3756 | 0.1840 | 0.1532 | 0.0000 | 0.0000 | 0.1819 | 13 | 0.9231 |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 604 | -0.0023 | -0.0289 | 0.1749 | 0.0821 | 0.0000 | 0.0000 | 0.1756 | 10 | 0.9000 |
| 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0264 | 0.3305 | 0.1685 | 0.1532 | 0.0000 | 0.0000 | 0.1845 | 13 | 0.9231 |
| 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0293 | 0.3658 | 0.1730 | 0.1532 | 0.0000 | 0.0000 | 0.1803 | 12 | 0.9167 |
| 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0279 | 0.3485 | 0.1824 | 0.1532 | 0.0000 | 0.0000 | 0.1879 | 13 | 0.9231 |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 672 | 0.0009 | 0.0114 | 0.1562 | 0.0755 | 0.0000 | 0.0000 | 0.1764 | 12 | 0.8333 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0275 | 0.3434 | 0.1860 | 0.1532 | 0.0000 | 0.0000 | 0.1813 | 10 | 0.9000 |

Distribution:

- pass: `5/8`
- fail: `3/8`
- mean vx: `0.0394 m/s`
- mean track ratio: `0.4926`
- mean push success: `0.7899`
- p95 velocity excess: `0.0000`
- max velocity excess: `0.0000`

## Failed-Seed No-Push Triage

Seeds 0, 2, and 6 were rerun with the same rough z=0.0075 terrain and `home-support` reset, but with pushes disabled.

| seed | status | samples | vx | track | pitch p95 | base min | p95 excess | max excess | tracking p95 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0256 | 0.3195 | 0.1668 | 0.1532 | 0.0000 | 0.0000 | 0.1784 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0256 | 0.3195 | 0.1668 | 0.1532 | 0.0000 | 0.0000 | 0.1784 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0256 | 0.3195 | 0.1668 | 0.1532 | 0.0000 | 0.0000 | 0.1784 |

## Decision

`PUSH_RECOVERY_LIMITED_AFTER_RESET_ALIGNMENT`

The candidate is not failing baseline rough z=0.0075 locomotion once reset is aligned to `home-support`. It remains in-envelope in both push and no-push triage. The remaining failures are caused by intermediate push perturbations or the recovery transient after them.

Seed 0 is an immediate push-recovery failure: one push event occurs, recovery rate is 0, and the rollout falls by sample 114 with high pitch and collapsed base height.

Seeds 2 and 6 tolerate most pushes but eventually terminate, while all targeted no-push reruns complete. These are late push-recovery or repeated-disturbance margin failures, not a need for more rough-terrain label weighting.

## Recommended Next Step

Do not add more feed-forward BC label weights for rough-terrain locomotion. The next Phase 2 action should target push recovery specifically:

1. Add a staged push-recovery curriculum from the current Iter10/base candidate or the last stable no-push candidate.
2. Start from `home-support` reset and rough z=0.0075 no-push stability.
3. Ramp push magnitude/frequency from gentle to intermediate.
4. Gate each stage against corrected-bridge velocity excess, tracking p95, base-height recovery, and push-recovery success.
5. Keep a separate canonical `playground` reset audit open; do not treat `home-support` as a deployability shortcut until reset-contract alignment is explicitly resolved.

This is still not a promotion result. A Phase 2 candidate needs full corrected-bridge gates and reviewed reset semantics before any robot-side validation.
