from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class RegistryError(RuntimeError):
    pass


def load_json(path: Path) -> Any:
    if not path.exists():
        raise RegistryError(f"registry not found: {path}")

    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise RegistryError(f"invalid JSON registry {path}: {exc}") from exc


class RepositoryRegistries:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    @property
    def anchors(self):
        return load_json(
            self.repo_root
            / "01-constitutional-source-map"
            / "source-integrity"
            / "anchors"
            / "CONSTITUTIONAL_SOURCE_ANCHORS.json"
        )

    @property
    def graph(self):
        return load_json(
            self.repo_root
            / "03-constitutional-dependency-graph"
            / "executable"
            / "EXECUTABLE_DEPENDENCY_GRAPH.json"
        )

    @property
    def jurisdiction(self):
        return load_json(
            self.repo_root
            / "08-jurisdiction-and-evidence"
            / "resolver"
            / "JURISDICTION_RULES.json"
        )

    @property
    def authority(self):
        return load_json(
            self.repo_root
            / "09-uaa-bridge"
            / "elections"
            / "resolver"
            / "UAA_AUTHORITY_RULES.json"
        )

    @property
    def consequence(self):
        return load_json(
            self.repo_root
            / "07-constitutional-state-integrity"
            / "resolver"
            / "CONSEQUENCE_GATE_CONTRACT.json"
        )
