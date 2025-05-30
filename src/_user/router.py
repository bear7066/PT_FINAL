from fastapi import HTTPException, APIRouter, Response, Request
from .service import *
from src._session.service import *
from .schemas import userReq, userRes
import time
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


@router.post("/login", response_model=userRes)
async def login_user(request: userReq, response: Response, fastapi_request: Request):
    user = getUserByMail(request.usermail)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verifyPassword(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    session_id = createSessionId()
    await insertNewSession(
        user_id=user.pk, session_id=session_id, fastapi_request=fastapi_request
    )

    response.set_cookie(key="session_id", value=session_id, httponly=True)

    return userRes(status=userRes.Status.SUCCESS, message="Login successful")


@router.get("/mfa")
async def test_mfa(fastapi_request: Request):
    session_id = fastapi_request.cookies.get("session_id")
    await validate_session_guard(session_id=session_id, fastapi_request=fastapi_request)
    return {"msg": "you passed session guard"}
