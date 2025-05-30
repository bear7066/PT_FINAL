import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.__utils.env import env
from src.redis_untils.service import initRedis
from src._user.router import router as userRouter
from src.__utils.middleware import SessionGuard
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logging.basicConfig(level=logging.getLevelName(env.log_level))
        await initRedis()
        yield
    except Exception as err:
        logging.critical(err, exc_info=err)
    finally:
        logging.debug("Exiting Lifespan")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionGuard)
app.include_router(userRouter)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=env.port)
