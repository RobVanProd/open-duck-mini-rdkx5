# Right-Knee Transition Spike Filter Result

Status: `HOLD_TRANSITION_SPIKE_FILTER_DOES_NOT_FIX_TRACKING`

This was an offline-only analysis. No robot tests, SSH, deploy, runtime behavior
change, or PPO training was performed.

## Question

The 4.3 rad/s rate-limit curation showed that simple clipping preserves forward
motion but does not solve the strict fitted-bridge tracking hold. A follow-up
audit showed the underlying right-knee action-rate spikes are strongly tied to
contact transitions:

```text
right-knee action-derived velocity > 3.75 rad/s: 506 / 3992 ticks
within 2 ticks of a contact transition: 404 / 506
dominant contacts: double support 11, left support 10
```

This probe tested whether dropping transition-adjacent right-knee spike samples
from the BC source traces would remove the problematic behavior while preserving
the closed-loop walking behavior.

## Artifacts

- filter tool: `tools/filter_bc_trace_transition_spikes.py`
- filter report: `outputs/analysis/SOURCE_VX_SELECTOR_TRACE_RK_TRANSITION_SPIKE_FILTERED.md`
- manifest: `outputs/analysis/SOURCE_VX_SELECTOR_TRACE_RK_TRANSITION_SPIKE_FILTERED_MANIFEST.md`
- smoke gate: `outputs/analysis/SOURCE_VX_SELECTOR_TRACE_RK_TRANSITION_SPIKE_FILTERED_BLEND080_EXACT_ONNX_FITTED_BRIDGE_BC_GATE_X008_10S.md`
- strict gate: `outputs/analysis/SOURCE_VX_SELECTOR_TRACE_RK_TRANSITION_SPIKE_FILTERED_BLEND080_EXACT_ONNX_MULTI_SEED_FITTED_BACKLASH_SUMMARY.md`

## Filter

Settings:

```text
vector_key: action
joint: right_knee
spike_velocity_rad_s: 3.75
transition_window_ticks: 2
drop_window_ticks: 1
```

Result:

```text
input samples: 4000
output samples: 3124
removed samples: 876
status: PASS_TRANSITION_SPIKE_FILTER_READY
```

The filtered manifest was BC-ready:

```text
dataset_id: 69c1466221e946cc
entries: 8
samples: 3124
status: PASS_BC_TRACE_MANIFEST_READY
```

## Result

The exact-blend ONNX exported cleanly and passed the smoke replay, but the
strict fitted-backlash x=0.08 8-seed gate still held on tracking:

```text
duration_complete: 8/8
falls: 0/8
mean vx: 0.0449 m/s
mean track ratio: 0.5617
max pitch velocity p95: 4.6244-4.7790 rad/s
max tracking p95: 0.2675-0.2782 rad
status: HOLD_CANDIDATE_TRACKING
```

## Comparison

| curation | vx mean | track ratio mean | max pitch velocity p95 mean | max tracking p95 mean |
|---|---:|---:|---:|---:|
| right-knee-only 4.3 | 0.0479 | 0.5992 | 4.2391 | 0.2720 |
| pitch-chain 4.3 | 0.0477 | 0.5965 | 4.2399 | 0.2735 |
| transition-spike filter | 0.0449 | 0.5617 | 4.6783 | 0.2721 |

The transition filter preserves stability but makes the target-velocity gate
worse and reduces forward progress.

## Interpretation

The transition-adjacent right-knee samples are not disposable noise. Removing
them weakens the gait while the exported exact-blend model still reconstructs a
high-rate right-knee transition in closed loop.

This closes the simple "drop bad transition samples" branch. The next
deployable-policy attempt needs a stronger mechanism than post-hoc trace
filtering:

- dynamics-aware relabeling through the transition,
- a recurrent/stateful or phase-aware student that can represent the transition
  without a discontinuous lookup,
- or gate-aware fine-tuning that directly penalizes simulated tracking while
  preserving the working selector behavior.

Do not proceed to robot validation from this candidate.
