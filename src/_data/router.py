from fastapi import HTTPException, APIRouter, Response, Request
from .schemas import *
from .models import Data
from src._session.service import validate_session_guard

# from src._user.service import isExisted

city_data = {
    "Taipei": {"city_name": "Taipei", "population": 2_480_881},
    "Phoenix": {"city_name": "Phoenix", "population": 1_675_144},
}

router = APIRouter(prefix="/api/search", tags=["Data Management"])


@router.get(("/city/{city_name}"), response_model=cityRes)
async def search_city(city_name: str, fastapi_request: Request):

    session_id = fastapi_request.cookies.get("session_id")
    await validate_session_guard(
        session_id=session_id, fastapi_request=fastapi_request, loginFlag=False
    )

    city_info = city_data.get(city_name)
    if city_info is None:
        raise HTTPException(status_code=404, detail="City not found")

    return city_info


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
