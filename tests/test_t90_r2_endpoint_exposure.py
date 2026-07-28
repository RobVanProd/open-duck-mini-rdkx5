from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "outputs"
    / "analysis"
    / "t90_r2_endpoint_exposure_audit.json"
)


def test_t90_closes_the_exact_endpoint_exposure_question() -> None:
    if not RESULT.exists():
        pytest.skip("formal T90 audit has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T90_R2_ENDPOINT_EXPOSURE_AUDIT"
    assert value["decision"] == (
        "EARN_T91_COM_ENDPOINT_RETENTION_DIAGNOSTIC_"
        "PREREGISTRATION_ONLY"
    )
    assert value["failed_checks"] == []
    assert value["source_green_before_t78"] == {
        "conditions_1_to_4": {
            "all_green": True,
            "cells": 64,
            "green_cells": 64,
        },
        "conditions_5_to_6": {
            "all_green": True,
            "cells": 32,
            "green_cells": 32,
        },
    }
    assert value["training_population"]["categories"] == [
        "broad_random",
        "nominal",
        "torso_com_x_neg",
        "torso_com_x_pos",
        "torso_com_y_neg",
        "torso_com_y_pos",
        "torso_com_z_neg",
        "torso_com_z_pos",
    ]
    exposure = value["r2_exact_exposure"]
    assert exposure["exact_condition_count"] == 8
    assert exposure["missing_exact_condition_count"] == 12
    assert exposure["broad_endpoint_equality_probability"] == 0.0
    assert [item["condition"] for item in value["post_t78_regressions"]] == [
        "JOINT_FRICTIONLOSS_HI",
        "ARMATURE_HI",
    ]
    assert not value["interpretation"]["hosted_run_earned"]
    assert value["execution"] == {
        "hosted_compute_units": 0,
        "new_behavior_cells": 0,
        "optimizer_steps": 0,
        "robot_or_rdk_access": 0,
    }
