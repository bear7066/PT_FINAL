import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import src.redis_untils.service as redis_service
from src._session.model import Session
from redis_om.model.model import NotFoundError

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
    "UNKNOWN_SUBNET": 10,
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


ALLOWED_PATHS = [
    "/api/user/login",
    "/api/user/register",
]


# ------------ Middleware ------------
class SessionGuard(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 讓 register, login 通過
        if request.url.path in ALLOWED_PATHS:
            return await call_next(request)

        sid = request.cookies.get("session_id")
        if not sid:
            logging.warning("[SessionGuard] Missing session_id cookie.")
            return Response(
                status_code=401,
                content='{"detail":"Missing session_id cookie."}',
                media_type="application/json",
            )

        try:
            logging.debug(
                f"[SessionGuard] Checking session {sid} from IP {request.client.host}"
            )
            try:
                session: Session = Session.get(sid)
            except NotFoundError:
                logging.warning("[SessionGuard] Session not found.")
                return Response(status_code=401, content="Invalid session")

            # session_data = session.dict()

            # request_info = {
            #     "ua": request.headers.get("user-agent", ""),
            #     "ip": request.client.host,
            #     "fp": request.headers.get("x-device-fp", None),
            #     "known_subnets": (
            #         session_data.get("known_subnets", "").split(",")
            #         if session_data.get("known_subnets")
            #         else []
            #     ),
            # }

            # risk = score_request(session_data, request_info)

            # if risk >= 60:
            #     logging.warning(
            #         f"[SessionGuard] Session risk too high: {risk}, forcing logout."
            #     )
            #     return Response(status_code=403, content="Session risk too high")

            # session.last_request_time = time.strftime(
            #     "%Y-%m-%dT%H:%M:%S", time.gmtime()
            # )
            # await session.save()

        except Exception as e:
            logging.exception("SessionGuard error")
            return Response(status_code=500, content="Session validation error")

        return await call_next(request)
