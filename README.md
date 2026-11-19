DESCRIPTION
    Lightweight static analysis tool for finding sensetive data leaks.
    Written in Python with minimal dependencies and regex-based detection.

FEATURES
    - Scans directories recursively for hardcoded secrets, API keys, and tokens
    - Colored console output and option to export report to file
    - Configurable regex patterns via rules.yaml
    - Respects .gitignore rules

INSTALL
    pip install leakfinder-cli

REQUIREMENTS
    - Python 3.11
    - Python libraries:
        - pyyaml
        - pathspec
    - POSIX environment

USAGE
    leakfinder ./my-project
    leakfinder ./my-project --rules ./custom-rules.yaml
    leakfinder ./my-project --output report-file.txt
