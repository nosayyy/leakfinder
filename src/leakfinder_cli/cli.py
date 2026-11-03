
from __future__ import annotations

import argparse
import sys
from importlib.resources import files
from pathlib import Path

from .report import Reporter
from .rules import RuleSet
from .scanner import Scanner

default_rules = files("leakfinder_cli") / "data" / "rules.yaml"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="leakfinder_cli",
        description="Find secrets in source code.",
    )
    parser.add_argument("path", help="Directory to scan")
    parser.add_argument(
        "--rules",
        default=str(default_rules),
        help="Path to rules.yaml (default: built-in rules)",
    )
    parser.add_argument(
        "--output",
        help="Path to report file (default: stdout)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    root = Path(args.path)
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 2

    ruleset = RuleSet.from_yaml(args.rules)
    scanner = Scanner(ruleset)
    findings = scanner.scan(root)

    reporter = Reporter(findings)
    if args.output:
        reporter.print_to_file(args.output)
    else:
        reporter.print()

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())