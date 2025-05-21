from pydantic import BaseModel, EmailStr
from enum import Enum

class userReq(BaseModel):
    username: str
    usermail: EmailStr
    password: str

class userRes(BaseModel):
    class Status(str, Enum):
        SUCCESS = "success"
        FAIL = "fail"
    status: Status
    message: str

