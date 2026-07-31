import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


PATH = Path(__file__).resolve().parents[1] / "tools" / "fit_actuator_response_model.py"
sys.path.insert(0, str(PATH.parent))
SPEC = importlib.util.spec_from_file_location("fit_actuator", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FixedTargetIngestTest(unittest.TestCase):
    def test_flat_fields_and_phase_selection(self):
        rows = []
        for phase in ("normal_p30", "gain_p31_34"):
            for tick in range(3):
                rows.append({
                    "phase": phase,
                    "tick": tick,
                    "timestamp_monotonic_s": tick * 0.02,
                    "target_rad": [float(tick)] * 14,
                    "actual_rad": [float(tick) / 2] * 14,
                })
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trace.jsonl"
            path.write_text("".join(json.dumps(row) + "\n" for row in rows))
            records = MODULE.load_records(path, 0, "gain_p31_34")
        self.assertEqual(len(records), 2)
        samples = MODULE.joint_series(records, "left_knee")
        self.assertEqual([row["target"] for row in samples], [1.0, 2.0])
        self.assertEqual([row["actual"] for row in samples], [0.5, 1.0])


if __name__ == "__main__":
    unittest.main()
