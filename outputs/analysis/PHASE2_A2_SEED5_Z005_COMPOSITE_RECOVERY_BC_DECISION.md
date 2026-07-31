# Phase 2 A2 Seed-5 z=0.005 Composite Recovery BC Decision

status: `PASS_COMPOSITE_BC_READY_HOLD_TARGET_SOURCE_GATE`

This is an offline manifest-curation artifact. It did not train, SSH, deploy,
run robot tests, grounded replay, or change runtime behavior.

## Purpose

The z=0.005 seed-5 recovery relabel slice is not sufficient by itself. This
artifact combines it with the stable Phase A2 z=0.002 seed-5 zero-command trace
to create a small policy-derived support/recovery manifest for a future smoke
test.

## Manifest

```text
outputs/analysis/PHASE2_A2_SEED5_Z005_COMPOSITE_RECOVERY_BC_MANIFEST.md
```

Result:

| metric | value |
|---|---:|
| status | `PASS_BC_TRACE_MANIFEST_READY` |
| dataset_id | `474aed4e249e54b2` |
| entries | `2` |
| samples | `141` |
| BC-ready entries | `2` |
| max source fraction | `0.5000` |

Entries:

| source | ticks | samples | role |
|---|---:|---:|---|
| `phase2_a2_seed5_z002_x000_2s_fullobs_trace.jsonl` | `0-99` | 100 | stable support behavior |
| `phase2_a2_seed5_z005_recovery_from_z002_relabel_trace.jsonl` | `20-60` | 41 | failing-state recovery labels |

## Sanity Check

```text
outputs/analysis/PHASE2_A2_SEED5_Z005_COMPOSITE_RECOVERY_BC_MANIFEST_CHECK.md
```

Result:

| metric | value |
|---|---:|
| status | `HOLD_TARGET_DATASET_SANITY_ERRORS` |
| BC readiness | `PASS_TARGET_DATASET_BC_READY` |
| warnings | none |

The target sanity hold is expected because this manifest contains zero-command
support/recovery material, including failing z=0.005 states, rather than a
forward-moving source-gate target.

## Decision

This composite manifest is acceptable as a bounded future BC/DAgger smoke input
only. It is not a z=0.005 source-gate pass and does not authorize promotion,
robot validation, or broader training by itself.

Next step should be a small supervised smoke against this manifest, followed by
the short seed-5 z=0.005 support gate. If the smoke collapses or overfits, stop
and redesign the recovery source instead of scaling this dataset.
