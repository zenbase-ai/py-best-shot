from collections import defaultdict
from operator import itemgetter

import numpy as np

from few_shots.utils.asyncio import asyncify_class

from .base import Vector, Shot, ShotWithSimilarity, Store


def cosine_similarity(a: Vector, b: Vector) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


class MemoryStore(Store):
    # namespace => id => (shot, vector)
    _storage: dict[str, dict[str, tuple[Shot, Vector]]]

    def __init__(self):
        self._storage = defaultdict(dict)

    def add(self, shots: list[Shot], vectors: list[Vector], namespace: str):
        for shot, vector in zip(shots, vectors):
            self._storage[namespace][shot.id] = (shot, vector)

    def remove(self, ids: list[str], namespace: str):
        for id in ids:
            del self._storage[namespace][id]

    def clear(self, namespace: str):
        self._storage[namespace].clear()

    def list(
        self,
        vector: Vector,
        namespace: str,
        limit: int,
    ) -> list[ShotWithSimilarity]:
        shots_with_similarities = [
            (shot, 1 - cosine_similarity(vector, emb))
            for (shot, emb) in self._storage[namespace].values()
        ]
        return sorted(shots_with_similarities, key=itemgetter(1), reverse=True)[:limit]


@asyncify_class
class AsyncMemoryStore(MemoryStore): ...
