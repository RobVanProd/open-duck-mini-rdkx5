#!/usr/bin/env bash
set -euo pipefail

SSH_TARGET="sunrise@192.168.1.50"
IDENTITY_FILE="/home/lsd/robots/.duck_access/rdk_key"
KNOWN_HOSTS="/home/lsd/robots/.duck_access/known_hosts"
ROBOT_RUNTIME="/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5"
ROBOT_PYTHON="/home/sunrise/duck_env/bin/python"
ROBOT_POLICY="/home/sunrise/BEST_WALK_ONNX_2.onnx"
ROBOT_LOG_DIR="/home/sunrise/duck_logs"
OUTPUT_DIR="outputs/first_evidence/$(date -u +%Y%m%dT%H%M%SZ)_grounded_rate165_gate01"
MODE="plan"
PHYSICALLY_PRESENT=0
GATE0_SNAPSHOT=""

usage() {
  cat <<'EOF'
Usage: collect_grounded_rate165_gate01.sh [options]

Modes are mutually exclusive:
  --run-gate0               Read-only SSH snapshot only.
  --run-gate1               Supported home-pose command and analysis only.
                            Requires --gate0-snapshot and
                            --i-am-physically-present.

Without a run mode, print the exact plan and perform no SSH.

Options:
  --gate0-snapshot PATH     Fresh reviewed v2 snapshot required by Gate 1.
  --i-am-physically-present Required for Gate 1.
  --ssh TARGET
  --identity-file PATH
  --known-hosts PATH
  --robot-runtime PATH
  --output-dir PATH
EOF
}

set_mode() {
  if [[ "$MODE" != "plan" ]]; then
    echo "Only one run mode may be selected." >&2
    exit 2
  fi
  MODE="$1"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-gate0) set_mode gate0; shift ;;
    --run-gate1) set_mode gate1; shift ;;
    --gate0-snapshot) GATE0_SNAPSHOT="$2"; shift 2 ;;
    --i-am-physically-present) PHYSICALLY_PRESENT=1; shift ;;
    --ssh) SSH_TARGET="$2"; shift 2 ;;
    --identity-file) IDENTITY_FILE="$2"; shift 2 ;;
    --known-hosts) KNOWN_HOSTS="$2"; shift 2 ;;
    --robot-runtime) ROBOT_RUNTIME="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

SSH_OPTS=(-i "$IDENTITY_FILE" -o "UserKnownHostsFile=$KNOWN_HOSTS"
  -o "StrictHostKeyChecking=yes" -o "ConnectTimeout=5")
REMOTE_TELEMETRY="$ROBOT_LOG_DIR/grounded_rate165_supported_home.jsonl"
REMOTE_TERMINAL="$ROBOT_LOG_DIR/grounded_rate165_supported_home_terminal.log"
LOCAL_TELEMETRY="$OUTPUT_DIR/supported_home.jsonl"
LOCAL_TERMINAL="$OUTPUT_DIR/supported_home_terminal.log"
LOCAL_MD="$OUTPUT_DIR/supported_home_telemetry_gate.md"
LOCAL_JSON="$OUTPUT_DIR/supported_home_telemetry_gate.json"

require_file() { [[ -f "$1" ]] || { echo "Missing required file: $1" >&2; exit 1; }; }

snapshot_command() {
  printf 'python3 tools/snapshot_robot_config.py --ssh %q --identity-file %q --known-hosts %q --strict-host-key-checking yes --output-dir %q' \
    "$SSH_TARGET" "$IDENTITY_FILE" "$KNOWN_HOSTS" "$OUTPUT_DIR"
}

remote_home_command() {
  printf 'mkdir -p %q && cd %q && set -o pipefail && %q sim2real_diagnostics.py home_pose_log_test --onnx_model_path %q --telemetry-path %q --torque-off-on-exit --i-understand-this-moves-the-robot 2>&1 | tee %q' \
    "$ROBOT_LOG_DIR" "$ROBOT_RUNTIME/scripts" "$ROBOT_PYTHON" "$ROBOT_POLICY" \
    "$REMOTE_TELEMETRY" "$REMOTE_TERMINAL"
}

print_plan() {
  cat <<EOF
Gate 0 (read-only SSH; requires explicit Gate-0 approval):
  $(snapshot_command)

Gate 1 (moves to supported home; separately approved; robot supported and Rob present):
  ssh ${SSH_OPTS[*]} $SSH_TARGET $(printf %q "$(remote_home_command)")
  scp ${SSH_OPTS[*]} $SSH_TARGET:$REMOTE_TELEMETRY $LOCAL_TELEMETRY
  scp ${SSH_OPTS[*]} $SSH_TARGET:$REMOTE_TERMINAL $LOCAL_TERMINAL
  python3 tools/evaluate_supported_home_telemetry.py $LOCAL_TELEMETRY \\
    --terminal-log $LOCAL_TERMINAL --output-md $LOCAL_MD --output-json $LOCAL_JSON

Gate 1 telemetry pass is not physical-pose approval. Record the visual decision separately.
EOF
}

require_file tools/snapshot_robot_config.py
require_file tools/evaluate_supported_home_telemetry.py
print_plan
[[ "$MODE" == "plan" ]] && exit 0

require_file "$IDENTITY_FILE"
require_file "$KNOWN_HOSTS"
mkdir -p "$OUTPUT_DIR"

if [[ "$MODE" == "gate0" ]]; then
  python3 tools/snapshot_robot_config.py --ssh "$SSH_TARGET" \
    --identity-file "$IDENTITY_FILE" --known-hosts "$KNOWN_HOSTS" \
    --strict-host-key-checking yes --output-dir "$OUTPUT_DIR"
  exit 0
fi

[[ "$PHYSICALLY_PRESENT" -eq 1 ]] || {
  echo "Gate 1 refused: --i-am-physically-present is required." >&2; exit 2; }
[[ -n "$GATE0_SNAPSHOT" ]] || {
  echo "Gate 1 refused: --gate0-snapshot is required." >&2; exit 2; }
require_file "$GATE0_SNAPSHOT"
python3 - "$GATE0_SNAPSHOT" <<'PY'
import datetime as dt, json, sys
data=json.load(open(sys.argv[1]))
assert data.get("schema_version") == "open_duck_mini_config_snapshot_v2", "Gate 0 snapshot must use v2 schema"
assert data.get("snapshot_utc"), "Gate 0 snapshot timestamp missing"
trusted_time=data.get("collector_utc") or data["snapshot_utc"]
stamp=dt.datetime.fromisoformat(trusted_time.replace("Z", "+00:00"))
age=(dt.datetime.now(dt.timezone.utc)-stamp).total_seconds()
assert -300 <= age <= 86400, f"Gate 0 snapshot must be no more than 24 hours old; age_s={age:.0f}"
PY

cat <<'EOF'
GATE 1 CAN MOVE THE ROBOT TO HOME.
Confirm the robot is supported, Rob is present, the area is clear, and power cut is accessible.
EOF
read -r -p "Type RUN_SUPPORTED_HOME_GATE1 to continue: " confirmation
[[ "$confirmation" == "RUN_SUPPORTED_HOME_GATE1" ]] || { echo "Aborted."; exit 1; }

# The reviewed remote command is intentionally assembled locally.
# shellcheck disable=SC2029
ssh "${SSH_OPTS[@]}" "$SSH_TARGET" "$(remote_home_command)"
scp "${SSH_OPTS[@]}" "$SSH_TARGET:$REMOTE_TELEMETRY" "$LOCAL_TELEMETRY"
scp "${SSH_OPTS[@]}" "$SSH_TARGET:$REMOTE_TERMINAL" "$LOCAL_TERMINAL"
python3 tools/evaluate_supported_home_telemetry.py "$LOCAL_TELEMETRY" \
  --terminal-log "$LOCAL_TERMINAL" --output-md "$LOCAL_MD" --output-json "$LOCAL_JSON"
echo "Telemetry analysis complete. Gate 1 remains open until visual geometry is recorded."
