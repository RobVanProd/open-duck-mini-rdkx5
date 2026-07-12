#!/usr/bin/env bash
set -euo pipefail

SSH_TARGET="sunrise@192.168.1.50"
IDENTITY_FILE="/home/lsd/robots/.duck_access/rdk_key"
KNOWN_HOSTS="/home/lsd/robots/.duck_access/known_hosts"
LIVE_RUNTIME="/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5"
STAGE_DIR="/home/sunrise/rate165_hard_vector_stage_20260712"

POLICY="/home/sunrise/phase2_grounded_rate165_20260712_e06643e5.onnx"
POLICY_SHA="e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33"
CONFIG_SHA="131a7b8fce1107b14f4727562f44f9e17324caf7fc22512ad7115911f050991b"
HWI_SHA="f352b66ab44ec5a302a08c413aeaa21fa693555c7a41c536d1ff18f208b43fdc"
LIVE_WALKER_SHA="b9732bfa1deca5d6a7a062f757589a6327c7b000d0d855f56eec500535c25c17"
LIVE_DIAG_SHA="f284332c543af360cc73931ac646a5198de4bc58ad27ad18681fb326a1b937c2"

LOCAL_WALKER="runtime/scripts/v2_rl_walk_mujoco.py"
LOCAL_PARSER="runtime/scripts/motor_velocity_limits.py"
LOCAL_DIAG="instrumentation/scripts/sim2real_diagnostics.py"
WALKER_SHA="e282f927c17bfc1c6c9fc9d958a597e2f8c1cf8733962ada3a44593a008632c5"
PARSER_SHA="dd139f1b7043a4ddbe64e5242ab8316e5a6216a6dbe2d4347a5f4c6eb3204eee"
DIAG_SHA="49f4074e0f1bbfa8749a5e1af398570eab0e70d40963ba40551499b38429493b"

RUN=0
APPROVE=0
SNAPSHOT=""
OUTPUT="outputs/analysis/rate165_hard_vector_stage_manifest.json"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --run) RUN=1; shift ;;
    --i-approve-stage-only) APPROVE=1; shift ;;
    --snapshot) SNAPSHOT="$2"; shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

cat <<EOF
Rate165 hard-vector side-by-side stage plan:
  destination: $STAGE_DIR
  live runtime files: unchanged
  HWI import / serial open / torque / motor motion: none
  next motor gate: not included
EOF

[[ "$RUN" -eq 1 ]] || exit 0
[[ "$APPROVE" -eq 1 ]] || { echo "Refused: --i-approve-stage-only required." >&2; exit 2; }
[[ -n "$SNAPSHOT" && -f "$SNAPSHOT" ]] || { echo "Refused: fresh --snapshot required." >&2; exit 2; }

python3 - "$SNAPSHOT" "$POLICY" "$POLICY_SHA" <<'PY'
import datetime as dt, json, sys
d=json.load(open(sys.argv[1])); policy=sys.argv[2]; expected=sys.argv[3]
assert d.get("schema_version") == "open_duck_mini_config_snapshot_v2"
stamp=dt.datetime.fromisoformat((d.get("collector_utc") or d["snapshot_utc"]).replace("Z", "+00:00"))
assert -300 <= (dt.datetime.now(dt.timezone.utc)-stamp).total_seconds() <= 600
inventory={x["path"]:x.get("sha256") for x in d.get("onnx_policy_inventory",[])}
assert inventory.get(policy) == expected
assert (d.get("duck_config") or {}).get("start_paused") is True
PY

for pair in "$LOCAL_WALKER:$WALKER_SHA" "$LOCAL_PARSER:$PARSER_SHA" "$LOCAL_DIAG:$DIAG_SHA"; do
  path=${pair%%:*}; expected=${pair##*:}
  [[ "$(sha256sum "$path" | awk '{print $1}')" == "$expected" ]] || {
    echo "Refused: local hash mismatch for $path" >&2; exit 2;
  }
done

SSH_OPTS=(-i "$IDENTITY_FILE" -o "UserKnownHostsFile=$KNOWN_HOSTS" -o "StrictHostKeyChecking=yes" -o "ConnectTimeout=5")
preflight='set -eu
test "$(sha256sum '"$POLICY"' | cut -d " " -f1)" = "'"$POLICY_SHA"'"
test "$(sha256sum /home/sunrise/duck_config.json | cut -d " " -f1)" = "'"$CONFIG_SHA"'"
test "$(sha256sum '"$LIVE_RUNTIME"'/mini_bdx_runtime/mini_bdx_runtime/rustypot_position_hwi.py | cut -d " " -f1)" = "'"$HWI_SHA"'"
test "$(sha256sum '"$LIVE_RUNTIME"'/scripts/v2_rl_walk_mujoco.py | cut -d " " -f1)" = "'"$LIVE_WALKER_SHA"'"
test "$(sha256sum '"$LIVE_RUNTIME"'/scripts/sim2real_diagnostics.py | cut -d " " -f1)" = "'"$LIVE_DIAG_SHA"'"
ps -eo comm=,args= | awk '\''$1 ~ /^python/ && $0 ~ /(v2_rl_walk|sim2real_diagnostics|mini_bdx_runtime)/ {found=1} END {exit found}'\''
! fuser /dev/ttyACM0 >/dev/null 2>&1
mkdir -p '"$STAGE_DIR"''
ssh -n "${SSH_OPTS[@]}" "$SSH_TARGET" "$preflight"

read -r -p "Type STAGE_RATE165_HARD_VECTOR_SIDE_BY_SIDE to continue: " confirmation
[[ "$confirmation" == "STAGE_RATE165_HARD_VECTOR_SIDE_BY_SIDE" ]] || { echo "Aborted."; exit 1; }

scp "${SSH_OPTS[@]}" "$LOCAL_WALKER" "$SSH_TARGET:$STAGE_DIR/v2_rl_walk_mujoco.py"
scp "${SSH_OPTS[@]}" "$LOCAL_PARSER" "$SSH_TARGET:$STAGE_DIR/motor_velocity_limits.py"
scp "${SSH_OPTS[@]}" "$LOCAL_DIAG" "$SSH_TARGET:$STAGE_DIR/sim2real_diagnostics.py"

remote_manifest=$(ssh -n "${SSH_OPTS[@]}" "$SSH_TARGET" "set -eu
  test \"\$(sha256sum '$STAGE_DIR/v2_rl_walk_mujoco.py' | cut -d ' ' -f1)\" = '$WALKER_SHA'
  test \"\$(sha256sum '$STAGE_DIR/motor_velocity_limits.py' | cut -d ' ' -f1)\" = '$PARSER_SHA'
  test \"\$(sha256sum '$STAGE_DIR/sim2real_diagnostics.py' | cut -d ' ' -f1)\" = '$DIAG_SHA'
  ps -eo comm=,args= | awk '\''\$1 ~ /^python/ && \$0 ~ /(v2_rl_walk|sim2real_diagnostics|mini_bdx_runtime)/ {found=1} END {exit found}'\''
  ! fuser /dev/ttyACM0 >/dev/null 2>&1
  python3 - <<'PY'
import hashlib,json,pathlib
root=pathlib.Path('$STAGE_DIR')
print(json.dumps({'status':'PASS_STAGE_ONLY','stage_dir':str(root),'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir() if p.is_file()},'hwi_initialized':False,'motors_engaged':False},sort_keys=True))
PY")
mkdir -p "$(dirname "$OUTPUT")"
printf '%s\n' "$remote_manifest" > "$OUTPUT"
echo "Stage-only complete. Stop for review; no live file or motor state changed."
