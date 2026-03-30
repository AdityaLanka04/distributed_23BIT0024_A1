import redis.asyncio as redis
import asyncio
import json
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Optional

from config import settings

redis_client: Optional[redis.Redis] = None
redis_pubsub: Optional[redis.client.PubSub] = None

LOCK_RELEASE_SCRIPT = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
end
return 0
"""

async def get_redis_client():
    global redis_client
    if redis_client is None:
        redis_client = await redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client

async def init_redis():
    await get_redis_client()

async def get_cache(key: str):
    client = await get_redis_client()
    data = await client.get(key)
    return json.loads(data) if data else None

async def set_cache(key: str, value: Any, expire: int = 3600):
    client = await get_redis_client()
    await client.setex(key, expire, json.dumps(value))

async def delete_cache(key: str):
    client = await get_redis_client()
    await client.delete(key)

async def get_leaderboard(quiz_id: str, limit: int = 10):
    client = await get_redis_client()
    key = f"leaderboard:{quiz_id}"
    return await client.zrevrange(key, 0, limit - 1, withscores=True)

async def update_leaderboard(quiz_id: str, user_id: str, score: float):
    client = await get_redis_client()
    key = f"leaderboard:{quiz_id}"
    await client.zadd(key, {user_id: score})

async def publish_message(channel: str, message: dict):
    client = await get_redis_client()
    await client.publish(channel, json.dumps(message))

async def subscribe_channel(channel: str):
    client = await get_redis_client()
    pubsub = client.pubsub()
    await pubsub.subscribe(channel)
    return pubsub


@asynccontextmanager
async def redis_lock(lock_name: str, timeout: Optional[int] = None, wait_timeout: Optional[int] = None):
    client = await get_redis_client()
    token = str(uuid.uuid4())
    timeout = timeout or settings.room_lock_timeout_seconds
    wait_timeout = wait_timeout or settings.room_lock_wait_seconds
    key = f"lock:{lock_name}"
    deadline = time.monotonic() + wait_timeout

    while True:
        acquired = await client.set(key, token, ex=timeout, nx=True)
        if acquired:
            break
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Timed out waiting for lock {lock_name}")
        await asyncio.sleep(0.05)

    try:
        yield
    finally:
        try:
            await client.eval(LOCK_RELEASE_SCRIPT, 1, key, token)
        except Exception:
            pass
