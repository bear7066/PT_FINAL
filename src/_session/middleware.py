import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import src.redis_untils.service as redis_service

from hashlib import sha256
import ipaddress

# ------------ Utilities from your scoring system ------------
def ua_hash(ua: str) -> str:
    return sha256(ua.encode()).hexdigest()

def get_subnet(ip: str, mask: int = 24) -> str:
    net = ipaddress.ip_network(f"{ip}/{mask}", strict=False)
    return str(net.network_address)

BASE_RULES = {
    "UA_MISMATCH": 40,
    "IP_CHANGE": 30,
    "NEW_DEVICE_FP": 40,
    "HI_FREQ": 20,
    "SESSION_EXPIRE": 10,
    "UNKNOWN_SUBNET": 10
}

def score_request(session: dict, request: dict) -> int:
    risk = 0

    if ua_hash(request["ua"]) != session.get("ua_hash"):
        risk += BASE_RULES["UA_MISMATCH"]

    subnet_val = get_subnet(request["ip"])
    if subnet_val != session.get("subnet"):
        risk += BASE_RULES["IP_CHANGE"]
        if subnet_val not in request.get("known_subnets", []):
            risk += BASE_RULES["UNKNOWN_SUBNET"]

    if request.get("fp") and request["fp"] != session.get("device_fp_hash"):
        risk += BASE_RULES["NEW_DEVICE_FP"]

    delta = time.time() - float(session.get("last_request_time", 0))
    if delta < 0.35:
        risk += BASE_RULES["HI_FREQ"]

    if time.time() > float(session.get("expire_time", 0)):
        risk += BASE_RULES["SESSION_EXPIRE"]

    return risk

# ------------ Middleware ------------
class SessionGuard(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        sid = request.cookies.get("session_id")
        if not sid:
            return await call_next(request)

        try:
            logging.debug(f"[SessionGuard] Checking session {sid} from IP {request.client.host}")

            session_data = await redis_service.redis.hgetall(sid)
            if not session_data:
                return Response(status_code=401, content="Invalid session")

            request_info = {
                "ua": request.headers.get("user-agent", ""),
                "ip": request.client.host,
                "fp": request.headers.get("x-device-fp", None),
                "known_subnets": session_data.get("known_subnets", "").split(",")
            }

            risk = score_request(session_data, request_info)
            
            if risk >= 60:
                logging.warning(f"Session risk too high: {risk}, forcing logout.")
                return Response(status_code=403, content="Session risk too high")

            # 更新最後請求時間
            await redis_service.redis.hset(sid, mapping={"last_request_time": str(time.time())})

        except Exception as e:
            logging.exception("SessionGuard error")
            return Response(status_code=500, content="Session validation error")

        return await call_next(request)
