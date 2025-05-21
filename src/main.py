import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.__utils.env import env
from src.redis_untils.service import initRedis
from src._user.router import router as userRouter


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

app.include_router(userRouter)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=env.port)