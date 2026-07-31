#!/usr/bin/env python3
"""Record why V159 cannot test a deployable frozen-contract policy."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v159_cadence_screen_preregistration.json"
RUNNER = ROOT / "tools/run_winner_v159_cadence_screen.py"
RUNTIME_ADAPTER = (
    ROOT / "runtime/mini_bdx_runtime/mini_bdx_runtime/winner_v2.py"
)
OUTPUT = ANALYSIS / "winner_v159_cadence_screen_invalidity.json"
MARKDOWN = ANALYSIS / "WINNER_V159_CADENCE_SCREEN_INVALIDITY_20260725.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluator-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    evaluator_root = args.evaluator_root.resolve()
    run_root = args.run_root.resolve()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V159: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator = Path(manifest["output"]["path"])
    # The source evaluator imports its Playground through the frozen V126
    # preregistration, so resolve the actual joystick from that record.
    v126_path = (
        ANALYSIS
        / "winner_v126_all_tick_supreme_clip_preregistration.json"
    )
    v126 = json.loads(v126_path.read_text(encoding="utf-8"))
    joystick = (
        Path(v126["external_inputs"]["playground"])
        / "playground/open_duck_mini_v2/joystick.py"
    )
    runtime_text = RUNTIME_ADAPTER.read_text(encoding="utf-8")
    joystick_text = joystick.read_text(encoding="utf-8")
    evaluator_text = evaluator.read_text(encoding="utf-8")
    files_in_failed_root = (
        [path for path in run_root.rglob("*") if path.is_file()]
        if run_root.exists()
        else []
    )
    checks = {
        "preregistration_was_one_point": (
            prereg.get("status")
            == "PREREGISTERED_WINNER_V159_CADENCE_SCREEN"
            and prereg["matrix"]["row"]["phase_frequency_factor"] == 0.95
        ),
        "runtime_requires_integer_unit_phase_step": (
            'if phase_step != 1:' in runtime_text
            and 'raise ValueError("winner-v2 requires one integer phase '
            'step per tick")' in runtime_text
        ),
        "runtime_reference_lookup_rejects_fractional_phase": (
            "not float(phase_index).is_integer()" in runtime_text
            and "phase_index must be an integer" in runtime_text
        ),
        "training_observation_table_is_integer_indexed": (
            'command_index, info["imitation_i"]' in joystick_text
        ),
        "fractional_evaluator_increment_present": (
            'state.info["imitation_i"] += config.phase_frequency_factor'
            in evaluator_text
        ),
        "failed_before_behavior_artifact": not files_in_failed_root,
        "no_training_hosted_compute_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v159.cadence_screen_invalidity.v1",
        "status": (
            "PASS_WINNER_V159_CADENCE_INVALIDITY_ATTRIBUTION"
            if not failed
            else "HOLD_WINNER_V159_CADENCE_INVALIDITY_ATTRIBUTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            "attributor": sha256(Path(__file__).resolve()),
            "preregistration": sha256(PREREG),
            "runner": sha256(RUNNER),
            "composition_manifest": sha256(manifest_path),
            "composed_evaluator": sha256(evaluator),
            "runtime_adapter": sha256(RUNTIME_ADAPTER),
            "v126_preregistration": sha256(v126_path),
            "training_joystick": sha256(joystick),
        },
        "observed_exception": {
            "type": "TypeError",
            "message": (
                "Indexer must have integer or boolean type, got indexer "
                "with type float32"
            ),
            "location": (
                "joystick.py reference_feature_actions[command_index, "
                "info['imitation_i']]"
            ),
            "behavior_ticks_completed": 0,
        },
        "interpretation": (
            "fractional cadence is not representable by this policy's "
            "frozen 115-D observation constructor or its RDK winner-v2 "
            "adapter; adding interpolation would change the policy contract"
        ),
        "decision": (
            "CLOSE_POSTEXPORT_CADENCE_MECHANISM_AS_NONDEPLOYABLE_"
            "UNDER_FROZEN_CONTRACT"
            if not failed
            else "HOLD_FOR_INVALIDITY_REVIEW"
        ),
        "selection_weight": 0,
        "authority": {
            "behavior_result": False,
            "training": False,
            "hosted_training": False,
            "runtime_or_observation_contract_change": False,
            "candidate_selection": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V159 cadence-screen invalidity\n\n"
        f"- Status: `{payload['status']}`\n"
        "- The CPU run stopped before behavior because the policy's 14-D "
        "reference-action observation is integer-phase indexed.\n"
        "- The RDK winner-v2 adapter independently requires one integer "
        "phase step per tick and rejects fractional phase.\n"
        "- Interpolation was not added because it would alter the frozen "
        "policy observation contract.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- Selection weight zero; no training, Colab, runtime change, "
        "deployment, Gate 5, or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
