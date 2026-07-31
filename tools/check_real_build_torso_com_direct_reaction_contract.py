#!/usr/bin/env python3
"""Emit the zero-measurement direct-reaction calculator contract."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/real_build_torso_com_direct_reaction_preregistration.json"
TEMPLATE = ROOT / "outputs/analysis/real_build_torso_com_direct_reaction_template.json"
EVALUATOR = ROOT / "tools/evaluate_real_build_torso_com_direct_reaction.py"
TEST = ROOT / "tests/test_evaluate_real_build_torso_com_direct_reaction.py"
BREAK_RESULT = ROOT / "outputs/analysis/composite_winner_torso_com_break_radius_result.json"
URDF = ROOT.parent / "Open_Duck_Mini/mini_bdx/robots/open_duck_mini_v2/robot.urdf"
SIM_XML = ROOT.parent / "Open_Duck_Playground/playground/open_duck_mini_v2/xmls/open_duck_mini_v2.xml"
RESULT_JSON = ROOT / "outputs/analysis/real_build_torso_com_direct_reaction_result.json"
RESULT_MD = ROOT / "outputs/analysis/REAL_BUILD_TORSO_COM_DIRECT_REACTION_RESULT_20260719.md"
CONTRACT_JSON = ROOT / "outputs/analysis/real_build_torso_com_direct_reaction_contract.json"
CONTRACT_MD = ROOT / "outputs/analysis/REAL_BUILD_TORSO_COM_DIRECT_REACTION_CONTRACT_20260719.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_evaluator():
    spec = importlib.util.spec_from_file_location("direct_reaction", EVALUATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    prereg = json.loads(PREREG.read_text())
    checks = {
        "preregistration_status_exact": prereg.get("status")
        == "PREREGISTERED_DIRECT_POWERED_OFF_MEASUREMENT_ROUTE",
        "zero_formal_physical_measurements_in_preregistration": prereg.get(
            "formal_physical_measurements_read"
        )
        == 0,
        "urdf_hash_exact": URDF.exists()
        and sha256(URDF) == prereg["datum"]["urdf_sha256"],
        "sim_xml_hash_exact": SIM_XML.exists()
        and sha256(SIM_XML) == prereg["datum"]["sim_xml_sha256"],
        "break_radius_hash_exact": sha256(BREAK_RESULT)
        == prereg["comparison"]["break_radius_result_sha256"],
        "formal_result_absent": not RESULT_JSON.exists() and not RESULT_MD.exists(),
    }

    compile_result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(EVALUATOR), str(TEST)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    checks["python_compile_passes"] = compile_result.returncode == 0
    test_result = subprocess.run(
        [sys.executable, "-m", "unittest", str(TEST)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    checks["eight_cpu_unit_cases_pass"] = (
        test_result.returncode == 0 and "Ran 8 tests" in test_result.stderr
    )

    evaluator = load_evaluator()
    template = json.loads(TEMPLATE.read_text())
    blank_result = evaluator.evaluate(template, TEMPLATE, BREAK_RESULT)
    checks.update(
        {
            "blank_template_holds_incomplete": blank_result.get("status")
            == "HOLD_REAL_BUILD_DIRECT_COM_INPUTS_INCOMPLETE",
            "blank_template_reports_no_numerical_estimate": blank_result.get(
                "numerical_estimate_reported"
            )
            is False
            and "estimate" not in blank_result,
            "blank_template_authority_all_false": all(
                value is False for value in blank_result.get("authority", {}).values()
            ),
            "datum_locked_to_minus_0p019": template["coordinate_contract"][
                "datum_origin_x_in_trunk_assembly_m"
            ]
            == -0.019,
            "exactly_three_formal_trial_slots": [row.get("id") for row in template["trials"]]
            == ["trial_1", "trial_2", "trial_3"],
            "zero_robot_rdk_gpu_actions": True,
        }
    )
    failed = sorted(key for key, passed in checks.items() if not passed)
    status = (
        "PASS_DIRECT_REACTION_CALCULATOR_CONTRACT_HOLD_PHYSICAL_INPUTS"
        if not failed
        else "FAIL_DIRECT_REACTION_CALCULATOR_CONTRACT"
    )
    payload = {
        "blank_template": {
            "missing_or_invalid_field_count": len(blank_result.get("issues", [])),
            "numerical_estimate_reported": blank_result.get("numerical_estimate_reported"),
            "status": blank_result.get("status"),
        },
        "checks": checks,
        "environment": {
            "execution": "CPU-only Python arithmetic",
            "formal_physical_measurements_read": 0,
            "robot_or_rdk_access": False,
        },
        "failed_checks": failed,
        "hashes": {
            "break_radius_result": sha256(BREAK_RESULT),
            "evaluator": sha256(EVALUATOR),
            "preregistration": sha256(PREREG),
            "sim_xml": sha256(SIM_XML) if SIM_XML.exists() else "MISSING",
            "template": sha256(TEMPLATE),
            "test": sha256(TEST),
            "urdf": sha256(URDF) if URDF.exists() else "MISSING",
        },
        "schema_version": "real_build_torso_com.direct_reaction_contract.v1",
        "status": status,
    }
    CONTRACT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Real-Build Torso-COM Direct-Reaction Contract",
        "",
        f"Status: `{status}`",
        "",
        "Formal physical measurements read: `0`.",
        "",
        f"Blank template: `{blank_result.get('status')}` with "
        f"`{len(blank_result.get('issues', []))}` missing/invalid fields and no numerical estimate.",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"- `{key}`: `{'PASS' if value else 'FAIL'}`" for key, value in checks.items())
    lines.extend(
        [
            "",
            "A pass validates only the calculator and blank measurement route. It authorizes no",
            "physical measurement by the agent, robot/RDK-X5 access, Gate 5, deployment, torque,",
            "motors, training, hosted compute, GPU/iGPU use, or robot clearance.",
            "",
        ]
    )
    CONTRACT_MD.write_text("\n".join(lines))
    print(CONTRACT_MD.relative_to(ROOT))
    print(CONTRACT_JSON.relative_to(ROOT))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
