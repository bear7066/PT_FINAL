from redis_om import HashModel, get_redis_connection
from datetime import datetime, timedelta

class Session(HashModel):
    session_id: str
    user_id: str
    expires_at: datetime

