from __future__ import annotations

from collections import defaultdict, deque
from typing import Any


class DeterministicRelevanceResolver:
    def __init__(self, graph: dict[str, Any]):
        self.graph = graph

        self.forward = defaultdict(set)
        self.reverse = defaultdict(set)

        for edge in graph.get("edges", []):
            source = edge["from"]
            target = edge["to"]
            self.forward[source].add(target)
            self.reverse[target].add(source)

    @staticmethod
    def _walk(start: str, adjacency) -> list[str]:
        visited = set()
        queue = deque(adjacency.get(start, set()))

        while queue:
            node = queue.popleft()

            if node in visited:
                continue

            visited.add(node)

            for nxt in adjacency.get(node, set()):
                if nxt not in visited:
                    queue.append(nxt)

        return sorted(visited)

    def resolve(self, node_id: str) -> dict[str, Any]:
        return {
            "node_id": node_id,
            "retrospective_relevance": self._walk(node_id, self.reverse),
            "prospective_relevance": self._walk(node_id, self.forward),
            "alteration_authorized": False,
        }
