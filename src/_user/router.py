from fastapi import HTTPException, APIRouter, Response
from .service import *
from src._session.service import *
from .schemas import userReq, userRes


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


session_store = {}

@router.post("/login", response_model=userRes)
async def login_user(request: userReq, response: Response):
    user = getUserByMail(request.usermail)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verifyPassword(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    session_id = createSessionId()
    

    response.set_cookie(key="session_id", value=session_id, httponly=True)

    return userRes(status=userRes.Status.SUCCESS, message="Login successful")
