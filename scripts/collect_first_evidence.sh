#!/usr/bin/env bash
set -euo pipefail

SSH_TARGET="sunrise@192.168.1.50"
IDENTITY_FILE="/home/lsd/robots/.duck_access/rdk_key"
KNOWN_HOSTS="/home/lsd/robots/.duck_access/known_hosts"
ROBOT_RUNTIME="/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5"
ROBOT_PYTHON="/home/sunrise/duck_env/bin/python"
ROBOT_POLICY="/home/sunrise/BEST_WALK_ONNX_2.onnx"
ROBOT_LOG_DIR="/home/sunrise/duck_logs"
OUTPUT_DIR="outputs/first_evidence/$(date -u +%Y%m%dT%H%M%SZ)"
DRY_RUN=0
PHYSICALLY_PRESENT=0
RUN_READONLY=0
RUN_MOVING=0

usage() {
  cat <<'USAGE'
Usage:
  bash scripts/collect_first_evidence.sh [options]

Default behavior:
  - create local output directories
  - validate local files/tools
  - print the exact evidence collection commands
  - do not run hardware-moving diagnostics

Options:
  --dry-run
      Print the plan only.
  --ssh TARGET
      SSH target, default sunrise@192.168.1.50.
  --identity-file PATH
      SSH private key path.
  --known-hosts PATH
      SSH known_hosts path.
  --robot-runtime PATH
      Board runtime path.
  --output-dir PATH
      Local evidence output directory.
  --i-am-physically-present
      Allow hardware-moving diagnostic commands to run when paired with --run-moving.
  --run-readonly
      Run only the read-only snapshot command and local summary scaffolding.
  --run-moving
      Run the hardware-moving/non-walking diagnostics. Requires --i-am-physically-present.

Examples:
  bash scripts/collect_first_evidence.sh --dry-run

  bash scripts/collect_first_evidence.sh --run-readonly

  bash scripts/collect_first_evidence.sh \
    --i-am-physically-present \
    --run-moving
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --ssh)
      SSH_TARGET="$2"
      shift 2
      ;;
    --identity-file)
      IDENTITY_FILE="$2"
      shift 2
      ;;
    --known-hosts)
      KNOWN_HOSTS="$2"
      shift 2
      ;;
    --robot-runtime)
      ROBOT_RUNTIME="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --i-am-physically-present)
      PHYSICALLY_PRESENT=1
      shift
      ;;
    --run-readonly)
      RUN_READONLY=1
      shift
      ;;
    --run-moving)
      RUN_MOVING=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

SSH_OPTS=(
  -i "$IDENTITY_FILE"
  -o "UserKnownHostsFile=$KNOWN_HOSTS"
  -o "StrictHostKeyChecking=no"
  -o "ConnectTimeout=5"
)

mkdir -p "$OUTPUT_DIR"

require_file() {
  local path="$1"
  if [[ ! -e "$path" ]]; then
    echo "Missing required file: $path" >&2
    exit 1
  fi
}

require_tool() {
  local name="$1"
  if ! command -v "$name" >/dev/null 2>&1; then
    echo "Missing required tool: $name" >&2
    exit 1
  fi
}

quote() {
  printf "%q" "$1"
}

ssh_cmd() {
  printf "ssh"
  for opt in "${SSH_OPTS[@]}"; do
    printf " %q" "$opt"
  done
  printf " %q" "$SSH_TARGET"
}

scp_from_cmd() {
  local remote_path="$1"
  local local_path="$2"
  printf "scp"
  for opt in "${SSH_OPTS[@]}"; do
    printf " %q" "$opt"
  done
  printf " %q:%q %q" "$SSH_TARGET" "$remote_path" "$local_path"
}

remote_home_pose_cmd() {
  printf "mkdir -p %q && cd %q && %q sim2real_diagnostics.py home_pose_log_test --onnx_model_path %q --telemetry-path %q --i-understand-this-moves-the-robot" \
    "$ROBOT_LOG_DIR" \
    "$ROBOT_RUNTIME/scripts" \
    "$ROBOT_PYTHON" \
    "$ROBOT_POLICY" \
    "$ROBOT_LOG_DIR/home_pose_log_test.jsonl"
}

remote_imu_tilt_cmd() {
  printf "mkdir -p %q && cd %q && %q sim2real_diagnostics.py imu_tilt_test --onnx_model_path %q --telemetry-path %q --duration 35" \
    "$ROBOT_LOG_DIR" \
    "$ROBOT_RUNTIME/scripts" \
    "$ROBOT_PYTHON" \
    "$ROBOT_POLICY" \
    "$ROBOT_LOG_DIR/imu_tilt_test.jsonl"
}

remote_foot_contact_cmd() {
  printf "mkdir -p %q && cd %q && %q sim2real_diagnostics.py foot_contact_test --telemetry-path %q --duration 20" \
    "$ROBOT_LOG_DIR" \
    "$ROBOT_RUNTIME/scripts" \
    "$ROBOT_PYTHON" \
    "$ROBOT_LOG_DIR/foot_contact_test.jsonl"
}

print_ssh_remote_cmd() {
  local remote_command="$1"
  ssh_cmd
  printf " %q" "$remote_command"
}

validate_local() {
  require_tool python3
  require_tool ssh
  require_tool scp
  require_file tools/snapshot_robot_config.py
  require_file tools/analyze_telemetry_obs.py
  require_file tools/summarize_first_evidence.py
  require_file docs/telemetry_schema.json
  require_file policy/BEST_WALK_ONNX_2.onnx
  require_file "$IDENTITY_FILE"
  require_file "$KNOWN_HOSTS"
}

safety_warning() {
  cat <<'WARNING'

SAFETY WARNING
--------------
The next commands can move hardware or require hands-on robot handling.
- Rob must be physically present.
- Robot must be supported for home_pose_log_test.
- Keep fingers clear.
- Be ready to cut power.
- Do not continue if the robot is not safe.

WARNING
}

print_plan() {
  local snapshot_glob="$OUTPUT_DIR/*_rdkx5_config_snapshot.json"
  local home_log="$OUTPUT_DIR/home_pose_log_test.jsonl"
  local home_analysis="$OUTPUT_DIR/home_pose_analysis.md"
  local imu_log="$OUTPUT_DIR/imu_tilt_test.jsonl"
  local imu_analysis="$OUTPUT_DIR/imu_tilt_analysis.md"
  local foot_log="$OUTPUT_DIR/foot_contact_test.jsonl"
  local foot_summary="$OUTPUT_DIR/foot_contact_summary.md"

  cat <<PLAN
First evidence output directory:
  $OUTPUT_DIR

A. Read-only snapshot
  python3 tools/snapshot_robot_config.py \\
    --ssh $(quote "$SSH_TARGET") \\
    --identity-file $(quote "$IDENTITY_FILE") \\
    --known-hosts $(quote "$KNOWN_HOSTS") \\
    --strict-host-key-checking no \\
    --output-dir $(quote "$OUTPUT_DIR")

B. Home pose log, run on robot only when physically present
  $(print_ssh_remote_cmd "$(remote_home_pose_cmd)")

C. Copy home pose log back
  $(scp_from_cmd "$ROBOT_LOG_DIR/home_pose_log_test.jsonl" "$home_log")

D. Analyze home pose locally
  python3 tools/analyze_telemetry_obs.py $(quote "$home_log") \\
    --onnx-model policy/BEST_WALK_ONNX_2.onnx \\
    --output $(quote "$home_analysis")

E. IMU tilt test, run on robot only when physically present
  $(print_ssh_remote_cmd "$(remote_imu_tilt_cmd)")

F. Copy IMU tilt log back
  $(scp_from_cmd "$ROBOT_LOG_DIR/imu_tilt_test.jsonl" "$imu_log")

G. Analyze IMU tilt locally
  python3 tools/analyze_telemetry_obs.py $(quote "$imu_log") \\
    --onnx-model policy/BEST_WALK_ONNX_2.onnx \\
    --output $(quote "$imu_analysis")

H. Foot contact test, run on robot only when physically present
  $(print_ssh_remote_cmd "$(remote_foot_contact_cmd)")

I. Copy foot contact log back
  $(scp_from_cmd "$ROBOT_LOG_DIR/foot_contact_test.jsonl" "$foot_log")

J. Create foot contact summary placeholder if needed
  printf '# Foot Contact Summary\n\nMISSING: fill from foot_contact_test output.\n' > $(quote "$foot_summary")

K. Summarize first evidence
  python3 tools/summarize_first_evidence.py $(quote "$OUTPUT_DIR") \\
    --output outputs/analysis/FIRST_EVIDENCE_SUMMARY.md

Expected snapshot path:
  $snapshot_glob
PLAN
}

run_readonly() {
  python3 tools/snapshot_robot_config.py \
    --ssh "$SSH_TARGET" \
    --identity-file "$IDENTITY_FILE" \
    --known-hosts "$KNOWN_HOSTS" \
    --strict-host-key-checking no \
    --output-dir "$OUTPUT_DIR"
  python3 tools/summarize_first_evidence.py "$OUTPUT_DIR" \
    --output outputs/analysis/FIRST_EVIDENCE_SUMMARY.md
}

run_moving_sequence() {
  if [[ "$PHYSICALLY_PRESENT" -ne 1 ]]; then
    echo "Refusing to run moving diagnostics without --i-am-physically-present." >&2
    exit 1
  fi

  safety_warning
  read -r -p "Type RUN_FIRST_EVIDENCE to continue: " confirmation
  if [[ "$confirmation" != "RUN_FIRST_EVIDENCE" ]]; then
    echo "Aborted."
    exit 1
  fi

  local home_log="$OUTPUT_DIR/home_pose_log_test.jsonl"
  local home_analysis="$OUTPUT_DIR/home_pose_analysis.md"
  local imu_log="$OUTPUT_DIR/imu_tilt_test.jsonl"
  local imu_analysis="$OUTPUT_DIR/imu_tilt_analysis.md"
  local foot_log="$OUTPUT_DIR/foot_contact_test.jsonl"
  local foot_summary="$OUTPUT_DIR/foot_contact_summary.md"

  run_readonly

  ssh "${SSH_OPTS[@]}" "$SSH_TARGET" "$(remote_home_pose_cmd)"
  scp "${SSH_OPTS[@]}" "$SSH_TARGET:$ROBOT_LOG_DIR/home_pose_log_test.jsonl" "$home_log"
  python3 tools/analyze_telemetry_obs.py "$home_log" \
    --onnx-model policy/BEST_WALK_ONNX_2.onnx \
    --output "$home_analysis"

  echo
  echo "Review $home_analysis before continuing to IMU tilt."
  read -r -p "Type CONTINUE_IMU_TILT to continue, or anything else to stop: " confirmation
  if [[ "$confirmation" != "CONTINUE_IMU_TILT" ]]; then
    python3 tools/summarize_first_evidence.py "$OUTPUT_DIR" \
      --output outputs/analysis/FIRST_EVIDENCE_SUMMARY.md
    exit 0
  fi

  ssh "${SSH_OPTS[@]}" "$SSH_TARGET" "$(remote_imu_tilt_cmd)"
  scp "${SSH_OPTS[@]}" "$SSH_TARGET:$ROBOT_LOG_DIR/imu_tilt_test.jsonl" "$imu_log"
  python3 tools/analyze_telemetry_obs.py "$imu_log" \
    --onnx-model policy/BEST_WALK_ONNX_2.onnx \
    --output "$imu_analysis"

  echo
  echo "Review $imu_analysis before continuing to foot contact."
  read -r -p "Type CONTINUE_FOOT_CONTACT to continue, or anything else to stop: " confirmation
  if [[ "$confirmation" != "CONTINUE_FOOT_CONTACT" ]]; then
    python3 tools/summarize_first_evidence.py "$OUTPUT_DIR" \
      --output outputs/analysis/FIRST_EVIDENCE_SUMMARY.md
    exit 0
  fi

  ssh "${SSH_OPTS[@]}" "$SSH_TARGET" "$(remote_foot_contact_cmd)"
  scp "${SSH_OPTS[@]}" "$SSH_TARGET:$ROBOT_LOG_DIR/foot_contact_test.jsonl" "$foot_log"
  {
    echo "# Foot Contact Summary"
    echo
    echo "Source: $foot_log"
    echo
    echo "Review the JSONL transitions and fill pass/fail notes here."
  } > "$foot_summary"

  python3 tools/summarize_first_evidence.py "$OUTPUT_DIR" \
    --output outputs/analysis/FIRST_EVIDENCE_SUMMARY.md
}

validate_local
print_plan

if [[ "$DRY_RUN" -eq 1 ]]; then
  exit 0
fi

if [[ "$RUN_MOVING" -eq 1 ]]; then
  run_moving_sequence
elif [[ "$RUN_READONLY" -eq 1 ]]; then
  run_readonly
else
  cat <<'NOTE'

No commands were run except local validation and directory creation.
Use --run-readonly for the snapshot, or --run-moving with --i-am-physically-present for the full first packet.
NOTE
fi
