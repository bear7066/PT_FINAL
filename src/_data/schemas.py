from pydantic import BaseModel, EmailStr

# from enum import Enum


class dataReq(BaseModel):
    username: str
    usermail: EmailStr


class dataRes(BaseModel):
    a: str
    b: str
    c: str


class cityRes(BaseModel):
    city_name: str
    population: int
