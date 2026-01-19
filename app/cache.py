import json
import redis
from typing import Optional, Any
from app.config import settings

redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True,
    socket_connect_timeout=5
)


def get_redis() -> redis.Redis:
    return redis_client


def cache_key(prefix: str, *args, **kwargs) -> str:
    key_parts = [prefix]
    if args:
        key_parts.extend(str(arg) for arg in args)
    if kwargs:
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return ":".join(key_parts)


def get_cache(key: str) -> Optional[Any]:
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
    except (redis.RedisError, json.JSONDecodeError):
        pass
    return None


def set_cache(key: str, value: Any, ttl: int = 60) -> bool:
    try:
        redis_client.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )
        return True
    except (redis.RedisError, TypeError):
        return False


def delete_cache(key: str) -> bool:
    try:
        redis_client.delete(key)
        return True
    except redis.RedisError:
        return False


def invalidate_pattern(pattern: str) -> int:
    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
        return 0
    except redis.RedisError:
        return 0
