from redis_om import HashModel, get_redis_connection
from datetime import datetime, timedelta

class Data(HashModel):
    status: str
    message: str
    timestamp: datetime
