import copy
import json
import unittest
from pathlib import Path

from companion.evaluator import ScenarioContractError, evaluate_scenario, label_matches, load_scenario


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "development"
SCHEMAS = ROOT / "schemas"


class EvaluatorTests(unittest.TestCase):
    def scenarios(self):
        return [load_scenario(path) for path in sorted(FIXTURES.glob("*.json"))]

    def test_every_development_label_matches(self):
        scenarios = self.scenarios()
        self.assertGreaterEqual(len(scenarios), 10)
        for scenario in scenarios:
            with self.subTest(scenario=scenario["scenario_id"]):
                self.assertTrue(label_matches(scenario, evaluate_scenario(scenario)))

    def test_expected_label_cannot_change_decision(self):
        scenario = self.scenarios()[0]
        before = evaluate_scenario(scenario)
        altered = copy.deepcopy(scenario)
        altered["expected_outcome"] = {
            "decision": "STOP",
            "reason_code": "FABRICATED_LABEL",
            "missing_evidence": [],
        }
        self.assertEqual(before, evaluate_scenario(altered))

    def test_unknown_state_stops(self):
        scenario = self.scenarios()[0]
        scenario["known_state"] = False
        self.assertEqual("STOP", evaluate_scenario(scenario)["decision"])

    def test_duplicate_evidence_is_rejected(self):
        scenario = self.scenarios()[0]
        scenario["evidence"].append(copy.deepcopy(scenario["evidence"][0]))
        with self.assertRaises(ScenarioContractError):
            evaluate_scenario(scenario)

    def test_decision_contract_has_no_execution_field(self):
        forbidden = {"command", "commands", "shell", "adb", "execute", "device_serial"}
        for scenario in self.scenarios():
            self.assertTrue(forbidden.isdisjoint(evaluate_scenario(scenario)))

    def test_fixture_cannot_reclassify_a_repairable_failure_as_consequential(self):
        scenario = load_scenario(FIXTURES / "05-install-rejection.json")
        scenario["consequential"] = True
        with self.assertRaises(ScenarioContractError):
            evaluate_scenario(scenario)

    def test_fixture_cannot_choose_failure_policy(self):
        scenario = load_scenario(FIXTURES / "05-install-rejection.json")
        scenario["known_failure"]["evidence_key"] = "device_owner_status"
        with self.assertRaises(ScenarioContractError):
            evaluate_scenario(scenario)

    def test_schema_documents_are_valid_json(self):
        for path in SCHEMAS.glob("*.json"):
            with self.subTest(schema=path.name), path.open(encoding="utf-8") as handle:
                self.assertIsInstance(json.load(handle), dict)


if __name__ == "__main__":
    unittest.main()
