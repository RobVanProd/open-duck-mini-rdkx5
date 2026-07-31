# Full-8 MLP Router Candidate Decision

status: `HOLD_FULL8_MLP_ROUTER_SEED0_REGRESSION`

The nonlinear stateless observation gate separates the selected source traces
well enough to justify an actual composed ONNX router, but the first closed-loop
candidate gate is not promotable. It preserves seed 5 and seed 7, while seed 0
falls under the hard rough+push screen.

This is offline diagnostic evidence. It did not train PPO/DR, deploy, SSH, run
robot tests, grounded replay, or change runtime behavior.

## Inputs

- branch_a_policy: `policy/candidates/phase2_parent_pair_lateral_seed7_weighted_command_gated_zero0020_20260705/candidate.onnx`
- branch_b_policy: `policy/candidates/phase2_z0075_iter25_dual_anchor_weight4_history_context_rate150_20260704/candidate.onnx`
- gate_npz: `outputs/analysis/phase2_full8_mlp_router_gate/gate_mlp.npz`
- gate_npz_sha256: `8192fc152205635f4ccdbd1d9972944659bca4782bf8dfe43241ae6228fc45c0`
- composed_candidate: `outputs/analysis/phase2_full8_mlp_router_candidate/candidate.onnx`
- composed_candidate_sha256: `6251a528b878fbfa3637727bd6d8463cd08b291556b285fbfe3cfab40ede5697`
- onnx_verify: `outputs/analysis/phase2_full8_mlp_router_candidate/onnx_verify.json`
- gate: `outputs/analysis/phase2_full8_mlp_router_candidate_x008_seed0_5_7_gate.json`

## Separability

The MLP gate was trained only as a branch classifier over the selected source
observations:

```text
train balanced accuracy: 99.01%
test balanced accuracy: 95.81%
test positive selected: 94.67%
test negative false selected: 3.05%
```

The composed ONNX verified exactly against the Python gate:

```text
PASS_ONNX_OBS_MLP_GATE_VERIFY
max_abs_error: 0.00000000
```

## Closed-Loop Gate Result

Hard screen:

```text
x=0.08
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.0075
bridge: corrected fitted
reset: home-support, settle 10
push: intermediate, 0.075-0.125 every 1.0-1.5 s
seeds: 0,5,7
```

Result:

```text
pass_count: 2/3
falls: 1
mean_vx_m_s: 0.0082
mean_track_ratio: 0.1020
max_p95_velocity_excess_rad_s: 0.0000
max_instant_velocity_excess_rad_s: 0.0000
```

| seed | status | samples | termination | vx | track_ratio | pitch_p95 | base_min | p95_excess | max_excess |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 321 | `fall_or_nan` | -0.0352 | -0.4394 | 0.1774 | 0.0705 | 0.0000 | 0.0000 |
| 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0312 | 0.3897 | 0.1779 | 0.1589 | 0.0000 | 0.0000 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0285 | 0.3556 | 0.2051 | 0.1575 | 0.0000 | 0.0000 |

## Decision

Do not promote this MLP-router candidate and do not launch Phase 2 domain
randomization from it. The result is still useful: nonlinear stateless routing
can preserve the seed-5 branch that static compression lost, but the classifier
gate is not closed-loop-safe yet and regresses seed 0.

## Next Recommendation

Keep the MLP-router direction, but train the gate with closed-loop validation
pressure or a branch-cost objective rather than source-label classification
alone. The next diagnostic should log branch decisions during the failed seed-0
rollout and penalize selecting the seed-5 branch on seed-0-like prefixes.
