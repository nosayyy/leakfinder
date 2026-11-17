import unittest
import tempfile
from pathlib import Path

from leakfinder_cli.rules import Rule, RuleSet
from leakfinder_cli.scanner import Scanner


class TestScanner(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        rule = Rule(
            id="test-secret",
            description="Test secret",
            regex=r"SECRET",
            severity="high",
        )
        self.ruleset = RuleSet([rule])
        self.scanner = Scanner(self.ruleset)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_scan_finds_secret(self):
        test_file = self.root / "app.py"
        test_file.write_text(
            "api_key = 'SECRET'\nprint(api_key)\n", encoding="utf-8"
        )

        findings = self.scanner.scan(self.root)

        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.path, str(test_file))
        self.assertEqual(finding.line, 1)  # секрет в первой строке
        self.assertEqual(finding.rule.id, "test-secret")
        self.assertEqual(finding.match, "SECRET")

    def test_scan_no_secret(self):
        clean_file = self.root / "clean.py"
        clean_file.write_text("print('hello')\n", encoding="utf-8")

        findings = self.scanner.scan(self.root)
        self.assertEqual(findings, [])

    def test_scan_empty_file(self):
        empty_file = self.root / "empty.txt"
        empty_file.write_text("", encoding="utf-8")

        findings = self.scanner.scan(self.root)
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
