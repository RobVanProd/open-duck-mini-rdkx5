# Phase 2 Command-Gated Seed5 Rate160 Anti-Lunge Transfer Decision
status: `PASS_SEED5_RATE160_ANTILUNGE_TRANSFER_DATA_READY`

## Scope
- Offline data curation only.
- No training, robot tests, SSH, deploy, grounded replay, or runtime behavior change was performed.

## Artifacts
- relabel: `outputs/analysis/phase2_command_gated_seed5_rate160_antilunge_relabel.json`
- manifest: `outputs/analysis/phase2_command_gated_seed5_rate160_antilunge_manifest.json`
- dataset_id: `aa55227d46236696`
- entries: `1`
- samples: `24`

## Selection
- tick window: `80-157`
- selected samples: `24`
- score threshold: `5.0`
- sample weight: `6.0`

## Interpretation
- This prepares a narrow seed-5 anti-lunge transfer dataset using command-gated failure observations and rate160 stable actions.
- The artifact is not a trained candidate and is not promotable by itself.
- The next bounded step is to merge this manifest into the command-gated/source manifest with low weight, train one student, and gate seed5 plus regression-control seeds before any full-8 rerun.
