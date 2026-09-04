from __future__ import annotations

import argparse
import json
from pathlib import Path

from .drp import DeterministicRelevanceResolver
from .execution_resolver import ExecutionResolver
from .registry import RepositoryRegistries
from .verifier import verify_source_hashes


def find_repo_root(start: Path) -> Path:
    current = start.resolve()

    while True:
        if (current / ".git").exists():
            return current

        if current.parent == current:
            raise RuntimeError("repository root not found")

        current = current.parent


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="orynth-csi",
        description="ORYNTH Constitutional State Integrity reference verifier",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("verify-sources")

    drp_parser = sub.add_parser("drp")
    drp_parser.add_argument("node_id")

    args = parser.parse_args()

    root = find_repo_root(Path.cwd())
    registries = RepositoryRegistries(root)

    if args.command == "verify-sources":
        result = verify_source_hashes(root)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "drp":
        resolver = DeterministicRelevanceResolver(registries.graph)
        result = resolver.resolve(args.node_id)
        print(json.dumps(result, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
