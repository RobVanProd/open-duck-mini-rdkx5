# Phase 2 Health-Routed Parent PPO-Loc Step-0 Decision

status: `HOLD_PPO_STEP0_SEED5_FAILURE`

This is an offline PPO warm-start construction and gate check. It did not SSH,
deploy, run robot tests, touch the robot, or change robot runtime behavior.

## Inputs

- source parent: `policy/candidates/phase2_health_routed_parent_phase_mod_rate150_20260706/candidate.onnx`
- PPO-loc BC prior NPZ: `outputs/analysis/phase2_health_routed_pass_parent_ppo_loc_rate150_prior/candidate_mlp.npz`
- PPO-loc BC prior NPZ sha256: `a4898be376c496b7f8de96844cb64827ac26b19c575482c622d129bdaefe2e16`
- PPO-loc BC prior ONNX: `outputs/analysis/phase2_health_routed_pass_parent_ppo_loc_rate150_prior/candidate.onnx`
- PPO-loc BC prior ONNX sha256: `3bb1f33da245ee5e79df9ba55407e465e32ee4b56749c49be0dc5fa80f4dd0e6`
- manifest: `outputs/analysis/phase2_health_routed_pass_parent_aggregate_manifest.json`

## Step-0 Export

- checkpoint: `outputs/analysis/phase2_health_routed_parent_ppo_loc_rate150_step0_checkpoint`
- exported ONNX: `outputs/analysis/phase2_health_routed_parent_ppo_loc_rate150_step0.onnx`
- exported ONNX sha256: `10499450f92307a49de9faf8de557cb6348977b9ec4f0ecb798758b57cfc5aa8`
- fidelity report: `outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_PPO_LOC_RATE150_STEP0_FIDELITY.md`
- fidelity JSON: `outputs/analysis/phase2_health_routed_parent_ppo_loc_rate150_step0_fidelity.json`
- fidelity JSON sha256: `bcdfa1d4d8067e77d1e4cd3585133963324940806c2360d4e5116c182923b5ab`
- fidelity status: `PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY`
- p95 action error: `0.0000001192`
- max action error: `0.0000004172`

The PPO parameter/checkpoint construction is valid: the exported PPO step-0
ONNX reproduces the PPO-loc BC prior at action level.

## X=0.08 Full8 Gate

- gate report: `outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_PPO_LOC_RATE150_STEP0_X008_FULL8_GATE.md`
- gate JSON: `outputs/analysis/phase2_health_routed_parent_ppo_loc_rate150_step0_x008_full8_gate.json`
- gate JSON sha256: `110e626948865fef867f02b76295ea00ffa06d80c2793f63f8553e4625af65ea`
- command: `x=0.08`
- task: `rough_terrain_backlash`
- terrain z scale: `0.0075`
- pushes: enabled, `0.075`-`0.125`
- bridge: corrected fitted bridge
- reset: `home-support`, settle ticks `10`

| seed | status | samples | termination | mean vx | track ratio | base height min | max vel p95 | max tracking p95 |
|---:|---|---:|---|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0280 | 0.3495 | 0.1591 | 1.5192 | 0.1809 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0281 | 0.3515 | 0.1589 | 1.5160 | 0.1848 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0270 | 0.3377 | 0.1582 | 1.5213 | 0.1814 |
| 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0264 | 0.3297 | 0.1584 | 1.5186 | 0.1810 |
| 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0283 | 0.3541 | 0.1583 | 1.5243 | 0.1827 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 625 | `fall_or_nan` | 0.0010 | 0.0122 | 0.0819 | 1.5172 | 0.1755 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0233 | 0.2911 | 0.1578 | 1.5194 | 0.1792 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0282 | 0.3520 | 0.1591 | 1.5188 | 0.1824 |

Summary:

- duration complete: `7 / 8`
- falls/terminations: `1 / 8`
- failing seed: `5`
- mean track ratio: `0.2972`
- mean vx: `0.0238` m/s
- velocity envelope excess: `0.0000` rad/s

## Decision

The PPO-loc step-0 checkpoint is a real restorable PPO artifact and preserves
the parent on most seeds, but it does **not** clear the current full8 x=0.08
gate. Do not launch Stage A DR from this checkpoint until seed 5 is corrected
or a stronger PPO-compatible parent clears both x=0.08 and x=0.0 gates.

The useful next branch is seed-5-specific diagnosis of the PPO-loc compression:

1. Trace seed 5 for the phase-modulated parent and the PPO step-0 export under
   identical x=0.08 rough+push settings.
2. Compare action deltas, phase/context dependence, contact timing, and base
   height collapse around samples 550-625.
3. Retrain or augment the PPO-compatible parent only if the trace shows a
   localized compression gap; otherwise the policy class needs the phase/context
   mechanism preserved in a restorable PPO actor.
