from fastapi import HTTPException, Request, WebSocket

from config import settings
from distributed.cache import get_redis_client


async def consume_rate_limit(bucket: str, limit: int, window_seconds: int) -> dict:
    client = await get_redis_client()
    key = f"rate_limit:{bucket}"
    count = await client.incr(key)
    if count == 1:
        await client.expire(key, window_seconds)

    ttl = await client.ttl(key)
    remaining = max(limit - count, 0)

    return {
        "allowed": count <= limit,
        "count": count,
        "remaining": remaining,
        "retry_after": max(ttl, 0),
    }


async def enforce_http_rate_limit(
    request: Request,
    scope: str,
    identity: str,
    limit: int = settings.rate_limit_requests,
    window_seconds: int = settings.rate_limit_window_seconds,
) -> None:
    result = await consume_rate_limit(f"http:{scope}:{identity}", limit, window_seconds)
    if not result["allowed"]:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Retry in {result['retry_after']} seconds.",
        )


async def enforce_websocket_rate_limit(
    websocket: WebSocket,
    scope: str,
    identity: str,
    limit: int = settings.rate_limit_requests,
    window_seconds: int = settings.rate_limit_window_seconds,
) -> None:
    result = await consume_rate_limit(f"ws:{scope}:{identity}", limit, window_seconds)
    if not result["allowed"]:
        await websocket.close(code=4408, reason="Rate limit exceeded")
        raise RuntimeError("WebSocket rate limit exceeded")
