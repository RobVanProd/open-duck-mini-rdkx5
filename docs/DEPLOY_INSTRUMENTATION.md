# Deploy Instrumentation To The RDK-X5

Purpose: safely stage sim-to-real diagnostic files and the opt-in walker telemetry patch onto the live RDK-X5 runtime without starting motors, walking, or changing robot behavior by default.

This deploy step is required before the first evidence packet if the board runtime does not already contain:

```text
/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/mini_bdx_runtime/mini_bdx_runtime/telemetry.py
/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/mini_bdx_runtime/mini_bdx_runtime/rustypot_position_hwi.py
/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts/sim2real_diagnostics.py
/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts/v2_rl_walk_mujoco.py
```

## Safety Rules

- Default mode is dry-run only.
- Do not deploy while a walking process is running.
- Do not run moving diagnostics from this workflow.
- Do not copy policy files.
- Do not copy `duck_config.json`.
- Do not change gains, offsets, IMU remaps, action scale, phase timing, or policy files.
- Back up existing board files before overwriting them.
- Walker telemetry must stay disabled unless `--log-telemetry` is explicitly passed.
- HWI bus counters must only observe existing retry failures; they must not add servo bus traffic.
- Keep SSH keys, known_hosts files, raw JSONL logs, videos, and secrets outside git.

## Local Contract Check

Before deploying the walker telemetry patch, verify the runtime exposes the
required default-off telemetry contract without importing hardware modules:

```bash
python3 tools/check_runtime_telemetry_contract.py
```

## Dry Run

Run this first. It validates local source files and tools, prints the plan, and writes a local dry-run summary. It does not run SSH or copy files.

```bash
bash scripts/deploy_instrumentation_to_duck.sh --dry-run
```

Optional explicit paths:

```bash
bash scripts/deploy_instrumentation_to_duck.sh \
  --dry-run \
  --ssh sunrise@192.168.1.50 \
  --identity-file /home/lsd/robots/.duck_access/rdk_key \
  --known-hosts /home/lsd/robots/.duck_access/known_hosts \
  --robot-runtime /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5 \
  --robot-python /home/sunrise/duck_env/bin/python
```

## Verify No Robot Process Is Running

Before applying, inspect the board manually and stop if any walking or motor process is active:

```bash
ssh -i /home/lsd/robots/.duck_access/rdk_key \
  -o UserKnownHostsFile=/home/lsd/robots/.duck_access/known_hosts \
  -o StrictHostKeyChecking=no \
  sunrise@192.168.1.50 \
  "pgrep -af 'v2_rl_walk|sim2real_diagnostics|run_xbox_walk|python.*walk' || true"
```

This is an inspection command only. Do not start, unpause, or run any movement from this step.

## Apply

Only apply after the dry-run plan looks correct.

```bash
bash scripts/deploy_instrumentation_to_duck.sh --apply
```

The script will ask for:

```text
DEPLOY_INSTRUMENTATION
```

Apply mode:

- validates the board runtime path and Python path,
- creates a board backup directory,
- backs up any destination file that already exists,
- copies only the intended instrumentation files and opt-in walker telemetry patch,
- verifies source and destination SHA256 hashes,
- runs non-moving import/help checks,
- writes a local deployment summary.

## Expected Output

Local deployment evidence:

```text
outputs/deployments/<timestamp>/DEPLOYMENT_SUMMARY.md
outputs/deployments/<timestamp>/import_check.txt
outputs/deployments/<timestamp>/sim2real_diagnostics_help.txt
outputs/deployments/<timestamp>/v2_rl_walk_mujoco_help.txt
```

Board backup path:

```text
/home/sunrise/duck_backups/<timestamp>/
```

The summary records source hashes, destination hashes, backup paths, commands run, and the explicit statement that no hardware-moving tests were run.

## Rollback

If a deployment needs to be reverted, copy the backed-up files from the board backup directory back to the runtime paths. Example:

```bash
ssh -i /home/lsd/robots/.duck_access/rdk_key \
  -o UserKnownHostsFile=/home/lsd/robots/.duck_access/known_hosts \
  -o StrictHostKeyChecking=no \
  sunrise@192.168.1.50 \
  "cp -p /home/sunrise/duck_backups/<timestamp>/scripts/sim2real_diagnostics.py /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts/sim2real_diagnostics.py"
```

Only restore files that exist in the backup. Do not replace the whole runtime tree.

For the opt-in walker telemetry patch, restore:

```text
/home/sunrise/duck_backups/<timestamp>/scripts/v2_rl_walk_mujoco.py
```

For the HWI bus counter patch, restore:

```text
/home/sunrise/duck_backups/<timestamp>/mini_bdx_runtime/mini_bdx_runtime/rustypot_position_hwi.py
```

## Next Step

After a clean deploy summary, continue to the first evidence packet in
[FIRST_EVIDENCE_PACKET.md](FIRST_EVIDENCE_PACKET.md):

```bash
bash scripts/collect_first_evidence.sh --run-readonly
```

Then, with Rob physically present and the Duck supported:

```bash
bash scripts/collect_first_evidence.sh \
  --i-am-physically-present \
  --run-moving
```

Stop before walking if home pose or IMU tilt evidence fails.
