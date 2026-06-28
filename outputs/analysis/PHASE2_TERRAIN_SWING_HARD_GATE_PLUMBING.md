# Phase 2 Terrain Swing Hard-Gate Plumbing

status: `PASS_TERRAIN_SWING_HARD_GATE_PLUMBING`

## Scope

Offline evaluator/tooling only. No robot, SSH, deploy, grounded replay, runtime
behavior change, training run, or policy overwrite was performed.

## Why

The C-stage terrain screens showed that a policy can look acceptable on
actuator tracking while still failing the carpet-relevant behavior: one foot
remains effectively planted, relative-foot excursion is near zero, and the gait
becomes a double-support shuffle. Those metrics need to be enforceable as a
terrain gate, not only reported.

## Added Optional Gate Flags

`tools/run_candidate_seed_sweep.py` now supports default-off terrain swing
thresholds:

```text
--min-swing-segments-per-foot
--min-swing-rel-x-range-p95-m
--min-swing-peak-lift-m
```

When any threshold is set, the tool records a `terrain_swing_gate` block in
each per-seed result. If the closed-loop evaluator reports
`PASS_CANDIDATE_SIM_GATE` but the optional terrain swing gate fails, the status
is downgraded to:

```text
HOLD_CANDIDATE_TERRAIN_SWING
```

Default behavior is unchanged when these flags are omitted.

## Validation Runs

Nominal two-seed terrain threshold screen:

```text
outputs/analysis/PHASE2_STAGE_C7_35120_TERRAIN_SWING_GATE_CPU.md
outputs/analysis/phase2_stage_c7_35120_terrain_swing_gate_cpu.json
```

Configuration:

```text
min_swing_segments_per_foot: 1
min_swing_rel_x_range_p95_m: 0.003
min_swing_peak_lift_m: 0.005
```

Result:

```text
seed 2: PASS_CANDIDATE_SIM_GATE
seed 4: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
```

Downgrade-path validation with intentionally strict lift threshold:

```text
outputs/analysis/PHASE2_STAGE_C7_35120_TERRAIN_SWING_GATE_DOWNGRADE_CPU.md
outputs/analysis/phase2_stage_c7_35120_terrain_swing_gate_downgrade_cpu.json
```

Configuration:

```text
min_swing_peak_lift_m: 0.02
```

Result:

```text
seed 2 status: HOLD_CANDIDATE_TERRAIN_SWING
observed min_swing_peak: 0.0096 m
```

This proves the optional terrain gate can reject a nominal pass when
carpet-relevant swing requirements are not met.

## Next

Future C-stage terrain gates should set explicit terrain swing thresholds once
the target source is chosen. The current evidence suggests starting from a
small, conservative gate such as:

```text
min_swing_segments_per_foot >= 1
min_swing_rel_x_range_p95_m >= 0.003
min_swing_peak_lift_m >= 0.005
```

Those are diagnostic thresholds, not final deployment criteria. A final terrain
candidate should improve them while preserving corrected actuator envelope,
tracking, and command conditioning.
