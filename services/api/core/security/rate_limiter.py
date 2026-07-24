import time
import logging
from fastapi import Request, HTTPException, status
import redis.asyncio as redis
from core.config import settings

logger = logging.getLogger(__name__)


class SlidingWindowRateLimiter:
    """
    Redis sliding window rate limiter enforcing per-user/IP request limits
    and workspace execution quotas using isolated Redis key namespaces (`phantom:rate_limit:`).
    """

    @classmethod
    async def check_rate_limit(
        cls,
        redis_client: redis.Redis,
        key_identifier: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> bool:
        if not redis_client:
            return True  # Fallback if Redis is unavailable in local dev

        now = time.time()
        clear_before = now - window_seconds
        redis_key = f"phantom:rate_limit:{key_identifier}"

        try:
            pipe = redis_client.pipeline()
            pipe.zremrangebyscore(redis_key, 0, clear_before)
            pipe.zcard(redis_key)
            pipe.zadd(redis_key, {str(now): now})
            pipe.expire(redis_key, window_seconds)
            results = await pipe.execute()

            request_count = results[1]
            if request_count >= max_requests:
                logger.warning(f"[RateLimiter] Rate limit exceeded for {key_identifier}: {request_count}/{max_requests}")
                return False
            return True
        except Exception as e:
            logger.warning(f"[RateLimiter] Redis error in rate limiter: {e}")
            return True
