import uuid
from .model import Session
from datetime import datetime, timedelta
from src.redis_untils.service import getRedisclient
from src.__utils.env import env
from fastapi import Request
import ipaddress
from hashlib import sha256
import logging
import random
from fastapi import HTTPException
import json


def createSessionId():
    session_id = str(uuid.uuid4())
    return session_id


def get_subnet(ip: str, mask: int = 24) -> str:
    net = ipaddress.ip_network(f"{ip}/{mask}", strict=False)
    return str(net.network_address)


def ua_hash(ua: str) -> str:
    return sha256(ua.encode()).hexdigest()


async def insertNewSession(user_id: str, session_id: str, fastapi_request: Request):
    ua = fastapi_request.headers.get("user-agent", "")
    ip = fastapi_request.client.host
    subnet = get_subnet(ip)
    fp = fastapi_request.headers.get("x-device-fp", "")

    now = datetime.utcnow()

    session = Session(
        pk=session_id,
        user_id=user_id,
        ua_hash=ua_hash(ua),
        subnet=subnet,
        device_fp_hash=fp,
        last_request_time=now,
        expires_at=now + timedelta(seconds=env.session_expire_seconds),
    )
    data = session.save()
    result = data.expire(num_seconds=env.session_expire_seconds)


def random_http_error():
    status = random.choice([404, 500])
    raise HTTPException(status_code=status, detail="Unexpected error occurred.")


async def validate_session_guard(session_id: str, fastapi_request: Request):
    redis = getRedisclient()

    session: Session = Session.get(session_id)
    if not session:
        raise random_http_error()

    current_ua = fastapi_request.headers.get("user-agent", "")
    current_ip = fastapi_request.client.host
    current_subnet = get_subnet(current_ip)
    current_time = datetime.utcnow()

    if ua_hash(current_ua) != session.ua_hash:
        raise random_http_error()

    if current_subnet != session.subnet:
        raise random_http_error()
    last_time = session.last_request_time

    if (current_time - last_time).total_seconds() < 1:
        raise random_http_error()

    session.last_request_time = current_time.isoformat()
    session.save()
