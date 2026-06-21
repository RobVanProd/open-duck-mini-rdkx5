#!/usr/bin/env bash
set -euo pipefail

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"

SSH_TARGET="sunrise@192.168.1.50"
IDENTITY_FILE="/home/lsd/robots/.duck_access/rdk_key"
KNOWN_HOSTS="/home/lsd/robots/.duck_access/known_hosts"
ROBOT_RUNTIME="/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5"
ROBOT_PYTHON="/home/sunrise/duck_env/bin/python"
OUTPUT_DIR="outputs/deployments/$timestamp"
BACKUP_DIR="/home/sunrise/duck_backups/$timestamp"
APPLY=0

SOURCE_FILES=(
  "instrumentation/mini_bdx_runtime/telemetry.py|mini_bdx_runtime/mini_bdx_runtime/telemetry.py"
  "instrumentation/scripts/sim2real_diagnostics.py|scripts/sim2real_diagnostics.py"
)

COMMANDS_RUN=()
FILE_ROWS=()
CHECK_ROWS=()

usage() {
  cat <<'USAGE'
Usage:
  bash scripts/deploy_instrumentation_to_duck.sh [options]

Default behavior:
  - dry-run only
  - print the deployment plan
  - write a local DEPLOYMENT_SUMMARY.md
  - do not SSH or copy files

Options:
  --dry-run
      Print and summarize the plan only. This is the default.
  --apply
      Copy files to the board after backing up existing destinations.
  --ssh TARGET
      SSH target, default sunrise@192.168.1.50.
  --identity-file PATH
      SSH private key path.
  --known-hosts PATH
      SSH known_hosts path.
  --robot-runtime PATH
      Board runtime path.
  --robot-python PATH
      Board Python path.
  --output-dir PATH
      Local deployment evidence directory.
  --backup-dir PATH
      Board backup directory.
  -h, --help
      Show this help.

Examples:
  bash scripts/deploy_instrumentation_to_duck.sh --dry-run

  bash scripts/deploy_instrumentation_to_duck.sh --apply
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      APPLY=0
      shift
      ;;
    --apply)
      APPLY=1
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
    --robot-python)
      ROBOT_PYTHON="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --backup-dir)
      BACKUP_DIR="$2"
      shift 2
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

quote() {
  printf "%q" "$1"
}

require_tool() {
  local name="$1"
  if ! command -v "$name" >/dev/null 2>&1; then
    echo "Missing required tool: $name" >&2
    exit 1
  fi
}

require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "Missing required file: $path" >&2
    exit 1
  fi
}

sha256_file() {
  sha256sum "$1" | awk '{print $1}'
}

file_size() {
  wc -c < "$1" | tr -d ' '
}

ssh_cmd_string() {
  printf "ssh"
  for opt in "${SSH_OPTS[@]}"; do
    printf " %q" "$opt"
  done
  printf " %q" "$SSH_TARGET"
}

scp_cmd_string() {
  local source="$1"
  local dest="$2"
  printf "scp"
  for opt in "${SSH_OPTS[@]}"; do
    printf " %q" "$opt"
  done
  printf " %q %q:%q" "$source" "$SSH_TARGET" "$dest"
}

ssh_run() {
  local remote_command="$1"
  COMMANDS_RUN+=("$(ssh_cmd_string) $(quote "$remote_command")")
  ssh "${SSH_OPTS[@]}" "$SSH_TARGET" "$remote_command"
}

scp_run() {
  local source="$1"
  local dest="$2"
  COMMANDS_RUN+=("$(scp_cmd_string "$source" "$dest")")
  scp "${SSH_OPTS[@]}" "$source" "$SSH_TARGET:$dest"
}

remote_runtime_check_cmd() {
  printf "test -d %q && test -d %q && test -d %q && test -x %q" \
    "$ROBOT_RUNTIME" \
    "$ROBOT_RUNTIME/scripts" \
    "$ROBOT_RUNTIME/mini_bdx_runtime/mini_bdx_runtime" \
    "$ROBOT_PYTHON"
}

remote_backup_cmd() {
  local dest="$1"
  local backup="$2"
  local dest_dir="$3"
  local backup_dir="$4"
  printf "mkdir -p %q && mkdir -p %q && if [ -f %q ]; then cp -p %q %q; fi" \
    "$dest_dir" \
    "$backup_dir" \
    "$dest" \
    "$dest" \
    "$backup"
}

remote_sha_cmd() {
  printf "sha256sum %q | awk '{print \$1}'" "$1"
}

remote_size_cmd() {
  printf "stat -c %%s %q" "$1"
}

remote_import_check_cmd() {
  local python_code="from mini_bdx_runtime.telemetry import SCHEMA_VERSION; print(SCHEMA_VERSION)"
  printf "PYTHONPATH=%q %q -c %q" \
    "$ROBOT_RUNTIME/mini_bdx_runtime" \
    "$ROBOT_PYTHON" \
    "$python_code"
}

remote_help_check_cmd() {
  printf "cd %q && PYTHONPATH=%q %q sim2real_diagnostics.py --help" \
    "$ROBOT_RUNTIME/scripts" \
    "$ROBOT_RUNTIME/mini_bdx_runtime" \
    "$ROBOT_PYTHON"
}

validate_local() {
  require_tool awk
  require_tool date
  require_tool scp
  require_tool sha256sum
  require_tool ssh
  require_tool stat
  require_tool wc
  require_tool rsync
  require_file "$IDENTITY_FILE"
  require_file "$KNOWN_HOSTS"
  for entry in "${SOURCE_FILES[@]}"; do
    require_file "${entry%%|*}"
  done
}

add_planned_rows() {
  FILE_ROWS=()
  for entry in "${SOURCE_FILES[@]}"; do
    local source="${entry%%|*}"
    local rel="${entry#*|}"
    local dest="$ROBOT_RUNTIME/$rel"
    local source_hash
    source_hash="$(sha256_file "$source")"
    FILE_ROWS+=("| \`$source\` | \`$dest\` | \`$source_hash\` | dry-run | not checked |")
  done
}

print_plan() {
  local mode="dry-run"
  if [[ "$APPLY" -eq 1 ]]; then
    mode="apply"
  fi

  cat <<PLAN
Instrumentation deployment plan
  mode: $mode
  ssh target: $SSH_TARGET
  robot runtime: $ROBOT_RUNTIME
  robot python: $ROBOT_PYTHON
  local output: $OUTPUT_DIR
  board backup dir: $BACKUP_DIR

Files:
PLAN

  for entry in "${SOURCE_FILES[@]}"; do
    local source="${entry%%|*}"
    local rel="${entry#*|}"
    local dest="$ROBOT_RUNTIME/$rel"
    printf "  %s -> %s\n" "$source" "$dest"
  done

  cat <<'PLAN'

Dry-run does not run SSH and does not copy files.
Apply mode backs up existing destination files before copying.
No policy files, duck_config.json, raw logs, SSH keys, or videos are copied.
No hardware-moving diagnostic is run.
PLAN
}

write_summary() {
  local status="$1"
  local summary="$OUTPUT_DIR/DEPLOYMENT_SUMMARY.md"
  mkdir -p "$OUTPUT_DIR"

  {
    echo "# Deployment Summary"
    echo
    echo "- timestamp_utc: \`$(date -u +%Y-%m-%dT%H:%M:%SZ)\`"
    echo "- status: \`$status\`"
    echo "- ssh_target: \`$SSH_TARGET\`"
    echo "- robot_runtime: \`$ROBOT_RUNTIME\`"
    echo "- robot_python: \`$ROBOT_PYTHON\`"
    echo "- backup_dir: \`$BACKUP_DIR\`"
    echo "- output_dir: \`$OUTPUT_DIR\`"
    echo "- hardware_moving_tests_run: \`no\`"
    echo "- runtime_behavior_changed_by_default: \`no\`"
    echo
    echo "## Files"
    echo
    echo "| source | destination | source_sha256 | destination_sha256 | backup_path |"
    echo "|---|---|---|---|---|"
    if [[ "${#FILE_ROWS[@]}" -gt 0 ]]; then
      printf "%s\n" "${FILE_ROWS[@]}"
    else
      echo "| MISSING | MISSING | MISSING | MISSING | MISSING |"
    fi
    echo
    echo "## Checks"
    echo
    if [[ "${#CHECK_ROWS[@]}" -gt 0 ]]; then
      printf "%s\n" "${CHECK_ROWS[@]}"
    else
      echo "- dry-run only: no board checks run"
    fi
    echo
    echo "## Commands Run"
    echo
    if [[ "${#COMMANDS_RUN[@]}" -gt 0 ]]; then
      for command in "${COMMANDS_RUN[@]}"; do
        echo "- \`$command\`"
      done
    else
      echo "- local validation and plan generation only"
    fi
    echo
    echo "## Notes"
    echo
    echo "- This workflow only deploys additive diagnostic/instrumentation files."
    echo "- It does not copy policy files or \`duck_config.json\`."
    echo "- It does not start walking, unpause the robot, or run moving diagnostics."
  } > "$summary"

  echo "Wrote $summary"
}

apply_deployment() {
  echo
  echo "APPLY MODE"
  echo "This copies diagnostic files to the board after backing up existing destinations."
  echo "It does not run moving diagnostics."
  read -r -p "Type DEPLOY_INSTRUMENTATION to continue: " confirmation
  if [[ "$confirmation" != "DEPLOY_INSTRUMENTATION" ]]; then
    echo "Aborted."
    write_summary "aborted"
    exit 1
  fi

  ssh_run "$(remote_runtime_check_cmd)" >/dev/null
  CHECK_ROWS+=("- runtime path check: passed")

  ssh_run "mkdir -p $(quote "$BACKUP_DIR")" >/dev/null

  FILE_ROWS=()
  for entry in "${SOURCE_FILES[@]}"; do
    local source="${entry%%|*}"
    local rel="${entry#*|}"
    local dest="$ROBOT_RUNTIME/$rel"
    local dest_dir="${dest%/*}"
    local backup="$BACKUP_DIR/$rel"
    local backup_parent="${backup%/*}"
    local source_hash
    local dest_hash
    local source_size
    local dest_size

    source_hash="$(sha256_file "$source")"
    source_size="$(file_size "$source")"
    ssh_run "$(remote_backup_cmd "$dest" "$backup" "$dest_dir" "$backup_parent")" >/dev/null
    scp_run "$source" "$dest" >/dev/null
    dest_hash="$(ssh_run "$(remote_sha_cmd "$dest")" | tr -d '[:space:]')"
    dest_size="$(ssh_run "$(remote_size_cmd "$dest")" | tr -d '[:space:]')"

    if [[ "$source_hash" != "$dest_hash" ]]; then
      echo "Checksum mismatch for $source -> $dest" >&2
      write_summary "failed"
      exit 1
    fi
    if [[ "$source_size" != "$dest_size" ]]; then
      echo "Size mismatch for $source -> $dest" >&2
      write_summary "failed"
      exit 1
    fi
    FILE_ROWS+=("| \`$source\` | \`$dest\` | \`$source_hash\` | \`$dest_hash\` | \`$backup\` |")
  done

  local import_output="$OUTPUT_DIR/import_check.txt"
  local help_output="$OUTPUT_DIR/sim2real_diagnostics_help.txt"
  mkdir -p "$OUTPUT_DIR"

  ssh_run "$(remote_import_check_cmd)" > "$import_output"
  CHECK_ROWS+=("- telemetry import check: passed, output \`$import_output\`")

  ssh_run "$(remote_help_check_cmd)" > "$help_output"
  CHECK_ROWS+=("- sim2real_diagnostics.py --help: passed, output \`$help_output\`")

  write_summary "applied"
}

validate_local
print_plan

if [[ "$APPLY" -eq 1 ]]; then
  apply_deployment
else
  add_planned_rows
  write_summary "dry-run"
fi
