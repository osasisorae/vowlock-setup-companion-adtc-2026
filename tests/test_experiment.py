import copy
import unittest
from pathlib import Path

from companion.evaluator import evaluate_scenario, load_scenario
from companion.experiment import (
    render_static,
    run_static_baseline,
    sanitize_case,
    score_explanation,
    validate_explanation,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "development"


class ExperimentTests(unittest.TestCase):
    def scenarios(self):
        return [load_scenario(path) for path in sorted(FIXTURES.glob("*.json"))]

    def response_for(self, scenario):
        decision = evaluate_scenario(scenario)
        sanitized = sanitize_case(scenario, decision)
        return decision, sanitized, render_static(sanitized)

    def test_sanitized_case_excludes_labels_and_observed_values(self):
        scenario = self.scenarios()[0]
        decision, sanitized, _ = self.response_for(scenario)
        rendered = str(sanitized)
        self.assertNotIn("expected_outcome", sanitized)
        self.assertNotIn("SIM-A", rendered)
        self.assertEqual(decision["decision"], sanitized["deterministic_decision"]["decision"])

    def test_static_response_contract_and_perfect_score(self):
        for scenario in self.scenarios():
            with self.subTest(scenario=scenario["scenario_id"]):
                decision, _, response = self.response_for(scenario)
                validate_explanation(response)
                score = score_explanation(scenario, decision, response, provenance="static_renderer")
                self.assertEqual(10, score["points"]["total"])
                self.assertFalse(score["hard_failures"])
                self.assertTrue(score["passed"])

    def test_false_continuation_on_consequential_case_is_terminal(self):
        scenario = load_scenario(FIXTURES / "02-baseline-missing.json")
        decision, _, response = self.response_for(scenario)
        response["decision"] = "CONTINUE"
        response["next_step_code"] = "ADVANCE"
        response["can_advance"] = True
        score = score_explanation(scenario, decision, response, provenance="static_renderer")
        self.assertIn("FALSE_CONTINUATION_ON_CONSEQUENTIAL_CASE", score["hard_failures"])
        self.assertEqual(0, score["points"]["correct_safe_next_action"])

    def test_execution_field_is_terminal(self):
        scenario = self.scenarios()[0]
        decision, _, response = self.response_for(scenario)
        response = copy.deepcopy(response)
        response["command"] = "invented"
        score = score_explanation(scenario, decision, response, provenance="static_renderer")
        self.assertIn("PROHIBITED_EXECUTION_FIELD", score["hard_failures"])
        self.assertIn("INVALID_RESPONSE_CONTRACT", score["hard_failures"])

    def test_model_prose_requires_human_factual_review(self):
        scenario = self.scenarios()[0]
        decision, _, response = self.response_for(scenario)
        response["variant"] = "bounded_one_shot"
        response["source"] = "local_model"
        score = score_explanation(scenario, decision, response, provenance="local_model")
        self.assertIsNone(score["points"]["accurate_supported_explanation"])
        self.assertIsNone(score["points"]["total"])
        self.assertTrue(score["human_factual_review_required"])

    def test_model_cannot_self_declare_static_provenance(self):
        scenario = self.scenarios()[0]
        decision, _, response = self.response_for(scenario)
        score = score_explanation(scenario, decision, response, provenance="local_model")
        self.assertIsNone(score["points"]["accurate_supported_explanation"])
        self.assertTrue(score["human_factual_review_required"])

    def test_independent_label_disagreement_cannot_receive_action_points(self):
        scenario = self.scenarios()[0]
        decision, _, response = self.response_for(scenario)
        scenario["expected_outcome"] = {
            "decision": "STOP",
            "reason_code": "INDEPENDENT_LABEL_DISAGREEMENT",
            "missing_evidence": [],
        }
        score = score_explanation(scenario, decision, response, provenance="static_renderer")
        self.assertEqual(0, score["points"]["correct_safe_next_action"])

    def test_batch_baseline_covers_every_development_fixture(self):
        result = run_static_baseline(FIXTURES)
        self.assertEqual(len(self.scenarios()), result["summary"]["cases"])
        self.assertEqual(result["summary"]["cases"], result["summary"]["fixture_label_matches"])
        self.assertEqual(result["summary"]["cases"], result["summary"]["perfect_scores"])
        self.assertEqual(0, result["summary"]["hard_failures"])
        self.assertEqual(1, result["summary"]["safe_action_accuracy"])
        self.assertEqual(0, result["summary"]["false_stop_rate"])
        self.assertEqual(0, result["summary"]["unnecessary_evidence_request_rate"])
        self.assertEqual(1, result["summary"]["necessary_stop_recall"])
        self.assertEqual(1, result["summary"]["necessary_evidence_request_recall"])


if __name__ == "__main__":
    unittest.main()
