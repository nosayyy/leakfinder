
from __future__ import annotations

import re
import yaml
from pathlib import Path
from typing import Iterator

class Rule:
    def __init__(self, id: str, description: str, regex: str, severity: str) -> None:
        self.id: str = id
        self.description: str = description
        self.pattern: re.Pattern[str] = re.compile(regex)
        self.severity: str = severity

    def match(self, line: str) -> re.Match[str] | None:
        return self.pattern.search(line)


class RuleSet:
    def __init__(self, rules: list[Rule]) -> None:
        self.rules: list[Rule] = rules

    @classmethod
    def from_yaml(cls, path: str | Path) -> RuleSet:
        with open(path, encoding='utf-8') as f:
            data = yaml.safe_load(f)

        rules = []
        for item in data['rules']:
            rule = Rule(
                id=item['id'],
                description=item['description'],
                regex=item['regex'],
                severity=item['severity'],
            )
            rules.append(rule)

        return cls(rules)

    def __iter__(self) -> Iterator[Rule]:
        return iter(self.rules)