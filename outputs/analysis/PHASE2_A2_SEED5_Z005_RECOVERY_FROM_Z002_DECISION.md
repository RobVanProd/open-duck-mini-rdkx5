# Phase 2 A2 Seed-5 z=0.005 Recovery From z=0.002 Decision

status: `PASS_RECOVERY_RELABEL_READY_HOLD_SOURCE_GATE`

This is an offline data-curation artifact. It did not train, SSH, deploy, run
robot tests, grounded replay, or change runtime behavior.

## Purpose

The Phase A2 candidate survives seed 5 at `terrain_hfield_z_scale=0.002` but
collapses at `0.005` from the same reset. The z=0.005 failure diverges between
ticks 20-60 while remaining inside the corrected actuator envelope. This
artifact creates a small recovery relabel slice: keep the failing z=0.005
observations, but label them with same-tick actions from the passing z=0.002
trace.

## Inputs

- failing trace: `outputs/analysis/phase2_a2_seed5_z005_x000_2s_fullobs_trace.jsonl`
- passing trace: `outputs/analysis/phase2_a2_seed5_z002_x000_2s_fullobs_trace.jsonl`
- relabel window: ticks `20-60`
- capped pitch-chain velocity: `2.0 rad/s`
- sample weight: `4.0`

## Outputs

| artifact | status |
|---|---|
| `outputs/analysis/PHASE2_A2_SEED5_Z005_RECOVERY_FROM_Z002_RELABEL.md` | `PASS_SEED_RECOVERY_NEIGHBOR_RELABEL_READY` |
| `outputs/analysis/PHASE2_A2_SEED5_Z005_RECOVERY_FROM_Z002_BC_MANIFEST.md` | `PASS_BC_TRACE_MANIFEST_READY` |
| `outputs/analysis/PHASE2_A2_SEED5_Z005_RECOVERY_FROM_Z002_BC_MANIFEST_CHECK.md` | `HOLD_TARGET_DATASET_SANITY_ERRORS` |

## Interpretation

The recovery slice is structurally usable as `obs[101] -> action[14]` BC data:

- samples: `41`
- missing neighbor ticks: `0`
- capped action components: `0`
- BC-ready manifest entries: `1/1`

It is not a standalone positive target-source window:

- mean vx is negative,
- body pitch and base-height metrics include the failing z=0.005 collapse,
- the slice contains a terminal row,
- the sanity checker correctly holds it as a target dataset.

This is expected. The slice is recovery supervision for student-visited failure
states, not a source gate pass.

## Decision

Do not train from this slice alone and do not treat it as a z=0.005 source-gate
pass. It can be used only as one weighted recovery component in a larger
policy-derived manifest that also contains stable Phase A2 walking/standing
windows.

Recommended next step:

1. assemble a composite policy-derived manifest with stable z=0.002 Phase A2
   windows plus this z=0.005 recovery relabel slice;
2. run a BC smoke or DAgger iteration only after the composite manifest passes
   BC readiness and does not over-concentrate on the failing seed-5 slice;
3. gate any resulting student first on the short seed-5 z=0.005 support check,
   then on the full 8-seed z=0.005 source gate.
