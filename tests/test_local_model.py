import json
import unittest
from pathlib import Path

from companion.local_model import LlamaServer, LocalModelError, build_user_message, parse_json_object


ROOT = Path(__file__).resolve().parents[1]


class LocalModelTests(unittest.TestCase):
    def setUp(self):
        self.protocol = json.loads((ROOT / "experiment-protocol.json").read_text(encoding="utf-8"))

    def test_user_message_contains_only_sanitized_packet(self):
        packet = {
            "title": "Evidence is missing",
            "scenario_id": "safe_case",
            "deterministic_decision": {"decision": "WAIT"},
        }
        message = build_user_message(packet)
        self.assertIn("Evidence is missing", message)
        self.assertIn('"decision":"WAIT"', message)
        self.assertNotIn("expected_outcome", message)
        self.assertNotIn("observed", message)

    def test_json_parser_rejects_markdown_fences(self):
        with self.assertRaisesRegex(LocalModelError, "INVALID_JSON"):
            parse_json_object('```json\n{"decision":"STOP"}\n```')

    def test_json_parser_requires_an_object(self):
        with self.assertRaisesRegex(LocalModelError, "INVALID_RESPONSE_CONTRACT"):
            parse_json_object("[]")

    def test_server_command_is_cpu_only_and_loopback(self):
        server = LlamaServer(
            binary=Path("/tmp/llama-server"),
            model=Path("/tmp/model.gguf"),
            port=32900,
            protocol=self.protocol,
            log_path=Path("/tmp/server.log"),
        )
        command = server.command()
        self.assertEqual("127.0.0.1", command[command.index("--host") + 1])
        self.assertEqual("0", command[command.index("--gpu-layers") + 1])
        self.assertEqual("4", command[command.index("--threads") + 1])
        self.assertEqual("2048", command[command.index("--ctx-size") + 1])
        self.assertEqual("0", command[command.index("--reasoning-budget") + 1])


if __name__ == "__main__":
    unittest.main()
