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
WALKER_SHA="e282f927c17bfc1c6c9fc9d958a597e2f8c1cf8733962ada3a44593a008632c5"
PARSER_SHA="dd139f1b7043a4ddbe64e5242ab8316e5a6216a6dbe2d4347a5f4c6eb3204eee"
DIAG_SHA="49f4074e0f1bbfa8749a5e1af398570eab0e70d40963ba40551499b38429493b"
RESTORE_SHA="9fd5f639ceb342dd5d33c203936907929af35e7fc78b7d8ee83e693e7838f152"
LIMITS="5.24,5.24,1.50,1.50,1.75,5.24,5.24,5.24,5.24,5.24,5.24,1.25,1.00,1.25"
RUN=0; PRESENT=0; SNAPSHOT=""
OUTPUT_DIR="outputs/first_evidence/$(date -u +%Y%m%dT%H%M%SZ)_rate165_hard_vector_x0"
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
Suspended rate165 hard-vector gate:
  command: x=0.00 only
  duration: 15 seconds
  limits: $LIMITS
  cleanup: independent torque off
This runner has no x=.08 or grounded mode.
EOF
[[ "$RUN" -eq 1 ]] || exit 0
[[ "$PRESENT" -eq 1 ]] || { echo "Refused: --i-am-physically-present required." >&2; exit 2; }
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
test "$(sha256sum '"$RUNTIME"'/scripts/v2_rl_walk_mujoco.py | cut -d " " -f1)" = "'"$WALKER_SHA"'"
test "$(sha256sum '"$RUNTIME"'/scripts/motor_velocity_limits.py | cut -d " " -f1)" = "'"$PARSER_SHA"'"
test "$(sha256sum '"$RUNTIME"'/scripts/sim2real_diagnostics.py | cut -d " " -f1)" = "'"$DIAG_SHA"'"
test "$(sha256sum '"$RUNTIME"'/scripts/restore_runtime_gains_and_turn_off.py | cut -d " " -f1)" = "'"$RESTORE_SHA"'"
ps -eo comm=,args= | awk '\''$1 ~ /^python/ && $0 ~ /(v2_rl_walk|sim2real_diagnostics|mini_bdx_runtime)/ {found=1} END {exit found}'\''
! fuser /dev/ttyACM0 >/dev/null 2>&1'
ssh -n "${SSH_OPTS[@]}" "$SSH_TARGET" "$preflight"
read -r -p "Type RUN_SUSPENDED_X0_HARD_VECTOR to continue: " confirmation
[[ "$confirmation" == "RUN_SUSPENDED_X0_HARD_VECTOR" ]] || { echo "Aborted."; exit 1; }
mkdir -p "$OUTPUT_DIR"
REMOTE_JSONL="/home/sunrise/duck_logs/rate165_hard_vector_x0.jsonl"
REMOTE_TERMINAL="/home/sunrise/duck_logs/rate165_hard_vector_x0_terminal.log"
cleanup() { ssh -n "${SSH_OPTS[@]}" "$SSH_TARGET" "cd '$RUNTIME/scripts' && '$PYTHON' restore_runtime_gains_and_turn_off.py" || true; }
trap cleanup EXIT
remote_run=$(printf 'rm -f %q %q && cd %q && set -o pipefail && printf "\\n" | %q sim2real_diagnostics.py suspended_policy_replay --onnx_model_path %q --command-x 0.0 --duration 15 --action_scale 0.25 --motor-velocity-limits-rad-s %q --telemetry-path %q --telemetry-every-n 1 --i-understand-this-moves-the-robot 2>&1 | tee %q' "$REMOTE_JSONL" "$REMOTE_TERMINAL" "$RUNTIME/scripts" "$PYTHON" "$POLICY" "$LIMITS" "$REMOTE_JSONL" "$REMOTE_TERMINAL")
ssh -n "${SSH_OPTS[@]}" "$SSH_TARGET" "$remote_run"
scp "${SSH_OPTS[@]}" "$SSH_TARGET:$REMOTE_JSONL" "$OUTPUT_DIR/suspended_x0.jsonl"
scp "${SSH_OPTS[@]}" "$SSH_TARGET:$REMOTE_TERMINAL" "$OUTPUT_DIR/suspended_x0_terminal.log"
python3 tools/analyze_suspended_replay.py "$OUTPUT_DIR/suspended_x0.jsonl" --terminal-log "$OUTPUT_DIR/suspended_x0_terminal.log" --output "$OUTPUT_DIR/suspended_x0_gate.md"
cleanup; trap - EXIT
echo "Hard-vector x=0 captured. Stop for numeric and visual review; x=.08 remains unauthorized."
