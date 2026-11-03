
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

import pathspec


class Walker:
    def __init__(self, root: str | Path,
        skip_dirs: tuple[str, ...] = (
            '.git', 'node_modules', 'venv', '.venv', '__pycache__',
            'dist', 'build', '.idea', '.vscode',
        ),
        skip_exts: tuple[str, ...] = (
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg',
            '.pdf', '.zip', '.tar', '.gz', '.rar',
            '.exe', '.dll', '.so', '.dylib', '.bin', '.pyc', '.class', '.jar',
            '.mp3', '.mp4', '.mov', '.avi',
        ),
        max_size: int = 5 * 1024 * 1024,
    ) -> None:
        self.root: str = str(root)
        self.skip_dirs: set[str] = set(skip_dirs)
        self.skip_exts: set[str] = set(skip_exts)
        self.max_size: int = max_size

        # читаем .gitignore из корня проекта (если он есть)
        self.spec = self._read_gitignore()

    def _read_gitignore(self):
        gi_path = os.path.join(self.root, '.gitignore')
        if not os.path.isfile(gi_path):
            return None

        with open(gi_path, encoding='utf-8', errors='ignore') as f:
            return pathspec.PathSpec.from_lines('gitwildmatch', f)

    def walk(self) -> Iterator[str]:
        for dirpath, dirnames, filenames in os.walk(self.root):
            # обрезаем dirnames -> os.walk не будет заходить в эти папки
            dirnames[:] = [
                d for d in dirnames
                if d not in self.skip_dirs
                and not self._is_ignored(os.path.join(dirpath, d), is_dir=True)
            ]

            for name in filenames:
                path = os.path.join(dirpath, name)
                if self.should_scan(path, name):
                    yield path

    def _is_ignored(self, path: str, is_dir: bool = False) -> bool:
        """True, если путь совпал с правилом из .gitignore."""
        if self.spec is None:
            return False

        # путь относительно корня, в git-стиле (через /)
        rel = os.path.relpath(path, self.root).replace(os.sep, '/')
        if is_dir:
            rel += '/'   # чтобы паттерны вида "build/" матчили папки

        # check_file возвращает (include, index):
        #   include is False  -> путь игнорируется
        #   include is True   -> сработала !-негация
        #   include is None   -> ни одно правило не подошло
        include, _ = self.spec.check_file(rel)
        return include is False

    def should_scan(self, path: str, name: str) -> bool:
        ext = os.path.splitext(name)[1].lower()
        if ext in self.skip_exts:
            return False

        try:
            size = os.path.getsize(path)
        except OSError:
            return False
        if size > self.max_size:
            return False

        if self._is_ignored(path):
            return False

        return True