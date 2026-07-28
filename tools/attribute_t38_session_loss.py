#!/usr/bin/env python3
"""Freeze T38's unrecoverable Colab-session attribution without policy weight."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t38_frozen_normalizer_hosted_preregistration.json"
)
PACKAGE_CONTRACT = (
    ANALYSIS / "t38_frozen_normalizer_hosted_package_contract.json"
)
LAUNCH_CONTRACT = ANALYSIS / "t38_colab_cli_launch_contract.json"
HISTORY = Path(
    "C:/Users/usa50/.config/colab-cli/history/"
    "t38-frozen-normalizer-20260727.jsonl"
)
STDOUT = Path(
    "D:/CodexArtifacts/open-duck-policy/t38_colab_exec_stdout.log"
)
STDERR = Path(
    "D:/CodexArtifacts/open-duck-policy/t38_colab_exec_stderr.log"
)
EXPECTED_LOCAL_OUTPUTS = {
    "result": Path(
        "D:/CodexArtifacts/open-duck-policy/t38_result.json"
    ),
    "archive": Path(
        "D:/CodexArtifacts/open-duck-policy/t38_artifacts.tar.gz"
    ),
    "receipt": Path(
        "D:/CodexArtifacts/open-duck-policy/t38_launch_receipt.json"
    ),
}
OUTPUT = ANALYSIS / "t38_unrecoverable_session_loss_attribution.json"
MARKDOWN = ANALYSIS / "T38_UNRECOVERABLE_SESSION_LOSS_20260728.md"
SESSION = "t38-frozen-normalizer-20260727"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_history(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def event(events: list[dict], event_type: str) -> dict:
    matches = [row for row in events if row.get("event_type") == event_type]
    if len(matches) != 1:
        raise ValueError(
            f"expected one {event_type!r} event, found {len(matches)}"
        )
    return matches[0]


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T38 attribution: {path}")

    prereg = load_json(PREREGISTRATION)
    package = load_json(PACKAGE_CONTRACT)
    launch = load_json(LAUNCH_CONTRACT)
    events = load_history(HISTORY)
    created = event(events, "session_created")
    uploaded = event(events, "file_operation")
    executed = event(events, "execution")
    terminated = event(events, "session_terminated")

    output_types = [
        str(row.get("output_type", "")) for row in executed.get("outputs", [])
    ]
    exit_values = [
        str(row.get("evalue"))
        for row in executed.get("outputs", [])
        if row.get("output_type") == "error"
    ]
    stderr_text = STDERR.read_text(encoding="utf-8")
    local_output_presence = {
        name: path.exists() for name, path in EXPECTED_LOCAL_OUTPUTS.items()
    }
    execution_seconds = (
        parse_time(executed["timestamp"])
        - datetime.fromtimestamp(STDERR.stat().st_ctime, tz=parse_time(
            executed["timestamp"]
        ).tzinfo)
    ).total_seconds()

    checks = {
        "preregistration_green": (
            prereg.get("status")
            == "PREREGISTERED_T38_FROZEN_NORMALIZER_HOSTED_CONTINUATION"
            and prereg.get("failed_checks") == []
        ),
        "package_contract_green": (
            package.get("status")
            == "PASS_T38_FROZEN_NORMALIZER_HOSTED_PACKAGE"
            and package.get("failed_checks") == []
        ),
        "launch_contract_green": (
            launch.get("status") == "PASS_T38_COLAB_CLI_LAUNCH_CONTRACT"
            and launch.get("failed_checks") == []
        ),
        "one_l4_session_created": (
            created.get("accelerator") == "L4"
            and sum(
                row.get("event_type") == "session_created" for row in events
            )
            == 1
        ),
        "exact_package_uploaded_once": (
            uploaded.get("op") == "upload"
            and uploaded.get("remote")
            == "/content/t38-frozen-normalizer-hosted-20260727.tar.gz"
            and sum(
                row.get("event_type") == "file_operation" for row in events
            )
            == 1
        ),
        "executor_returned_system_exit_zero": (
            "error" in output_types
            and "0" in exit_values
            and "SystemExit" in stderr_text
            and " 0" in stderr_text
        ),
        "session_terminated_pruned": terminated.get("reason") == "pruned",
        "expected_outputs_absent_locally": not any(
            local_output_presence.values()
        ),
        "optimizer_steps_unverifiable": True,
        "no_policy_result_claimed": True,
        "no_retry_or_resume_authorized": (
            not prereg["authority"]["additional_training_or_retry"]
            and not launch["recovery"]["retry"]
            and not launch["recovery"]["resume"]
        ),
        "robot_or_rdk_absent": (
            not prereg["authority"]["rdkx5_or_robot"]
            and not launch["authority"]["rdkx5_or_robot"]
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)

    value = {
        "schema_version": "open_duck.t38_session_loss_attribution.v1",
        "status": (
            "PASS_T38_UNRECOVERABLE_SESSION_LOSS_ATTRIBUTION"
            if not failed
            else "HOLD_T38_SESSION_LOSS_ATTRIBUTION"
        ),
        "decision": (
            "CLOSE_T38_ZERO_WEIGHT_NO_RETRY_"
            "EARN_T39_UNIFORM_NORMALIZER_ROLLBACK_PREREGISTRATION"
            if not failed
            else "HOLD_FOR_T38_ATTRIBUTION_REPAIR"
        ),
        "checks": checks,
        "failed_checks": failed,
        "session": {
            "name": SESSION,
            "accelerator": created.get("accelerator"),
            "created_at": created.get("timestamp"),
            "package_uploaded_at": uploaded.get("timestamp"),
            "execution_recorded_at": executed.get("timestamp"),
            "terminated_at": terminated.get("timestamp"),
            "termination_reason": terminated.get("reason"),
            "observed_execution_wall_seconds": execution_seconds,
            "history_event_types": [
                str(row.get("event_type")) for row in events
            ],
            "execution_output_types": output_types,
            "execution_exit_values": exit_values,
        },
        "recovery": {
            "expected_local_outputs": {
                name: {
                    "path": str(path),
                    "exists": local_output_presence[name],
                }
                for name, path in EXPECTED_LOCAL_OUTPUTS.items()
            },
            "remote_state_after_prune": "unavailable",
            "result_integrity": "unverifiable",
            "archive_integrity": "unverifiable",
            "receipt_integrity": "unverifiable",
        },
        "classification": {
            "executor_return_code": 0,
            "training_completion": "indicated_but_unverifiable",
            "optimizer_steps": None,
            "policy_checkpoint_count": None,
            "behavior_cells": 0,
            "policy_decision_weight": 0,
            "policy_pass": False,
            "policy_failure": False,
            "hosted_retry": False,
        },
        "hashes": {
            "preregistration": sha256(PREREGISTRATION),
            "package_contract": sha256(PACKAGE_CONTRACT),
            "launch_contract": sha256(LAUNCH_CONTRACT),
            "history": sha256(HISTORY),
            "stdout_log": sha256(STDOUT),
            "stderr_log": sha256(STDERR),
        },
        "authority": {
            "t39_uniform_normalizer_rollback_preregistration": not failed,
            "t39_behavior_evaluation": False,
            "additional_hosted_training": False,
            "t38_retry_or_resume": False,
            "checkpoint_selection": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T38 unrecoverable Colab session attribution",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Executor: `SystemExit 0` recorded",
                "- Result/archive/receipt: `UNRECOVERABLE`",
                "- Optimizer steps/checkpoints: `UNVERIFIABLE`",
                "- Policy pass/failure weight: `0/0`",
                "- Retry/resume: `CLOSED`",
                "- Gate 5 / robot authority: `CLOSED`",
                "",
                "T38 is an infrastructure/session-loss result, not a policy "
                "result. Its missing artifacts prevent checkpoint integrity "
                "checks and behavior evaluation.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
