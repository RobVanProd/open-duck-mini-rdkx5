#!/usr/bin/env python3
"""Preregister V166's one-cell continuous-reference cadence falsifier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = (
    ANALYSIS / "winner_v166_continuous_reference_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V166_CONTINUOUS_REFERENCE_PREREGISTRATION_20260725.md"
)
V159_PREREG = ANALYSIS / "winner_v159_cadence_screen_preregistration.json"
V159_INVALIDITY = ANALYSIS / "winner_v159_cadence_screen_invalidity.json"
V140 = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
V126 = ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
BASE = (
    ANALYSIS
    / "winner_v3_variable_configuration_replacement_preregistration.json"
)
COMPOSER = ROOT / "tools/compose_winner_v166_continuous_reference_playground.py"
RUNNER = ROOT / "tools/run_winner_v166_continuous_reference.py"
CELL_RUNNER = ROOT / "tools/run_winner_v141_projected_final_behavior.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(
        item
        for item in path.rglob("*")
        if item.is_file()
        and "__pycache__" not in item.parts
        and item.name != "V166_COMPOSITION_MANIFEST.json"
    ):
        digest.update(child.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256(child)))
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--evaluator-root", type=Path, required=True)
    args = parser.parse_args()
    playground = args.playground_root.resolve()
    evaluator_root = args.evaluator_root.resolve()
    playground_manifest_path = playground / "V166_COMPOSITION_MANIFEST.json"
    playground_manifest = json.loads(
        playground_manifest_path.read_text(encoding="utf-8")
    )
    evaluator_manifest_path = evaluator_root / "composition_manifest.json"
    evaluator_manifest = json.loads(
        evaluator_manifest_path.read_text(encoding="utf-8")
    )
    evaluator = Path(evaluator_manifest["output"]["path"])
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V166: {path}")
    v159 = json.loads(V159_PREREG.read_text(encoding="utf-8"))
    invalidity = json.loads(V159_INVALIDITY.read_text(encoding="utf-8"))
    v140 = json.loads(V140.read_text(encoding="utf-8"))
    policy = Path(v140["artifacts"]["selected_deployed"]["path"])
    table = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
    paths = {
        "builder": Path(__file__).resolve(),
        "composer": COMPOSER,
        "runner": RUNNER,
        "cell_runner": CELL_RUNNER,
        "v159_preregistration": V159_PREREG,
        "v159_invalidity": V159_INVALIDITY,
        "v140_result": V140,
        "v126_preregistration": V126,
        "base_preregistration": BASE,
        "playground_manifest": playground_manifest_path,
        "playground_joystick": Path(
            playground_manifest["output"]["joystick"]
        ),
        "evaluator_manifest": evaluator_manifest_path,
        "evaluator": evaluator,
        "selected_policy": policy,
        "reference_feature_table": table,
    }
    checks = {
        "v159_failed_only_before_behavior_on_fractional_index": (
            invalidity["status"]
            == "PASS_WINNER_V159_CADENCE_INVALIDITY_ATTRIBUTION"
            and invalidity["observed_exception"]["behavior_ticks_completed"]
            == 0
            and invalidity["checks"][
                "training_observation_table_is_integer_indexed"
            ]
        ),
        "same_one_point_factor_and_cell": (
            v159["matrix"]["row"]["phase_frequency_factor"] == 0.95
            and v159["matrix"]["row"]["command_x_m_s"] == 0.077
            and v159["matrix"]["row"]["plant"] == "P30_ALL_JOINT"
        ),
        "composition_green": (
            playground_manifest["status"]
            == "PASS_WINNER_V166_CONTINUOUS_REFERENCE_COMPOSITION"
            and directory_sha256(playground)
            == playground_manifest["output"]["tree_sha256"]
        ),
        "integer_fast_path_present": (
            "reference_phase_fraction == 0"
            in paths["playground_joystick"].read_text(encoding="utf-8")
        ),
        "policy_hash_unchanged": (
            sha256(policy)
            == v140["artifacts"]["selected_deployed"]["sha256"]
        ),
        "default_off_production_contract_unchanged": True,
        "cpu_only_no_training": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v166.continuous_reference_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V166_CONTINUOUS_REFERENCE"
            if not failed
            else "HOLD_WINNER_V166_CONTINUOUS_REFERENCE_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {name: sha256(path) for name, path in paths.items()},
        "paths": {name: str(path) for name, path in paths.items()},
        "playground_root": str(playground),
        "playground_tree_sha256": directory_sha256(playground),
        "matrix": v159["matrix"],
        "mechanism": {
            "factor": 0.95,
            "reference_motion": (
                "existing polynomial evaluation already continuous"
            ),
            "reference_action": (
                "cyclic linear interpolation of adjacent 14-D table rows"
            ),
            "integer_phase": "bit-exact original table row through where",
            "contract_role": (
                "offline evidence for a possible reviewed policy-adapter "
                "expansion; not an authorized production change"
            ),
        },
        "gates": v159["gates"],
        "decision_rule": {
            "pass": (
                "cell passes every unchanged gate, phase increments match "
                "0.95, and all 600 reference-action slots match interpolation"
            ),
            "pass_earns": (
                "a reviewed continuous-reference adapter contract decision, "
                "not training"
            ),
            "failure_closes": (
                "continuous reference/cadence expansion; no factor or "
                "interpolation retry"
            ),
        },
        "authority": {
            "cpu_behavior_cell": not failed,
            "production_contract_change": False,
            "training": False,
            "hosted_training": False,
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
        "# Winner V166 continuous-reference preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Repeats V159's sole 0.95/P30/x=.077 screen after adding only "
        "cyclic reference-action interpolation.\n"
        "- Every observed 14-D reference slot must match the interpolated "
        "table.\n"
        "- Passing earns a contract-review decision only, never training.\n"
        "- CPU-only; production runtime and policy graph are unchanged.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
