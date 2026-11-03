
from __future__ import annotations

from .scanner import Finding

class Reporter:
    def __init__(self, findings: list[Finding],
        severity_order: tuple[str, ...] = ('critical', 'high', 'medium', 'low'),
        colors: dict[str, str] = {
            'critical': '\033[95m',
            'high':     '\033[91m',
            'medium':   '\033[93m',
            'low':      '\033[94m',
        },
        reset: str = '\033[0m',
    ) -> None:
        self.findings: list[Finding] = findings
        self.severity_order: tuple[str, ...] = severity_order
        self.colors: dict[str, str] = colors
        self.reset: str = reset

    def print(self) -> None:
        if not self.findings:
            print('No secrets found.')
            return

        for finding in self.sorted_findings():
            self.print_finding(finding)

        self.print_total()

    def print_to_file(self, file):
        with open(file, 'w', encoding='utf-8') as file:
            if not self.findings:
                file.write('No secrets found.')
                return

            for finding in self.sorted_findings():
                file.write(str(self.print_finding(finding)))

            file.write(str(self.print_total()))

    def sorted_findings(self) -> list[Finding]:
        def sort_key(finding: Finding) -> tuple[int, str, int]:
            severity = finding.rule.severity
            if severity in self.severity_order:
                rank = self.severity_order.index(severity)
            else:
                rank = len(self.severity_order)

            return (rank, finding.path, finding.line)

        return sorted(self.findings, key=sort_key)

    def print_finding(self, finding: Finding) -> None:
        severity = finding.rule.severity
        color = self.colors.get(severity, '')
        label = severity.upper()

        header = f'{color}[{label}]{self.reset} {finding.path}:{finding.line}'
        print(header)
        print(f'  {finding.rule.description}')
        print(f'  {self.mask(finding.match)}')
        print()

    def print_total(self) -> None:
        print(f'Total: {len(self.findings)} finding(s)')

    @staticmethod
    def mask(text: str) -> str:
        text = text.strip()

        if len(text) > 80:
            text = text[:80] + '...'

        if len(text) <= 8:
            return '*' * len(text)

        middle = '*' * (len(text) - 8)
        return text[:4] + middle + text[-4:]