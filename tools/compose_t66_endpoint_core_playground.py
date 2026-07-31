#!/usr/bin/env python3
"""Compose the T66 endpoint-bank recurrent-core training source."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = Path("D:/CodexProjects/Open_Duck_Playground-composed-t37-v1")
OUTPUT = Path("D:/CodexProjects/Open_Duck_Playground-composed-t66-v2")
MODULE = ROOT / "patches" / "t66_endpoint_core_continuation.py"
MANIFEST = OUTPUT / "T66_COMPOSED_SOURCE_MANIFEST.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(path for path in path.rglob("*") if path.is_file()):
        digest.update(item.relative_to(path.parents[len(path.parts)]).as_posix().encode())
    return digest.hexdigest()


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"expected one replacement in {path}, found {count}: {old[:80]!r}"
        )
    path.write_text(
        text.replace(old, new),
        encoding="utf-8",
        newline="\n",
    )


def file_inventory(root: Path) -> dict[str, dict[str, Any]]:
    return {
        path.relative_to(root).as_posix(): {
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in sorted(root.rglob("*"))
        if path.is_file() and path != MANIFEST
    }


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"refusing to overwrite T66 source: {OUTPUT}")
    shutil.copytree(BASE, OUTPUT)
    destination_module = (
        OUTPUT
        / "playground"
        / "common"
        / "t66_endpoint_core_continuation.py"
    )
    shutil.copy2(MODULE, destination_module)

    duck_runner = (
        OUTPUT / "playground" / "open_duck_mini_v2" / "runner.py"
    )
    replace_once(
        duck_runner,
        """        if (
            args.winner_t37_freeze_observation_normalizer
            and not args.winner_t31_action_margin_trainthrough
        ):
            raise ValueError(
                "T37 frozen observation normalizer requires T31 "
                "action-margin train-through"
            )
""",
        """        if (
            args.winner_t37_freeze_observation_normalizer
            and not args.winner_t31_action_margin_trainthrough
        ):
            raise ValueError(
                "T37 frozen observation normalizer requires T31 "
                "action-margin train-through"
            )
        if args.winner_t66_endpoint_core_continuation and not (
            args.winner_t37_freeze_observation_normalizer
            and args.winner_t31_action_margin_trainthrough
            and args.winner_t19_support_trainthrough
            and args.winner_v3_variable_configuration
            and args.policy_architecture
            == "reference_residual_recurrent_adapter"
        ):
            raise ValueError(
                "T66 requires the frozen-normalizer T31/T19 recurrent "
                "variable-configuration contract"
            )
""",
    )
    replace_once(
        duck_runner,
        """            self.randomizer = winner_v3.make_winner_v3_configuration_randomizer(
                torso_body_id=torso_body_id,
                deviation_scale=args.winner_v3_deviation_scale,
            )
            print(
""",
        """            self.randomizer = winner_v3.make_winner_v3_configuration_randomizer(
                torso_body_id=torso_body_id,
                deviation_scale=args.winner_v3_deviation_scale,
            )
            if args.winner_t66_endpoint_core_continuation:
                from playground.common.t66_endpoint_core_continuation import (
                    make_endpoint_bank_randomizer,
                )

                self.randomizer = make_endpoint_bank_randomizer(
                    self.randomizer,
                    torso_body_id=torso_body_id,
                )
                print(
                    "T66_ENDPOINT_CORE_CONTINUATION="
                    "strata=8,broad=1,isolated=7,"
                    "actor_updates=recurrent_core_only"
                )
            print(
""",
    )
    replace_once(
        duck_runner,
        """    parser.add_argument(
        "--winner_t37_freeze_observation_normalizer",
        action="store_true",
    )
""",
        """    parser.add_argument(
        "--winner_t37_freeze_observation_normalizer",
        action="store_true",
    )
    parser.add_argument(
        "--winner_t66_endpoint_core_continuation",
        action="store_true",
    )
""",
    )

    common_runner = OUTPUT / "playground" / "common" / "runner.py"
    replace_once(
        common_runner,
        """        if getattr(
            self.args, "winner_t37_freeze_observation_normalizer", False
        ):
            from playground.common.t37_frozen_observation_normalizer import (
                frozen_observation_statistics_updates,
            )

            with frozen_observation_statistics_updates():
                _, params, _ = train_call()
        else:
            _, params, _ = train_call()
""",
        """        from contextlib import ExitStack

        with ExitStack() as stack:
            if getattr(
                self.args, "winner_t37_freeze_observation_normalizer", False
            ):
                from playground.common.t37_frozen_observation_normalizer import (
                    frozen_observation_statistics_updates,
                )

                stack.enter_context(frozen_observation_statistics_updates())
            if getattr(
                self.args, "winner_t66_endpoint_core_continuation", False
            ):
                from playground.common.t66_endpoint_core_continuation import (
                    recurrent_core_only_updates,
                )

                stack.enter_context(recurrent_core_only_updates())
            _, params, _ = train_call()
""",
    )

    inventory = file_inventory(OUTPUT)
    manifest = {
        "schema_version": "open_duck.t66_composed_source.v1",
        "base": {
            "path": str(BASE.resolve()),
        },
        "sources": {
            "module": {
                "path": str(MODULE.resolve()),
                "bytes": MODULE.stat().st_size,
                "sha256": sha256(MODULE),
            },
            "composer": {
                "path": str(Path(__file__).resolve()),
                "bytes": Path(__file__).stat().st_size,
                "sha256": sha256(Path(__file__)),
            },
        },
        "mechanism": {
            "randomizer": (
                "one broad stratum plus nominal and six isolated "
                "torso-COM endpoints, 32 environments each"
            ),
            "actor_updates": (
                "recurrent adapter obs/hidden projections and hidden bias only"
            ),
            "critic_updates": "unchanged",
            "normalizer": "exact frozen restored statistics",
            "reward_change": False,
            "policy_abi_change": False,
            "runtime_change": False,
        },
        "python_inventory": {
            key: value
            for key, value in inventory.items()
            if key.endswith(".py")
        },
    }
    MANIFEST.write_text(
        json.dumps(manifest, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"COMPOSED_T66={OUTPUT}")
    print(f"manifest_sha256={sha256(MANIFEST)}")
    print(f"python_files={len(manifest['python_inventory'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
