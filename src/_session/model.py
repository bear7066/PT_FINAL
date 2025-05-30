from redis_om import JsonModel
from typing import Optional
from datetime import datetime


class Session(JsonModel):
    pk: str
    user_id: str
    ua_hash: Optional[str]
    subnet: Optional[str]
    device_fp_hash: Optional[str]
    last_request_time: Optional[datetime]
    expires_at: Optional[datetime]
