#!/usr/bin/env bash
set -euo pipefail

SSH_TARGET="sunrise@192.168.1.50"
IDENTITY_FILE="/home/lsd/robots/.duck_access/rdk_key"
KNOWN_HOSTS="/home/lsd/robots/.duck_access/known_hosts"
RUNTIME="/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5"
STAGE_DIR="/home/sunrise/rate165_hard_vector_stage_20260712"
POLICY="/home/sunrise/phase2_grounded_rate165_20260712_e06643e5.onnx"
POLICY_SHA="e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33"
CONFIG_SHA="131a7b8fce1107b14f4727562f44f9e17324caf7fc22512ad7115911f050991b"
HWI_SHA="f352b66ab44ec5a302a08c413aeaa21fa693555c7a41c536d1ff18f208b43fdc"
OLD_WALKER_SHA="b9732bfa1deca5d6a7a062f757589a6327c7b000d0d855f56eec500535c25c17"
OLD_DIAG_SHA="f284332c543af360cc73931ac646a5198de4bc58ad27ad18681fb326a1b937c2"
WALKER_SHA="e282f927c17bfc1c6c9fc9d958a597e2f8c1cf8733962ada3a44593a008632c5"
PARSER_SHA="dd139f1b7043a4ddbe64e5242ab8316e5a6216a6dbe2d4347a5f4c6eb3204eee"
DIAG_SHA="49f4074e0f1bbfa8749a5e1af398570eab0e70d40963ba40551499b38429493b"
RUN=0; APPROVE=0; SNAPSHOT=""
OUTPUT="outputs/analysis/rate165_hard_vector_install_manifest.json"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --run) RUN=1; shift ;;
    --i-approve-live-install) APPROVE=1; shift ;;
    --snapshot) SNAPSHOT="$2"; shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done
cat <<EOF
Rate165 hard-vector live installation plan:
  source: verified side-by-side stage
  changes: walker, parser, diagnostic only
  backup: timestamped board-local directory
  HWI import / serial open / torque / movement: none
This runner does not execute a policy or motor test.
EOF
[[ "$RUN" -eq 1 ]] || exit 0
[[ "$APPROVE" -eq 1 ]] || { echo "Refused: --i-approve-live-install required." >&2; exit 2; }
[[ -n "$SNAPSHOT" && -f "$SNAPSHOT" ]] || { echo "Refused: fresh --snapshot required." >&2; exit 2; }
python3 - "$SNAPSHOT" "$POLICY" "$POLICY_SHA" <<'PY'
import datetime as dt,json,sys
d=json.load(open(sys.argv[1])); stamp=dt.datetime.fromisoformat((d.get('collector_utc') or d['snapshot_utc']).replace('Z','+00:00'))
assert -300 <= (dt.datetime.now(dt.timezone.utc)-stamp).total_seconds() <= 600
assert (d.get('duck_config') or {}).get('start_paused') is True
assert {x['path']:x.get('sha256') for x in d.get('onnx_policy_inventory',[])}.get(sys.argv[2]) == sys.argv[3]
PY
SSH_OPTS=(-i "$IDENTITY_FILE" -o "UserKnownHostsFile=$KNOWN_HOSTS" -o "StrictHostKeyChecking=yes" -o "ConnectTimeout=5")
preflight='set -eu
test "$(sha256sum '"$POLICY"' | cut -d " " -f1)" = "'"$POLICY_SHA"'"
test "$(sha256sum /home/sunrise/duck_config.json | cut -d " " -f1)" = "'"$CONFIG_SHA"'"
test "$(sha256sum '"$RUNTIME"'/mini_bdx_runtime/mini_bdx_runtime/rustypot_position_hwi.py | cut -d " " -f1)" = "'"$HWI_SHA"'"
test "$(sha256sum '"$RUNTIME"'/scripts/v2_rl_walk_mujoco.py | cut -d " " -f1)" = "'"$OLD_WALKER_SHA"'"
test "$(sha256sum '"$RUNTIME"'/scripts/sim2real_diagnostics.py | cut -d " " -f1)" = "'"$OLD_DIAG_SHA"'"
test "$(sha256sum '"$STAGE_DIR"'/v2_rl_walk_mujoco.py | cut -d " " -f1)" = "'"$WALKER_SHA"'"
test "$(sha256sum '"$STAGE_DIR"'/motor_velocity_limits.py | cut -d " " -f1)" = "'"$PARSER_SHA"'"
test "$(sha256sum '"$STAGE_DIR"'/sim2real_diagnostics.py | cut -d " " -f1)" = "'"$DIAG_SHA"'"
ps -eo comm=,args= | awk '\''$1 ~ /^python/ && $0 ~ /(v2_rl_walk|sim2real_diagnostics|mini_bdx_runtime)/ {found=1} END {exit found}'\''
! fuser /dev/ttyACM0 >/dev/null 2>&1'
ssh -n "${SSH_OPTS[@]}" "$SSH_TARGET" "$preflight"
read -r -p "Type INSTALL_RATE165_HARD_VECTOR_LIVE to continue: " confirmation
[[ "$confirmation" == "INSTALL_RATE165_HARD_VECTOR_LIVE" ]] || { echo "Aborted."; exit 1; }
remote_manifest=$(ssh -n "${SSH_OPTS[@]}" "$SSH_TARGET" "set -eu
  backup=/home/sunrise/runtime_backup_rate165_vector_\$(date -u +%Y%m%dT%H%M%SZ)
  mkdir -p \"\$backup\"
  cp '$RUNTIME/scripts/v2_rl_walk_mujoco.py' \"\$backup/\"
  cp '$RUNTIME/scripts/sim2real_diagnostics.py' \"\$backup/\"
  test ! -e '$RUNTIME/scripts/motor_velocity_limits.py' || cp '$RUNTIME/scripts/motor_velocity_limits.py' \"\$backup/\"
  install -m 0644 '$STAGE_DIR/v2_rl_walk_mujoco.py' '$RUNTIME/scripts/v2_rl_walk_mujoco.py'
  install -m 0644 '$STAGE_DIR/motor_velocity_limits.py' '$RUNTIME/scripts/motor_velocity_limits.py'
  install -m 0644 '$STAGE_DIR/sim2real_diagnostics.py' '$RUNTIME/scripts/sim2real_diagnostics.py'
  /home/sunrise/duck_env/bin/python -m py_compile '$RUNTIME/scripts/v2_rl_walk_mujoco.py' '$RUNTIME/scripts/motor_velocity_limits.py' '$RUNTIME/scripts/sim2real_diagnostics.py'
  test \"\$(sha256sum '$RUNTIME/scripts/v2_rl_walk_mujoco.py' | cut -d ' ' -f1)\" = '$WALKER_SHA'
  test \"\$(sha256sum '$RUNTIME/scripts/motor_velocity_limits.py' | cut -d ' ' -f1)\" = '$PARSER_SHA'
  test \"\$(sha256sum '$RUNTIME/scripts/sim2real_diagnostics.py' | cut -d ' ' -f1)\" = '$DIAG_SHA'
  ps -eo comm=,args= | awk '\''\$1 ~ /^python/ && \$0 ~ /(v2_rl_walk|sim2real_diagnostics|mini_bdx_runtime)/ {found=1} END {exit found}'\''
  ! fuser /dev/ttyACM0 >/dev/null 2>&1
  printf '{\"status\":\"PASS_LIVE_INSTALL_NO_HWI\",\"backup\":\"%s\",\"hwi_initialized\":false,\"motors_engaged\":false}\n' \"\$backup\"")
mkdir -p "$(dirname "$OUTPUT")"; printf '%s\n' "$remote_manifest" > "$OUTPUT"
echo "Live install complete. Stop for fresh snapshot/review; no motor test was run."
