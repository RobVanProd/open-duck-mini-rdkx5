#!/usr/bin/env python3
"""Audit exact R2 endpoint exposure in the T78 training population."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T52_RESULT = ANALYSIS / "t52_uniform_half_head_qualification_result.json"
T53_RESULT = ANALYSIS / "t53_uniform_half_head_r2_remainder_result.json"
T66_PREREG = ANALYSIS / "t66_endpoint_core_cpu_preregistration.json"
T78_PREREG = (
    ANALYSIS / "t78_endpoint_joint_adapter_hosted_preregistration.json"
)
T86_RESULT = ANALYSIS / "t86_rolling_midpoint_r2_result.json"
T89_RESULT = ANALYSIS / "t89_terminal_final_r2_remainder_result.json"
R2_BASIS = ANALYSIS / "t41_uniform_normalizer_r2_preregistration.json"
T66_MODULE = ROOT / "patches" / "t66_endpoint_core_continuation.py"
VARIABLE_CONFIGURATION = Path(
    "D:/CodexProjects/Open_Duck_Playground-composed-t77-v1/"
    "playground/common/winner_v3_variable_configuration.py"
)
OUTPUT = ANALYSIS / "t90_r2_endpoint_exposure_audit.json"
MARKDOWN = ANALYSIS / "T90_R2_ENDPOINT_EXPOSURE_AUDIT_20260728.md"

NOMINAL_EQUIVALENT_CONDITIONS = (
    "FLOOR_FRICTION_HI",
    "ARMATURE_LO",
)
COM_ENDPOINT_CONDITIONS = (
    "TORSO_COM_X_NEG",
    "TORSO_COM_X_POS",
    "TORSO_COM_Y_NEG",
    "TORSO_COM_Y_POS",
    "TORSO_COM_Z_NEG",
    "TORSO_COM_Z_POS",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("result_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def assigned_names(path: Path, name: str) -> tuple[str, ...]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == name
        ):
            value = ast.literal_eval(node.value)
            return tuple(str(item) for item in value)
    raise RuntimeError(f"{name} not found in {path}")


def condition_by_id(
    result: dict[str, Any],
    condition_id: str,
) -> dict[str, Any]:
    return next(
        item
        for item in result["conditions"]
        if item["condition_id"] == condition_id
    )


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T90 output: {path}")

    sources = {
        "t52_result": T52_RESULT,
        "t53_result": T53_RESULT,
        "t66_preregistration": T66_PREREG,
        "t78_preregistration": T78_PREREG,
        "t86_result": T86_RESULT,
        "t89_result": T89_RESULT,
        "r2_basis": R2_BASIS,
        "t66_endpoint_module": T66_MODULE,
        "variable_configuration_source": VARIABLE_CONFIGURATION,
    }
    missing_sources = sorted(
        name for name, path in sources.items() if not path.is_file()
    )
    if missing_sources:
        raise FileNotFoundError(
            f"T90 source files missing: {missing_sources}"
        )

    t52 = read_json(T52_RESULT)
    t53 = read_json(T53_RESULT)
    t66 = read_json(T66_PREREG)
    t78 = read_json(T78_PREREG)
    t86 = read_json(T86_RESULT)
    t89 = read_json(T89_RESULT)
    r2 = read_json(R2_BASIS)

    endpoint_names = assigned_names(T66_MODULE, "ENDPOINT_NAMES")
    condition_ids = tuple(item["id"] for item in r2["conditions"])
    exact_condition_ids = (
        *NOMINAL_EQUIVALENT_CONDITIONS,
        *COM_ENDPOINT_CONDITIONS,
    )
    missing_exact = tuple(
        item for item in condition_ids if item not in exact_condition_ids
    )
    variable_source = VARIABLE_CONFIGURATION.read_text(encoding="utf-8")

    source_green = {
        "conditions_1_to_4": {
            "green_cells": t52["summary"]["green_cells"],
            "cells": t52["summary"]["completed_cells"],
            "all_green": t52["summary"]["all_four_conditions_green"],
        },
        "conditions_5_to_6": {
            "green_cells": sum(
                condition_by_id(t53, condition)["green_cells"]
                for condition in ("ARMATURE_LO", "ARMATURE_HI")
            ),
            "cells": sum(
                condition_by_id(t53, condition)["cells"]
                for condition in ("ARMATURE_LO", "ARMATURE_HI")
            ),
            "all_green": all(
                condition_by_id(t53, condition)["condition_green"]
                for condition in ("ARMATURE_LO", "ARMATURE_HI")
            ),
        },
    }
    post_t78_regressions = [
        {
            "condition": "JOINT_FRICTIONLOSS_HI",
            "checkpoint_scope": "T84 rolling half and final",
            "green_cells": condition_by_id(
                t86, "JOINT_FRICTIONLOSS_HI"
            )["green_cells"],
            "cells": condition_by_id(t86, "JOINT_FRICTIONLOSS_HI")[
                "cells"
            ],
        },
        {
            "condition": "ARMATURE_HI",
            "checkpoint_scope": "T84 rolling final diagnostic",
            "green_cells": condition_by_id(t89, "ARMATURE_HI")[
                "green_cells"
            ],
            "cells": condition_by_id(t89, "ARMATURE_HI")["cells"],
        },
    ]

    checks = {
        "source_green_conditions_one_through_six": (
            source_green["conditions_1_to_4"] == {
                "green_cells": 64,
                "cells": 64,
                "all_green": True,
            }
            and source_green["conditions_5_to_6"] == {
                "green_cells": 32,
                "cells": 32,
                "all_green": True,
            }
        ),
        "t78_population_exact": (
            t78["training"]["num_envs"] == 256
            and t78["training"]["endpoint_strata"] == 8
            and t78["training"]["environments_per_stratum"] == 32
        ),
        "t66_categories_exact": (
            endpoint_names
            == (
                "broad_random",
                "nominal",
                "torso_com_x_neg",
                "torso_com_x_pos",
                "torso_com_y_neg",
                "torso_com_y_pos",
                "torso_com_z_neg",
                "torso_com_z_pos",
            )
            and tuple(t66["mechanism"]["endpoint_categories"])
            == endpoint_names
        ),
        "broad_stratum_samples_continuously": all(
            token in variable_source
            for token in (
                "return low + jax.random.uniform",
                "floor = _uniform(keys[0], floor_low, floor_high)",
                "friction_scale = _uniform(",
                "shape=(model.nu,)",
                "armature_scale = _uniform(",
            )
        ),
        "exact_r2_coverage_is_eight_of_twenty": (
            len(condition_ids) == 20
            and len(exact_condition_ids) == 8
            and len(missing_exact) == 12
        ),
        "post_t78_regressions_are_missing_exact_endpoints": (
            all(
                item["condition"] in missing_exact
                and item["green_cells"] == item["cells"] - 1
                for item in post_t78_regressions
            )
        ),
        "no_new_behavior_or_training": True,
        "no_robot_or_rdk": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)

    value: dict[str, Any] = {
        "schema_version": "open_duck.t90_r2_endpoint_exposure_audit.v1",
        "status": (
            "PASS_T90_R2_ENDPOINT_EXPOSURE_AUDIT"
            if not failed
            else "HOLD_T90_R2_ENDPOINT_EXPOSURE_AUDIT"
        ),
        "classification": (
            "POST_T78_REGRESSION_ALIGNS_WITH_MISSING_EXACT_ENDPOINT_REPLAY"
            if not failed
            else "T90_EVIDENCE_INCOMPLETE"
        ),
        "decision": (
            "EARN_T91_COM_ENDPOINT_RETENTION_DIAGNOSTIC_"
            "PREREGISTRATION_ONLY"
            if not failed
            else "STOP_T90_AND_REPAIR_EVIDENCE"
        ),
        "question": (
            "Did T78 train the exact frozen R2 endpoints whose robustness "
            "later regressed, or only a continuous broad sample plus exact "
            "nominal and torso-COM strata?"
        ),
        "training_population": {
            "environments": t78["training"]["num_envs"],
            "strata": t78["training"]["endpoint_strata"],
            "environments_per_stratum": t78["training"][
                "environments_per_stratum"
            ],
            "categories": list(endpoint_names),
            "broad_strata": 1,
            "exact_nominal_or_com_strata": 7,
        },
        "r2_exact_exposure": {
            "condition_count": len(condition_ids),
            "exact_condition_count": len(exact_condition_ids),
            "missing_exact_condition_count": len(missing_exact),
            "exact_condition_ids": list(exact_condition_ids),
            "missing_exact_condition_ids": list(missing_exact),
            "broad_endpoint_equality_probability": 0.0,
            "reason": (
                "The broad stratum uses continuous uniform draws. Joint "
                "friction and armature are independently drawn per joint, "
                "whereas the R2 endpoint applies one exact scale to every "
                "controlled joint. Exact endpoint vectors therefore have "
                "measure zero in that stratum."
            ),
        },
        "source_green_before_t78": source_green,
        "post_t78_regressions": post_t78_regressions,
        "interpretation": {
            "supported": (
                "T78 changed an actor that had passed R2 conditions 1-6 "
                "while exactly replaying nominal and COM endpoints but not "
                "the later failed friction-high and armature-high endpoints."
            ),
            "not_yet_proven": (
                "Exact endpoint replay is sufficient. T91 must first test "
                "whether the T84 pair retained the exact COM-X-negative "
                "endpoint that T78 explicitly trained."
            ),
            "hosted_run_earned": False,
        },
        "checks": checks,
        "failed_checks": failed,
        "source_receipts": {
            name: receipt(path) for name, path in sources.items()
        },
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "execution": {
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "t91_com_endpoint_retention_diagnostic_preregistration": (
                not failed
            ),
            "additional_training": False,
            "colab": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T90 R2 endpoint-exposure audit",
                "",
                f"- Status: `{value['status']}`",
                f"- Classification: `{value['classification']}`",
                "- T78 population: `8 strata x 32 = 256`",
                "- Exact frozen R2 exposure: `8/20 conditions`",
                "- Missing exact frozen R2 exposure: `12/20 conditions`",
                (
                    "- Regressions: source was `96/96` through conditions "
                    "1-6; T84 later lost one friction-high cell and its "
                    "terminal final lost one armature-high cell"
                ),
                (
                    "- Next: one CPU-only COM-X-negative retention "
                    "diagnostic; no hosted run is earned yet"
                ),
                "- Training / Colab / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"missing_exact={list(missing_exact)}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
