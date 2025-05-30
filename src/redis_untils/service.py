from redis_om import get_redis_connection, Migrator
import logging
from src._user.service import ensureSuperAdmin
import redis.asyncio as redis_lib

import redis.asyncio as redis_lib

redis = None

async def initRedis():
    global redis
    redis = redis_lib.Redis(host="localhost", port=6379, decode_responses=True)
    await redis.ping()
    
def getRedisclient():
    return get_redis_connection()