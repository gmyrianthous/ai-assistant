from abc import ABC
from abc import abstractmethod
from typing import Any
from uuid import UUID

from ai_assistant.models.base import BaseModel


class AbstractRepository(ABC):
    model: type[BaseModel]

    @abstractmethod
    async def get_by_id(self, id_: UUID, /) -> Any:
        raise NotImplementedError()
