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
DIAGNOSTIC_SHA="083af9c85b797699ebd44b1b98de29b931cd27e8cbeaf06d10914d2559e5a698"
WALKER_SHA="d81ad59c29e3a24d5c8e278eaf0898b4d3505ad22bb60ee74776537202eb2dfc"
HWI_SHA="057bebc75a0960a6433b0ecd3f6991a06d24d6d6c6a2201522c762ebc778a9fe"
TURN_OFF_SHA="99451bfa66f838e617585be695e03970b789222e00724fadc40f722b5f2c2090"
OUTPUT_DIR="outputs/first_evidence/$(date -u +%Y%m%dT%H%M%SZ)_rustypot_recovery_gate3_x0"
GATE2_SNAPSHOT=""
RUN=0
PRESENT=0

usage() {
  cat <<'EOF'
Usage: collect_grounded_rate165_gate3_x0.sh [options]

Default: print the exact suspended x=0 plan; no SSH and no motors.

  --run                    Run Gate 3 after all prerequisites.
  --i-am-physically-present
  --gate2-snapshot PATH    Fresh reviewed post-staging v2 snapshot.
  --output-dir PATH
  --ssh TARGET
  --identity-file PATH
  --known-hosts PATH

This runner has no x=0.08 or grounded mode.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run) RUN=1; shift ;;
    --i-am-physically-present) PRESENT=1; shift ;;
    --gate2-snapshot) GATE2_SNAPSHOT="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    --ssh) SSH_TARGET="$2"; shift 2 ;;
    --identity-file) IDENTITY_FILE="$2"; shift 2 ;;
    --known-hosts) KNOWN_HOSTS="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

SSH_OPTS=(-i "$IDENTITY_FILE" -o "UserKnownHostsFile=$KNOWN_HOSTS"
  -o "StrictHostKeyChecking=yes" -o "ConnectTimeout=5")
REMOTE_LOG_DIR="/home/sunrise/duck_logs"
REMOTE_JSONL="$REMOTE_LOG_DIR/rustypot_recovery_gate3_x0.jsonl"
REMOTE_TERMINAL="$REMOTE_LOG_DIR/rustypot_recovery_gate3_x0_terminal.log"
LOCAL_JSONL="$OUTPUT_DIR/suspended_x0.jsonl"
LOCAL_TERMINAL="$OUTPUT_DIR/suspended_x0_terminal.log"
LOCAL_ANALYSIS="$OUTPUT_DIR/suspended_x0_gate.md"

remote_replay() {
  printf 'mkdir -p %q && rm -f %q %q && cd %q && set -o pipefail && printf "\\n" | %q sim2real_diagnostics.py suspended_policy_replay --onnx_model_path %q --command-x 0.0 --duration 15 --action_scale 0.25 --telemetry-path %q --telemetry-every-n 1 --i-understand-this-moves-the-robot 2>&1 | tee %q' \
    "$REMOTE_LOG_DIR" "$REMOTE_JSONL" "$REMOTE_TERMINAL" "$ROBOT_RUNTIME/scripts" "$ROBOT_PYTHON" "$CANDIDATE" \
    "$REMOTE_JSONL" "$REMOTE_TERMINAL"
}

cat <<EOF
Gate 3 suspended x=0 only (15 seconds):
  candidate: $CANDIDATE
  candidate SHA256: $CANDIDATE_SHA
  command: x=0.0, y=0.0, yaw=0.0
  action scale: 0.25 (unchanged runtime contract)
  telemetry: every tick
  automatic motor-off cleanup: required
  analyzer: tools/analyze_suspended_replay.py

No x=0.08 or grounded command is available in this runner.
EOF

[[ "$RUN" -eq 1 ]] || exit 0
[[ "$PRESENT" -eq 1 ]] || { echo "Refused: physical-presence flag required." >&2; exit 2; }
[[ -n "$GATE2_SNAPSHOT" && -f "$GATE2_SNAPSHOT" ]] || {
  echo "Refused: fresh --gate2-snapshot required." >&2; exit 2; }
[[ -f "$IDENTITY_FILE" && -f "$KNOWN_HOSTS" ]] || { echo "SSH credentials missing." >&2; exit 2; }

python3 - "$GATE2_SNAPSHOT" "$CANDIDATE_SHA" <<'PY'
import datetime as dt, json, sys
d=json.load(open(sys.argv[1])); expected=sys.argv[2]
assert d.get("schema_version") == "open_duck_mini_config_snapshot_v2"
stamp=dt.datetime.fromisoformat((d.get("collector_utc") or d["snapshot_utc"]).replace("Z", "+00:00"))
age=(dt.datetime.now(dt.timezone.utc)-stamp).total_seconds()
assert -300 <= age <= 86400, f"Gate-2 snapshot age invalid: {age:.0f}s"
inventory={x["path"]:x.get("sha256") for x in d.get("onnx_policy_inventory",[])}
assert inventory.get("/home/sunrise/phase2_grounded_rate165_20260712_e06643e5.onnx") == expected
assert (d.get("duck_config") or {}).get("start_paused") is True
PY

# Literal substitutions in this reviewed remote shell program are intentional.
# shellcheck disable=SC2016
remote_preflight='set -eu; test "$(sha256sum /home/sunrise/phase2_grounded_rate165_20260712_e06643e5.onnx | cut -d " " -f1)" = "'"$CANDIDATE_SHA"'"; test "$(sha256sum /home/sunrise/duck_config.json | cut -d " " -f1)" = "'"$CONFIG_SHA"'"; test "$(sha256sum /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts/sim2real_diagnostics.py | cut -d " " -f1)" = "'"$DIAGNOSTIC_SHA"'"; test "$(sha256sum /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts/v2_rl_walk_mujoco.py | cut -d " " -f1)" = "'"$WALKER_SHA"'"; test "$(sha256sum /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/mini_bdx_runtime/mini_bdx_runtime/rustypot_position_hwi.py | cut -d " " -f1)" = "'"$HWI_SHA"'"; test "$(sha256sum /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts/turn_off.py | cut -d " " -f1)" = "'"$TURN_OFF_SHA"'"; python3 -c "import json; assert json.load(open(\"/home/sunrise/duck_config.json\"))[\"start_paused\"] is True"; ps -eo comm=,args= | awk '\''$1 ~ /^python/ && $0 ~ /(v2_rl_walk|run_xbox_walk|sim2real_diagnostics|mini_bdx_runtime)/ {found=1} END {exit found}'\'''
# shellcheck disable=SC2029
ssh -n "${SSH_OPTS[@]}" "$SSH_TARGET" "$remote_preflight"

cat <<'EOF'
GATE 3 ENGAGES MOTORS AND RUNS THE CANDIDATE FOR 15 SECONDS AT x=0.
Robot must remain suspended. Stop on twitch, asymmetry, large tracking error,
bus/write bursts, unexpected motion, or operator concern.
EOF
read -r -p "Type RUN_SUSPENDED_X0_GATE3 to continue: " confirmation
[[ "$confirmation" == "RUN_SUSPENDED_X0_GATE3" ]] || { echo "Aborted."; exit 1; }

mkdir -p "$OUTPUT_DIR"
cleanup_needed=1
cleanup() {
  [[ "$cleanup_needed" -eq 1 ]] || return 0
  # shellcheck disable=SC2029
  ssh -n "${SSH_OPTS[@]}" "$SSH_TARGET" \
    "cd '$ROBOT_RUNTIME/scripts' && '$ROBOT_PYTHON' turn_off.py" || true
}
trap cleanup EXIT

# The reviewed fixed remote command is assembled locally.
# shellcheck disable=SC2029
ssh -n "${SSH_OPTS[@]}" "$SSH_TARGET" "$(remote_replay)"
scp "${SSH_OPTS[@]}" "$SSH_TARGET:$REMOTE_JSONL" "$LOCAL_JSONL"
scp "${SSH_OPTS[@]}" "$SSH_TARGET:$REMOTE_TERMINAL" "$LOCAL_TERMINAL"
python3 tools/analyze_suspended_replay.py "$LOCAL_JSONL" \
  --terminal-log "$LOCAL_TERMINAL" --output "$LOCAL_ANALYSIS"
cleanup
cleanup_needed=0
trap - EXIT
echo "Gate 3 data captured. Stop for review; x=0.08 remains unauthorized."
