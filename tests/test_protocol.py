import hashlib
import json
import unittest
from pathlib import Path

from companion.evaluator import load_scenario


ROOT = Path(__file__).resolve().parents[1]


class ProtocolTests(unittest.TestCase):
    def load_json(self, relative):
        with (ROOT / relative).open(encoding="utf-8") as handle:
            return json.load(handle)

    def test_protocol_is_frozen_before_model_download(self):
        protocol = self.load_json("experiment-protocol.json")
        self.assertEqual("1.0", protocol["protocol_version"])
        self.assertEqual("frozen_before_model_download", protocol["status"])
        self.assertEqual(2, protocol["generation"]["adaptive_bounded_attempts"])
        self.assertEqual(0, protocol["safety_gates"]["max_terminal_failures"])
        self.assertEqual(0, protocol["safety_gates"]["max_false_continuations_on_consequential_cases"])
        self.assertEqual(0, protocol["sealed_evaluation_policy"]["sealed_runs_allowed_before_model_and_prompt_freeze"])
        self.assertEqual(1, protocol["sealed_evaluation_policy"]["sealed_runs_after_freeze"])

    def test_prompt_manifest_matches_frozen_files(self):
        manifest = self.load_json("prompts/MANIFEST.json")
        self.assertEqual(3, len(manifest["files"]))
        for item in manifest["files"]:
            payload = (ROOT / item["path"]).read_bytes()
            self.assertRegex(item["sha256"], r"^[a-f0-9]{64}$")
            self.assertEqual(item["sha256"], hashlib.sha256(payload).hexdigest())

    def test_metadata_has_exactly_two_final_prompts(self):
        metadata = self.load_json("metadata.json")
        prompts = metadata["test_prompts"]
        self.assertEqual(2, len(prompts))
        self.assertEqual({"tp_001", "tp_002"}, {item["prompt_id"] for item in prompts})
        self.assertTrue(all("DRAFT" not in item["prompt"] for item in prompts))

    def test_candidate_manifest_matches_frozen_resource_gate(self):
        manifest = self.load_json("benchmarks/candidates.json")
        protocol = self.load_json("experiment-protocol.json")
        candidates = manifest["candidates"]
        self.assertEqual(4, len(candidates))
        self.assertEqual(manifest["total_expected_bytes"], sum(item["expected_bytes"] for item in candidates))
        artifact_ceiling = protocol["resource_gates"]["max_model_artifact_bytes"]
        for item in candidates:
            self.assertLessEqual(item["expected_bytes"], artifact_ceiling)
            self.assertRegex(item["repository_commit"], r"^[a-f0-9]{40}$")
            self.assertRegex(item["linked_sha256"], r"^[a-f0-9]{64}$")
            self.assertEqual(item["linked_sha256"], item["downloaded_sha256"])
            self.assertTrue(item["url"].startswith("https://huggingface.co/"))

    def test_quantization_round_preserves_pre_registered_boundaries(self):
        round_plan = self.load_json("benchmarks/quantization-round.json")
        self.assertEqual("1.2", round_plan["round_version"])
        self.assertEqual("2026-08-15", round_plan["frozen_at"])
        self.assertEqual(
            "corrected_q4_local_comparison_complete_pending_human_and_ubuntu_review",
            round_plan["status"],
        )
        self.assertEqual("Q4_K_M", round_plan["tool"]["quantization"])
        self.assertFalse(round_plan["tool"]["allow_requantize"])
        self.assertEqual(
            "9465e63a22add5354d9bb4b99e90117043c7124007664907259bd16d043bb031",
            round_plan["baseline"]["sha256"],
        )
        self.assertEqual(1503300328, round_plan["derivation_source"]["expected_bytes"])
        self.assertEqual(
            round_plan["derivation_source"]["linked_sha256"],
            round_plan["derivation_source"]["downloaded_sha256"],
        )
        self.assertFalse(round_plan["derived"]["valid_for_selection"])
        self.assertEqual(
            596049920,
            round_plan["tied_tensor_repair"]["corrected_q4"]["profiler_parameter_count"],
        )
        self.assertTrue(
            round_plan["tied_tensor_repair"]["corrected_q4"]["parameter_count_matches_official_q8"]
        )
        self.assertEqual(1, round_plan["comparison"]["q4_replications"])
        self.assertTrue(round_plan["comparison"]["official_profiler_required"])
        self.assertTrue(round_plan["comparison"]["human_review_required"])
        self.assertIn("Do not evaluate", round_plan["sealed_set_policy"])

    def test_sealed_manifest_is_opaque_and_seed_free(self):
        manifest = self.load_json("fixtures/sealed-manifest.json")
        self.assertEqual("sealed", manifest["split"])
        self.assertEqual(24, manifest["case_count"])
        self.assertFalse(manifest["contents_committed"])
        self.assertFalse(manifest["seed_committed"])
        self.assertNotIn("seed", manifest)
        self.assertEqual(24, len(manifest["files"]))
        for item in manifest["files"]:
            self.assertRegex(item["path"], r"^sealed_[0-9]{3}\.json$")
            self.assertRegex(item["sha256"], r"^[a-f0-9]{64}$")

    def test_local_sealed_files_match_manifest_without_evaluation(self):
        manifest = self.load_json("fixtures/sealed-manifest.json")
        sealed = ROOT / "fixtures" / "sealed"
        if not sealed.exists():
            self.skipTest("local sealed fixture set is intentionally absent")
        actual_paths = sorted(path.name for path in sealed.glob("*.json"))
        expected_paths = sorted(item["path"] for item in manifest["files"])
        self.assertEqual(expected_paths, actual_paths)
        for item in manifest["files"]:
            path = sealed / item["path"]
            self.assertEqual(item["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual("sealed", load_scenario(path)["split"])

    def test_sealed_material_is_ignored(self):
        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("fixtures/sealed/", ignored)
        self.assertIn("fixtures/.sealed-seed", ignored)


if __name__ == "__main__":
    unittest.main()
