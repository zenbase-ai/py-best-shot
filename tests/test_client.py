import pytest
from sentence_transformers import SentenceTransformer

from best_shot.client import BestShots
from best_shot.embed.transformers import TransformersEmbedder
from best_shot.store.memory import MemoryStore
from best_shot.types import Shot


@pytest.fixture(scope="function")
def client():
    return BestShots(
        embedder=TransformersEmbedder(model=SentenceTransformer("all-MiniLM-L6-v2")),
        store=MemoryStore(),
    )


def test_functional_flow(client: BestShots):
    inputs = {"a": 1}
    outputs = {"b": 2}

    id = client.add(inputs, outputs)
    assert id == Shot(inputs, outputs).id

    results = client.list(inputs, limit=1)
    results = [shot for shot, _ in results]
    assert results == [Shot(inputs, outputs)]

    results = client.list(inputs, limit=5)
    results = [shot for shot, _ in results]
    assert results == [Shot(inputs, outputs)]

    client.remove((inputs, outputs))
    assert [] == client.list(inputs, limit=1)

    client.add(inputs, outputs)
    client.clear(namespace="default")
    assert [] == client.list(inputs)


def test_messages_flow(client: BestShots):
    inputs = "User question..."
    outputs = "AI answer..."

    id = client.add(inputs, outputs)
    assert id == Shot(inputs, outputs).id

    results = client.list(inputs, limit=1)
    results = [shot for shot, _ in results]
    assert results == [Shot(inputs, outputs)]

    results = client.list(inputs, limit=5)
    results = [shot for shot, _ in results]
    assert results == [Shot(inputs, outputs)]

    client.remove(inputs, outputs)
    assert [] == client.list(inputs, limit=1)

    client.add(inputs, outputs)
    client.clear(namespace="default")
    assert [] == client.list(inputs)
