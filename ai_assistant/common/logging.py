import logging
from typing import Any

from pythonjsonlogger.jsonlogger import JsonFormatter

from ai_assistant.common.settings import settings


class CustomJsonFormatter(JsonFormatter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs['timestamp'] = True
        super().__init__(*args, **kwargs)
    
    def add_fields(
        self, 
        log_record: dict[str, Any], 
        record: logging.LogRecord, 
        message_dict: dict[str, Any]
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record['environment'] = settings.ENVIRONMENT
        log_record['level'] = record.levelname
        log_record['name'] = record.name

class UnivornAccessFilter(logging.Filter):
    """Skip the logging on HTTP requests by Uvicorn"""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.name != 'uvicorn.access'

class CustomStreamHandler(logging.StreamHandler):  # type: ignore[type-arg]
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)
        self.addFilter(UnivornAccessFilter())
