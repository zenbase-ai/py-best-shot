from dataclasses import dataclass
from typing import overload

from best_shot.types import Shot, data_key, Datum, IO, ShotWithSimilarity, is_io_value

from .embed.base import AsyncEmbedder
from .store.base import AsyncStore


@dataclass
class AsyncBestShots:
    embed: AsyncEmbedder
    store: AsyncStore

    @overload
    async def add(
        self,
        inputs: IO,
        outputs: IO,
        *,
        id: str = "",
        namespace: str = "default",
    ) -> str: ...

    @overload
    async def add(
        self,
        data: list[Datum],
        *,
        namespace: str = "default",
    ) -> list[str]: ...

    async def add(
        self,
        maybe_inputs: IO | list[Datum],
        maybe_outputs: IO | None = None,
        *,
        id: str = "",
        namespace: str = "default",
    ) -> str | list[str]:
        is_io = is_io_value(maybe_inputs) and is_io_value(maybe_outputs)
        data: list[Datum] = (
            [(maybe_inputs, maybe_outputs, id)] if is_io else maybe_inputs
        )
        shots = [Shot(*datum) for datum in data]
        embeddings = await self.embed([shot.key for shot in shots])
        await self.store.add(shots, embeddings, namespace)

        ids = [shot.id for shot in shots]
        return ids[0] if is_io else ids

    @overload
    async def remove(self, id: str, *, namespace: str = "default"): ...

    @overload
    async def remove(self, ids: list[str], *, namespace: str = "default"): ...

    @overload
    async def remove(
        self,
        inputs: IO,
        outputs: IO | None = None,
        *,
        id: str = "",
        namespace: str = "default",
    ): ...

    @overload
    async def remove(self, data: list[Datum], namespace: str = "default"): ...

    async def remove(
        self,
        maybe_inputs: IO | list[Datum],
        maybe_outputs: IO | None = None,
        *,
        id: str = "",
        namespace: str = "default",
    ):
        is_io = is_io_value(maybe_inputs) and is_io_value(maybe_outputs)
        data: list[Datum] = (
            [(maybe_inputs, maybe_outputs, id)] if is_io else maybe_inputs
        )
        match data:
            case str() as id:
                await self.remove([id], namespace)
            case tuple() as datum:
                await self.remove([Shot(*datum).id], namespace)
            case list():
                is_ids = isinstance(data[0], str)
                ids = data if is_ids else [Shot(*datum).id for datum in data]
                await self.store.remove(ids, namespace)
            case _:
                raise ValueError(f"Invalid data type: {type(data)}")

    async def clear(self, namespace: str = "default"):
        await self.store.clear(namespace)

    async def list(
        self,
        inputs: IO,
        *,
        namespace: str = "default",
        limit: int = 5,
    ) -> list[ShotWithSimilarity]:
        embedding = await self.embed([data_key(inputs)])
        return await self.store.list(embedding[0], namespace, limit)
