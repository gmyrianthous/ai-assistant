import uuid
from datetime import datetime
from datetime import timezone

from factory import Factory
from factory import LazyFunction

from ai_assistant.models.session import Session as SessionModel


class SessionFactory(Factory):
    class Meta:
        model = SessionModel

    id = LazyFunction(uuid.uuid4)
    user_id = LazyFunction(uuid.uuid4)
    created_at = LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = LazyFunction(lambda: datetime.now(timezone.utc))
    ended_at = None
