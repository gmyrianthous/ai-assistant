from abc import ABC
from abc import abstractmethod
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ai_assistant.models.base import BaseModel


class AbstractRepository(ABC):
    model: type[BaseModel]

    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def get_by_id(self, id_: UUID, /) -> Any:
        raise NotImplementedError()
