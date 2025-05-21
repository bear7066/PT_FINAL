from .models import User
from .schemas import userReq
import bcrypt
from src.__utils.env import env
import logging


async def isExisted(usermail: str):
    return await User.isExisted(usermail=usermail)


def hashPassword(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode()


async def insertNewUser(userReq: userReq, password: str):
    user = User(username=userReq.username, usermail=userReq.usermail ,password=password)
    user.save()


async def ensureSuperAdmin():
    maybeSuperAdmin = list(User.find(User.usermail == "superadmin@mail.com.tw").all())

    if not maybeSuperAdmin:
        superAdmin = User(
            username="SuperAdmin",
            usermail="superadmin@mail.com.tw",
            password=hashPassword(env.superadmin_password),
        )
        superAdmin.save()
        logging.debug("Super Admin created")
    else:
        logging.debug("Super Admin already exists")


def getUserByMail(usermail: str):
    return User.find(User.usermail == usermail).first()


def verifyPassword(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())