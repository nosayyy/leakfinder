
from __future__ import annotations

import re
from pathlib import Path

from .rules import Rule, RuleSet
from .walker import Walker


class Finding:
    def __init__(self, path: str, line: int, rule: Rule, match: str) -> None:
        self.path: str = path
        self.line: int = line
        self.rule: Rule = rule
        self.match: str = match


class Scanner:
    def __init__(self, ruleset: RuleSet) -> None:
        self.ruleset: RuleSet = ruleset

    def scan(self, root: str | Path) -> list[Finding]:
        walker = Walker(root)
        findings: list[Finding] = []

        for path in walker.walk():
            findings.extend(self._scan_file(path))

        return findings

    def _scan_file(self, path: str) -> list[Finding]:
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except OSError:
            return []
        if not text:
            return []

        results = []
        for rule in self.ruleset:
            rx = re.compile(rule.pattern.pattern, rule.pattern.flags | re.MULTILINE)
            seen = set()
            for m in rx.finditer(text):
                lineno = text.count("\n", 0, m.start()) + 1
                if lineno in seen:
                    continue
                seen.add(lineno)
                results.append(Finding(path, lineno, rule, m.group(0)))
        return results