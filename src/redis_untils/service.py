from redis_om import get_redis_connection, Migrator
import logging
from src.__utils.env import env
from src._user.service import ensureSuperAdmin

async def initRedis():
    get_redis_connection()
    Migrator().run()
    logging.info("connecting to redis")
    await ensureSuperAdmin()
    
def getRedisclient():
    return get_redis_connection()