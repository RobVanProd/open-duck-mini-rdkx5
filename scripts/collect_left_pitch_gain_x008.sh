#!/usr/bin/env bash
set -euo pipefail

SSH_TARGET="sunrise@192.168.1.50"
IDENTITY_FILE="/home/lsd/robots/.duck_access/rdk_key"
KNOWN_HOSTS="/home/lsd/robots/.duck_access/known_hosts"
RUNTIME="/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5"
PYTHON="/home/sunrise/duck_env/bin/python"
POLICY="/home/sunrise/phase2_grounded_rate165_20260712_e06643e5.onnx"
POLICY_SHA="e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33"
CONFIG_SHA="131a7b8fce1107b14f4727562f44f9e17324caf7fc22512ad7115911f050991b"
HWI_SHA="f352b66ab44ec5a302a08c413aeaa21fa693555c7a41c536d1ff18f208b43fdc"
WALKER_SHA="b9732bfa1deca5d6a7a062f757589a6327c7b000d0d855f56eec500535c25c17"
DIAG_SHA="f284332c543af360cc73931ac646a5198de4bc58ad27ad18681fb326a1b937c2"
RESTORE_SHA="9fd5f639ceb342dd5d33c203936907929af35e7fc78b7d8ee83e693e7838f152"
SNAPSHOT=""
OUTPUT_DIR="outputs/first_evidence/$(date -u +%Y%m%dT%H%M%SZ)_left_pitch_gain_x008"
RUN=0
PRESENT=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run) RUN=1; shift ;;
    --i-am-physically-present) PRESENT=1; shift ;;
    --snapshot) SNAPSHOT="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

cat <<EOF
Suspended left pitch-chain gain Gate 4:
  command: x=0.08 only
  duration: 15 seconds
  left_hip_pitch P: 31
  left_knee P: 34
  cleanup: restore body/head P 30/8, D 0; torque off
This runner has no x=0 or grounded mode.
EOF

[[ "$RUN" -eq 1 ]] || exit 0
[[ "$PRESENT" -eq 1 ]] || { echo "Refused: physical-presence flag required." >&2; exit 2; }
[[ -n "$SNAPSHOT" && -f "$SNAPSHOT" ]] || { echo "Refused: fresh --snapshot required." >&2; exit 2; }

python3 - "$SNAPSHOT" "$POLICY_SHA" <<'PY'
import datetime as dt, json, sys
d=json.load(open(sys.argv[1])); expected=sys.argv[2]
assert d.get("schema_version") == "open_duck_mini_config_snapshot_v2"
stamp=dt.datetime.fromisoformat((d.get("collector_utc") or d["snapshot_utc"]).replace("Z", "+00:00"))
assert -300 <= (dt.datetime.now(dt.timezone.utc)-stamp).total_seconds() <= 86400
inventory={x["path"]:x.get("sha256") for x in d.get("onnx_policy_inventory",[])}
assert inventory.get("/home/sunrise/phase2_grounded_rate165_20260712_e06643e5.onnx") == expected
assert (d.get("duck_config") or {}).get("start_paused") is True
PY

SSH_OPTS=(-i "$IDENTITY_FILE" -o "UserKnownHostsFile=$KNOWN_HOSTS"
  -o "StrictHostKeyChecking=yes" -o "ConnectTimeout=5")
REMOTE_JSONL="/home/sunrise/duck_logs/left_pitch_gain_x008.jsonl"
REMOTE_TERMINAL="/home/sunrise/duck_logs/left_pitch_gain_x008_terminal.log"
LOCAL_JSONL="$OUTPUT_DIR/suspended_x008.jsonl"
LOCAL_TERMINAL="$OUTPUT_DIR/suspended_x008_terminal.log"

preflight='set -eu
test "$(sha256sum /home/sunrise/phase2_grounded_rate165_20260712_e06643e5.onnx | cut -d " " -f1)" = "'"$POLICY_SHA"'"
test "$(sha256sum /home/sunrise/duck_config.json | cut -d " " -f1)" = "'"$CONFIG_SHA"'"
test "$(sha256sum '"$RUNTIME"'/mini_bdx_runtime/mini_bdx_runtime/rustypot_position_hwi.py | cut -d " " -f1)" = "'"$HWI_SHA"'"
test "$(sha256sum '"$RUNTIME"'/scripts/v2_rl_walk_mujoco.py | cut -d " " -f1)" = "'"$WALKER_SHA"'"
test "$(sha256sum '"$RUNTIME"'/scripts/sim2real_diagnostics.py | cut -d " " -f1)" = "'"$DIAG_SHA"'"
test "$(sha256sum '"$RUNTIME"'/scripts/restore_runtime_gains_and_turn_off.py | cut -d " " -f1)" = "'"$RESTORE_SHA"'"
ps -eo comm=,args= | awk '\''$1 ~ /^python/ && $0 ~ /(v2_rl_walk|sim2real_diagnostics|mini_bdx_runtime)/ {found=1} END {exit found}'\''
! fuser /dev/ttyACM0 >/dev/null 2>&1'
ssh -n "${SSH_OPTS[@]}" "$SSH_TARGET" "$preflight"

read -r -p "Type RUN_SUSPENDED_X008_GAIN_31_34 to continue: " confirmation
[[ "$confirmation" == "RUN_SUSPENDED_X008_GAIN_31_34" ]] || { echo "Aborted."; exit 1; }
mkdir -p "$OUTPUT_DIR"
cleanup() {
  ssh -n "${SSH_OPTS[@]}" "$SSH_TARGET" \
    "cd '$RUNTIME/scripts' && '$PYTHON' restore_runtime_gains_and_turn_off.py" || true
}
trap cleanup EXIT

remote_run=$(printf 'rm -f %q %q && cd %q && set -o pipefail && printf "\\n" | %q sim2real_diagnostics.py suspended_policy_replay --onnx_model_path %q --command-x 0.08 --duration 15 --action_scale 0.25 --left-hip-pitch-kp 31 --left-knee-kp 34 --telemetry-path %q --telemetry-every-n 1 --i-understand-this-moves-the-robot 2>&1 | tee %q' \
  "$REMOTE_JSONL" "$REMOTE_TERMINAL" "$RUNTIME/scripts" "$PYTHON" "$POLICY" \
  "$REMOTE_JSONL" "$REMOTE_TERMINAL")
ssh -n "${SSH_OPTS[@]}" "$SSH_TARGET" "$remote_run"
scp "${SSH_OPTS[@]}" "$SSH_TARGET:$REMOTE_JSONL" "$LOCAL_JSONL"
scp "${SSH_OPTS[@]}" "$SSH_TARGET:$REMOTE_TERMINAL" "$LOCAL_TERMINAL"
python3 tools/analyze_suspended_replay.py "$LOCAL_JSONL" \
  --terminal-log "$LOCAL_TERMINAL" --output "$OUTPUT_DIR/suspended_x008_gate.md"
cleanup
trap - EXIT
echo "Gain x=0.08 gate captured. Stop for review; no grounded continuation."
