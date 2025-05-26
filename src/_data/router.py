from fastapi import HTTPException, APIRouter, Response
from .schemas import *
from .models import Data
from src._user.service import isExisted

router = APIRouter(prefix="/api/data", tags=["Data Management"])


@router.post("/search", response_model=dataRes)
async def register_user(request: dataReq):

    if await isExisted(request.usermail):
        raise HTTPException(status_code=400, detail="Usermail already exists.")



# session_store = {}

# @router.post("/login", response_model=userRes)
# async def login_user(request: userReq, response: Response):
#     user = getUserByMail(request.usermail)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     if not verifyPassword(request.password, user.password):
#         raise HTTPException(status_code=401, detail="Invalid password")
    
#     session_id = createSessionId()
    

#     response.set_cookie(key="session_id", value=session_id, httponly=True)

#     return userRes(status=userRes.Status.SUCCESS, message="Login successful")
