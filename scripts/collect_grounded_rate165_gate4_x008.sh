#!/usr/bin/env bash
set -euo pipefail

SSH_TARGET="sunrise@192.168.1.50"
IDENTITY_FILE="/home/lsd/robots/.duck_access/rdk_key"
KNOWN_HOSTS="/home/lsd/robots/.duck_access/known_hosts"
ROBOT_RUNTIME="/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5"
ROBOT_PYTHON="/home/sunrise/duck_env/bin/python"
CANDIDATE="/home/sunrise/phase2_grounded_rate165_20260712_e06643e5.onnx"
CANDIDATE_SHA="e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33"
CONFIG_SHA="131a7b8fce1107b14f4727562f44f9e17324caf7fc22512ad7115911f050991b"
HWI_SHA="f352b66ab44ec5a302a08c413aeaa21fa693555c7a41c536d1ff18f208b43fdc"
DIAGNOSTIC_SHA="083af9c85b797699ebd44b1b98de29b931cd27e8cbeaf06d10914d2559e5a698"
WALKER_SHA="d81ad59c29e3a24d5c8e278eaf0898b4d3505ad22bb60ee74776537202eb2dfc"
TURN_OFF_SHA="99451bfa66f838e617585be695e03970b789222e00724fadc40f722b5f2c2090"
OUTPUT_DIR="outputs/first_evidence/$(date -u +%Y%m%dT%H%M%SZ)_id13last_gate4_x008"
SNAPSHOT=""
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
Suspended Gate 4 only:
  command: x=0.08, y=0, yaw=0
  duration: 15 seconds
  policy: $CANDIDATE
  policy SHA256: $CANDIDATE_SHA
  HWI SHA256: $HWI_SHA (ID 13 read last)
  action scale: 0.25
  telemetry: every tick

This runner has no x=0 mode and no grounded mode.
EOF

[[ "$RUN" -eq 1 ]] || exit 0
[[ "$PRESENT" -eq 1 ]] || { echo "Refused: physical-presence flag required." >&2; exit 2; }
[[ -n "$SNAPSHOT" && -f "$SNAPSHOT" ]] || { echo "Refused: fresh --snapshot required." >&2; exit 2; }

python3 - "$SNAPSHOT" "$CANDIDATE_SHA" <<'PY'
import datetime as dt, json, sys
d=json.load(open(sys.argv[1])); expected=sys.argv[2]
assert d.get("schema_version") == "open_duck_mini_config_snapshot_v2"
stamp=dt.datetime.fromisoformat((d.get("collector_utc") or d["snapshot_utc"]).replace("Z", "+00:00"))
age=(dt.datetime.now(dt.timezone.utc)-stamp).total_seconds()
assert -300 <= age <= 86400, f"snapshot age invalid: {age:.0f}s"
inventory={x["path"]:x.get("sha256") for x in d.get("onnx_policy_inventory",[])}
assert inventory.get("/home/sunrise/phase2_grounded_rate165_20260712_e06643e5.onnx") == expected
assert (d.get("duck_config") or {}).get("start_paused") is True
PY

SSH_OPTS=(-i "$IDENTITY_FILE" -o "UserKnownHostsFile=$KNOWN_HOSTS"
  -o "StrictHostKeyChecking=yes" -o "ConnectTimeout=5")
REMOTE_JSONL="/home/sunrise/duck_logs/id13last_gate4_x008.jsonl"
REMOTE_TERMINAL="/home/sunrise/duck_logs/id13last_gate4_x008_terminal.log"
LOCAL_JSONL="$OUTPUT_DIR/suspended_x008.jsonl"
LOCAL_TERMINAL="$OUTPUT_DIR/suspended_x008_terminal.log"
LOCAL_ANALYSIS="$OUTPUT_DIR/suspended_x008_gate.md"

remote_preflight='set -eu
test "$(sha256sum /home/sunrise/phase2_grounded_rate165_20260712_e06643e5.onnx | cut -d " " -f1)" = "'"$CANDIDATE_SHA"'"
test "$(sha256sum /home/sunrise/duck_config.json | cut -d " " -f1)" = "'"$CONFIG_SHA"'"
test "$(sha256sum /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/mini_bdx_runtime/mini_bdx_runtime/rustypot_position_hwi.py | cut -d " " -f1)" = "'"$HWI_SHA"'"
test "$(sha256sum /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts/sim2real_diagnostics.py | cut -d " " -f1)" = "'"$DIAGNOSTIC_SHA"'"
test "$(sha256sum /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts/v2_rl_walk_mujoco.py | cut -d " " -f1)" = "'"$WALKER_SHA"'"
test "$(sha256sum /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts/turn_off.py | cut -d " " -f1)" = "'"$TURN_OFF_SHA"'"
python3 -c "import json; assert json.load(open(\"/home/sunrise/duck_config.json\"))[\"start_paused\"] is True"
ps -eo comm=,args= | awk '\''$1 ~ /^python/ && $0 ~ /(v2_rl_walk|run_xbox_walk|sim2real_diagnostics|mini_bdx_runtime|servo_crc)/ {found=1} END {exit found}'\''
! fuser /dev/ttyACM0 >/dev/null 2>&1'
ssh -n "${SSH_OPTS[@]}" "$SSH_TARGET" "$remote_preflight"

echo "This engages motors for 15 seconds at suspended x=0.08."
read -r -p "Type RUN_SUSPENDED_X008_GATE4 to continue: " confirmation
[[ "$confirmation" == "RUN_SUSPENDED_X008_GATE4" ]] || { echo "Aborted."; exit 1; }

mkdir -p "$OUTPUT_DIR"
cleanup() {
  ssh -n "${SSH_OPTS[@]}" "$SSH_TARGET" \
    "cd '$ROBOT_RUNTIME/scripts' && '$ROBOT_PYTHON' turn_off.py" || true
}
trap cleanup EXIT

remote_run=$(printf 'mkdir -p /home/sunrise/duck_logs && rm -f %q %q && cd %q && set -o pipefail && printf "\\n" | %q sim2real_diagnostics.py suspended_policy_replay --onnx_model_path %q --command-x 0.08 --duration 15 --action_scale 0.25 --telemetry-path %q --telemetry-every-n 1 --i-understand-this-moves-the-robot 2>&1 | tee %q' \
  "$REMOTE_JSONL" "$REMOTE_TERMINAL" "$ROBOT_RUNTIME/scripts" "$ROBOT_PYTHON" \
  "$CANDIDATE" "$REMOTE_JSONL" "$REMOTE_TERMINAL")
ssh -n "${SSH_OPTS[@]}" "$SSH_TARGET" "$remote_run"
scp "${SSH_OPTS[@]}" "$SSH_TARGET:$REMOTE_JSONL" "$LOCAL_JSONL"
scp "${SSH_OPTS[@]}" "$SSH_TARGET:$REMOTE_TERMINAL" "$LOCAL_TERMINAL"
python3 tools/analyze_suspended_replay.py "$LOCAL_JSONL" \
  --terminal-log "$LOCAL_TERMINAL" --output "$LOCAL_ANALYSIS"
cleanup
trap - EXIT
echo "Gate 4 captured. Stop for numeric and visual review; no grounded continuation."
