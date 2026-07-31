# Phase 2 Home-Reset z0.0026 Rate-Cap A100 Transport Hold

status: `HOLD_COLAB_TRANSPORT_ARTIFACT_EMPTY`

## Setup

- source candidate: `policy/candidates/corrected_bridge_cmd_conditioned_rate175_20260627/candidate.onnx`
- source candidate sha256: `63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e`
- warm-start checkpoint: `outputs/analysis/phase2_restore_checkpoints/ppo_bc_command_conditioned_rate175_step0_checkpoint`
- Colab session: `open-duck-a100-phase2-ratecap`
- Colab hardware: `A100`
- workflow: `phase2-z0025-boundary`
- terrain hfield z scale: `0.0026`
- reset randomization: zero jitter / unit qpos multiplier
- robot/SSH/deploy/grounded replay: `not run`

## Intended Recipe Delta

This follow-up was launched because the previous A100 continuation trained with
`target_rate_scale=0.0`, then failed the evaluator by producing over-envelope
target velocities. This attempt added the corrected per-joint rate penalties:

- `--phase2-target-rate-scale -0.02`
- `--phase2-actuator-tracking-scale -0.01`
- `--phase2-forward-swing-target-rate-limit-scale -0.04`
- `--phase2-forward-swing-target-rate-limit-joint-indices 2,3,4,11,12,13`
- `--phase2-forward-swing-target-rate-limit-values 2.5,3.25,2.75,2.25,2.75,2.0`
- `--restore-policy-kl-scale 8`

## Observed Result

The Colab backend later reported the session as `IDLE`, but the downloaded final
artifact contained only:

- `COLAB_CLI_EXIT_STATUS.txt`
- `COLAB_CLI_HEARTBEAT.json`
- `POLICY_SIM_CONTRACT_AUDIT_CUDA.md`
- `policy_sim_contract_audit_cuda.json`

No training checkpoint, ONNX export, smoke manifest, stdout, or stderr was
present in the bundle. The expected remote `.log` and `.exit` files were also
not downloadable through the CLI.

Artifact bundle:

- path: `outputs/analysis/colab_cli/open-duck-a100-phase2-ratecap-phase2-z0025-boundary-20260703T052320Z/final_download/open_duck_colab_cli_phase2-z0025-boundary_20260703T052331Z_artifacts.tar.gz`
- sha256: `a8524c9744a76b7c26195a8559402400224136b5d88920510232579a67c3615c`

Driver script:

- path: `outputs/analysis/colab_cli/open-duck-a100-phase2-ratecap-phase2-z0025-boundary-20260703T052320Z/open_duck_colab_cli_phase2-z0025-boundary_20260703T052331Z_driver.py`
- sha256: `fa0b58ed306a8abf95526c3c62437fe349534718207c9813025203f767414e86`

## Decision

This run is not a valid training result and must not be interpreted as evidence
that the rate-cap recipe passed or failed. It is an infrastructure hold caused
by the Colab CLI execution/artifact path returning an empty heartbeat-only
bundle.

Next A100 launch should run the remote driver detached inside the Colab VM and
poll artifact files, instead of relying on one long-lived `colab exec` transport
stream.
