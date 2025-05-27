from fastapi import HTTPException, APIRouter, Response, Request
from .service import *
from src._session.service import *
from .schemas import userReq, userRes
import time
from hashlib import sha256
import ipaddress
import src.redis_untils.service as redis_service

router = APIRouter(prefix="/api/user", tags=["User Management"])


@router.post("/register", response_model=userRes)
async def register_user(request: userReq):
    if await isExisted(request.usermail):
        raise HTTPException(status_code=400, detail="Usermail already exists.")

    hashed = hashPassword(request.password)
    await insertNewUser(userReq=request, password=hashed)
    return userRes(
        status=userRes.Status.SUCCESS, message="User registered successfully"
    )


def ua_hash(ua: str) -> str:
    return sha256(ua.encode()).hexdigest()

def get_subnet(ip: str, mask: int = 24) -> str:
    net = ipaddress.ip_network(f"{ip}/{mask}", strict=False)
    return str(net.network_address)


@router.post("/login", response_model=userRes)
async def login_user(request: userReq, response: Response, fastapi_request: Request):
    user = getUserByMail(request.usermail)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verifyPassword(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    session_id = createSessionId()

    # 準備 session 資料
    ua = fastapi_request.headers.get("user-agent", "")
    ip = fastapi_request.client.host
    subnet = get_subnet(ip)
    fp = fastapi_request.headers.get("x-device-fp", "")

    session_data = {
        "user_id": str(user.pk),
        "ua_hash": ua_hash(ua),
        "subnet": subnet,
        "device_fp_hash": fp,
        "known_subnets": subnet,
        "last_request_time": str(time.time()),
        "expire_time": str(time.time() + 3600),  # 1 小時有效
    }

    # 寫入 Redis
    await redis_service.redis.hset(session_id, mapping=session_data)

    # 設置 cookie
    response.set_cookie(key="session_id", value=session_id, httponly=True)

    return userRes(status=userRes.Status.SUCCESS, message="Login successful")


@router.get("/test/mfa")
async def test_mfa():
    return {"msg": "you passed session guard"}
