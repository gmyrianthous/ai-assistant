import json
from collections.abc import AsyncGenerator
from collections.abc import Hashable
from contextlib import asynccontextmanager
from typing import Any
from urllib.parse import parse_qsl
from urllib.parse import urlencode
from urllib.parse import urlparse

from pydantic import pydantic_encoder
from pydantic_settings import PostgresDsn
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from ai_assistant.common.settings import settings

DbEngineKey = tuple[str, frozenset[tuple[str, Hashable]]]

_db_engines: dict[DbEngineKey, AsyncEngine] = {}


def _get_cache_key_from_uri(uri: str, /, **kwargs: Hashable) -> DbEngineKey:
    """
    Get a cache key from a uri. Used to cache the engine.

    Args:
        uri (str): The uri to get the cache key from.
        kwargs (Hashable): The keyword arguments to get the cache key from.

    Returns:
        (DbEngineKey): The cache key.
    """
    uri_parsed = urlparse(uri)

    query_params = parse_qsl(uri_parsed.query)
    query_params = sorted(query_params)

    query = urlencode(query_params)

    uri_parsed = uri_parsed._replace(query=query)

    uri = uri_parsed.geturl()

    # we convert the dictionary into a set of tuples so it can be hashbable
    kwargs_set = frozenset((k, v) for k, v in kwargs.items())

    return (uri, kwargs_set)


def _pydantic_json_serializer(*args: Any, **kwargs: Any) -> str:
    """
    Encodes json in the same way that pydantic does.

    Args:
        args (Any): The arguments to encode.
        kwargs (Any): The keyword arguments to encode.

    Returns:
        (str): The encoded json.
    """
    return json.dumps(*args, default=pydantic_encoder, **kwargs)


def get_or_create_engine(
    url: PostgresDsn = settings.DATABASE_URL,
    echo: bool = False,
) -> AsyncEngine:
    """
    Get or create an async engine.

    Args:
        url (PostgresDsn): The url of the database.
        echo (bool): Whether to echo the sql statements.

    Returns:
        (AsyncEngine): The async engine.
    """
    key = _get_cache_key_from_uri(str(url), echo=echo)
    if key not in _db_engines:
        options = {
            'echo': echo,
            'future': True,
            'poolclass': NullPool,
            'json_serializer': _pydantic_json_serializer,
        }

        engine = create_async_engine(str(url), **options)
        _db_engines[key] = engine

    return _db_engines[key]


def get_session(url: PostgresDsn = settings.DATABASE_URL, echo: bool = False) -> AsyncSession:
    """
    Get a session.

    Args:
        url (PostgresDsn): The url of the database.
        echo (bool): Whether to echo the sql statements.

    Returns:
        (AsyncSession): The async session.
    """
    engine = get_or_create_engine(url, echo)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=True)
    return async_session()


@asynccontextmanager
async def db_session(
    url: PostgresDsn = settings.DATABASE_URL,
    echo: bool = False,
    autocommit: bool = True,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get a session context manager.

    Args:
        url (PostgresDsn): The url of the database.
        echo (bool): Whether to echo the sql statements.
        autocommit (bool): Whether to autocommit the session.

    Returns:
        (AsyncSession): The async session.
    """
    session = get_session(url, echo)
    try:
        yield session
        if autocommit:
            await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()
