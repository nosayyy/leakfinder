import unittest
from pathlib import Path
import tempfile
import yaml
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from leakfinder_cli.rules import Rule, RuleSet

class TestRule(unittest.TestCase):
	def setUp(self):
		self.rule = Rule(id="test-secret",
				 description="Test secret",
				 regex=r"SECRET",
				 severity="high",
				)

	def test_match_found(self):
		line = "const apiKey = 'SECRET';"
		match = self.rule.match(line)
		self.assertIsNotNone(match)
		self.assertEqual(match.group(0), "SECRET")

	def test_match_not_found(self):
		line = "const apiKey = 'public';"
		self.assertIsNone(self.rule.match(line))

class TestRuleSet(unittest.TestCase):
	def test_from_yaml(self):
		yaml_content = """
rules:
  - id: aws-access-key
    description: AWS Access Key ID
    regex: 'AKIA[0-9A-Z]{16}'
    severity: high

  - id: github-token
    description: GitHub Personal Access Token
    regex: 'ghp_[A-Za-z0-9]{36}'
    severity: high
"""
		with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
			f.write(yaml_content)
			temp_path = Path(f.name)

		try:
			ruleset = RuleSet.from_yaml(temp_path)
			rules = list(ruleset)
			
			self.assertEqual(len(rules), 2)
			self.assertEqual(rules[0].id, "aws-access-key")
			self.assertEqual(rules[1].id, "github-token")

			self.assertIsNotNone(rules[0].pattern)

		finally:
			temp_path.unlink(missing_ok=True)

if __name__ == "__main__":
	unittest.main()


